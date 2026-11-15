"""第28弾：サファリゾーン（赤）・サファリゲーム を 金へ。
   クリスタル版の サファリの しくみ（バンク $6E）を 新しい バンク SB の 同じ 住所へ うつし、金の 住所に 読みかえる。
     6E:$5000〜$50B7  歩数・ボールの ゆれ・つり・おわりの しらべ・はじめ・おわり（第28弾）
     6E:$7140         サファリの マップの 中か（carry）
     6E:$7400〜$76C6  サファリの 戦い（ボール・エサ・いし・にげる）、6E:$7800〜 スタートメニューの 歩数と ボール
     6E:$62E4・$6826・$6A03〜 その セリフと 文字
   フック（金）：
     0F:$405A DoBattle の ld a,[wBattleType]〜（13 バイト）→ farcall。サファリなら 戦いを して DoBattle から もどる
     03:$7F16 ボールの ゆれ（8 バイト）→ farcall（ゆれの 数は 中で wThrownBallWobbleCount から）
     03:$524D つり（farcall Fish）→ カントーの つり（第57弾 47:$7174）→ サファリの つり → 金の Fish
     25:$6AB2 CountStep の farcall → 歩数を へらしてから 元の farcall
     04:$6B6D・$6B7A スタートメニューの むしとり大会の 表示 → サファリゲーム中も
   クリスタル版の 0F:$7FE0（敵の 絵を 消す）は 金の SlideBattlePicOut（0F:$534A〜$537C）を SB に うつして よぶ。
"""
import sys
sys.path.insert(0, '/home/claude/work/scripts')
from asmx import L, RX, RAM_FIX, CSD, GJ, GB
def fo(b, a): return b * 0x4000 + a - 0x4000

SAF = 0x6E
BT_SAFARI = 0x0D
CALLASM = {(SAF, 0x507D), (SAF, 0x5099), (SAF, 0x50AE)}   # マップの スクリプトが よぶ もの
# うつす 所（クリスタル版 6E の 住所。SB でも 同じ 住所）
CODE = [(0x5000, 0x5075), (0x507D, 0x50B8), (0x7140, 0x7151),
        (0x7400, 0x74B3), (0x74BB, 0x759C), (0x75AD, 0x76C7), (0x7800, 0x7837)]
DATA = [(0x5075, 0x507D), (0x62E4, 0x6307), (0x6826, 0x68FF), (0x6A03, 0x6A35), (0x74B3, 0x74BB), (0x759C, 0x75AD),
        (0x7837, 0x7844)]
TEXTS = [(0x62E4, 0x6307), (0x6826, 0x68FF), (0x6A1E, 0x6A35)]     # セリフ（つづけて 並んでいる）
MENU_DBA = [0x75A7, 0x75AA]                                       # 戦いの メニューの dba（バンク）
# ホームの ルーチン（クリスタル → 金）
HOME = {0x0468: 0x033C, 0x0FD2: 0x0EC1, 0x1041: 0x0F30, 0x1057: 0x0F46, 0x1BD2: 0x1A51, 0x1D00: 0x1B59,
        0x1FED: 0x1E40,   # InterpretBattleMenu → 金の _2DMenu（金の 戦いの メニューは みな これ）
        0x1F82: 0x1DD6, 0x2F5E: 0x305E, 0x2F9D: 0x309D, 0x2FAD: 0x30AD, 0x2FD7: 0x30BB, 0x3069: 0x3114,
        0x30E5: 0x317A, 0x30F0: 0x3185, 0x3164: 0x31F9, 0x32C5: 0x34A8, 0x3826: 0x39DD, 0x3BB0: 0x3D45, 0x3BE2: 0x3D77}
