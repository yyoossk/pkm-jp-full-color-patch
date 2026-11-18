"""ジョウトの 人・看板に 話しかけて 出る 文を 3つの ROM で くらべる"""
import sys, pickle
sys.path.insert(0,'/home/claude/sameboy-harness/python'); sys.path.insert(0,'/home/claude/repo/gold-kanto-johto/tools/check')
from gr import GR; from walker import W, DIRS
J, T = pickle.load(open('jlist.pkl','rb'))
ROMS = {'base': '/home/claude/work/goldsrc/base.gbc', 'kit': '/home/claude/work/ref/kin64.gbc', 'full': '/home/claude/work/out/gold_full.gbc'}
OPP = {'U': 'D', 'D': 'U', 'L': 'R', 'R': 'L'}
# 話しかける 所の 一覧（full の マップで 決める）
g0 = GR(ROMS['full']); w0 = W(g0, ROMS['full'])
JOBS = []
for mid in J:
    m = w0.maps[mid]; a = m['attr']; c = w0.coll(mid)
    occ = {(o[2] - 4, o[1] - 4) for o in a['objs']}
    tg = [('o', i, (o[2] - 4, o[1] - 4)) for i, o in enumerate(a['objs'])] + [('b', i, (b[1], b[0])) for i, b in enumerate(a['bgs'])]
    for kind, i, (tx, ty) in tg:
        for d, (dx, dy) in DIRS.items():
            sx, sy = tx - dx, ty - dy           # ここに 立って d を 向く
            if (sx, sy) in occ: continue
            v = c(sx, sy)
            if v is None or not w0.passable(v, (sx, sy), d) and v not in (0,): continue
            if (w0.rom[w0.CP + v] & 0x0F) != 0: continue
            JOBS.append((mid, kind, i, sx, sy, d)); break
g0.close()
print('しらべる 数', len(JOBS), flush=True)
out = {}
for n, R in [(a, ROMS[a]) for a in sys.argv[1:]]:
    g = GR(R)
    for job in JOBS:
        mid, kind, i, x, y, d = job
        g.load_state('jt_%s.st' % n); g.wait(2)
        g.poke(0xD9C6, mid[0]); g.poke(0xD9C7, mid[1]); g.poke(0xD9C9, x); g.poke(0xD9C8, y)
        g.poke(0xCF20, 255); g.poke(0xFFA1, 0xF1); g.poke(0xD14B, 1)
        g.wait(130); g.press(d, 2, 12); g.press('A', 4, 50)
        pages = []
        for k in range(7):
            t = g.peek(0xC3A0 + 20 * 12, 120)
            if not pages or pages[-1] != t: pages.append(t)
            g.press('A', 4, 50)
        out[(n,) + job] = pages
        if len(out) % 100 == 0: print(n, len(out), flush=True)
    g.close(); print(n, 'おわり', flush=True)
    pickle.dump((JOBS, out), open('jtalk_%s.pkl' % n, 'wb'))
