"""クリスタルの コードの 形（住所の 引数を ぬいて）で 金の 同じ所を さがす"""
import re, sys
sys.path.insert(0, '/home/claude/work/scripts')
from asmx import L
def pattern(M, o, n):
    """o から n バイトぶんの 命令を、3バイト命令の 引数を ワイルドカードに した 正規表現に"""
    p = 0; out = b''
    while p < n:
        op = M[o + p]; ln = L[op]
        if ln == 3: out += re.escape(bytes([op])) + b'..'
        elif op in (0xE0, 0xF0): out += re.escape(bytes([op])) + b'.'
        else: out += re.escape(bytes(M[o + p:o + p + ln]))
        p += ln
    return re.compile(out, re.S)
def find(M, o, n, G, bank=None):
    pat = pattern(M, o, n); res = []
    lo, hi = (bank * 0x4000, bank * 0x4000 + 0x4000) if bank is not None else (0, len(G))
    if bank == 0: hi = 0x4000
    for m in pat.finditer(G, lo, hi): res.append(m.start())
    return res
def ga(o): return '%02X:%04X' % (o // 0x4000, o % 0x4000 + (0x4000 if o >= 0x4000 else 0))
if __name__ == '__main__':
    M = open('/home/claude/roms/Pocket Monsters - Crystal Version (Japan).gbc', 'rb').read(); G = open('/home/claude/work/ref/kin_late.gbc', 'rb').read()
    b, a = [int(x, 16) for x in sys.argv[1].split(':')]; n = int(sys.argv[2])
    o = b * 0x4000 + a - 0x4000 if a >= 0x4000 else a
    print([ga(x) for x in find(M, o, n, G)])
