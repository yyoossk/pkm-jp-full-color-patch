def w(b,o): return b[o]|b[o+1]<<8
B=0xE*0x4000-0x4000
def groups(r, tbl, n):
    ptrs=[w(r,B+tbl+2*i) for i in range(n)]
    out=[]
    for i,p in enumerate(ptrs):
        end=ptrs[i+1] if i+1<n else None
        out.append(parse(r,p,end))
    return ptrs,out
def parse(r,p,end,maxn=80):
    o=B+p; L=[]
    while (end is None and len(L)<maxn) or (end is not None and o<B+end):
        s=o
        while r[o]!=0x50: o+=1
        o+=1; t=r[o]; o+=1
        sz={0:2,1:6,2:3,3:7}.get(t)
        if sz is None: break
        while r[o]!=0xFF: o+=sz
        o+=1; L.append(bytes(r[s:o]))
        if end is None and r[o] in (0x00,0xff): break
    return L

def merged(c, p, g, CT=0x59BA, GT=0x595C):
    """金の手持ちリスト（クラスごと）：金の i 番目までは 金（ただし MOD が変えた所は MOD）、その先は MOD のものを そのまま"""
    _, C = groups(c, CT, 67); _, M = groups(p, CT, 67); _, G = groups(g, GT, 66)
    out = []
    for i in range(66):
        L = []
        for j in range(len(M[i])):
            if j < len(G[i]):
                L.append(M[i][j] if (j < len(C[i]) and M[i][j] != C[i][j]) or j >= len(C[i]) else G[i][j])
            else:
                L.append(M[i][j])
        out.append(L)
    return out
