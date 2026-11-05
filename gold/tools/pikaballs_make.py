# ピカチュウ版フルカラーから取ったボールの絵（balls.json、pikaballs_cap.py で作る）を、
# 金の投げるボールの並び（10タイル：0・1 まっすぐの左、2〜5 かたむき、6 ふた、7 下、8・9 まっすぐの右）にする。
#   python3 tools/pikaballs_make.py balls.json pokegold/gfx/battle_anims/pokeball.2bpp
#   → gfxdata/pikaballs.2bpp（マスター・ハイパー・スーパー・モンスター・サファリ の順に 10タイルずつ）
#     gfxdata/pikaballs.pal（同じ順に 上半分・下半分 の OBJ パレット 8バイトずつ）、prev.png（見本）
#   ・まっすぐ・かたむきは ピカチュウ版の絵を、金の絵と同じ位置（はしの点）にずらす。
#   ・ふた（6）は 金の絵の色を そのボールの上半分の色に置きかえ、下（7）は 金の絵のまま（下半分の色で出る）。
import json, sys
from PIL import Image
d=json.load(open(sys.argv[1] if len(sys.argv)>1 else 'balls.json'))
gold=open(sys.argv[2] if len(sys.argv)>2 else 'pokegold/gfx/battle_anims/pokeball.2bpp','rb').read()
def dec(b): return [[((b[2*y]>>(7-x))&1)|(((b[2*y+1]>>(7-x))&1)<<1) for x in range(8)] for y in range(8)]
def enc(t):
    out=bytearray()
    for y in range(8):
        lo=hi=0
        for x in range(8):
            v=t[y][x]; lo|=(v&1)<<(7-x); hi|=(v>>1)<<(7-x)
        out+=bytes([lo,hi])
    return bytes(out)
def assemble(s):
    img=[[0]*16 for _ in range(16)]; half=[[None]*16 for _ in range(16)]
    ys=min(e[0] for e in s['ents']); xs=min(e[1] for e in s['ents'])
    for e in s['ents']:
        attr=e[3]; t=dec(bytes.fromhex((s['tiles1'] if attr&8 else s['tiles'])[str(e[2])]))
        for y in range(8):
            for x in range(8):
                xx=7-x if attr&0x20 else x; yy=7-y if attr&0x40 else y
                img[e[0]-ys+y][e[1]-xs+x]=t[yy][xx]
    return img
def bbox(img):
    p=[(x,y) for y in range(16) for x in range(16) if img[y][x]]
    return min(a for a,b in p),min(b for a,b in p),max(a for a,b in p),max(b for a,b in p)
def shift(img,dx,dy):
    o=[[0]*16 for _ in range(16)]
    for y in range(16):
        for x in range(16):
            if img[y][x]: o[y+dy][x+dx]=img[y][x]
    return o
def g16(tiles):  # gold tiles (TL,TR,BL,BR) -> 16x16
    o=[[0]*16 for _ in range(16)]
    for k,t in enumerate(tiles):
        tt=dec(gold[t*16:t*16+16]) if isinstance(t,int) else t
        for y in range(8):
            for x in range(8): o[(k//2)*8+y][(k%2)*8+x]=tt[y][x]
    return o
def mirror(t): return [row[::-1] for row in t]
gu=g16([0,mirror(dec(gold[0:16])),1,mirror(dec(gold[16:32]))])
gt=g16([2,3,4,5])
def split(img):
    return [[row[x:x+8] for row in img[y:y+8]] for y in (0,8) for x in (0,8)]
names=['master','ultra','great','poke','safari']   # order = item id 1,2,4,5 と サファリ（asm の表）
pals={}
out=b''; prev=Image.new('RGB',(len(names)*4*18,18),(200,200,200))
def c555(v): return ((v&31)*255//31,((v>>5)&31)*255//31,((v>>10)&31)*255//31)
for bi,n in enumerate(names):
    up=assemble(d[n][5]); ti=assemble(d[n][1])
    for img,ref,lab in ((up,gu,'u'),(ti,gt,'t')):
        bx=bbox(img); br=bbox(ref)
        print(n,lab,bx,br)
    gx=bbox(gu); px=bbox(up); up=shift(up,gx[0]-px[0],gx[1]-px[1])
    gx=bbox(gt); px=bbox(ti); ti=shift(ti,gx[0]-px[0],gx[1]-px[1])
    ob=d[n][5]['pals'].split('OB:')[1]
    top=bytes.fromhex(ob[6*16:7*16]); bot=bytes.fromhex(ob[7*16:8*16])
    pals[n]=(top,bot)
    U=split(up); T=split(ti)
    # lid (gold tile 6) and lower (gold tile 7)
    lid=dec(gold[6*16:7*16]); low=dec(gold[7*16:8*16])
    lidmap={'poke':{1:1,2:2,3:3},'great':{1:2,2:2,3:3},'ultra':{1:2,2:3,3:3},'master':{1:2,2:3,3:3},'safari':{1:1,2:2,3:3}}[n]
    lid=[[lidmap.get(v,0) if v else 0 for v in row] for row in lid]
    tiles=[U[0],U[2],T[0],T[1],T[2],T[3],lid,low,U[1],U[3]]
    out+=b''.join(enc(t) for t in tiles)
    # preview upright & tilted & open
    tp=[c555(int.from_bytes(top[i*2:i*2+2],'little')) for i in range(4)]
    bp=[c555(int.from_bytes(bot[i*2:i*2+2],'little')) for i in range(4)]
    for k,img in enumerate((up,ti)):
        for y in range(16):
            for x in range(16):
                v=img[y][x]
                if v: prev.putpixel(((bi*4+k)*18+1+x,1+y),(tp if y<8 else bp)[v])
    op=[[0]*16 for _ in range(8)]
    for y in range(8):
        for x in range(8): op[y][x]=lid[y][x]; op[y][15-x]=lid[y][x]
    for y in range(8):
        for x in range(16):
            v=op[y][x]
            if v: prev.putpixel(((bi*4+2)*18+1+x,5+y),tp[v])
    for y in range(8):
        for x in range(8):
            for xx in (x,15-x):
                v=low[y][x]
                if v: prev.putpixel(((bi*4+3)*18+1+xx,5+y),bp[v])
open('gfxdata/pikaballs.2bpp','wb').write(out)
open('gfxdata/pikaballs.pal','wb').write(b''.join(pals[n][0]+pals[n][1] for n in names))
prev.resize((prev.width*6,prev.height*6),Image.NEAREST).save('prev.png')
print(len(out))
