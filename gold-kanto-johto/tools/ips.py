import sys,zlib
def apply(rom,ips):
    r=bytearray(rom); p=5
    assert ips[:5]==b'PATCH'
    while not (ips[p:p+3]==b'EOF' and len(ips)-p in (3,6)):
        o=int.from_bytes(ips[p:p+3],'big'); n=int.from_bytes(ips[p+3:p+5],'big'); p+=5
        if n==0:
            n=int.from_bytes(ips[p:p+2],'big'); d=bytes([ips[p+2]])*n; p+=3
        else: d=ips[p:p+n]; p+=n
        if o+n>len(r): r+=bytes(o+n-len(r))
        r[o:o+n]=d
    if len(ips)>=p+6: r=r[:int.from_bytes(ips[p+3:p+6],'big')]
    return bytes(r)
if __name__=='__main__':
    out=apply(open(sys.argv[1],'rb').read(),open(sys.argv[2],'rb').read())
    open(sys.argv[3],'wb').write(out); print('%08X'%zlib.crc32(out),len(out))