VALUE = {0x002B, 0x0100, 0x0102, 0x0203, 0x0307, 0x16E1, 0x16E2, 0x8105, 0x760A, 0x3C0A}   # 住所でない 数（SFX・アニメの 番号・lb bc）
SRAM = {0xAD10: 0xAD10}          # sBoxCount（金も 同じ）
GOLD_RAM = {
    0xC6EF: 0xCBC1, 0xC6F0: 0xCBC2, 0xC6F1: 0xCBC3,   # wSafariMonAngerCount・Eating・その次（金も 同じ 並び）
    0xD21C: 0xD0C6,                                   # wThrownBallWobbleCount
    0xD237: 0xD0E1, 0xD245: 0xD0EF, 0xD247: 0xD0F1, 0xD249: 0xD0F3, 0xD250: 0xD0FA,   # wEnemyMon（種類・状態・HP・最大HP・すばやさの 下）
    0xD25C: 0xD106, 0xD270: 0xD11B,                   # wEnemyMonCatchRate・wBaseCatchRate
    0xDC9D: 0xD9E8,                                   # wPartyCount
}
for _v in range(0xC4A0, 0xC608): GOLD_RAM[_v] = _v - 0x100      # wTilemap（クリスタル $C4A0 → 金 $C3A0）
NAMED = {0xC644, 0xC67D, 0xCF54, 0xCF7C, 0xCFB6, 0xCFB7, 0xCFBE, 0xD092, 0xD0AE, 0xD0C6, 0xD261, 0xD840,
         0xDC3F, 0xDC40, 0xDC41, 0xDC7B, 0xDC7C, 0xC2DD, 0xC616}  # 名前で 読みかえる（下で 名前を たしかめる）
CHECK = {0xC644: 'wWildMon', 0xC67D: 'wBattleAnimParam', 0xCF54: 'wCurSpecies', 0xCF7C: 'wMenuCursorPosition',
         0xCFB6: 'wFXAnimID', 0xCFB7: 'wFXAnimID', 0xCFBE: 'wBattleAfterAnim', 0xD092: 'wBattleMenuCursorPosition',
         0xD0AE: 'wBattleResult', 0xD0C6: 'wCurItem', 0xD261: 'wBattleType', 0xD840: 'wStatusFlags2',
         0xDC3F: 'wSafariBallsRemaining', 0xDC40: 'wSafariTimeRemaining', 0xDC41: 'wSafariTimeRemaining',
         0xDC7B: 'wMapGroup', 0xDC7C: 'wMapNumber', 0xC616: 'wEnemyMonNickname'}

def ram(v):
    if v in GOLD_RAM: return GOLD_RAM[v]
    if v in RAM_FIX: return RAM_FIX[v]
    g, nm = RX.x(v)
    assert v in CHECK and nm.split('+')[0] == CHECK[v], ('RAM', hex(v), nm)
    return g

def xlat_code(M, g, SB, lo, hi, far, notes):
    p = lo
    while p < hi:
        o = fo(SAF, p); d = fo(SB, p); op = M[o]; ln = L[op]
        if op in (0xE0, 0xF0) and M[o + 1] >= 0x80:
            h = M[o + 1]; assert 0x8D <= h < 0xE8, hex(h); g[d + 1] = h + 2
        if ln == 3 and op != 0x31:
            v = M[o + 1] | M[o + 2] << 8; nv = None
            if op == 0x21 and M[o - 2] == 0x3E and M[o + 3] == 0xCF:      # farcall
                fb = M[o - 1]; t = far[(fb, v)]; g[d - 1] = t[0]; nv = t[1]
            elif v in VALUE: nv = v
            elif v < 0x4000: nv = HOME[v]
            elif v < 0x8000:
                assert any(a <= v < b for a, b in CODE + DATA), ('バンクの中', hex(p), hex(v)); nv = v
            elif 0xA000 <= v < 0xC000: nv = SRAM[v]
            elif 0xC000 <= v < 0xE000: nv = ram(v)
            else: raise Exception(hex(v))
            g[d + 1] = nv & 0xFF; g[d + 2] = nv >> 8
        p += ln

def fix_texts(M, g, SB, lo, hi):
    """つづけて 並んだ セリフの RAM（text_ram など）を 読みかえる"""
    p = lo
    while p < hi:
        c = M[fo(SAF, p)]; p += 1
        if c == 0x00:
            while M[fo(SAF, p)] not in (0x50, 0x57, 0x58): p += 1
            if M[fo(SAF, p)] == 0x50: p += 1
            else: p += 1                         # done / prompt：この セリフの おわり
        elif c in (0x01, 0x02, 0x09):
            v = M[fo(SAF, p)] | M[fo(SAF, p + 1)] << 8; nv = ram(v)
            g[fo(SB, p)] = nv & 0xFF; g[fo(SB, p) + 1] = nv >> 8; p += 2 + (c != 0x01)
        elif c in (0x50, 0x57, 0x58): pass       # セリフの おわり（次の セリフへ）
        elif c in (0x05, 0x06, 0x07, 0x0A, 0x0B, 0x0D): pass
        else: raise Exception('セリフの 命令 %02X at %04X' % (c, p - 1))

