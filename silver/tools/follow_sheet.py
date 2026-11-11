# 連れ歩きの 色の 見くらべ表を 作る（正面・横・後ろ ＝ 今の あて方、右の 2つ ＝ 色1・色2 を 入れかえた とき）
#   python3 tools/follow_sheet.py  → follow_sheet.png（251匹。8匹 ずつ ならぶ）
#   横の 絵（からだの 色）が 正面と 同じに 見える 方を えらぶ。ちがえば tools/follow_gen.py の WALK_SWAP_FIX に 足す。
# 金の ファイルの ならび（src/follow_data.inc の FollowerOwnPals・FollowerWalkPals、gfxdata/follow_icon/%03d.2bpp
#   〔1匹 6コマ：0 正面・1 後ろ・2 横・3 正面歩き・4 後ろ歩き・5 横歩き、1コマ 4タイル〕）を 読む。
import sys
from PIL import Image, ImageDraw
G=sys.argv[1] if len(sys.argv)>1 else './'
inc=open(G+'src/follow_data.inc').read()
def tbl(name):
    s=inc.split(name+':')[1]; v=[]
    for l in s.split('\n')[1:]:
        if not l.strip().startswith('dw'): break
        v.append([int(x.strip()[1:],16) for x in l.split(';')[0].strip()[2:].split(',')])
    return v
OWN=tbl('FollowerOwnPals'); WALK=tbl('FollowerWalkPals')
def rgb(c): return ((c&31)*8,((c>>5)&31)*8,((c>>10)&31)*8)
def frame(d,f,pal):
    im=Image.new('RGB',(16,16),(255,255,255))
    for k,(tx,ty) in enumerate([(0,0),(1,0),(0,1),(1,1)]):
        t=d[(f*4+k)*16:(f*4+k)*16+16]
        for y in range(8):
            for x in range(8):
                c=((t[y*2]>>(7-x))&1)|(((t[y*2+1]>>(7-x))&1)<<1)
                im.putpixel((tx*8+x,ty*8+y),[(255,255,255),rgb(pal[0]),rgb(pal[1]),(0,0,0)][c])
    return im
S=3; cols=8; W=cols*(5*16*S+16); rows=(251+cols-1)//cols
img=Image.new('RGB',(W,rows*(16*S+14)),(200,200,200)); dr=ImageDraw.Draw(img)
for i in range(1,252):
    d=open(G+'gfxdata/follow_icon/%03d.2bpp'%(i-1),'rb').read()
    w=WALK[i][:2]
    fs=[frame(d,0,OWN[i][:2]),frame(d,2,w),frame(d,1,w),frame(d,2,w[::-1]),frame(d,1,w[::-1])]
    x=((i-1)%cols)*(5*16*S+16); y=((i-1)//cols)*(16*S+14)
    for k,f in enumerate(fs): img.paste(f.resize((16*S,16*S),Image.NEAREST),(x+k*16*S+(6 if k>=3 else 0),y+12))
    dr.text((x+2,y),str(i),fill=(0,0,0))
img.save('follow_sheet.png')
