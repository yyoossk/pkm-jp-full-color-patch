# 連れ歩きの 絵（gfxdata/follow/*.2bpp）と 色の 表を src/follow_data.inc に 書き出す
import csv,os
from PIL import Image
K='gfxdata/follow/'
rows=list(csv.reader(open(K+'一覧.csv',encoding='utf-8-sig')))[1:]
byno={r[0]:r for r in rows}
order=[]
for n in range(1,252): order.append(byno['%03d'%n][1])
order.append(byno['TAMAGO'][1])
for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ': order.append(byno['U_'+c][1])
PAL={'RED':0,'BLUE':1,'GREEN':2,'BROWN':3,'PURPLE':4,'PINK':4}
out=['; tools/follow_gen.py で 作る（手で 書きかえない）',
     '; 絵：番号 0〜250 = 種類 1〜251、251 = タマゴ、252〜277 = アンノーン A〜Z。1匹 384バイト（24タイル）',
     '; バンク $%02x から 1バンクに 42匹'%0x60]
PER=42
# 絵：Crystal Crunch の 手持ちの アイコン（gfxdata/follow_cc/icons/*.png。16×32 ＝ 16×16 の 2コマ。tools/follow_cc_extract.py で
#   取り出した もの）から、Crystal Crunch の GetFollowerIconSprite と 同じ ように 作る：
#   下向き（正面）は 手持ちと まったく 同じ 絵（Polished Crystal の ミニアイコン gfxdata/minis.2bpp。止まり ＝ 1コマ目、
#   歩き ＝ 2コマ目。アンノーンは 手持ちと 同じ 1つの 絵、タマゴは タマゴ）。
#   後ろ・横は 向きの ある 歩行グラフィック（gfxdata/follow/、連れ歩きキットの 絵）を 使う（アイコンには 後ろ・横の 絵が ない）。
#   アンノーンは 文字ごとの アイコン、タマゴは タマゴの アイコン。
os.makedirs('gfxdata/follow_icon',exist_ok=True)
ICON='gfxdata/follow_cc/icons/'
MINIS=open('gfxdata/minis.2bpp','rb').read()
# 手持ちの アイコンは 目・顔などの 白を 透明（色0）で かいて いる（手持ちの 画面は 背景が 白なので 白に 見える）。
# フィールドでも 同じに 見せる ため、外と つながって いない 透明の 所（あな）だけ 色1 に した「白い したじき」の 絵を 作る
# （gfxdata/follow_icon/mask.bin、1匹 128バイト ＝ 正面の 止まり・歩き 各4タイル）。ゲームでは 連れ歩きの 後ろに
# 白（OBJ パレット5 の 色1）で かさねる（follow_crystal.asm の Fw_Underlay）。絵と 色は 手持ちと まったく 同じ（ユーザーの 希望）。
MASKS=bytearray()
def make_mask(d):
    out=bytearray()
    for f in range(2):
        px=[[0]*16 for _ in range(16)]
        for k,(ox,oy) in enumerate(((0,0),(8,0),(0,8),(8,8))):
            t=d[f*64+k*16:f*64+k*16+16]
            for y in range(8):
                for x in range(8): px[oy+y][ox+x]=((t[y*2]>>(7-x))&1)|(((t[y*2+1]>>(7-x))&1)<<1)
        seen=set(); st=[(x,y) for x in range(16) for y in (0,15)]+[(x,y) for y in range(16) for x in (0,15)]
        st=[q for q in st if px[q[1]][q[0]]==0]
        while st:
            x,y=st.pop()
            if (x,y) in seen: continue
            seen.add((x,y))
            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                a,b=x+dx,y+dy
                if 0<=a<16 and 0<=b<16 and px[b][a]==0 and (a,b) not in seen: st.append((a,b))
        m=[[1 if (px[y][x]==0 and (x,y) not in seen) else 0 for x in range(16)] for y in range(16)]
        out+=tiles(m)
    return bytes(out)
GRAY={255:0,170:1,85:2,0:3}
def icon_frames(name):
    im=Image.open(ICON+name+'.png').convert('L'); px=im.load()
    frames=[]
    for f in range(2):
        b=[[GRAY[min(GRAY,key=lambda k:abs(k-px[x,f*16+y]))] for x in range(16)] for y in range(16)]
        frames.append(b)
    return frames
