import re,bisect,sys
def load(p):
    L=[]
    for l in open(p):
        m=re.match(r'([0-9a-f]+):([0-9a-f]+) (\S+)',l)
        if m: L.append(((int(m.group(1),16) if int(m.group(2),16)>=0x4000 else 0)*0x10000+int(m.group(2),16),m.group(3)))
    L.sort(); return L
def near(L,bank,addr):
    k=(bank if addr>=0x4000 else 0)*0x10000+addr
    i=bisect.bisect_right([x for x,_ in L],k)-1
    return (L[i][1],k-L[i][0]) if i>=0 else None
if __name__=='__main__':
    L=load(sys.argv[1])
    for x in sys.argv[2:]:
        b,a=x.split(':'); print(x,near(L,int(b,16),int(a,16)))
