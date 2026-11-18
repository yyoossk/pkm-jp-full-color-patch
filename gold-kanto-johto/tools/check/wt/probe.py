"""python3 probe.py 段 [キー列...] -> shots/probe_N.png を並べる。キー: A B U D L R S w(待つ)"""
import sys
sys.path.insert(0,'/home/claude/sameboy-harness/python')
from gr import GR
from PIL import Image
R='/home/claude/work/out/gold_full.gbc'; D='/home/claude/work/wt'
g=GR(R); g.load_state('%s/%s.st'%(D,sys.argv[1])); g.wait(3)
sh=[]
def s():
    p='%s/shots/probe_%02d.png'%(D,len(sh)); g.shot(p); sh.append(p)
s()
save=None
for k in sys.argv[2:]:
    if k.startswith('>'): save=k[1:]; continue
    if k=='w': g.wait(60)
    else: g.press(k, 4, 40)
    s()
if save: g.save_state('%s/%s.st'%(D,save))
im=Image.new('RGB',(160*6,144*((len(sh)+5)//6)))
for i,p in enumerate(sh): im.paste(Image.open(p),((i%6)*160,(i//6)*144))
im.save('%s/shots/probe.png'%D); g.close()
