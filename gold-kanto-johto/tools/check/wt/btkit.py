import sys, time
sys.path.insert(0,'/home/claude/sameboy-harness/python'); sys.path.insert(0,'/home/claude/repo/gold-kanto-johto/tools/check')
from gr import GR; from walker import W
ROMS = {'base': '/home/claude/work/goldsrc/base.gbc', 'kit': '/home/claude/work/ref/kin64.gbc', 'full': '/home/claude/work/out/gold_full.gbc'}
for n in sys.argv[1:]:
    R = ROMS[n]
    g = GR(R); g.load_state('jt_%s.st' % n); g.wait(2)
    w = W(g, R)
    m = w.maps[(4,9)]
    # BT の 入口の 前へ
    wp = [x for x in m['warps'] if x[2] == (3,13)][0]
    g.poke(0xD9C6, 4); g.poke(0xD9C7, 9); g.poke(0xD9C9, wp[0]); g.poke(0xD9C8, wp[1]+2)
    g.poke(0xCF20, 255); g.poke(0xFFA1, 0xF1); g.poke(0xD14B, 1); g.wait(200)
    w.t0 = time.time(); w.budget = 200; w.run_wild = True
    for d in 'DDUUU': w.step(d); g.wait(10)
    g.wait(60); print(n, w.pos())
    o=g.oam(); print([ (o[i]-16,o[i+1]-8,hex(o[i+2]),hex(o[i+3])) for i in range(0,160,4) if 0<o[i]<160 and o[i+1]<168])
    g.shot('shots/btk_%s_0.png' % n)
    try:
        for i in range(4): w.advance(None, n=200); w.settle()
    except TimeoutError: pass
    g.wait(30); g.shot('shots/btk_%s_1.png' % n)
    o=g.oam(); print([ (o[i]-16,o[i+1]-8,hex(o[i+2]),hex(o[i+3])) for i in range(0,160,4) if 0<o[i]<160 and o[i+1]<168])
    g.close()
