"""段ごとに 進める：python3 st.py g|c 段の番号"""
import sys; sys.path.insert(0,'/home/claude/sameboy-harness/python'); sys.path.insert(0,'/home/claude/repo/gold-kanto-johto/tools/check'); sys.path.insert(0,'/home/claude/work/scripts')
from gr import GR; from walker import W; from play import newgame
from PIL import Image
which=sys.argv[1]; stage=int(sys.argv[2]); P='/home/claude/work/out/gold_full.gbc'
rom=P if which=='g' else '/home/claude/work/ref/crystal_kj2.gbc'
kw={} if which=='g' else dict(wmap=0xDC7B,pstruct=0xD4C9,wbattle=0,wbank=1)
if stage==0: g=newgame(rom); g.wait(30)
else: g=GR(rom); g.load_state('/tmp/wt/st_%s_%d.st'%(which,stage-1 if stage!=3 else 1)); g.wait(5)
w=W(g,P,**kw); sh=[]
def s(tag): p='/tmp/wt/st%s%d_%02d.png'%(which,stage,len(sh)); g.shot(p); sh.append(p)
if stage==0:
    w.clear(); w.goto(7,0); g.wait(60); s('1F')
    w.goto(6,3); w.face('L'); g.press('A',4,60); w.clear(); s('ママあと')
    w.goto(2,7); w.step('D'); g.wait(90); s('マサラ')
    w.goto(10,1); w.step('U'); g.wait(30)
    w.advance(s, n=80); s('研究所')
elif stage==1:
    for k in range(12):
        w.advance(s, n=30)
        if w.pos()[:2]==(13,6) and not w.textbox():
            g.wait(60)
            if not w.textbox(): break
        g.wait(30)
    s('自由')
    w.goto(6,4); w.face('U'); g.press('A',4,60)
    for i in range(18): g.wait(40); g.press('A',4,30)
    s('名前のあと')
elif stage==2:
    w.advance(s, n=40); s('自由')
    m=w.maps[w.pos()[:2]]; x,y,_=m['warps'][0]; w.goto(x,y-1); s('出口の前')
    w.step('D'); g.wait(30); s('呼びとめ')
    for i in range(10): g.press('A',4,40); s('t')
if stage==3:
    w.clear(key='B'); w.goto(6,4); s('ボールの下'); w.face('U'); g.press('A',4,60)
    for i in range(18): g.wait(40); s('t'); g.press('A',4,30)
    for i in range(10): g.wait(40); s('t'); g.press('A',4,30)
g.save_state('/tmp/wt/st_%s_%d.st'%(which,stage)); print(which,stage,w.pos()); g.close()
im=Image.new('RGB',(160*6,144*((len(sh)+5)//6)))
for k,p in enumerate(sh): im.paste(Image.open(p),((k%6)*160,(k//6)*144))
im.save('/tmp/wt/st_%s_%d.png'%(which,stage))
