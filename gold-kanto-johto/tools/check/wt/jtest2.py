import sys, pickle
sys.path.insert(0,'/home/claude/sameboy-harness/python')
from gr import GR
J, T = pickle.load(open('jlist.pkl','rb'))
ROMS = {'base': '/home/claude/work/goldsrc/base.gbc', 'kit': '/home/claude/work/ref/kin64.gbc', 'full': '/home/claude/work/out/gold_full.gbc'}
out = {}
for n, R in ROMS.items():
    g = GR(R)
    for mid in J:
        x, y = T[mid]
        g.load_state('jt_%s.st' % n); g.wait(2)
        g.poke(0xD9C6, mid[0]); g.poke(0xD9C7, mid[1]); g.poke(0xD9C9, x); g.poke(0xD9C8, y)
        g.poke(0xCF20, 255); g.poke(0xFFA1, 0xF1); g.poke(0xD14B, 1)
        g.wait(390)
        tm = g.peek(0xC3A0, 360); am = g.peek(0xCCCD, 360); pal = g.pals()
        objs = []
        for i in range(1, 13):
            b = g.peek(0xD1F2 + 0x28 * i, 0x28)
            if b[0]: objs.append((b[0], b[1], b[0x10], b[0x11]))   # sprite, map obj index, x, y
        out[(n, mid)] = dict(tm=tm, am=am, pal=pal, objs=objs, ow=g.peek(0xC700, 256))
    g.close(); print(n, 'おわり', flush=True)
pickle.dump(out, open('jt2.pkl', 'wb'))
