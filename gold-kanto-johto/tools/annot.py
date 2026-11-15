import sys, pickle; sys.path.insert(0,'/home/claude/work/scripts')
from near import load, near
CS=load('/home/claude/work/ref/crystal_jp.sym')
regs=pickle.load(open('/tmp/regs_mf.pkl','rb'))
banks=[int(x,16) for x in sys.argv[1].split(',')]
for a,b in regs:
    bk=a//0x4000
    if bk not in banks: continue
    ad=a%0x4000+(0x4000 if bk else 0)
    print('%02X:%04X +%d  %s'%(bk,ad,b-a,near(CS,bk,ad)))
