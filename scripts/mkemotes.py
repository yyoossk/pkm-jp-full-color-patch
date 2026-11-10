#!/usr/bin/env python3
"""連れ歩きの気持ちのアイコン（16×16、7つ）を 2bpp にする → kit/follow/emotes.2bpp
   . = 透明、w = 白（色1）、r = 赤（色2）、k = 黒（色3）。タイルの並びは 左上・右上・左下・右下"""
import os
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRAME=["..kkkkkkkkkkkk..",
       ".kwwwwwwwwwwwwk.",
       "kwwwwwwwwwwwwwwk",
       "kwwwwwwwwwwwwwwk",
       "kwwwwwwwwwwwwwwk",
       "kwwwwwwwwwwwwwwk",
       "kwwwwwwwwwwwwwwk",
       "kwwwwwwwwwwwwwwk",
       "kwwwwwwwwwwwwwwk",
       "kwwwwwwwwwwwwwwk",
       "kwwwwwwwwwwwwwwk",
       ".kwwwwwwwwwwwwk.",
       "..kkkwwkkkkkkk..",
       "....kwk.........",
       "....kk..........",
       "................"]
SYM={  # 10×9 を 左上 (3,2) から
 'shock':["....kk....","....kk....","....kk....","....kk....","....kk....","..........","....kk....","....kk....",".........."],
 'question':["...kkkk...","..kk..kk..","......kk..",".....kk...","....kk....","....kk....","..........","....kk....","....kk...."],
 'happy':["....kkkk..","....k..k..","....k..k..","....k..k..","..kkk.kk..",".kkkkkkk..",".kkk.kkk..","..........",".........."],
 'sad':["..........",".kk....kk.","..k....k..","..........","...kkkk...","..k....k..",".k......k.","..........",".........."],
 'heart':["..........","..rr..rr..",".rrrrrrrr.",".rrrrrrrr.","..rrrrrr..","...rrrr...","....rr....","..........",".........."],
 'bolt':[".....kkk..","....kkk...","...kkk....","..kkkkkk..","....kkk...","...kkk....","..kkk.....","..kk......",".........."],
 'sleep':["..kkkk....","....k.....","...k......","..kkkk....",".....kkk..","......k...",".....k....",".....kkk..",".........."],
}
ORDER=['shock','question','happy','sad','heart','bolt','sleep']
def img(name):
    p=[list(r) for r in FRAME]
    for y,row in enumerate(SYM[name]):
        for x,c in enumerate(row):
            if c!='.': p[2+y][3+x]=c
    return p
out=bytearray()
for n in ORDER:
    p=img(n)
    for t in range(4):
        ox,oy=(t&1)*8,(t>>1)*8
        for y in range(8):
            lo=hi=0
            for x in range(8):
                v='.wrk'.index(p[oy+y][ox+x])
                lo|=(v&1)<<(7-x); hi|=((v>>1)&1)<<(7-x)
            out+=bytes([lo,hi])
open(os.path.join(R,'kit/follow/emotes.2bpp'),'wb').write(out)
print(len(out))
