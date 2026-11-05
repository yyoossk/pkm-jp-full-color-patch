import sys
def apply(rom,ips):
    r=bytearray(rom); p=ips; assert p[:5]==b'PATCH'; i=5
    while True:
        if p[i:i+3]==b'EOF':
            if len(p)>=i+6: del r[int.from_bytes(p[i+3:i+6],'big'):]
            return bytes(r)
        o=int.from_bytes(p[i:i+3],'big'); s=int.from_bytes(p[i+3:i+5],'big'); i+=5
        if s==0:
            n=int.from_bytes(p[i:i+2],'big'); v=p[i+2]; i+=3; d=bytes([v])*n
        else: d=p[i:i+s]; i+=s
        if len(r)<o+len(d): r.extend(b'\0'*(o+len(d)-len(r)))
        r[o:o+len(d)]=d
