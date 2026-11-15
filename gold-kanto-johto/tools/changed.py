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
        eo=fo(at['scbank'],at['events']); diff|=mod[eo:eo+300]!=van[eo:eo+300]
        bo=fo(at['blkbank'],at['blk']); n=at['h']*at['w']; diff|=mod[bo:bo+n]!=van[bo:bo+n]
        for k,b in W.blobs.items():
            o=fo(b['bank'],b['addr']); 
            if mod[o:o+len(b['data'])]!=van[o:o+len(b['data'])]: diff=True
        if diff: res.append((m['name'],len(W.blobs),W.notes))
    return res
