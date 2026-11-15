import sys; sys.path.insert(0,'/home/claude/work/scripts')
from cmaps import *; from cwalk import Walk, fo
def changed_maps(van, mod):
    res=[]; allnotes={}
    for m in maplist(mod,CMGP,'pokecrystal'):
        W=Walk(mod)
        try:
            at=W.map(m['attr'],m['name']); W.run()
        except Exception as e:
            res.append((m['name'],'ERR '+str(e))); continue
        diff=mod[m['hdr']:m['hdr']+9]!=van[m['hdr']:m['hdr']+9]
        a=m['attr']; diff|=mod[a:a+12+len(at['connections'])]!=van[a:a+12+len(at['connections'])]
        eo=fo(at['scbank'],at['events']); el=2+3+5*len(at['warps'])+8*len(at['coords'])+5*len(at['bgs'])+1+13*len(at['objs']); diff|=mod[eo:eo+el]!=van[eo:eo+el]
        so=fo(at['scbank'],at['scripts']); sl=2+4*len(at['scenes'])+3*len(at['callbacks']); diff|=mod[so:so+sl]!=van[so:so+sl]
        bo=fo(at['blkbank'],at['blk']); n=at['h']*at['w']; diff|=mod[bo:bo+n]!=van[bo:bo+n]
        for k,b in W.blobs.items():
            o=fo(b['bank'],b['addr']); 
            if mod[o:o+len(b['data'])]!=van[o:o+len(b['data'])]: diff=True
        if diff: res.append((m['name'],len(W.blobs),W.notes))
    return res
