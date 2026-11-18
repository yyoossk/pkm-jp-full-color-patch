import sys; sys.path.insert(0,'/home/claude/sameboy-harness/python'); sys.path.insert(0,'/home/claude/repo/gold-kanto-johto/tools/check')
from gr import GR; from walker import W
R='/home/claude/work/out/gold_full.gbc'; g=GR(R); g.load_state(sys.argv[1]); g.wait(3); w=W(g,R)
mid=tuple(map(int,sys.argv[2].split(','))) if len(sys.argv)>2 else w.pos()[:2]
c=w.coll(mid); m=w.maps[mid]
ob={(o[2]-4,o[1]-4):o[0] for o in m['attr']['objs']}
wp={(x,y) for x,y,_ in m['warps']}
print(w.pos(), 'repel', w.rd(0xD9B1))
print('   '+''.join(str(x%10) for x in range(m['w']*2)))
for y in range(m['h']*2):
    row=''
    for x in range(m['w']*2):
        v=c(x,y) or 0
        ch='.' if v==0 else '#' if v==7 else '~' if v==0x29 else '%x'%(v>>4)
        if (x,y) in wp: ch='W'
        if (x,y) in ob: ch='B' if ob[(x,y)]==90 else 'o'
        if (x,y)==tuple(w.pos()[2:]) and mid==w.pos()[:2]: ch='@'
        row+=ch
    print('%2d '%y+row)
for o in m['attr']['objs']: print((o[2]-4,o[1]-4),o[0],o[3], 'flag', (o[11]|o[12]<<8) if len(o)>12 else None)
