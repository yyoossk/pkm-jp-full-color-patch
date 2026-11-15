import sys; sys.path.insert(0,'/home/claude/sameboy-harness/python')
from gr import GR
def newgame(rom, shots=None):
    g=GR(rom); g.wait(400)
    for i in range(400):
        g.press('A',4,16)
        if i%25==0 and shots: g.shot('%s_%03d.png'%(shots,i))
    return g
