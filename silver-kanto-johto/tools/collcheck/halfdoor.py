import sys,pickle; sys.path.insert(0,'/home/claude/test'); import play
M=pickle.load(open('M.pkl','rb'))
PASS=set(play.PASS)
out=[]
for o,n in sorted(M.items()):
    if o[0] in (16,20): continue
    try: cg=play.grid(*o); ws=play.events(*o)['warps']
    except Exception: continue
    wp={(w[0],w[1]):w for w in ws}
    H,W=len(cg),len(cg[0])
    for (y,x),w in wp.items():
        for dx in (-1,1):
            nx=x+dx
            if not (0<=nx<W) or (y,nx) in wp: continue
            c=cg[y][nx]
            if c in PASS:
                # door-like: the tile beyond in one vertical direction is wall for both
                for dy in (-1,1):
                    yy=y+dy
                    if 0<=yy<H and cg[yy][x] not in PASS and cg[yy][nx] not in PASS:
                        out.append((o,n,(y,x),(y,nx),'%02x'%cg[y][x],'%02x'%c,'wall at dy',dy))
for r in out: print(r)
print(len(out))
