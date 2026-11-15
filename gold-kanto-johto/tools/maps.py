import re
REF='/home/claude/work/mod/ref/'
def groups(repo):
    s=open(REF+repo+'/data/maps/maps.asm').read()
    out=[];cur=None
    for l in s.splitlines():
        m=re.match(r'MapGroup_(\w+):',l)
        if m: cur=[];out.append((m.group(1),cur))
        m=re.match(r'\s*map (\w+),',l)
        if m and cur is not None: cur.append(m.group(1))
    return out
def w(b,o): return b[o]|b[o+1]<<8
def headers(rom,mgp,repo):
    """-> {mapname:(group,num,fileoffset)}"""
    G=groups(repo); d={}
    for gi,(gn,maps) in enumerate(G):
        p=w(rom,mgp+2*gi); base=(mgp//0x4000)*0x4000+p-0x4000
        for mi,mn in enumerate(maps): d[mn]=(gi+1,mi+1,base+9*mi)
    return d
CMGP=0x94000; GMGP=0x94000+0x40ed-0x4000
