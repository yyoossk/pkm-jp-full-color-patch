import sys; sys.path.insert(0,'/home/claude/sameboy-harness/python'); sys.path.insert(0,'/home/claude/repo/gold-kanto-johto/tools/check'); sys.path.insert(0,'/home/claude/repo/gold-kanto-johto/tools')
from gr import GR; from walker import W
from jpchar import ENC
from PIL import Image
import time
HAI=bytes([ENC['は'],ENC['い']])
R='/home/claude/work/out/gold_full.gbc'
g=GR(R); w=W(g,R)
def setfl(n, v):
    n-=0x998; a=0xD790+n//8; b=n%8; x=g.peek(a)[0]; g.poke(a,(x|(1<<b)) if v else (x&~(1<<b)))
def yesno(): return HAI in bytes(g.peek(0xC3A0,360))
g.load_state('jo0.st'); g.wait(2)
for i,f in enumerate([0x9C9,0x9CA,0x9CB]): setfl(f, i==0)
g.poke(0xD9C6,26); g.poke(0xD9C7,131); g.poke(0xD9C9,5); g.poke(0xD9C8,7); g.poke(0xCF20,255); g.poke(0xFFA1,0xF1); g.poke(0xD14B,1); g.wait(200)
w.t0=time.time(); w.budget=60
fr=[]
def sh(): g.shot('/tmp/tt.png'); fr.append(Image.open('/tmp/tt.png').copy())
for tries in range(6):
    w.settle(); objs=[]
    for i in range(2,13):
        b=g.peek(0xD1F2+0x28*i,0x14)
        if b[0] and b[1]!=19: objs.append((b[0x10]-4,b[0x11]-4))
    ox,oy=objs[0]
    for d,(dx,dy) in [('U',(0,-1)),('D',(0,1)),('L',(-1,0)),('R',(1,0))]:
        if w.goto_safe(ox-dx,oy-dy): w.face(d); break
    g.press('A',4,40)
    if HAI in bytes(g.peek(0xC3A0,360)) or g.peek(0xC3A0+20*12)[0]==0x79: break
for k in range(14):
    sh()
    if yesno() and k<6: g.press('B',4,50)     # 1つめの はい／いいえ に いいえ
    else: g.press('A',4,50)
out=Image.new('RGB',(160*7,144*2))
for i,im in enumerate(fr): out.paste(im,((i%7)*160,(i//7)*144))
out.save('/tmp/tt7.png')
