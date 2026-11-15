import sys; sys.path.insert(0,'/home/claude/work/scripts')
from maps import groups, w, CMGP, GMGP
def fo(b,a): return a if a<0x4000 else b*0x4000+a-0x4000
def maplist(rom, mgp, repo):
    out=[]
    for gi,(gn,maps) in enumerate(groups(repo)):
        base=fo(mgp//0x4000, w(rom,mgp+2*gi))
        for mi,mn in enumerate(maps):
            h=base+9*mi; out.append(dict(name=mn,group=gi+1,num=mi+1,hdr=h,attr=fo(rom[h],w(rom,h+3))))
    return out
