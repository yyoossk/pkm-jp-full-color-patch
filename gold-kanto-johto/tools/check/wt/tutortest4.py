"""ジム以外の 6人：わざマシンの フラグ なし／あり で 話しかける"""
import sys; sys.path.insert(0,'/home/claude/sameboy-harness/python'); sys.path.insert(0,'/home/claude/repo/gold-kanto-johto/tools/check')
from gr import GR; from walker import W, DIRS
from PIL import Image
R='/home/claude/work/out/gold_full.gbc'
NP = [((0x90,0x4D82),[0x9C4]), ((0x92,0x735A),[0x607]), ((0xA3,0x6AB3),[0x849]), ((0xA9,0x570C),[0x9C8]), ((0xA2,0x44D3),[0x9DA]), ((0xA9,0x592F),[0x9C9,0x9CA,0x9CB])]
g=GR(R); w=W(g,R)
def fl_addr(n):
    if n < 0x800: return 0xD7AA + n//8, n%8
    if n < 0x998: n-=0x800; return 0xD70D + n//8, n%8
    n-=0x998; return 0xD790 + n//8, n%8
def setfl(n, v):
    a,b=fl_addr(n); x=g.peek(a)[0]; g.poke(a, (x|(1<<b)) if v else (x&~(1<<b)))
targets=[]
for (bk,ptr),fls in NP:
    for mid,m in w.maps.items():
        if m['attr']['scbank']!=bk: continue
        for o in m['attr']['objs']:
            if (o[9]|o[10]<<8)==ptr: targets.append((mid,(o[2]-4,o[1]-4),fls))
print(targets)
rows=[]
for mid,(ox,oy),fls in targets:
    c=w.coll(mid)
    stand=None
    for d,(dx,dy) in DIRS.items():
        sx,sy=ox-dx,oy-dy; v=c(sx,sy)
        if v is not None and (w.rom[w.CP+v]&0x0F)==0 if False else (v==0): stand=(sx,sy,d); break
    for mode in ('none','some','all'):
        g.load_state('jo0.st'); g.wait(2)
        for i,f in enumerate(fls): setfl(f, mode=='all' or (mode=='some' and i==0))
        g.poke(0xD9C6,mid[0]); g.poke(0xD9C7,mid[1]); g.poke(0xD9C9,stand[0]); g.poke(0xD9C8,stand[1])
        g.poke(0xCF20,255); g.poke(0xFFA1,0xF1); g.poke(0xD14B,1); g.wait(200)
        if mid==(26,131) or True:
            # 歩く 人は うごくので、すぐに 話しかける
            pass
        g.press(stand[2],2,8); g.press('A',4,60)
        fr=[]
        for k in range(5):
            g.shot('/tmp/tt.png'); fr.append(Image.open('/tmp/tt.png').copy()); g.press('A',4,50)
        rows.append(fr)
        print(mid,(ox,oy),stand,mode, flush=True)
out=Image.new('RGB',(160*5,144*len(rows)))
for j,fr in enumerate(rows):
    for i,im in enumerate(fr): out.paste(im,(i*160,j*144))
out.save('/tmp/tt4.png')
