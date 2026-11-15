import sys; sys.path.insert(0,'/home/claude/work/scripts')
from cwalk import Walk, fo
from cmaps import maplist; from maps import CMGP
M=open('/home/claude/work/ref/crystal_kj.gbc','rb').read()
def r16(b,o): return b[o]|b[o+1]<<8
T=fo(0x6A,0x4000)
name=sys.argv[1]
m={x['name']:x for x in maplist(M,CMGP,'pokecrystal')}[name]
ts=M[m['hdr']+1]; at=Walk(M).map(m['attr'],'c')
e=M[T+15*ts:T+15*ts+15]; cb,ca=e[6],r16(e,7)
blk=M[fo(at['blkbank'],at['blk']):][:at['w']*at['h']]
for by in range(at['h']):
    for sub in (0,1):
        s=''
        for bx in range(at['w']):
            b=blk[by*at['w']+bx]; c=M[fo(cb,ca)+4*b:fo(cb,ca)+4*b+4]
            for sx in (0,1):
                v=c[sub*2+sx]; s+= 'L' if v&0xF0==0xA0 else '~' if v==0x29 else '.' if v==0 else '"' if v==0x18 else '#' if v==0x07 else '%X'%(v&15)
        print('%2d %s'%(by*2+sub,s))
