#!/usr/bin/env python3
# 251匹そろう版の 出現表（銀 日本版）を 作る
#   python3 tools/wild251_jp.py base.gbc src/wild_silver.asm data/かえる枠_銀.txt src/wild251_silver.asm <pokegold>
# ・251匹そろう版キットの かえる枠_銀.txt（英語版 pokegold の 表から 作った もの）を、日本版 銀の ROM の 表に あてる。
# ・日本版 金銀は ヒメグマ・リングマ と ゴマゾウ・ドンファン が 英語版と 入れかわって いる（日本版 銀に ヒメグマ・リングマ）ので、
#   かえる枠の ヒメグマ⇔ゴマゾウ・リングマ⇔ドンファン を 入れかえて あてる（入れかえると 124 の 枠が ぜんぶ 日本版の 表と あう）。
# ・まず wild_silver.asm（殿堂入りの 前の 書きかえ）を あて、そのあと かえる枠を あて、元の ROM と ちがう 表を ぜんぶ 書く。
import sys,re
rom_path,cur_asm,frame_txt,out_asm,pg=sys.argv[1:6]
ids={}; n=0
for l in open(pg+'/constants/pokemon_constants.asm'):
    m=re.match(r'\s*const (\w+)',l)
    if m:
        n+=1; ids[m.group(1)]=n
        if m.group(1)=='CELEBI': break
SW={'TEDDIURSA':'PHANPY','PHANPY':'TEDDIURSA','URSARING':'DONPHAN','DONPHAN':'URSARING'}
mapid={}; g=0
for l in open(pg+'/constants/map_constants.asm'):
    if re.match(r'\s*newgroup',l): g+=1; m=0; continue
    mm=re.match(r'\s*map_const (\w+),',l)
    if mm: m+=1; mapid[mm.group(1)]=(g,m)
base=open(rom_path,'rb').read(); rom=bytearray(base)
s=open(cur_asm,encoding='utf-8').read()
for mm in re.finditer(r'ROMX\[\$(\w+)\], BANK\[\$(\w+)\]\n\tdb ([^\n]+)',s):
    o=int(mm.group(2),16)*0x4000+int(mm.group(1),16)-0x4000
    b=bytes(int(x.strip()[1:],16) for x in mm.group(3).split(',')); rom[o:o+len(b)]=b
def tabs(off,L):
    out=[]
    while rom[off]!=0xff: out.append(off); off+=L
    return out,off+1
START=0x2ac1b                                  # JohtoGrassWildMons（日本版 銀）
jg,o=tabs(START,47); jw,o=tabs(o,9); kg,o=tabs(o,47); kw,o=tabs(o,9)
grass={(rom[x],rom[x+1]):x for x in jg+kg}; water={(rom[x],rom[x+1]):x for x in jw+kw}
for l in open(frame_txt,encoding='utf-8'):
    m=re.match(r'(\w+)\s+(朝|昼|夜|なみのり)\s+(\d)わくめ\s+(\w+) Lv(\d+) → (\w+) Lv(\d+)',l)
    if not m: continue
    mp,tm,slot,fs,fl,ts,tl=m.groups(); slot=int(slot); fs=SW.get(fs,fs); ts=SW.get(ts,ts)
    w=tm=='なみのり'; tab=water if w else grass
    off=tab[mapid[mp]]
    p=off+3+2*(slot-1) if w else off+5+2*({'朝':0,'昼':1,'夜':2}[tm]*7+slot-1)
    if (rom[p],rom[p+1])!=(int(fl),ids[fs]): sys.exit('あわない: '+l)
    rom[p]=int(tl); rom[p+1]=ids[ts]
out=['; 251匹そろう版の 出現表（銀 日本版。wild_silver.asm の 殿堂入りの 前の 書きかえ ＋ 251版の かえる枠）',
     '; tools/wild251_jp.py で 作った もの。日本版 金銀は ヒメグマ・リングマ と ゴマゾウ・ドンファン が 英語版と 入れかわって いる',
     '; （日本版 銀に ヒメグマ・リングマ）ので、銀に 足すのは ゴマゾウ・ドンファン','']
for lst,L in ((jg,47),(jw,9),(kg,47),(kw,9)):
    for off in lst:
        if rom[off:off+L]!=base[off:off+L]:
            out.append('SECTION "wild251 %04x", ROMX[$%04x], BANK[$%02x]'%(off%0x10000,off%0x4000+0x4000,off//0x4000))
            out.append('\tdb '+', '.join('$%02x'%x for x in rom[off:off+L]))
open(out_asm,'w',encoding='utf-8').write('\n'.join(out)+'\n')
print('ok',out_asm)
