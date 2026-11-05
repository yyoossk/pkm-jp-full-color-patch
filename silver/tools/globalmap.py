import align as A, pickle, sys, collections
A.load(sys.argv[1])
votes=collections.defaultdict(collections.Counter)
labjp={}
names=[n for n,(b,a) in A.SYM.items() if a<0x8000]
for n in names:
    b,a=A.SYM[n]; e=A.endof(b,a); L=e-a
    if L<10: continue
    r=A.locate(n, n=min(L,64))
    if len(r)!=1: continue
    labjp[n]=A.ptr(r[0])
    for (op,v),j in A.operands(n,r[0],n=L).items():
        votes[v][j]+=1
m={v:c.most_common(1)[0][0] for v,c in votes.items()}
pickle.dump((m,labjp,votes),open(sys.argv[2],'wb'))
print(len(labjp),len(m))
