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
#   止まり（下・上・横）＝ 1コマ目、歩き（下・上・横）＝ 2コマ目、そのあと 下向きの 2つを 左右反転（こちらへ 歩く ときと
#   むこうへ 歩く ときで ちがう ように 見せる）。横は アイコンの 向き、反対は 左右反転（ゲームの しくみ）。
#   アンノーンは 文字ごとの アイコン、タマゴは タマゴの アイコン。
os.makedirs('gfxdata/follow_icon',exist_ok=True)
ICON='gfxdata/follow_cc/icons/'
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
    f1,f2=icon_frames(icon_name(i,name))
    data=tiles(f1,True)+tiles(f1)+tiles(f1)+tiles(f2,True)+tiles(f2)+tiles(f2)
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

# 連れ歩きの 色：Crystal Crunch と 同じ（gfxdata/follow_cc/pals.bin。戦闘の 絵の 2色を Crystal Crunch の
#   icon_palette_order で あてた もの。0 = タマゴ、1〜251、1匹 8バイト：ふつうの 明るい・暗い、色ちがいの 明るい・暗い）。
#   夜・暗い 所の 色は ゲームの 中で かえる（follow_crystal.asm の Fw_OwnColors）。
CP=open('gfxdata/follow_cc/pals.bin','rb').read()
out2=['; tools/follow_gen.py で 作る（手で 書きかえない）',
      '; 連れ歩きの 色：0 = タマゴ、1〜251。1匹 8バイト（ふつうの 色1・色2、色ちがいの 色1・色2）。Crystal Crunch と 同じ 色',
      'SECTION "follow own pals", ROMX[$6000], BANK[$7b]',
      'FollowerOwnPals:']
for i in range(252):
    e=CP[i*8:i*8+8]
    out2.append('\tdw '+', '.join('$%04x'%(e[k]|e[k+1]<<8) for k in range(0,8,2)))
open('src/follow_data.inc','a').write('\n'.join(out2)+'\n')
