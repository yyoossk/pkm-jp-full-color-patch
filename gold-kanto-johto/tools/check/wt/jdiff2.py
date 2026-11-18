import pickle
names = pickle.load(open('goldnames.pkl','rb'))
D = pickle.load(open('jt2.pkl','rb')); J, T = pickle.load(open('jlist.pkl','rb'))
def nd(a, b): return sum(x != y for x, y in zip(a, b))
res = []
for mid in J:
    k, f, b = D[('kit', mid)], D[('full', mid)], D[('base', mid)]
    r = dict(tm=nd(k['tm'], f['tm']), am=nd(k['am'], f['am']), pal=k['pal'] != f['pal'], ow=nd(k['ow'], f['ow']),
             objs=sorted(o[:2] for o in k['objs']) != sorted(o[:2] for o in f['objs']),
             kb_tm=nd(k['tm'], b['tm']), kb_pal=k['pal'] != b['pal'])
    if r['tm'] or r['am'] or r['pal'] or r['ow'] or r['objs']: res.append((mid, names[mid], r))
for x in res: print(x)
print(len(res), '/', len(J))
