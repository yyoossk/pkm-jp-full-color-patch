"""英語版 pokegold のラベル → 日本版 金 のアドレスを探す。
命令の並びで検索し、16ビットのアドレス（と ldh のアドレス）は無視して照合する。
照合できたら、その部分の命令のオペランドを英→日で対応づける。"""
import re, sys
EN = open('/home/claude/work/pokegold/pokegold.gbc', 'rb').read()
JP = None
SYM = {}; ADDR2 = {}
for l in open('/home/claude/work/pokegold/pokegold.sym'):
    m = re.match(r'([0-9a-f]+):([0-9a-f]+) (\S+)', l)
    if m:
        b, a, n = int(m.group(1), 16), int(m.group(2), 16), m.group(3)
        SYM[n] = (b, a)
LAB = sorted(set((b, a) for b, a in SYM.values() if a < 0x8000))

def off(b, a): return a if a < 0x4000 else b * 0x4000 + a - 0x4000

L1 = set()
L2 = {0x06,0x0e,0x16,0x1e,0x26,0x2e,0x36,0x3e,0x18,0x20,0x28,0x30,0x38,0xc6,0xce,0xd6,0xde,0xe6,0xee,0xf6,0xfe,0xe0,0xf0,0xe8,0xf8,0xcb}
L3 = {0x01,0x11,0x21,0x31,0x08,0xc2,0xc3,0xca,0xd2,0xda,0xc4,0xcc,0xd4,0xdc,0xcd,0xea,0xfa}
def ilen(op): return 3 if op in L3 else 2 if op in L2 else 1

def mask(code):
    """(値, 照合するか) の並び、と命令の先頭位置"""
    out = []; i = 0; starts = []
    while i < len(code):
        op = code[i]; n = ilen(op); starts.append(i)
        out.append((op, True))
        if n == 3:
            out += [(code[i+1] if i+1 < len(code) else 0, False), (code[i+2] if i+2 < len(code) else 0, False)]
        elif n == 2:
            v = code[i+1] if i+1 < len(code) else 0
            out.append((v, op not in (0xe0, 0xf0)))   # ldh のアドレスは無視
        i += n
    return out[:len(code)], starts

def find(pat, rom, lo=0, hi=None):
    hi = hi or len(rom)
    first = [k for k, (v, c) in enumerate(pat) if c]
    res = []
    k0 = first[0]; v0 = pat[k0][0]
    i = rom.find(bytes([v0]), lo + k0)
    while i != -1 and i < hi:
        s = i - k0
        if s + len(pat) <= len(rom) and all(rom[s+k] == v for k, (v, c) in enumerate(pat) if c):
            res.append(s)
        i = rom.find(bytes([v0]), i + 1)
    return res

def endof(b, a):
    for bb, aa in LAB:
        if (bb == b or a < 0x4000) and aa > a:
            if (aa < 0x4000) == (a < 0x4000) and (a < 0x4000 or bb == b): return aa
    return a + 0x40

def locate(name, n=None, jp=None, bank=None):
    jp = jp or JP
    b, a = SYM[name]
    e = endof(b, a)
    n = n or min(e - a, 48)
    code = EN[off(b, a):off(b, a) + n]
    pat, _ = mask(code)
    lo, hi = 0, len(jp)
    if bank is not None: lo, hi = bank * 0x4000, bank * 0x4000 + 0x4000
    r = find(pat, jp, lo, hi)
    return r

def ptr(o):
    return (o // 0x4000, o % 0x4000 + (0x4000 if o >= 0x4000 else 0))

def operands(name, jo, n=None):
    """照合できた所の 16ビット・ldh オペランドの英→日の対応"""
    b, a = SYM[name]
    n = n or (endof(b, a) - a)
    eo = off(b, a); m = {}
    i = 0
    while i < n:
        op = EN[eo+i]; k = ilen(op)
        if JP[jo+i] != op: break
        if k == 3:
            m[(op, EN[eo+i+1] | EN[eo+i+2] << 8)] = JP[jo+i+1] | JP[jo+i+2] << 8
        elif op in (0xe0, 0xf0):
            m[(op, 0xff00 | EN[eo+i+1])] = 0xff00 | JP[jo+i+1]
        i += k
    return m

def load(p):
    global JP; JP = open(p, 'rb').read(); return JP
