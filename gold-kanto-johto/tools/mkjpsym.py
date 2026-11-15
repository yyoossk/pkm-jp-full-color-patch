"""US シンボル → 日本版 ROM の住所（同じバンクで命令の並びをくらべて、1か所だけ見つかったもの）"""
import re, sys
L=[1]*256
for op in [0x06,0x0E,0x16,0x1E,0x26,0x2E,0x36,0x3E,0x18,0x20,0x28,0x30,0x38,0xC6,0xCE,0xD6,0xDE,0xE6,0xEE,0xF6,0xFE,0xE0,0xF0,0xE8,0xF8,0xCB,0x10]: L[op]=2
for op in [0x01,0x11,0x21,0x31,0x08,0xC2,0xC3,0xCA,0xD2,0xDA,0xC4,0xCC,0xCD,0xD4,0xDC,0xEA,0xFA]: L[op]=3
M16={0x01,0x11,0x21,0x31,0x08,0xC2,0xC3,0xCA,0xD2,0xDA,0xC4,0xCC,0xCD,0xD4,0xDC,0xEA,0xFA}
def pat(code):
    out=b'';i=0
    while i<len(code):
        op=code[i];n=L[op]
        if i+n>len(code): break
        if op in M16: out+=re.escape(bytes([op]))+b'..'
        elif op in (0xE0,0xF0): out+=re.escape(bytes([op]))+b'.'
        else: out+=re.escape(code[i:i+n])
        i+=n
    return out
def main(usrom,ussym,jprom,out):
    us=open(usrom,'rb').read(); jp=open(jprom,'rb').read()
    syms=[]
    for l in open(ussym):
        m=re.match(r'([0-9a-f]+):([0-9a-f]+) (\S+)',l)
        if m:
            b,a=int(m.group(1),16),int(m.group(2),16)
            if a<0x8000: syms.append((b,a,m.group(3)))
    res={}
    for b,a,n in syms:
        if '.' in n: continue
        o=a if a<0x4000 else b*0x4000+a-0x4000
        if b*0x4000>=len(jp) and a>=0x4000: continue
        found=None
        for ln in (12,20,32,48):
            p=pat(us[o:o+ln]); lo,hi=(0,0x4000) if a<0x4000 else (b*0x4000,b*0x4000+0x4000)
            hits=[m.start() for m in re.finditer(p,jp[lo:hi],re.S)]
            if len(hits)==1: found=lo+hits[0]; break
            if not hits: break
        if found is not None: res[n]=(b, found if a<0x4000 else (found%0x4000)+0x4000)
    with open(out,'w') as f:
        for n,(b,a) in res.items(): f.write('%02x:%04x %s\n'%(b,a,n))
    print(len(syms),len(res))
main(*sys.argv[1:])
