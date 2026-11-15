"""カントーの トレーナーが 勝った あと（マップに 入りなおすと）消える（第104弾の 銀版）：クリスタル版の マップを 写した カントーでは、
   トレーナーの 人の「見える／見えない」の 印が その トレーナーの「勝った」の 印と 同じ だった（182人：24・25ばんどうろ ほか
   ほとんどの 道路、トキワのもり、チャンピオンロード、かくとう道場 など）。その 人の 印を -1（いつも 見える）に。赤と 同じく のこる。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
from gsc import fo, r16


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    gt = fo(0x25, 0x40ED); seen = set(); n = 0
    for g in range(1, 27):
        gp = fo(0x25, r16(rom, gt + 2 * (g - 1))); nxt = fo(0x25, r16(rom, gt + 2 * g)) if g < 26 else None
        for m in range(200):
            h = gp + 9 * m
            if (nxt is not None and h >= nxt) or rom[h] in (0, 0xFF): break
            ao = fo(rom[h], r16(rom, h + 3)); sb = rom[ao + 6]; ev = fo(sb, r16(rom, ao + 9)) + 2
            if (sb, ev) in seen: continue
            seen.add((sb, ev))
            p = ev; k = rom[p]; p += 1 + 5 * k; k = rom[p]; p += 1 + 8 * k; k = rom[p]; p += 1 + 5 * k; k = rom[p]; p += 1
            for i in range(k):
                o = p + 13 * i; fl = r16(rom, o + 11)
                if rom[o + 7] & 0x0F == 2 and fl != 0xFFFF and r16(rom, fo(sb, r16(rom, o + 9))) == fl:
                    rom[o + 11] = rom[o + 12] = 0xFF; n += 1
    assert n == 182, n
    log.append('カントーの トレーナーは 勝った あとも のこる（%d 人）' % n)
    return rom