RGBDS = '/home/claude/rgbds-src'
def hud_bytes(addr):
    import subprocess, tempfile, os
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'asm', 'gold_safarihud.asm')
    G = open('/home/claude/work/ref/kin_late.gbc', 'rb').read(); font = fo(0x3E, 0x42F2)   # 金の 字（1bpp、$80〜）
    tiles = [0x7F, 0xE5, 0xB1, 0xC4, 0xCE, 0x9C, 0xE3, 0xA6, 0xBA] + list(range(0xF6, 0x100))
    inc = ''
    for t in tiles:
        b = bytes(8) if t < 0x80 else G[font + (t - 0x80) * 8:font + (t - 0x80) * 8 + 8]
        inc += '\tdb $%02x, %s\n' % (t, ', '.join('$%02x' % x for x in b))
    with tempfile.TemporaryDirectory() as d:
        open(d + '/glyphs.inc', 'w').write(inc)
        subprocess.run([RGBDS + '/rgbasm', '-I', d, '-DHUD_ADDR=%d' % addr, '-o', d + '/h.o', src], check=True)
        subprocess.run([RGBDS + '/rgblink', '-n', d + '/h.sym', '-o', d + '/h.gbc', d + '/h.o'], check=True)
        r = open(d + '/h.gbc', 'rb').read()
        end = max(int(l.split()[0].split(':')[1], 16) for l in open(d + '/h.sym') if l[:3] == '01:')
    b = r[0x4000 + addr - 0x4000:]
    n = len(b.rstrip(b'\x00\xff'))
    return b[:n]

class A:
    """小さな アセンブラ（ラベルつき）"""
    def __init__(s, base): s.base = base; s.b = bytearray(); s.lab = {}; s.fix = []
    def here(s): return s.base + len(s.b)
    def db(s, *x): s.b += bytes(x)
    def dw(s, v):
        if isinstance(v, str): s.fix.append((len(s.b), v, 'w')); s.b += b'\0\0'
        else: s.b += bytes([v & 0xFF, v >> 8])
    def jr(s, op, lab): s.b.append(op); s.fix.append((len(s.b), lab, 'r')); s.b.append(0)
    def L(s, n): s.lab[n] = s.here()
    def far(s, bank, addr): s.db(0x3E, bank, 0x21); s.dw(addr); s.db(0xCF)
    def fin(s, ext={}):
        lab = dict(ext); lab.update(s.lab)
        for pos, n, k in s.fix:
            v = lab[n]
            if k == 'w': s.b[pos] = v & 0xFF; s.b[pos + 1] = v >> 8
            else:
                r = v - (s.base + pos + 1); assert -128 <= r < 128, n; s.b[pos] = r & 0xFF
        return bytes(s.b)