def tiles(fr,mirror=False):
    out=bytearray()
    for (ox,oy) in ((0,0),(8,0),(0,8),(8,8)):
        for y in range(8):
            lo=hi=0
            for x in range(8):
                xx=ox+x
                if mirror: xx=15-xx
                c=fr[oy+y][xx]; lo|=(c&1)<<(7-x); hi|=(c>>1)<<(7-x)
            out+=bytes([lo,hi])
    return bytes(out)
def icon_name(i,name):
    if i==251: return 'egg'
    if i>=252: return 'unown_'+'abcdefghijklmnopqrstuvwxyz'[i-252]
    n=name.split('_',1)[1]
    return 'unown_a' if n=='unown' else n
for i,name in enumerate(order):
    b=0x60+i//PER; a=0x4000+(i%PER)*384
    if i%PER==0: out.append('SECTION "follow gfx %d", ROMX[$4000], BANK[$%02x]'%(i//PER,b))
    # 正面：手持ちと 同じ 絵（gfxdata/minis.2bpp：0 = タマゴ、1〜251。1匹 8タイル ＝ 2コマ。左右反転しない）
    mi=0 if i==251 else (201 if i>=252 else i+1)
    MF=MINIS[mi*128:mi*128+128]
    MASKS.extend(make_mask(MF))
    # 後ろ・横は 歩行グラフィック（gfxdata/follow/*.2bpp：止まり 下・上・横、歩き 下・上・横 の 24タイル）の 絵
    A=open(K+name+'.2bpp','rb').read(); T=64
    data=MF[0:T]+A[T:2*T]+A[2*T:3*T]+MF[T:2*T]+A[4*T:5*T]+A[5*T:6*T]
    open('gfxdata/follow_icon/%03d.2bpp'%i,'wb').write(data)
    out.append('\tINCBIN "gfxdata/follow_icon/%03d.2bpp"'%i)
# ボールの 絵（Crystal Crunch の gfx/sprites/anim_pokeball.png。開いた・半分・とじた の 3コマ）→ 番号 278
#   止まりの 下 ＝ 開いた、上 ＝ 半分、横 ＝ とじた（Crystal Crunch の OW_DOWN・OW_UP・OW_LEFT と 同じ）、歩きも 同じ
im=Image.open('gfxdata/follow_cc/anim_pokeball.png').convert('L'); px=im.load()
bf=[[[GRAY[min(GRAY,key=lambda k:abs(k-px[x,f*16+y]))] for x in range(16)] for y in range(16)] for f in range(3)]
ball=tiles(bf[0])+tiles(bf[1])+tiles(bf[2])
ball=ball+ball
open('gfxdata/follow_icon/ball.2bpp','wb').write(ball)
out.append('\tINCBIN "gfxdata/follow_icon/ball.2bpp"   ; 278：ボール')
# 正面の 白い したじき（番号 0〜277、1匹 128バイト）：バンク $67 から 1バンクに 128匹
open('gfxdata/follow_icon/mask.bin','wb').write(MASKS)
for k in range(0,len(MASKS),0x4000):
    out.append('SECTION "follow mask %d", ROMX[$4000], BANK[$%02x]'%(k//0x4000,0x67+k//0x4000))
    out.append('\tINCBIN "gfxdata/follow_icon/mask.bin", %d, %d'%(k,min(0x4000,len(MASKS)-k)))
out.append('')
out.append('SECTION "follow pals", ROMX[$7c00], BANK[FW_BANK]')
out.append('; 種類 1〜251・タマゴ の フィールドの 色（上 4ビット = ふつう、下 4ビット = 色ちがい。PAL_OW_ の 番号）')
out.append('FollowerPals:')
vals=[]
for n in range(1,252):
    r=byno['%03d'%n]; vals.append(PAL[r[4]]<<4|PAL[r[5]])
vals.append(2<<4|2)   # タマゴ：みどり
for i in range(0,len(vals),16):
    out.append('\tdb '+', '.join('$%02x'%v for v in vals[i:i+16]))
open('src/follow_data.inc','w').write('\n'.join(out)+'\n')
print(len(order),'gfx', 'last bank $%02x'%(0x60+(len(order)-1)//PER))

# 連れ歩きの 色：手持ちと 同じ（gfxdata/minipals.bin。以前は Crystal Crunch の gfxdata/follow_cc/pals.bin。戦闘の 絵の 2色を Crystal Crunch の
#   icon_palette_order で あてた もの。0 = タマゴ、1〜251、1匹 8バイト：ふつうの 明るい・暗い、色ちがいの 明るい・暗い）。
#   夜・暗い 所の 色は ゲームの 中で かえる（follow_crystal.asm の Fw_OwnColors）。
CP=open('gfxdata/minipals.bin','rb').read()   # 手持ちと 同じ 色（ユーザーの 希望）
out2=['; tools/follow_gen.py で 作る（手で 書きかえない）',
      '; 連れ歩きの 色：0 = タマゴ、1〜251。1匹 8バイト（ふつうの 色1・色2、色ちがいの 色1・色2）。手持ちと 同じ 色（minipals.bin）',
      'SECTION "follow own pals", ROMX[$6000], BANK[$7b]',
      'FollowerOwnPals:']
for i in range(252):
    e=CP[i*8:i*8+8]
    out2.append('\tdw '+', '.join('$%04x'%(e[k]|e[k+1]<<8) for k in range(0,8,2)))
# 後ろ・横（歩行グラフィック）用の 色：正面（手持ち）と 同じ その ポケモンの 2色を 使う（ユーザーの 希望）。
#   歩行グラフィックの 色1（明るい 所）・色2（暗い 所）に どちらを あてるかを ポケモンごとに 自動で 決める：
#   1) 正面で 色1・色2 が しめる 広さの わりあいと、後ろ・横で 同じ わりあいに なる 方（差が 0.15 より 大きい とき）
#   2) そうで なければ、歩行グラフィックが かかれた 元の 色（色1 ＝ はだ (31,19,10)、色2 ＝ 一覧.csv の フィールド色）に
#      色あい・明るさが 近い 方。色ちがいも ふつうと 同じ あて方。
import colorsys
OW={'RED':(31,7,1),'BLUE':(10,9,31),'GREEN':(7,23,3),'BROWN':(15,10,3),'PURPLE':(18,4,18),'PINK':(18,4,18)}
SKIN=(31,19,10)
def _un(c): return (c&31,(c>>5)&31,(c>>10)&31)
def _hls(t): return colorsys.rgb_to_hls(*[x/31 for x in t])
def _dist(a,b):
    ha,la,sa=_hls(a); hb,lb,sb=_hls(b)
    dh=min(abs(ha-hb),1-abs(ha-hb))
    return dh*2*min(sa,sb)+abs(la-lb)+abs(sa-sb)*0.5
def _counts(d,frames):
    n=[0,0,0,0]
    for f in frames:
        for k in range(4):
            t=d[(f*4+k)*16:(f*4+k)*16+16]
            for y in range(8):
                for x in range(8): n[((t[y*2]>>(7-x))&1)|(((t[y*2+1]>>(7-x))&1)<<1)]+=1
    return n
def walk_swap(i):
    """i = 色の 表の 番号（0 = タマゴ、1〜251）。True なら 色1・色2 を 入れかえて あてる"""
    gi=251 if i==0 else i-1
    d=open('gfxdata/follow_icon/%03d.2bpp'%gi,'rb').read()
    fa=_counts(d,[0,3]); wa=_counts(d,[1,2,4,5])
    tf=(fa[1]+fa[2]) or 1; tw=(wa[1]+wa[2]) or 1
    f1=fa[1]/tf; keep=abs(wa[1]/tw-f1); swap=abs(wa[2]/tw-f1)
    if abs(keep-swap)>0.15: return swap<keep
    c1=_un(CP[i*8]|CP[i*8+1]<<8); c2=_un(CP[i*8+2]|CP[i*8+3]<<8)
    fc=OW['GREEN'] if i==0 else OW[byno['%03d'%i][4]]
    return _dist(c2,SKIN)+_dist(c1,fc) < _dist(c1,SKIN)+_dist(c2,fc)
out2+=['; 後ろ・横 用（その ポケモンの 2色。歩行グラフィックの 明るい 所・暗い 所への あて方は ポケモンごと）','FollowerWalkPals:']
for i in range(252):
    e=[CP[i*8+k]|CP[i*8+k+1]<<8 for k in range(0,8,2)]
    if walk_swap(i): e=[e[1],e[0],e[3],e[2]]
    out2.append('\tdw '+', '.join('$%04x'%v for v in e)+('   ; タマゴ' if i==0 else ''))
open('src/follow_data.inc','a').write('\n'.join(out2)+'\n')
