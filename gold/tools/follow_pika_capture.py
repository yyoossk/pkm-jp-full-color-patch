import sys; sys.path.insert(0,'/home/claude/sameboy-harness/python')
from gr import GR
from PIL import Image
import os, pickle
res={}
for n in range(0x1d):
    g=GR('/tmp/claude-0/h11/ypatch.gbc',state='/tmp/claude-0/h11/yfree.st'); g.wait(10)
    g.shot('/tmp/claude-0/h11/ybase.png'); base=Image.open('/tmp/claude-0/h11/ybase.png').convert('RGB')
    g.poke(0xd3c8,n); g.press('S',4,0)
    fr=[]
    for f in range(700):
        g.wait(1); g.shot('/tmp/claude-0/h11/yt.png')
        fr.append(Image.open('/tmp/claude-0/h11/yt.png').convert('RGB').tobytes())
    g.close()
    res[n]=(base.tobytes(),fr)
    print(n, flush=True)
pickle.dump(res,open('/tmp/claude-0/h11/ycap_all.pkl','wb'))