def apply(g, M, E, log):
    SB = E.next_bank; E.next_bank += 1
    G = bytes(g)
    # ---- 金の まわりの ルーチン
    FISH = (0x24, 0x68C9)                        # 金の Fish
    assert G[fo(0x03, 0x524D):fo(0x03, 0x5253)] == bytes([0x3E, 0x24, 0x21, 0xC9, 0x68, 0xCF])
    POKEBALL_MID = (0x03, 0x6D7C)                # クリスタル 03:$6CAB（PokeBallEffect の なか：投げる ところから）
    assert G[fo(0x03, 0x6D7C):fo(0x03, 0x6D7F)] == bytes([0x21, 0xEF, 0xD0])
    far = {(0x0F, 0x6DE3): (GB['EmptyBattleTextbox'], GJ['EmptyBattleTextbox']),
           (0x33, 0x40E5): (GB['PlayBattleAnim'], GJ['PlayBattleAnim']),
           (0x03, 0x6CAB): POKEBALL_MID, (0x0F, 0x7FE0): (SB, 0x7FE0), (0x24, 0x6975): FISH}
    # ---- うつす
    for a, b in CODE + DATA: g[fo(SB, a):fo(SB, b)] = M[fo(SAF, a):fo(SAF, b)]
    notes = []
    for a, b in CODE: xlat_code(M, g, SB, a, b, far, notes)
    for a, b in TEXTS: fix_texts(M, g, SB, a, b)
    for a in MENU_DBA: assert g[fo(SB, a)] == SAF; g[fo(SB, a)] = SB
    # 敵の 絵を 消す（クリスタル版 0F:$7FE0）：金の SlideBattlePicOut を うつして
    sl = G[fo(0x0F, 0x534A):fo(0x0F, 0x537D)]; assert sl[:3] == bytes([0xE0, 0xB1, 0x4F]) and sl[-1] == 0xC9
    g[fo(SB, 0x534A):fo(SB, 0x537D)] = sl
    g[fo(SB, 0x7FE0):fo(SB, 0x7FE8)] = bytes([0x21, 0xB2, 0xC3, 0x3E, 0x08, 0xC3, 0x4A, 0x53])   # hlcoord 18,0
    # ---- 新しい ルーチン（$5100〜）
    a = A(0x5100)
    # DoBattle（0F:$405A）
    a.L('battle')
    a.db(0xFA); a.dw(0xD10B); a.db(0xFE, BT_SAFARI); a.jr(0x28, 'b_go')
    a.db(0xA7); a.jr(0x28, 'b_chk'); a.db(0xFE, 0x04); a.jr(0x20, 'b_norm')
    a.L('b_chk'); a.db(0xFA); a.dw(0xD565); a.db(0xCB, 0x4F); a.jr(0x28, 'b_norm')
    a.db(0xCD); a.dw(0x7140); a.jr(0x30, 'b_norm')
    a.db(0x3E, BT_SAFARI, 0xEA); a.dw(0xD10B)
    a.L('b_go'); a.db(0xCD); a.dw(0x7400); a.db(0x37, 0xC9)                       # call 戦い / scf / ret
    a.L('b_norm'); a.db(0xFA); a.dw(0xD10B); a.db(0xFE, 0x02); a.jr(0x28, 'b_z'); a.db(0xFE, 0x03); a.jr(0x28, 'b_z')
    a.db(0xF6, 0x01, 0xC9)                                                          # nz nc
    a.L('b_z'); a.db(0xAF, 0xC9)                                                    # z nc
    # ボールの ゆれ（03:$7F16）
    a.L('wobble'); a.db(0xFA); a.dw(0xD0C6); a.db(0x4F); a.db(0xC3); a.dw(0x5019)
    # 歩く（25:$6AB2 の farcall の かわり）
    a.L('step'); a.db(0xCD); a.dw(0x5000); a.far(0x24, 0x413E); a.db(0xC9)
    # スタートメニュー（04:$6B6D・$6B7A）
    a.L('mbox'); a.db(0xFA); a.dw(0xD565); a.db(0xCB, 0x4F); a.jr(0x20, 'm_saf'); a.db(0xCB, 0x57, 0xC8)
    a.far(0x09, 0x4B1E); a.db(0xC9)
    a.L('mprint'); a.db(0xFA); a.dw(0xD565); a.db(0xCB, 0x4F); a.jr(0x20, 'm_saf'); a.db(0xCB, 0x57, 0xC8)
    a.far(0x09, 0x4B29); a.db(0xC9)
    a.L('m_saf'); a.db(0xC3); a.dw(0x7800)
    # カントーの つり（第57弾 47:$7174〜$71DA。表 47:$71DB・$7242）
    a.L('kfish'); kf = M[fo(0x47, 0x7174):fo(0x47, 0x71DB)]; kb = a.here(); a.b += kf
    def kpatch(off, val):
        p = kb - a.base + off; a.b[p] = val & 0xFF; a.b[p + 1] = val >> 8
    assert kf[0:3] == bytes([0xFA, 0x7B, 0xDC]) and kf[4:7] == bytes([0xFA, 0x7C, 0xDC]); kpatch(1, 0xD9C6); kpatch(5, 0xD9C7)
    assert kf[8] == 0x21; kmaps_at = 9
    assert kf[0x1F:0x26] == bytes([0x3E, 0x6E, 0x21, 0x34, 0x50, 0xCF, 0xC9])
    a.b[kb - a.base + 0x1F:kb - a.base + 0x26] = bytes([0xC3, 0x34, 0x50, 0, 0, 0, 0])   # → サファリの つり
    for k in range(len(kf)):
        if kf[k] == 0xCD and kf[k + 1:k + 3] == bytes([0x5E, 0x2F]): kpatch(k + 1, 0x305E)
    assert kf[0x4A] == 0x21 and kf[0x4B:0x4D] == bytes([0x42, 0x72]); krod_at = 0x4B
    tab = bytearray(); n = 0; o = fo(0x47, 0x71DB); skipped = []
    while M[o] != 0xFF:
        cg, cn, sg = M[o:o + 3]; o += 3
        import c2g
        nm = c2g.CMAP.get((cg, cn)); nm = c2g.MAPALIAS.get(nm, nm)
        if nm not in c2g.GMAP: skipped.append(nm or (cg, cn)); continue
        gg, gn = c2g.GMAP[nm]
        tab += bytes([gg, gn, sg]); n += 1
    tab += b'\xff'
    a.L('kmaps'); kpatch(kmaps_at, a.here()); a.b += tab
    ng = max(t for t in tab[2::3] if t != 0xFF) + 1 if n else 0
    a.L('krod'); kpatch(krod_at, a.here()); a.b += M[fo(0x47, 0x7242):fo(0x47, 0x7242) + 8 * 24]
    blob = a.fin(); assert a.base + len(blob) <= 0x534A
    g[fo(SB, a.base):fo(SB, a.base) + len(blob)] = blob
    lab = a.lab
    # ---- フック
    o = fo(0x0F, 0x405A); assert G[o:o + 13] == bytes.fromhex('fa0bd1fe02cae240fe03cae240')
    g[o:o + 13] = bytes([0x3E, SB, 0x21, lab['battle'] & 0xFF, lab['battle'] >> 8, 0xCF, 0xD8, 0xCA, 0xE2, 0x40, 0, 0, 0])
    o = fo(0x03, 0x7F16); assert G[o:o + 7] == bytes.fromhex('fa41d1a70e00c0')   # 金は ret nz
    g[o:o + 6] = bytes([0x3E, SB, 0x21, lab['wobble'] & 0xFF, lab['wobble'] >> 8, 0xCF])
    o = fo(0x03, 0x524D); g[o + 1] = SB; g[o + 3] = lab['kfish'] & 0xFF; g[o + 4] = lab['kfish'] >> 8
    o = fo(0x25, 0x6AB2); assert G[o:o + 6] == bytes([0x3E, 0x24, 0x21, 0x3E, 0x41, 0xCF])
    g[o + 1] = SB; g[o + 3] = lab['step'] & 0xFF; g[o + 4] = lab['step'] >> 8
    for adr, l_ in ((0x6B6D, 'mbox'), (0x6B7A, 'mprint')):
        o = fo(0x04, adr); assert G[o:o + 3] == bytes([0x21, 0x65, 0xD5])
        n_ = 13 if adr == 0x6B6D else 15
        g[o:o + n_] = bytes([0x3E, SB, 0x21, lab[l_] & 0xFF, lab[l_] >> 8, 0xCF, 0xC9]) + bytes(n_ - 7)
    # ---- 第65弾：歩いて いる ときの 表示（asm/gold_safarihud.asm を この バンクの $7900 に）
    hud = hud_bytes(0x7900); assert len(hud) < 0x300
    g[fo(SB, 0x7900):fo(SB, 0x7900) + len(hud)] = hud
    o = fo(0x25, 0x672C); assert G[o:o + 6] == bytes([0x3E, 0x03, 0x21, 0xA9, 0x57, 0xCF])
    g[o + 1] = SB; g[o + 3] = 0x00; g[o + 4] = 0x79
    # ---- マップの スクリプトの callasm
    for k in CALLASM: E.loc[k] = (SB, k[1])
    log.append('サファリ：バンク %02X（戦い 7400・メニュー 7800・つり %04X：カントー %d マップ、とばした %s）' %
               (SB, lab['kfish'], n, skipped))
    return SB
