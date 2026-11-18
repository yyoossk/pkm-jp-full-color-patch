import sys, time
sys.path.insert(0,'/home/claude/sameboy-harness/python'); sys.path.insert(0,'/home/claude/repo/gold-kanto-johto/tools/check')
from gr import GR; from walker import W
R = '/home/claude/work/out/gold_full.gbc'
g = GR(R); g.load_state('jt_full.st'); g.wait(2)
w = W(g, R)
m = w.maps[(4,9)]
wp = [x for x in m['warps'] if x[2] == (3,13)][0]
g.poke(0xD9C6, 4); g.poke(0xD9C7, 9); g.poke(0xD9C9, wp[0]); g.poke(0xD9C8, wp[1]+2)
g.poke(0xCF20, 255); g.poke(0xFFA1, 0xF1); g.poke(0xD14B, 1); g.wait(200)
w.t0 = time.time(); w.budget = 200
def structs(tag):
    print(tag)
    for i in range(13):
        b = g.peek(0xD1F0 + 0x28*i, 0x28)
        if b[0]: print('  %2d spr %02x mapobj %02x flags1 %02x flags2 %02x vtile %02x pal %02x mv %02x xy %d,%d' % (i, b[0], b[1], b[4], b[5], b[2], b[6], b[3], b[0x10]-4, b[0x11]-4))
for d in 'DD': w.step(d); g.wait(10)
structs('外')
g.save_state('btdbg_out.st')
w.step('U'); g.wait(10); w.step('U'); 
for k in range(12):
    g.wait(8); structs('入って %d' % k)
g.close()
