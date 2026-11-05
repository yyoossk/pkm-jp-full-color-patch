import sys
def ips(a,b):
    out=bytearray(b'PATCH'); i=0; n=len(b)
    while i<n:
        if i<len(a) and a[i]==b[i]: i+=1; continue
        j=i
        while j<n and (j>=len(a) or a[j]!=b[j] or (j+1<n and j+1<len(a) and a[j+1]!=b[j+1] and False)) and j-i<0xffff: j+=1
        # merge small gaps
        while j<n and j-i<0xfff0:
            k=j
            while k<n and k<len(a) and a[k]==b[k] and k-j<6: k+=1
            if k<n and k-j<6 and (k>=len(a) or a[k]!=b[k]):
                j=k
                while j<n and (j>=len(a) or a[j]!=b[j]) and j-i<0xffff: j+=1
            else: break
        s=i
        if s==0x454f46: s-=1
        out+=s.to_bytes(3,'big')+(j-s).to_bytes(2,'big')+b[s:j]; i=j
    out+=b'EOF'; return bytes(out)
def apply(a,p):
    a=bytearray(a); i=5
    while p[i:i+3]!=b'EOF':
        o=int.from_bytes(p[i:i+3],'big'); l=int.from_bytes(p[i+3:i+5],'big'); i+=5
        if l==0:
            rl=int.from_bytes(p[i:i+2],'big'); a[o:o+rl]=bytes([p[i+2]])*rl; i+=3
        else: a[o:o+l]=p[i:i+l]; i+=l
    return bytes(a)
if __name__=='__main__':
    a=open(sys.argv[1],'rb').read(); b=open(sys.argv[2],'rb').read()
    p=ips(a,b); assert apply(a,p)==b; open(sys.argv[3],'wb').write(p); print(sys.argv[3],len(p))
