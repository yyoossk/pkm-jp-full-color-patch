import sys; sys.path.insert(0,'/home/claude/sameboy-harness/python'); sys.path.insert(0,'/home/claude/repo/gold-kanto-johto/tools/check')
from gr import GR; from walker import W, DIRS
from collections import deque
R='/home/claude/work/out/gold_full.gbc'; g=GR(R); w=W(g,R)
GYMS={'CeladonX':((21,21),(7,15)),'Pewter':((14,4),(6,11)),'Cerulean':((7,6),(7,13)),'Vermilion':((12,11),(7,15)),'Celadon':((21,21),None),'Saffron':((25,4),(9,14)),'Viridian':((23,4),(7,13))}
for nm,(mid,gd) in GYMS.items():
    m=w.maps[mid]; c=w.coll(mid)
    doors=[(x,y) for x,y,t in m['warps'] if t!=mid]
    occ={(o[2]-4,o[1]-4) for o in m['attr']['objs']}
    cells=[(x,y-1) for x,y in doors]
    if gd is None:
        print(nm,'doors',doors,'cells',cells); continue
    occ.discard(gd)
    res={}
    for p in cells:
        best=None
        for tgt,face in (((p[0]+1,p[1]),'L'),((p[0]-1,p[1]),'R')):
            if tgt in occ or tgt in cells and tgt!=p: pass
            # BFS from guide
            prev={gd:None}; q=deque([gd])
            while q:
                a=q.popleft()
                if a==tgt: break
                for d,(dx,dy) in DIRS.items():
                    n=(a[0]+dx,a[1]+dy)
                    if n in prev or n in occ or n==p or n==(p[0],p[1]-1): continue
                    v=c(*n)
                    if v is None or not w.passable(v,a,d): continue
                    prev[n]=(a,d); q.append(n)
            if tgt in prev:
                path=[]; k=tgt
                while prev[k]: k,d=prev[k]; path.append(d)
                path=path[::-1]
                if best is None or len(path)<len(best[0]): best=(path,face,tgt)
        res[p]=best
    print(nm, mid, 'guide',gd,'doors',doors, res)
