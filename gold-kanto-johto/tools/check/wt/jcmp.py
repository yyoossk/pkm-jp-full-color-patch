import sys; sys.path.insert(0,'/home/claude/repo/gold-kanto-johto/tools/check'); sys.path.insert(0,'/home/claude/repo/gold-kanto-johto/tools')
from redmap import port_maps
R = {n: bytearray(open(p,'rb').read()) for n,p in [('base','/home/claude/work/goldsrc/base.gbc'),('kit','/home/claude/work/ref/kin64.gbc'),('full','/home/claude/work/out/gold_full.gbc')]}
M = {n: port_maps(g) for n,g in R.items()}
for n in M: print(n, len(M[n]))
def sig(m, g):
    a = m['attr']; h = m['hdr']
    return dict(size=(m['w'],m['h']), blk=m['blk'], ts=m['ts'], hdr=bytes(g[h+5:h+9]), hdr2=g[h+2],
                warps=m['warps'], objs=[tuple(o[:11]) for o in a['objs']], bgs=[tuple(b[:3]) for b in a['bgs']],
                coords=[bytes(c[:5]) for c in a['coords']], conn=a.get('conn'))
diffs = {}
for mid in sorted(M['base']):
    if mid not in M['full'] or mid not in M['kit']: print('ない', mid, mid in M['kit'], mid in M['full']); continue
    sb, sk, sf = sig(M['base'][mid], R['base']), sig(M['kit'][mid], R['kit']), sig(M['full'][mid], R['full'])
    d = [k for k in sb if sf[k] != sk[k]]
    dk = [k for k in sb if sk[k] != sb[k]]
    if d or dk: diffs[mid] = (d, dk)
for mid, (d, dk) in diffs.items(): print(mid, '移植で変わった', d, '| キットで変わった', dk)
import pickle
names = pickle.load(open('goldnames.pkl','rb'))
KANTO3 = ('MOUNT_MOON','ROCK_TUNNEL','VICTORY_ROAD','DIGLETTS','SEAFOAM','TOHJO','CERULEAN_CAVE','POWER_PLANT','UNDERGROUND','KANTO','SILPH','POKEMON_TOWER','ROCKET_HIDEOUT_K')
def johto(mid):
    g, n = mid; nm = names.get(mid, '')
    if not nm: return False
    if g in (1,2,4,5,8,9,10,11,22,24,26,19,15,20): return not nm.startswith('VERMILION')
    if g == 3: return not any(k in nm for k in KANTO3)
    if g == 16: return nm.startswith('ROUTE_23') is False and False
    return False
print('==== ジョウト')
J = [m for m in sorted(names) if johto(m)]
print(len(J))
for mid in J:
    if mid in diffs: print(mid, names[mid], diffs[mid])
print('==== くわしく')
for mid in J:
    if mid in diffs and (diffs[mid][0]):
        a = M['kit'][mid]['attr']; b = M['full'][mid]['attr']
        print(mid, names[mid])
        for k in ('objs','coords','bgs'):
            x = [bytes(o).hex() for o in a[k]]; y = [bytes(o).hex() for o in b[k]]
            if x != y:
                for i in range(max(len(x),len(y))):
                    xi = x[i] if i < len(x) else '-'; yi = y[i] if i < len(y) else '-'
                    if xi != yi: print('  ', k, i, xi, '->', yi)
