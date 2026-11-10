import json,sys,re
from efind import syms
m = json.load(open('/tmp/sv/emap.json'))
ram = {int(k,16): v for k,v in m['ram'].items()}
fn = m['fn']
keys = sorted(ram)
def J(name):
    if name in fn and syms[name][0] < 0x40 and syms[name][1] < 0x8000: b,a = fn[name]; return f'{b:02x}:{a:04x}'
    b,a = syms[name]
    if a in ram: 
        c = ram[a]; return f'${c[0][0]:04x}' + ('' if len(c)==1 else f' ({c})')
    # 近い もの
    lo = max([k for k in keys if k <= a and a-k < 0x40], default=None)
    hi = min([k for k in keys if k >= a and k-a < 0x40], default=None)
    s = []
    for k in (lo,hi):
        if k is not None: s.append(f'{hex(k)}→${ram[k][0][0]:04x} => ${a - k + ram[k][0][0]:04x}?')
    return ' / '.join(s) or '??'
for n in [x for x in sys.argv[1:] if x in syms or print(x, "?? no sym")]:
    print(f'{n:36} E {syms[n][0]:02x}:{syms[n][1]:04x}  J {J(n)}')
