"""python3 run.py 前の段 新しい段 [秒]：前の段の ステートから stage 関数を 動かして 新しい段で 保存"""
import sys, time, os
sys.path.insert(0,'/home/claude/sameboy-harness/python'); sys.path.insert(0,'/home/claude/repo/gold-kanto-johto/tools/check')
from gr import GR; from walker import W
from PIL import Image
R='/home/claude/work/out/gold_full.gbc'; D='/home/claude/work/wt'
src, dst, fn = sys.argv[1], sys.argv[2], sys.argv[3]; budget = float(sys.argv[4]) if len(sys.argv) > 4 else 95
g=GR(R); g.load_state('%s/%s.st'%(D,src)); g.wait(3)
w=W(g,R); w.t0=time.time(); w.budget=budget; sh=[]
def s(tag):
    if len(sh) >= 60: return
    p='%s/shots/%s_%02d.png'%(D,dst,len(sh)); g.shot(p); sh.append(p)
w.shot=s
import stages
try: done = getattr(stages, fn)(w, s)
except TimeoutError: done = False; w.log.append('時間切れ')
g.save_state('%s/%s.st'%(D,dst))
print(dst, 'done' if done else 'not done', w.pos(), [ (p['sp'],p['lv'],p['hp'],p['mx']) for p in w.party()], w.log[-3:])
g.close()
if sh:
    im=Image.new('RGB',(160*6,144*((len(sh)+5)//6)))
    for k,p in enumerate(sh): im.paste(Image.open(p),((k%6)*160,(k//6)*144))
    im.save('%s/shots/%s.png'%(D,dst))
