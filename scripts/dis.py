#!/usr/bin/env python3
"""小さな SM83 逆アセンブラ: dis.py rom bank addr [count]"""
import sys
R=['b','c','d','e','h','l','[hl]','a']; RP=['bc','de','hl','sp']; RP2=['bc','de','hl','af']
CC=['nz','z','nc','c']; ALU=['add a,','adc a,','sub ','sbc a,','and ','xor ','or ','cp ']
ROT=['rlc','rrc','rl','rr','sla','sra','swap','srl']
def op(m,pc):
    o=m(pc); x,y,z=o>>6,(o>>3)&7,o&7; p,q=y>>1,y&1
    b1=lambda:m(pc+1); w=lambda:m(pc+1)|m(pc+2)<<8
    if o==0xCB:
        c=b1(); cx,cy,cz=c>>6,(c>>3)&7,c&7
        return 2,(f'{ROT[cy]} {R[cz]}' if cx==0 else f"{['','bit','res','set'][cx]} {cy}, {R[cz]}")
    if x==1: return (1,'halt') if o==0x76 else (1,f'ld {R[y]}, {R[z]}')
    if x==2: return 1,f'{ALU[y]}{R[z]}'
    if x==0:
        if z==0:
            if y==0: return 1,'nop'
            if y==1: return 3,f'ld [${w():04X}], sp'
            if y==2: return 2,'stop'
            if y==3: e=b1(); e-=256*(e>127); return 2,f'jr ${pc+2+e:04X}'
            e=b1(); e-=256*(e>127); return 2,f'jr {CC[y-4]}, ${pc+2+e:04X}'
        if z==1: return (3,f'ld {RP[p]}, ${w():04X}') if q==0 else (1,f'add hl, {RP[p]}')
        if z==2:
            t=['[bc]','[de]','[hli]','[hld]'][p]
            return 1,(f'ld {t}, a' if q==0 else f'ld a, {t}')
        if z==3: return 1,f"{'inc' if q==0 else 'dec'} {RP[p]}"
        if z==4: return 1,f'inc {R[y]}'
        if z==5: return 1,f'dec {R[y]}'
        if z==6: return 2,f'ld {R[y]}, ${b1():02X}'
        return 1,['rlca','rrca','rla','rra','daa','cpl','scf','ccf'][y]
    # x==3
    if z==0:
        if y<4: return 1,f'ret {CC[y]}'
        return [(2,f'ldh [$FF{b1():02X}], a'),(2,f'add sp, {b1()}'),(2,f'ldh a, [$FF{b1():02X}]'),(2,f'ld hl, sp+{b1()}')][y-4]
    if z==1:
        if q==0: return 1,f'pop {RP2[p]}'
        return 1,['ret','reti','jp hl','ld sp, hl'][p]
    if z==2:
        if y<4: return 3,f'jp {CC[y]}, ${w():04X}'
        return [(1,'ld [$FF00+c], a'),(3,f'ld [${w():04X}], a'),(1,'ld a, [$FF00+c]'),(3,f'ld a, [${w():04X}]')][y-4]
    if z==3: return {0:(3,f'jp ${w():04X}'),6:(1,'di'),7:(1,'ei')}.get(y,(1,f'db ${o:02X}'))
    if z==4: return (3,f'call {CC[y]}, ${w():04X}') if y<4 else (1,f'db ${o:02X}')
    if z==5: return (1,f'push {RP2[p]}') if q==0 else ((3,f'call ${w():04X}') if p==0 else (1,f'db ${o:02X}'))
    if z==6: return 2,f'{ALU[y]}${b1():02X}'
    return 1,f'rst ${y*8:02X}'
def dis(d,bank,addr,n=40):
    base=0 if addr<0x4000 else bank*0x4000-0x4000
    m=lambda a:d[base+a] if a>=0x4000 or True else 0
    out=[]; pc=addr
    for _ in range(n):
        l,s=op(lambda a:d[(a if a<0x4000 else base+a)],pc)
        bs=' '.join('%02X'%d[(pc+i if pc+i<0x4000 else base+pc+i)] for i in range(l))
        out.append(f'{bank:02X}:{pc:04X}  {bs:<9} {s}'); pc+=l
    return out
if __name__=='__main__':
    d=open(sys.argv[1],'rb').read()
    print('\n'.join(dis(d,int(sys.argv[2],16),int(sys.argv[3],16),int(sys.argv[4]) if len(sys.argv)>4 else 40)))
