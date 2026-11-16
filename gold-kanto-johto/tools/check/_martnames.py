import sys,re
sys.argv=['x','/home/claude/work/out/gold_full.gbc']
src=open('/tmp/t2/cv.py').read().split("out = []; nd = 0")[0]
exec(src)
from cwalk import Walk
isrc=open('/home/claude/repo/gold/pokegold/constants/item_constants.asm').read()
names={}; v=0
inm=False
for l in isrc.splitlines():
    if l.startswith('MACRO'): inm=True; continue
    if l.startswith('ENDM'): inm=False; continue
    if inm: continue
    m=re.match(r'\s*const (\w+)',l)
    if m: names[v]=m.group(1); v+=1; continue
    m=re.match(r'\s*add_tm (\w+)',l)
    if m: names[v]='TM_'+m.group(1); v+=1; continue
    m=re.match(r'\s*add_hm (\w+)',l)
    if m: names[v]='HM_'+m.group(1); v+=1
def mart(k):
    p=r16(fo(5,0x65EA)+2*k); o=fo(5,p); n=g[o]; return [names.get(i,hex(i)) for i in g[o+1:o+1+n]]
Y=open('/home/claude/work/mod/ref/pokered/data/items/marts.asm').read()
ym=dict((a,[x.strip().replace('THUNDER_STONE','THUNDERSTONE') for x in b.split(',')]) for a,b in re.findall(r'(\w+)ClerkText::\s*\n\s*script_mart (.*)',Y))
ym.update(dict((a,[x.strip() for x in b.split(',')]) for a,b in re.findall(r'(\w+)Clerk\dText::\s*\n\s*script_mart (.*)',Y)))
# per yellow map with mart: find matched port map, then pokemart ids
for name, ymp in sorted(ymaps.items()):
    keys=[k for k in re.findall(r'(\w+?)(?:Clerk\d?)?Text::\s*\n\s*script_mart',Y) if k.startswith(name.replace('Mart','Mart').replace('CeladonDeptStore','CeladonMart'))]
    lists=re.findall(r'(%s\w*)Text::\s*\n\s*script_mart (.*)'%re.escape(name.replace('CeladonDeptStore','CeladonMart').replace('IndigoPlateauLobby','IndigoPlateauLobby')),Y)
    if not lists: continue
    best=None
    for pm in pmaps:
        if (pm['w'],pm['h'])!=(ymp['w'],ymp['h']): continue
        s=sum(a==b for a,b in zip(pm['blk'],ymp['blk']))/len(ymp['blk'])
        if not best or s>best[0]: best=(s,pm)
    pm=best[1]; a=Walk(g).map(fo(g[pm['hdr']],r16(pm['hdr']+3)),'x'); ids=[]
    for ob in a['objs']:
        sp=fo(a['scbank'],ob[9]|ob[10]<<8)
        mm=re.search(rb'\x93\x00(.)',g[sp:sp+16],re.S)
        if mm: ids.append(mm.group(1)[0])
    print('==',name,pm['id'],'%.0f%%'%(best[0]*100))
    for (ln,items) in lists:
        yl=[x.strip().replace('THUNDER_STONE','THUNDERSTONE') for x in items.split(',')]
        found=[k for k in ids if sorted(mart(k))==sorted(yl)]
        print('  ',ln, 'OK' if found else ('ちがう', yl, [mart(k) for k in ids]))
