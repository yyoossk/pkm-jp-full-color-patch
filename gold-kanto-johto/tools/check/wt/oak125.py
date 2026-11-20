import sys; sys.path.insert(0,'/home/claude/sameboy-harness/python'); sys.path.insert(0,'/home/claude/repo/gold-kanto-johto/tools/check'); sys.path.insert(0,'/home/claude/work/scripts')
from gr import GR; from walker import W
P='/home/claude/work/out/gold_full.gbc'
res=[]
for var in range(10):
    g=GR(P); g.load_state('/tmp/wt/st_g_7.st'); g.wait(5+var*3)
    w=W(g,P); w.talk_to(4,2)
    bad=None; seen=set()
    for i in range(140):
        g.wait(7+var*5+(i*var)%11); g.press('A',2+var%3,3+var)
        pc=g.pc(); b=int(pc.split('bank=')[1][:2],16); a=int(pc[3:7],16)
        p=w.pos(); seen.add(p[:2])
        if p[:2]!=(13,6): bad=('map',p,pc); break
    g.shot('/tmp/wt/oak125_%d.png'%var)
    dex=w.objs()
    res.append((var,bad,w.pos(),dex)); print(var,bad,w.pos(),dex,flush=True)
    g.close()
