import sys; sys.path.insert(0,'/home/claude/work/scripts'); from changed import *; from consts import *; from cwalk import Walk, fo
from collections import defaultdict
def collect(van, mod, names=None):
    M={m['name']:m for m in maplist(mod,CMGP,'pokecrystal')}
    if names is None: names=[x[0] for x in changed_maps(van,mod)]
    used=defaultdict(set); walks={}
    for nm in names:
        W=Walk(mod)
        try: at=W.map(M[nm]['attr'],nm); W.run()
        except Exception as e: print('skip',nm,e); continue
        walks[nm]=(W,at)
        for ob in at['objs']:
            used[('obj','sprite')].add(ob[0]); fl=ob[11]|ob[12]<<8
            if fl!=0xffff: used[('obj','event_flag')].add(fl)
        for k,b in W.blobs.items():
            for off,t,sem,name in b['fix']:
                o=fo(b['bank'],b['addr'])+off
                v=mod[o] if t=='db' else mod[o]|mod[o+1]<<8 if t in ('dw','map_id') else (mod[o],mod[o+1]|mod[o+2]<<8)
                used[(name,sem)].add(v)
    return used, walks
