#!/usr/bin/env python3
"""青フルカラー 改良ビルド
使い方: python3 build.py [版...]   （版を書かなければ12版すべて）
  base/<版>.gbc に src/main.asm を当てて out/<版>.gbc を作る。
  base/ が無ければ、元の「青」ROM（CRC E4468D14）と v232/ の ips から作る:
    python3 build.py --makebase 元の青.gb
"""
import os, sys, subprocess, zlib, glob
from ips import apply
R = os.path.dirname(os.path.abspath(__file__)); os.chdir(R)
T = os.path.join(R, 'tools', 'rgbds')
VARS = ['full_kin','full_kin_60','full_sho','full_sho_60',
        'color_kin','color_kin_60','color_sho','color_sho_60',
        'all151_kin','all151_kin_60','all151_sho','all151_sho_60']
IPS = {'full':'1_完全版','color':'2_カラー化のみ','all151':'3_151匹そろう版'}

def tool(n): p=os.path.join(T,n); return p if os.path.exists(p) else n

def makebase(src):
    d=open(src,'rb').read(); assert '%08X'%zlib.crc32(d)=='E4468D14','元の青ROMではありません'
    os.makedirs('base',exist_ok=True)
    for f in glob.glob('v232/**/*.ips',recursive=True):
        p=f.split(os.sep); ed=[k for k,v in IPS.items() if v in p][0]
        g='sho' if '初代' in p[-2] else 'kin'; fps='_60' if '60fps' in p[-1] else ''
        open(f'base/{ed}_{g}{fps}.gbc','wb').write(apply(d,open(f,'rb').read()))

def defs(v):
    ed,g=v.split('_')[:2]
    d=['-D','ED_'+ed.upper(),'-D','GFX_'+g.upper()]
    if v.endswith('_60'): d+=['-D','FPS60']
    return d

def build(v):
    os.makedirs('obj',exist_ok=True); os.makedirs('out',exist_ok=True)
    with open('obj/vars.inc','w') as f: f.write(f'INCLUDE "vars/{v}.inc"\nINCLUDE "common.inc"\n')
    objs=[]
    for src in [l.strip() for l in open('src/files.txt',encoding='utf-8') if l.strip() and not l.startswith(';')]:
        o=f'obj/{v}_'+os.path.basename(src)[:-4]+'.o'
        subprocess.run([tool('rgbasm'),'-I','obj','-I','src','-I','.','-P','vars.inc']+defs(v)+['-o',o,src],check=True)
        objs.append(o)
    out=f'out/{v}.gbc'
    subprocess.run([tool('rgblink'),'-O',f'base/{v}.gbc','-n',f'out/{v}.sym','-m',f'out/{v}.map','-l','src/layout.link','-o',out]+objs,check=True)
    subprocess.run([tool('rgbfix'),'-v','-p','0',out],check=True,stderr=subprocess.DEVNULL)
    print('%-14s %08X'%(v,zlib.crc32(open(out,'rb').read())))

if __name__=='__main__':
    a=sys.argv[1:]
    if a[:1]==['--makebase']: makebase(a[1]); sys.exit()
    for v in (a or VARS): build(v)
