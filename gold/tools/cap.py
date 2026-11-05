import sys, json; sys.path.insert(0,'/home/claude/work/sameboy-harness/python')
from gr import GR
res={}
for name,val in (('poke',4),('great',3),('ultra',2),('master',1),('safari',8)):
    g=GR('pika.gbc',state='pm.state'); g.poke(0xcf78,val)
    g.press('A',4,0)
    seen={}
    for f in range(0,420,2):
        g.wait(2)
        o=g.oam()
        ents=[tuple(o[i:i+4]) for i in range(0,160,4) if o[i] and o[i]<100 and o[i+1]>80]
        if not ents: continue
        key=tuple(sorted((e[2],e[3]) for e in ents))
        if key not in seen:
            tiles={t:bytes(g.vpeek(0,0x8000+t*16,16)).hex() for t,_ in key}
            tiles1={t:bytes(g.vpeek(1,0x8000+t*16,16)).hex() for t,_ in key}
            seen[key]=dict(frame=f,ents=ents,tiles=tiles,tiles1=tiles1,pals=g.pals())
    g.close()
    res[name]=[dict(v,key=[list(k) for k in key]) for key,v in seen.items()]
    print(name,len(seen))
json.dump(res,open('balls.json','w'),default=str)
