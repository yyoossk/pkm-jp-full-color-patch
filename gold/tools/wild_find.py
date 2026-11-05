#!/usr/bin/env python3
# 出現表の書きかえ：ルール（data/wild_*.txt）の 元の表を ROM の中で探して、書きかえ用の asm を作る
#   python3 wild_find.py 元のROM.gbc data/wild_crystal.txt 出力.asm
import sys
rom=open(sys.argv[1],'rb').read()
out=['; 殿堂入りの前に出る ポケモン（%s から作ったもの）'%sys.argv[2],'']
for l in open(sys.argv[2],encoding='utf-8'):
    if l.startswith('#') or not l.strip(): continue
    mp,a,b=l.split()
    a=bytes.fromhex(a); b=bytes.fromhex(b)
    i=rom.find(a)
    if i<0: sys.exit('%s の表が見つからない'%mp)
    if rom.find(a,i+1)>=0: sys.exit('%s の表が 2か所以上ある'%mp)
    bank=i//0x4000; addr=i%0x4000+0x4000
    out.append('SECTION "wild %s", ROMX[$%04x], BANK[$%02x]'%(mp,addr,bank))
    out.append('\tdb '+', '.join('$%02x'%x for x in b))
open(sys.argv[3],'w').write('\n'.join(out)+'\n')
print('ok', sys.argv[3])
