"""英語版の RAM 住所 → 日本版の RAM 住所（同じルーチンの 命令の 引数を 並べて くらべる）"""
import re, sys
from collections import Counter, defaultdict
L=[1]*256
for op in [0x06,0x0E,0x16,0x1E,0x26,0x2E,0x36,0x3E,0x18,0x20,0x28,0x30,0x38,0xC6,0xCE,0xD6,0xDE,0xE6,0xEE,0xF6,0xFE,0xE0,0xF0,0xE8,0xF8,0xCB,0x10]: L[op]=2
for op in [0x01,0x11,0x21,0x31,0x08,0xC2,0xC3,0xCA,0xD2,0xDA,0xC4,0xCC,0xCD,0xD4,0xDC,0xEA,0xFA]: L[op]=3
def fo(b,a): return a if a<0x4000 else b*0x4000+a-0x4000
def build(us, ussym, jp, jpaddrs):
    """jpaddrs: {label:(bank,addr)} の 日本版の住所"""
    S={}
    for l in open(ussym):
        m=re.match(r'([0-9a-f]+):([0-9a-f]+) (\S+)',l)
        if m: S[m.group(3)]=(int(m.group(1),16),int(m.group(2),16))
    votes=defaultdict(Counter)
    for n,(jb,ja) in jpaddrs.items():
        if n not in S or S[n][1]>=0x8000: continue
        ub,ua=S[n]; uo=fo(ub,ua); jo=fo(jb,ja)
        i=0
        while i<200:
            op=us[uo+i]
            if op!=jp[jo+i]: break
            n_=L[op]
            if n_==3 and op in (0x01,0x11,0x21,0x31,0xEA,0xFA,0x08):
                u=us[uo+i+1]|us[uo+i+2]<<8; j=jp[jo+i+1]|jp[jo+i+2]<<8
                if 0xC000<=u<0xE000 and 0xC000<=j<0xE000: votes[u][j]+=1
            if op in (0xC9,0xC3,0x18,0xD9): break
            i+=n_
    return {u:c.most_common(1)[0][0] for u,c in votes.items()}
def labels(ussym):
    d={}
    for l in open(ussym):
        m=re.match(r'([0-9a-f]+):([0-9a-f]+) (\S+)',l)
        if m:
            a=int(m.group(2),16)
            if 0xC000<=a<0xE000: d.setdefault(m.group(3),(int(m.group(1),16),a))
    return d

class RamX:
    """日本版クリスタルの RAM → 日本版金の RAM（英語版のラベル名を 通して）"""
    def __init__(s):
        import pickle
        R='/home/claude/work/mod/ref/'
        CM,GM=pickle.load(open('/home/claude/work/ref/rammaps.pkl','rb'))
        s.CL=labels(R+'pokecrystal/pokecrystal.sym'); s.GL=labels(R+'pokegold/pokegold.sym')
        ca={a:n for n,(b,a) in s.CL.items()}; ga={a:n for n,(b,a) in s.GL.items()}
        # 名前のある所だけで ずれ（JP-US）を 求める
        s.c_pairs=sorted((j,u) for u,j in CM.items() if u in ca)
        s.g_pairs=sorted((u,j) for u,j in GM.items() if u in ga)
        s.ca=sorted(ca.items()); s.cnames=ca
    def c_jp2us(s, j):
        best=None
        for jj,u in s.c_pairs:
            if jj<=j and (best is None or jj>=best[0]): best=(jj,u)
        return best[1]+(j-best[0]) if best else None
    def g_us2jp(s, u):
        best=None
        for uu,j in s.g_pairs:
            if uu<=u and (best is None or uu>=best[0]): best=(uu,j)
        return best[1]+(u-best[0]) if best else None
    def name_of_us(s, u):
        base=max(a for a,n in s.ca if a<=u); return s.cnames[base], u-base
    def x(s, j):
        u=s.c_jp2us(j)
        if u is None: return None, None
        n,off=s.name_of_us(u)
        g=s.GL.get(n)
        if g is None: return None, '%s+%d'%(n,off)
        return s.g_us2jp(g[1]+off), '%s+%d'%(n,off)
