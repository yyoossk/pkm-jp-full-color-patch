# 英語版の 全関数を 日本版から さがして、RAM と 関数の 対応表を 作る（emap.json）
import json
from efind import *
from collections import defaultdict, Counter
ram = defaultdict(Counter); fn = {}
names = [n for n,(b,a) in syms.items() if '.' not in n and b < 0x40]
for n in names:
    b,a = syms[n]
    try: h = find(n, 20)
    except Exception: continue
    if len(h) != 1: continue
    fn[n] = h[0]
    try: ps = pairs(n, h[0], n=48)
    except Exception: continue
    for p in ps:
        if p[0] == 'diff@': break
        ev, jv = int(p[0],16), int(p[1],16)
        if ev >= 0xc000: ram[ev][jv] += 1
out = {'fn': {k:list(v) for k,v in fn.items()}, 'ram': {hex(k): v.most_common(3) for k,v in ram.items()}}
json.dump(out, open('/tmp/sv/emap.json','w'))
print(len(fn), len(ram))
