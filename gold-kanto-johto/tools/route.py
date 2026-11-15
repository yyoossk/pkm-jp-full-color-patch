import sys; sys.path.insert(0,'/home/claude/work/scripts'); from play import *
from PIL import Image
MOM="RRRRUUUU"+"a"*44+"bbbb"+"DDDDDLLLLDDD"
def go(rom, keys, out, start_state=None):
    if start_state: g=GR(rom,state=start_state)
    else:
        g=newgame(rom); g.press('B',4,30); g.press('B',4,30)
    shots=[]
    for i,k in enumerate(keys):
        if k=='|': g.wait(30); p='/tmp/_%s_%d.png'%(out,i); g.shot(p); shots.append(p); continue
        if k=='a': g.press('A',4,40); continue
        if k=='b': g.press('B',4,40); continue
        if k=='$': g.save_state('/tmp/%s.state'%out); continue
        g.press(k,16,4)
    g.close(); return shots
def sheet(fs,out,cols=6):
    im=Image.new('RGB',(162*cols,146*((len(fs)+cols-1)//cols)),'white')
    for i,f in enumerate(fs): im.paste(Image.open(f),((i%cols)*162,(i//cols)*146))
    im.save(out)
