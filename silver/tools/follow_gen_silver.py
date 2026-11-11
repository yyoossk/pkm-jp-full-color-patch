# 連れ歩きの 絵・したじき・色の 表を src/follow_data.inc に 書き出す（銀）
#   絵と したじき（gfxdata/follow_icon/*.2bpp・mask.bin・ball.2bpp）は クリスタルで 作った もの（金銀クリスタル共通）を そのまま 使う。
#   色は 銀の 手持ちの 色（gfxdata/minipals.bin）から 作る（tools/follow_gen.py〔クリスタル〕の 色の 部分と 同じ 作り方）。
import csv,colorsys
GFX_BANK=0x50; MASK_BANK=0x57; PALS_BANK=0x4e; PER=42
K='gfxdata/follow/'
rows=list(csv.reader(open(K+'一覧.csv',encoding='utf-8-sig')))[1:]
byno={r[0]:r for r in rows}
PAL={'RED':0,'BLUE':1,'GREEN':2,'BROWN':3,'PURPLE':4,'PINK':4}
out=['; tools/follow_gen_silver.py で 作る（手で 書きかえない）',
     '; 絵：番号 0〜250 = 種類 1〜251、251 = タマゴ、252〜277 = アンノーン A〜Z、278 = ボール。1匹 384バイト（24タイル）',
     '; バンク $%02x から 1バンクに %d匹。したじきは バンク $%02x から 同じ 数え方'%(GFX_BANK,PER,MASK_BANK)]
for i in range(279):
    if i%PER==0: out.append('SECTION "follow gfx %d", ROMX[$4000], BANK[$%02x]'%(i//PER,GFX_BANK+i//PER))
    out.append('\tINCBIN "gfxdata/follow_icon/%03d.2bpp"'%i if i<278 else '\tINCBIN "gfxdata/follow_icon/ball.2bpp"   ; 278：ボール')
MASKS=open('gfxdata/follow_icon/mask.bin','rb').read()
for k in range(0,len(MASKS),PER*384):
    out.append('SECTION "follow mask %d", ROMX[$4000], BANK[$%02x]'%(k//(PER*384),MASK_BANK+k//(PER*384)))
    out.append('\tINCBIN "gfxdata/follow_icon/mask.bin", %d, %d'%(k,min(PER*384,len(MASKS)-k)))
out.append('')
out.append('SECTION "follow pals", ROMX[$7c00], BANK[FW_BANK]')
out.append('; 種類 1〜251・タマゴ の フィールドの 色（上 4ビット = ふつう、下 4ビット = 色ちがい。PAL_OW_ の 番号）')
out.append('FollowerPals:')
vals=[]
for n in range(1,252):
    r=byno['%03d'%n]; vals.append(PAL[r[4]]<<4|PAL[r[5]])
vals.append(2<<4|2)
for i in range(0,len(vals),16):
    out.append('\tdb '+', '.join('$%02x'%v for v in vals[i:i+16]))
CP=open('gfxdata/minipals.bin','rb').read()
out+=['; 連れ歩きの 色：0 = タマゴ、1〜251。1匹 8バイト（ふつうの 色1・色2、色ちがいの 色1・色2）。手持ちと 同じ 色（minipals.bin）',
      'SECTION "follow own pals", ROMX[$4000], BANK[$%02x]'%PALS_BANK,'FollowerOwnPals:']
for i in range(252):
    e=CP[i*8:i*8+8]
    out.append('\tdw '+', '.join('$%04x'%(e[k]|e[k+1]<<8) for k in range(0,8,2)))
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
# 自動の きめ方では 横の 絵の 色が 正面と ちがって 見えた ポケモン（手で きめる。True ＝ 入れかえる）
#   245 スイクン：横の からだが むらさき に なった → 入れかえない
#   16 ポッポ：横・後ろの せなかが クリーム色 に なった → 入れかえない
WALK_SWAP_FIX={245:False,16:False}
def walk_swap(i):
    """i = 色の 表の 番号（0 = タマゴ、1〜251）。True なら 色1・色2 を 入れかえて あてる"""
    if i in WALK_SWAP_FIX: return WALK_SWAP_FIX[i]
    gi=251 if i==0 else i-1
    d=open('gfxdata/follow_icon/%03d.2bpp'%gi,'rb').read()
    fa=_counts(d,[0,3]); wa=_counts(d,[1,2,4,5])
    tf=(fa[1]+fa[2]) or 1; tw=(wa[1]+wa[2]) or 1
    f1=fa[1]/tf; keep=abs(wa[1]/tw-f1); swap=abs(wa[2]/tw-f1)
    if abs(keep-swap)>0.15: return swap<keep
    c1=_un(CP[i*8]|CP[i*8+1]<<8); c2=_un(CP[i*8+2]|CP[i*8+3]<<8)
    fc=OW['GREEN'] if i==0 else OW[byno['%03d'%i][4]]
    return _dist(c2,SKIN)+_dist(c1,fc) < _dist(c1,SKIN)+_dist(c2,fc)
out+=['; 後ろ・横 用（その ポケモンの 2色。歩行グラフィックの 明るい 所・暗い 所への あて方は ポケモンごと）','FollowerWalkPals:']
for i in range(252):
    e=[CP[i*8+k]|CP[i*8+k+1]<<8 for k in range(0,8,2)]
    if walk_swap(i): e=[e[1],e[0],e[3],e[2]]
    out.append('\tdw '+', '.join('$%04x'%v for v in e)+('   ; タマゴ' if i==0 else ''))
open('src/follow_data.inc','w').write('\n'.join(out)+'\n')
print('ok')
