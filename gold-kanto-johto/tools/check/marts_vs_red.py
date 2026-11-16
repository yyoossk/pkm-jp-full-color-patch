import sys,re,os,glob
sys.argv=['x','/home/claude/work/out/gold_full.gbc']
src=open('/tmp/t2/cv.py').read().split("out = []; nd = 0")[0]
exec(src)
from cwalk import Walk
exec(open('/tmp/t2/mart.py').read().split("# per yellow map")[0].split("from cwalk import Walk")[1])
const2name={}
for f in glob.glob(os.path.join('/home/claude/work/mod/ref/pokeyellow','data/maps/headers/*.asm')):
    m=re.search(r'map_header (\w+), (\w+), (\w+)',open(f).read())
    if m: const2name[m.group(2)]=m.group(1)
def match(ym):
    best=None
    for pm in pmaps:
        if (pm['w'],pm['h'])!=(ym['w'],ym['h']): continue
        s=sum(a==b for a,b in zip(pm['blk'],ym['blk']))/len(ym['blk'])
        if not best or s>best[0]: best=(s,pm)
    return best
pbyid={pm['id']:pm for pm in pmaps}
# yellow: which town warp leads to each mart map
target={}
for f in glob.glob(os.path.join('/home/claude/work/mod/ref/pokeyellow','data/maps/objects/*.asm')):
    town=os.path.basename(f)[:-4]
    for x,y,d in re.findall(r'warp_event\s+(\d+),\s*(\d+),\s*(\w+)',open(f).read()):
        n=const2name.get(d)
        if n and n in ymaps and town in ymaps: target.setdefault(n,(town,int(x),int(y)))
Yt=open('/home/claude/work/mod/ref/pokered/data/items/marts.asm').read()
for name in sorted(ymaps):
    lists=re.findall(r'(%s\w*)Text::\s*\n\s*script_mart (.*)'%re.escape(name.replace('CeladonDeptStore','CeladonMart')),Yt)
    if not lists: continue
    # find port map: via town warp
    pid=None
    if name in target:
        town,x,y=target[name]; b=match(ymaps[town])
        if b and b[0]>0.8:
            a=Walk(g).map(fo(g[b[1]['hdr']],r16(b[1]['hdr']+3)),'x')
            for wv in a['warps']:
                if (wv[1],wv[0])==(x,y): pid=(wv[3],wv[4])
    if pid is None: print('==',name,'見つからない'); continue
    if pid not in pbyid: print('==',name,pid,'?'); continue
    pm=pbyid[pid]; a=Walk(g).map(fo(g[pm['hdr']],r16(pm['hdr']+3)),'x'); ids=[]
    for ob in a['objs']:
        bk,ad=a['scbank'],ob[9]|ob[10]<<8
        for _ in range(3):
            sp=fo(bk,ad)
            if g[sp]==0x04: bk,ad=g[sp+1],g[sp+2]|g[sp+3]<<8
            else: break
        for mm in re.finditer(rb'\x93\x00(.)',g[sp:sp+80],re.S): ids.append(mm.group(1)[0])
    for (ln,items) in lists:
        yl=[x.strip().replace('THUNDER_STONE','THUNDERSTONE') for x in items.split(',')]
        found=[k for k in ids if mart(k)==yl]; fs=[k for k in ids if sorted(mart(k))==sorted(yl)]
        print('==',name,pid,ln, 'OK' if found else 'ならびだけ ちがう' if fs else ('ちがう', yl, [(hex(k),mart(k)) for k in ids]))
