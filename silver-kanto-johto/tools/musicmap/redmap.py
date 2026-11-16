import sys,re,os
sys.path.insert(0,'/home/claude/pkm-jp-full-color-patch/silver-kanto-johto/tools')
from gsc import fo,r16
import cmaps,port,gsc
R='/home/claude/pkm-jp-full-color-patch/silver-kanto-johto/build/銀カントー＆ジョウト.gbc'
PR='/home/claude/ref/pokered'
def camel(n): return ''.join(w.capitalize() if not w.isdigit() else w for w in n.split('_'))
red={}   # NAME -> (w,h,blk)
for l in open(PR+'/constants/map_constants.asm'):
    m=re.match(r'\s*map_const (\w+),\s*(\d+),\s*(\d+)',l)
    if m: red[m.group(1)]=(int(m.group(2)),int(m.group(3)))
# blk file per map from data/maps/headers? use maps/<Camel>.blk; find via map_header file names
blkfile={}
for f in os.listdir(PR+'/data/maps/headers'):
    s=open(PR+'/data/maps/headers/'+f).read()
    m=re.search(r'map_header (\w+), (\w+),',s)
    if m: blkfile[m.group(2)]=m.group(1)
song={}
for l in open(PR+'/data/maps/songs.asm'):
    m=re.match(r'\s*db (MUSIC_\w+),.*; (\w+)',l)
    if m: song[m.group(2)]=m.group(1)
blks={}
for n,(w,h) in red.items():
    c=blkfile.get(n)
    if not c: continue
    # find blk path via data/maps/maps? use grep in maps.asm for INCBIN
    blks[n]=None
inc={}
for f in ['/data/maps/map_header_pointers.asm']: pass
txt=open(PR+'/maps.asm').read() if os.path.exists(PR+'/maps.asm') else ''
for m in re.finditer(r'(\w+)_Blocks:\s*INCBIN "maps/(\w+)\.blk"',txt): inc[m.group(1)]=m.group(2)
r=open(R,'rb').read()
gt=fo(0x25,0x40ED)
def ours(g,m):
    hp=fo(0x25,r16(r,gt+2*(g-1)))+9*(m-1); h=r[hp:hp+9]; ao=fo(h[0],r16(h,3))
    H,W=r[ao+1],r[ao+2]; bb,bp=r[ao+3],r16(r,ao+4); return h,W,H,r[fo(bb,bp):fo(bb,bp)+W*H]
bykey={}
for n,(w,h) in red.items():
    c=blkfile.get(n)
    if not c or c not in inc: continue
    b=open(PR+'/maps/%s.blk'%inc[c],'rb').read()
    bykey.setdefault((w,h,b),[]).append(n)
print(len(bykey),'red blk', len(song),'songs', len(inc))
cmod=open(cmaps.CMOD,'rb').read(); CM=cmaps.CMaps(cmod)
P=port.Port.__new__(port.Port); P.CM=CM; P.SM=gsc.Maps(r[:0x100000], gsc.PG+'/constants/map_constants.asm'); P.todo={}
inv={}
for k in CM.hdr:
    try: inv[P.x_map(*k)]=CM.name.get(k)
    except Exception: pass
res={}
for g in range(1,27):
    base=fo(0x25,r16(r,gt+2*(g-1))); end=fo(0x25,r16(r,gt+2*g)) if g<26 else base+9*158
    m=1
    while base+9*(m-1)<end:
        try:
            h,W,H,b=ours(g,m)
            key=(W,H,bytes(b)); names=bykey.get(key)
            how='blk'
            if not names:
                nm=inv.get((g,m))
                names=[nm] if nm in song else None; how='name'
            res[(g,m)]=(names,how,h[6])
        except Exception as e: res[(g,m)]=(None,'err',None)
        m+=1
import pickle; pickle.dump(res,open('res.pkl','wb'))
if __name__=='__main__':
  for k,v in sorted(res.items()):
    if v[0]: print(k,v[0][:2],v[1],v[2],song[v[0][0]])
