"""クリスタル版の 小さな asm を 金へ 読みかえる（命令の 長さで 区切り、住所の 引数を 名前で 読みかえ）"""
import re, sys
sys.path.insert(0, '/home/claude/work/scripts')
from near import load, near
import rammap

L = [1] * 256
for op in [0x06,0x0E,0x16,0x1E,0x26,0x2E,0x36,0x3E,0x18,0x20,0x28,0x30,0x38,0xC6,0xCE,0xD6,0xDE,0xE6,0xEE,0xF6,0xFE,0xE0,0xF0,0xE8,0xF8,0xCB,0x10]: L[op] = 2
for op in [0x01,0x11,0x21,0x31,0x08,0xC2,0xC3,0xCA,0xD2,0xDA,0xC4,0xCC,0xCD,0xD4,0xDC,0xEA,0xFA]: L[op] = 3
JR = {0x18, 0x20, 0x28, 0x30, 0x38}
JPS = {0xC2, 0xC3, 0xCA, 0xD2, 0xDA, 0xC4, 0xCC, 0xCD, 0xD4, 0xDC}
END = {0xC9, 0xC3, 0xD9, 0x18, 0xE9}
HW_OK = set(range(0x00, 0x80))          # ハードウェアの レジスタ（$FF00〜$FF7F）は 同じ

CS = load('/home/claude/work/ref/crystal_jp.sym')
CSD = {}
for l in open('/home/claude/work/ref/crystal_jp.sym'):
    m = re.match(r'([0-9a-f]+):([0-9a-f]+) (\S+)', l)
    if m: CSD[(int(m.group(1), 16) if int(m.group(2), 16) >= 0x4000 else 0, int(m.group(2), 16))] = m.group(3)
GJ = {}; GB = {}
for l in open('/home/claude/work/goldsrc/src/jp_all.inc'):
    m = re.match(r'DEF J(B?)_(\S+) EQU \$([0-9a-f]+)', l)
    if m: (GB if m.group(1) else GJ)[m.group(2)] = int(m.group(3), 16)
RX = rammap.RamX()
RAM_FIX = {0xC2DD: 0xD165, 0xD071: 0xCF9D, 0xD296: 0xD143}   # D296：NewPokedexEntry の ポケモン（金 wNamedObjectIndex）   # 確かめた もの（c2g と 同じ）
# クリスタル版の 足した フラグ（$800〜：$DA01〜）・シーンの 変数（$DA5F〜$DA64）→ 金（gold_flags.py の 並べ方）
for _k in range(51): RAM_FIX[0xDA01 + _k] = 0xD70D + _k
for _k in range(51, 67): RAM_FIX[0xDA01 + _k] = 0xD790 + (_k - 51)
for _k in range(6): RAM_FIX[0xDA5F + _k] = 0xD7A4 + _k
HRAM = {}                                     # クリスタル hXX → 金 hXX（必要に なったら 足す）

def fo(b, a): return b * 0x4000 + a - 0x4000

def extent(M, bank, a):
    o = fo(bank, a); p = o; mx = o
    while True:
        op = M[p]; n = L[op]
        if op in JR:
            d = M[p + 1]; t = p + 2 + (d - 256 if d > 127 else d); mx = max(mx, t)
        if op in (0xC2, 0xCA, 0xD2, 0xDA, 0xC3):
            t = fo(bank, M[p + 1] | M[p + 2] << 8)
            if o <= t < o + 0x400: mx = max(mx, t)
        p += n
        if op in END and p > mx: return p - o
        if p - o > 0x300: raise Exception('長すぎる')

def xlat(M, bank, a, new_addr, notes, size=None, code_len=None):
    """→ (bytes, 問題の リスト)"""
    o = fo(bank, a); n = size or extent(M, bank, a); b = bytearray(M[o:o + n]); prob = []
    p = 0
    while p < (code_len or n):
        op = b[p]; ln = L[op]
        if op in (0xE0, 0xF0) and b[p + 1] not in HW_OK:
            h = b[p + 1]
            if h in HRAM: b[p + 1] = HRAM[h]
            else: prob.append('hram $FF%02X' % h)
        if ln == 3 and op not in (0x31,):
            v = b[p + 1] | b[p + 2] << 8; nv = None
            if 0xC000 <= v < 0xE000:
                nv = RAM_FIX.get(v)
                if nv is None:
                    gv, nm = RX.x(v)
                    if gv is None: prob.append('RAM %04X（%s）' % (v, nm))
                    else: nv = gv; notes.append('RAM %04X → %04X（%s）' % (v, gv, nm))
            elif v < 0x4000 and (op in JPS or op in (0x21, 0x11, 0x01)):
                nm = CSD.get((0, v))
                if nm and nm in GJ and GB.get(nm, 0) == 0: nv = GJ[nm]; notes.append('%s %04X → %04X' % (nm, v, nv))
                elif op in JPS: prob.append('ホーム %04X（%s）' % (v, near(CS, 0, v)))
            elif 0x4000 <= v < 0x8000:
                if op == 0x21 and p >= 2 and b[p - 2] == 0x3E and p + 3 < n and b[p + 3] == 0xCF: pass   # farcall（下で）
                elif a <= v < a + n: nv = new_addr + (v - a)
                elif op in JPS: prob.append('バンクの中 %02X:%04X（%s）' % (bank, v, near(CS, bank, v)))
                else: prob.append('データ? %02X:%04X' % (bank, v))
            if nv is not None: b[p + 1] = nv & 0xFF; b[p + 2] = nv >> 8
        # farcall：ld a,bb / ld hl,xxxx / rst 08
        if op == 0x3E and p + 5 < n and b[p + 2] == 0x21 and b[p + 5] == 0xCF:
            fb = b[p + 1]; fa = M[o + p + 3] | M[o + p + 4] << 8
            nm = CSD.get((fb, fa))
            if nm and nm in GJ and nm in GB: b[p + 1] = GB[nm]; b[p + 3] = GJ[nm] & 0xFF; b[p + 4] = GJ[nm] >> 8; notes.append('farcall %s' % nm)
            else: prob.append('farcall %02X:%04X（%s）' % (fb, fa, near(CS, fb, fa)))
        p += ln
    return bytes(b), prob
