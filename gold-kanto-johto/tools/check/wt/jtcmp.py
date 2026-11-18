import pickle, sys
import team
inv = {v: k for k, v in team.cm.items()}
names = pickle.load(open('goldnames.pkl','rb'))
JOBS, K = pickle.load(open('jtalk_kit.pkl','rb')); _, F = pickle.load(open('jtalk_full.pkl','rb'))
MODMAPS = {(3,18),(3,32),(3,41),(3,68),(5,1),(9,6),(11,6),(15,1),(15,3),(15,5),(15,6),(15,10),(15,11),(19,4),(24,4),(24,5),(24,6),(26,10)}
def txt(t):
    rows = [t[i*20:(i+1)*20] for i in range(6)]
    return ' / '.join(''.join(inv.get(c, '·') if c not in (0x7f,) else ' ' for c in r[1:19]).strip() for r in (rows[2], rows[4]))
same = diff = 0; rep = []
def norm(pages):
    ps = [p for p in pages if p[0] == 121 and p[19] == 123]
    ts = [txt(p) for p in ps]; out = []
    for i, s in enumerate(ts):
        nxt = ts[i + 1] if i + 1 < len(ts) else ''
        a = s.replace(' / ', '').replace(' ', ''); b = nxt.replace(' / ', '').replace(' ', '')
        if b.startswith(a) and a != b: continue
        if out and out[-1] == s: continue
        out.append(s)
    return out[:4]
for job in JOBS:
    k = norm(K[('kit',) + job]); f = norm(F[('full',) + job])
    if k == f: same += 1; continue
    diff += 1
    rep.append((job[0] in MODMAPS, job, k, f))
print('同じ', same, 'ちがう', diff, '（MODで かえた マップ', sum(1 for r in rep if r[0]), '）')
for m, job, a, b in rep:
    if m: continue
    print(job, names[job[0]]); print('  キット:', a); print('  いま  :', b)
