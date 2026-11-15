import sys; sys.path.insert(0,'/home/claude/work/scripts'); from play import *
from PIL import Image
def run(rom, keys, out):
    g=newgame(rom); g.press('B',4,30); g.press('B',4,30)
    shots=[]
    for i,k in enumerate(keys):
        if k=='|': g.wait(30); p='/tmp/_%s_%d.png'%(out,i); g.shot(p); shots.append(p); continue
        if k=='a': g.press('A',4,40); continue
        if k=='b': g.press('B',4,40); continue
        g.press(k,16,4)
    g.close(); return shots
def side(a,b,out):
    n=len(a); im=Image.new('RGB',(330,148*n),'white')
    for i,(x,y) in enumerate(zip(a,b)): im.paste(Image.open(x),(0,148*i)); im.paste(Image.open(y),(170,148*i))
    im.save(out)
if __name__=='__main__':
    keys=sys.argv[1]
    a=run('out/gold_p9.gbc',keys,'g'); b=run('ref/crystal_p9.gbc',keys,'c'); side(a,b,sys.argv[2])
