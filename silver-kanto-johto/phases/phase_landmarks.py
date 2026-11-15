"""地名の 看板（第101弾の 銀版）：クリスタル版の マップの 地名の まちがい
   おつきみやま 1F・B1F・B2F（クリスタル 26:37〜39）：3ばんどうろ → おつきみやま、
   ちかつうろの 入口（26:140〜142）：5ばんどうろ → 6・7・8ばんどうろ、ディグダのあなの 11ばんどうろの 入口（26:110）→ ディグダのあな。
   銀の 地名の 番号は クリスタルの −1。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
import cmaps, port, gsc
from gsc import fo, r16

MT_MOON, ROUTE_3, ROUTE_5, ROUTE_6, ROUTE_7, ROUTE_8, ROUTE_11, DIGLETTS = 0x34, 0x33, 0x39, 0x3B, 0x3E, 0x3F, 0x48, 0x3D
FIX = {(26, 37): (ROUTE_3, MT_MOON), (26, 38): (ROUTE_3, MT_MOON), (26, 39): (ROUTE_3, MT_MOON),
       (26, 140): (ROUTE_5, ROUTE_6), (26, 141): (ROUTE_5, ROUTE_7), (26, 142): (ROUTE_5, ROUTE_8),
       (26, 110): (ROUTE_11, DIGLETTS)}


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    cmod = open(cmaps.CMOD, 'rb').read()
    P = port.Port.__new__(port.Port)
    P.CM = cmaps.CMaps(cmod); P.SM = gsc.Maps(bytes(rom[:0x100000]), gsc.PG + '/constants/map_constants.asm'); P.todo = {}
    gt = fo(0x25, 0x40ED); out = []
    for (cg, cm), (old, new) in FIX.items():
        g, m = P.x_map(cg, cm)
        h = fo(0x25, r16(rom, gt + 2 * (g - 1))) + 9 * (m - 1)
        assert rom[h + 5] == old, ((cg, cm), (g, m), hex(rom[h + 5]))
        rom[h + 5] = new; out.append('%d-%d' % (g, m))
    log.append('地名の 看板：おつきみやま・ちかつうろ・ディグダのあな（%s）' % ' '.join(out))
    return rom
