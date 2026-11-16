import sys,re,os
exec(open('redmap.py').read().split("if __name__")[0])
sys.path.insert(0,'/home/claude/test'); import play
# red warps
rw={}
for f in os.listdir(PR+'/data/maps/objects'):
    s=open(PR+'/data/maps/objects/'+f).read()
    c=f[:-4]
    nm=[n for n,cc in blkfile.items() if cc==c]
    if not nm: continue
    ws=[(int(m.group(1)),int(m.group(2)),m.group(3)) for m in re.finditer(r'warp_event\s+(\d+),\s*(\d+),\s*(\w+),',s)]
    for n in nm: rw[n]=ws
M={k:v[0][0] for k,v in res.items() if v[0] and len(v[0])==1}
# also include LAST_MAP handling: skip
changed=True
while changed:
    changed=False
    for o,rn in list(M.items()):
        try: ow=play.events(*o)['warps']
        except Exception: continue
        for (x,y,dest) in rw.get(rn,[]):
            if dest=='LAST_MAP': continue
            for w in ow:
                if (w[0],w[1])==(y,x):
                    o2=(w[3],w[4])
                    if o2 not in M: M[o2]=dest; changed=True
import pickle; pickle.dump(M,open('M.pkl','wb'))
matched=set(M.values())
print(len(M), [n for n in song if n not in matched and n in blkfile])
