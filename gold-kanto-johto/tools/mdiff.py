"""MOD とバニラの 同じ住所を 並べて 逆アセンブル： mdiff.py BANK ADDR [N] [before]"""
import sys; sys.path.insert(0, '/home/claude/work/scripts')
from dis import dis
V = open('/home/claude/roms/Pocket Monsters - Crystal Version (Japan).gbc', 'rb').read()
M = open('/home/claude/work/ref/crystal_kj.gbc', 'rb').read()
b = int(sys.argv[1], 16); a = int(sys.argv[2], 16); n = int(sys.argv[3]) if len(sys.argv) > 3 else 10
bef = int(sys.argv[4]) if len(sys.argv) > 4 else 6
a0 = a - bef
x = dis(V, b, a0, n).split('\n'); y = dis(M, b, a0, n).split('\n')
for i in range(max(len(x), len(y))):
    l = x[i] if i < len(x) else ''; r = y[i] if i < len(y) else ''
    print('%-44s | %s%s' % (l[:44], r, '' if l == r else '   <<'))
