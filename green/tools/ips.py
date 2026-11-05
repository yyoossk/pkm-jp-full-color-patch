import sys
def apply(src,p):
    out=bytearray(src);i=5
    while p[i:i+3]!=b'EOF':
        o=int.from_bytes(p[i:i+3],'big');n=int.from_bytes(p[i+3:i+5],'big');i+=5
        if n==0: r=int.from_bytes(p[i:i+2],'big');d=bytes([p[i+2]])*r;i+=3
        else: d=p[i:i+n];i+=n
        if len(out)<o+len(d): out.extend(bytes(o+len(d)-len(out)))
        out[o:o+len(d)]=d
    return bytes(out)
