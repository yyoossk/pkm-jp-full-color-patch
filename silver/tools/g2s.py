# 金の アドレス（バンク, アドレス）→ 銀の アドレス（近くの ラベル + ずれ）
import re, sys, bisect, collections
K='/home/claude/k3/kit/src/'
def load(fn):
    J={}; B={}
    for l in open(K+fn,encoding='utf-8'):
        m=re.match(r'DEF (J_|JB_)(\S+) EQU \$([0-9a-f]+)',l)
        if m:
            (J if m.group(1)=='J_' else B)[m.group(2)]=int(m.group(3),16)
    by=collections.defaultdict(list)
    for n,a in J.items():
        if n in B: by[B[n]].append((a,n))
    for b in by: by[b].sort()
    return J,B,by
GJ,GB,Gby=load('jp_all.inc'); SJ,SB,Sby=load('jp_all_silver.inc')
SROM=open('/home/claude/k3/kit/base.gbc','rb').read()
def g2s(bank,addr):
    if addr<0x4000: bank=0
    L=Gby.get(bank,[])
    i=bisect.bisect_right(L,(addr,'~'))-1
    if i<0: return None
    a,n=L[i]
    if n not in SJ: return (None,n,addr-a)
    sa=SJ[n]+(addr-a); sb=SB[n]
    return (sb,sa,n,addr-a)
def sbytes(bank,addr,n=8):
    o=addr if addr<0x4000 else bank*0x4000+addr-0x4000
    return SROM[o:o+n].hex(' ')
if __name__=='__main__':
    for arg in sys.argv[1:]:
        b,a=arg.split(':'); b=int(b,16); a=int(a,16)
        r=g2s(b,a); print(arg,'->',r, sbytes(r[0],r[1]) if r and r[0] is not None else '')
