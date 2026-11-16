import re,os,sys,pickle
exec(open('redmap.py').read().split("if __name__")[0])
sys.path.insert(0,'/home/claude/test'); import play
M=pickle.load(open('M.pkl','rb'))
# red tileset per map
rts={}
for f in os.listdir(PR+'/data/maps/headers'):
    s=open(PR+'/data/maps/headers/'+f).read()
    m=re.search(r'map_header \w+, (\w+), (\w+)',s)
    if m: rts[m.group(1)]=m.group(2)
blockfile={}
for l in open(PR+'/gfx/tilesets.asm'):
    for lab in re.findall(r'(\w+)_Block::',l): blockfile[lab]=None
cur=[]
for l in open(PR+'/gfx/tilesets.asm'):
    labs=re.findall(r'(\w+)_Block::',l); cur+=labs
    m=re.search(r'INCBIN "(gfx/blocksets/\w+\.bst)"',l)
    if m:
        for c in cur: blockfile[c]=m.group(1)
        cur=[]
coll={}; cur=[]
for l in open(PR+'/data/tilesets/collision_tile_ids.asm'):
    cur+=re.findall(r'(\w+)_Coll::',l)
    m=re.search(r'coll_tiles(.*)',l)
    if m and cur:
        v=[int(x.strip().lstrip('$'),16) for x in m.group(1).split(',') if x.strip()]
        for c in cur: coll[c]=set(v)
        cur=[]
TSN={}
for i,l in enumerate([l for l in open(PR+'/data/tilesets/tileset_headers.asm') if l.strip().startswith('tileset ')]):
    TSN[re.match(r'\s*tileset (\w+)',l).group(1).upper()]=re.match(r'\s*tileset (\w+)',l).group(1)
def camel_ts(c):
    for k,v in TSN.items():
        if k==c.replace('_',''): return v
    return None
def redgrid(name):
    w,h=red[name]; c=blkfile[name]; b=open(PR+'/maps/%s.blk'%inc[c],'rb').read()
    ts=camel_ts(rts[name]); bst=open(PR+'/'+blockfile[ts],'rb').read(); cl=coll[ts]
    g=[[0]*(w*2) for _ in range(h*2)]
    for y in range(h*2):
        for x in range(w*2):
            blk=b[(y//2)*w+x//2]; t=bst[blk*16+((y%2)*2+1)*4+(x%2)*2]
            g[y][x]=1 if t in cl else 0
    return g,ts
def redwarps(name):
    c=blkfile[name]; s=open(PR+'/data/maps/objects/%s.asm'%c).read()
    return set((int(m.group(2)),int(m.group(1))) for m in re.finditer(r'warp_event\s+(\d+),\s*(\d+)',s))
res=[]
for o,n in sorted(M.items()):
    if o[0] in (16,20): continue
    try: rg,ts=redgrid(n)
    except Exception as e: continue
    og=play.grid(*o)
    if len(og)!=len(rg) or len(og[0])!=len(rg[0]): res.append((o,n,'size',len(og[0]),len(og),len(rg[0]),len(rg))); continue
    ow=set((w[0],w[1]) for w in play.events(*o)['warps']); rw=redwarps(n)
    a=[];b=[];wd=[]
    for y in range(len(og)):
        for x in range(len(og[0])):
            ours=og[y][x] in play.PASS; red_=rg[y][x]==1
            if ours and not red_ and (y,x) not in rw: a.append((y,x,og[y][x]))
            if red_ and not ours: b.append((y,x,og[y][x]))
            if 0x70<=og[y][x]<=0x7F and (y,x) not in ow: wd.append((y,x,og[y][x]))
    res.append((o,n,ts,a,b,wd,sorted(ow^rw)))
pickle.dump(res,open('collres.pkl','wb'))
for r_ in res:
    if r_[2]=='size': continue
    o,n,ts,a,b,wd,wx=r_
    if a or b or wd or wx: print(o,n,ts,'walk+',len(a),a[:6],'walk-',len(b),b[:6],'fakewarp',wd[:6],'warpdiff',wx[:6])
print('size-mismatch',sum(1 for r_ in res if r_[2]=='size'), 'compared',sum(1 for r_ in res if r_[2]!='size'))
