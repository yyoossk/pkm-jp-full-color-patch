import numpy as np, glob, pickle, os
from PIL import Image
names = pickle.load(open('goldnames.pkl','rb'))
L = lambda p: np.asarray(Image.open(p).convert('RGB')).astype(int)
rows = []
for f in sorted(glob.glob('jt/full_*b.png')):
    k = f.replace('full_', 'kit_'); b = f.replace('full_', 'base_')
    F, K, B = L(f), L(k), L(b)
    fk = (np.abs(F - K).sum(2) > 0).mean(); kb = (np.abs(K - B).sum(2) > 0).mean()
    g, m = os.path.basename(f)[5:-5].split('_'); mid = (int(g), int(m))
    rows.append((fk, kb, mid, names.get(mid)))
rows.sort(reverse=True)
for r in rows[:60]: print('%.3f %.3f %s %s' % r)
print('同じ', sum(1 for r in rows if r[0] == 0), '/', len(rows))
