import sys, pickle
sys.path.insert(0,'/home/claude/sameboy-harness/python'); sys.path.insert(0,'/home/claude/repo/gold-kanto-johto/tools/check')
from gr import GR; from walker import W
J, T = pickle.load(open('jlist.pkl','rb')); names = pickle.load(open('goldnames.pkl','rb'))
ROMS = {'kit': '/home/claude/work/ref/kin64.gbc', 'full': '/home/claude/work/out/gold_full.gbc'}
g0 = GR(ROMS['full']); w0 = W(g0, ROMS['full'])
jobs = []
for mid in J:
    if mid not in w0.maps: continue
    m = w0.maps[mid]; c = w0.coll(mid); found = None
    for y in range(m['h'] * 2):
        for x in range(m['w'] * 2 - 1):
            if c(x, y) == 0x18 and c(x + 1, y) == 0x18: found = (x, y); break
        if found: break
    if found: jobs.append((mid, found))
g0.close(); print('草むら', len(jobs), flush=True)
out = {}
for n, R in ROMS.items():
    g = GR(R)
    for mid, (x, y) in jobs:
        res = []
        for t in range(3):
            g.load_state('jt_%s.st' % n); g.wait(2); g.poke(0xD9B1, 0)
            g.poke(0xD9C6, mid[0]); g.poke(0xD9C7, mid[1]); g.poke(0xD9C9, x); g.poke(0xD9C8, y)
            g.poke(0xCF20, 255); g.poke(0xFFA1, 0xF1); g.poke(0xD14B, 1); g.wait(130 + 37 * t)
            for k in range(60):
                g.press('R' if k % 2 == 0 else 'L', 12, 6)
                if g.peek(0xD108)[0]: break
            if g.peek(0xD108)[0]:
                g.wait(200); res.append((g.peek(0xD0E1)[0], g.peek(0xD0EE)[0]))
            else: res.append(None)
        out[(n, mid)] = res
    g.close(); print(n, 'おわり', flush=True)
pickle.dump((jobs, out), open('jwild.pkl', 'wb'))
