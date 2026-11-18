import sys, pickle, os
sys.path.insert(0,'/home/claude/sameboy-harness/python'); sys.path.insert(0,'/home/claude/repo/gold-kanto-johto/tools/check')
from gr import GR
exec(open('jcmp.py').read().split("print('==== ジョウト')")[0].replace("for mid, (d, dk) in diffs.items(): print(mid, '移植で変わった', d, '| キットで変わった', dk)",""))
J = [m for m in sorted(names) if johto(m) and m in M['full'] and m in M['kit']]
ROMS = {'base': '/home/claude/work/goldsrc/base.gbc', 'kit': '/home/claude/work/ref/kin64.gbc', 'full': '/home/claude/work/out/gold_full.gbc'}
def target(mid):
    m = M['full'][mid]
    if m['warps']: x, y, _ = m['warps'][0]; return x, y
    return m['w'], m['h']
for n, R in ROMS.items():
    g = GR(R)
    for mid in J:
        x, y = target(mid)
        g.load_state('jt_%s.st' % n); g.wait(2)
        g.poke(0xD9C6, mid[0]); g.poke(0xD9C7, mid[1]); g.poke(0xD9C9, x); g.poke(0xD9C8, y)
        g.poke(0xCF20, 255); g.poke(0xFFA1, 0xF1); g.poke(0xD14B, 1)
        g.wait(150); g.shot('jt/%s_%02d_%03d.png' % (n, mid[0], mid[1]))
        g.wait(240); g.shot('jt/%s_%02d_%03db.png' % (n, mid[0], mid[1]))
        p = g.peek(0xD9C6, 2)
        if tuple(p) != mid: print(n, mid, 'ちがう マップ', p)
    g.close(); print(n, 'おわり', flush=True)
