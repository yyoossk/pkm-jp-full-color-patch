import sys, re
M=open('/home/claude/work/ref/crystal_kj.gbc','rb').read()
def addr(o): return '%02X:%04X'%(o//0x4000,o%0x4000+(0x4000 if o>=0x4000 else 0))
def callers(bank, lo, hi):
    """bank 内の lo..hi を 指す call/jp/farcall/ld hl"""
    out=[]
    for m in re.finditer(rb'[\xcd\xc3\xca\xc2\xda\xd2\xcc\xc4\xd4\xdc\x21\x11]..', M, re.S):
        o=m.start(); v=M[o+1]|M[o+2]<<8
        if not (lo<=v<hi): continue
        ob=o//0x4000
        if M[o]==0x21 and o>=2 and M[o-2]==0x3E and M[o+3]==0xCF:
            if M[o-1]==bank: out.append(('far',addr(o),hex(v)))
        elif M[o] in (0xCD,0xC3) and (ob==bank or bank==0):
            out.append(('call',addr(o),hex(v)))
    return out
if __name__=='__main__':
    b=int(sys.argv[1],16); lo=int(sys.argv[2],16); hi=int(sys.argv[3],16)
    for c in callers(b,lo,hi): print(*c)
