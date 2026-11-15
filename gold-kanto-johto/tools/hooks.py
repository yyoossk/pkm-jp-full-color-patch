import sys, pickle; sys.path.insert(0,'/home/claude/work/scripts')
from near import load, near
from asmx import L
CS=load('/home/claude/work/ref/crystal_jp.sym')
M=open('/home/claude/work/ref/crystal_kj.gbc','rb').read()
regs=pickle.load(open('/tmp/regs_mf.pkl','rb'))
banks=[int(x,16) for x in sys.argv[1].split(',')]
for a,b in regs:
    bk=a//0x4000
    if bk not in banks or b-a>40: continue
    ad=a%0x4000+(0x4000 if bk else 0)
    # 命令の 並び： a の すこし 前から
    s=''
    o=a-3
    seg=M[o:b+3]
    s=seg.hex()
    print('%02X:%04X +%-3d %-28s %s'%(bk,ad,b-a,str(near(CS,bk,ad))[:28],s[:60]))
