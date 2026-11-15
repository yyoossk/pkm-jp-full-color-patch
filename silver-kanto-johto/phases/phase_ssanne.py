"""サントアンヌごうの 扉と 階段（第106弾の 銀版）：
   ・かんぱん（へさき）の 船に もどる 扉（赤の (13,6)・(13,7)）：ブロック $24 の 右半分の 当たりが「上／下を 押すと 移る」
     （$78・$70）で、右へ 歩いても もどれなかった → 両方「右へ 歩くと 移る」（$7E）。
   ・せんちょうの へや (0,7)・1かい (37,15)・地下1かい (27,5) の 階段：「乗って 下を 押すと 移る」（$70）で、一歩 おりて もどると
     移らなかった → 乗れば すぐ 移る 階段（$73）。
   当たりは タイルセットの 当たりの 表（$E1:$4000 の 表の +6・+7）。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
import cmaps, port, gsc
from gsc import fo, r16

BOW, DOOR_XY, BLOCK = (26, 45), (13, 6), 0x24
STAIRS = [((26, 47), (0, 7)), ((26, 41), (37, 15)), ((26, 44), (27, 5))]
TS_TAB = (0xE1, 0x4000)


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    cmod = open(cmaps.CMOD, 'rb').read()
    P = port.Port.__new__(port.Port)
    P.CM = cmaps.CMaps(cmod); P.SM = gsc.Maps(bytes(rom[:0x100000]), gsc.PG + '/constants/map_constants.asm'); P.todo = {}
    gt = fo(0x25, 0x40ED)
    def info(cg, cm):
        g, m = P.x_map(cg, cm); h = fo(0x25, r16(rom, gt + 2 * (g - 1))) + 9 * (m - 1)
        ao = fo(rom[h], r16(rom, h + 3)); W = rom[ao + 2]; Hh = rom[ao + 1]
        blk = fo(rom[ao + 3], r16(rom, ao + 4)); ts = rom[h + 1]
        sb = rom[ao + 6]; ev = fo(sb, r16(rom, ao + 9)) + 2; n = rom[ev]
        warps = [(rom[ev + 1 + 5 * i + 1], rom[ev + 1 + 5 * i]) for i in range(n)]          # (x, y)
        return dict(g=g, m=m, W=W, H=Hh, blk=blk, ts=ts, warps=warps)
    def coll(ts):
        te = fo(*TS_TAB) + 15 * ts; return fo(rom[te + 6], r16(rom, te + 7))
    allmaps = []
    for g in range(1, 27):
        gp = fo(0x25, r16(rom, gt + 2 * (g - 1))); nxt = fo(0x25, r16(rom, gt + 2 * g)) if g < 26 else None
        for m in range(200):
            h = gp + 9 * m
            if (nxt is not None and h >= nxt) or rom[h] in (0, 0xFF): break
            ao = fo(rom[h], r16(rom, h + 3)); allmaps.append(((g, m + 1), rom[h + 1], fo(rom[ao + 3], r16(rom, ao + 4)), rom[ao + 1] * rom[ao + 2]))
    def alone(me, ts, b):
        return all(b not in rom[bp:bp + n] for k, t, bp, n in allmaps if t == ts and k != (me['g'], me['m']))
    bow = info(*BOW); assert bow['warps'] == [(13, 6), (13, 7)], bow['warps']
    assert rom[bow['blk'] + (DOOR_XY[1] // 2) * bow['W'] + DOOR_XY[0] // 2] == BLOCK and alone(bow, bow['ts'], BLOCK)
    co = coll(bow['ts']) + 4 * BLOCK; assert rom[co:co + 4] == bytes([0x00, 0x78, 0x00, 0x70]), rom[co:co + 4].hex()
    rom[co + 1] = rom[co + 3] = 0x7E
    for k, (x, y) in STAIRS:
        me = info(*k); assert (x, y) in me['warps'] and me['ts'] == bow['ts']
        b = rom[me['blk'] + (y // 2) * me['W'] + x // 2]; q = (y % 2) * 2 + x % 2
        assert alone(me, me['ts'], b), (k, hex(b))
        c = coll(me['ts']) + 4 * b + q; assert rom[c] == 0x70, (k, rom[c]); rom[c] = 0x73
    log.append('サントアンヌごう：へさきの 扉は 右へ（$7E）、階段 3つは 乗れば 移る（$73）。タイルセット %d' % bow['ts'])
    return rom
