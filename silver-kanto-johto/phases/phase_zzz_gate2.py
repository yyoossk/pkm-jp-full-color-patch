"""2ばんどうろの ゲート（ひでんマシン05の ゲート）の 北の 入口：2マスの 入口の 右（(x17,y35)）に 立っても
   入れなかった（ワープが 左 (x16,y35) だけ）。右にも 同じ ゲートへの ワープを 足す（左は ゲートの 左の 出入口、右は 右へ）。
   2ばんどうろの スクリプトの バンク（$69）は いっぱい なので、$69 を まるごと $F2 に 写して 2ばんどうろだけ $F2 を
   使う ように し、$F2 の 中の ほかの マップの イベントの 場所（2ばんどうろは 使わない）に 新しい イベントを 書く。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
import gsc
from gsc import fo, r16

NB = 0xF2
ROUTE2 = (23, 1)
GATE = (26, 79)


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    SM = gsc.Maps(bytes(rom), gsc.PG + '/constants/map_constants.asm')
    a = SM.attributes(ROUTE2); ev = SM.events(ROUTE2); ob = a['scripts_bank']
    assert ob == 0x69 and not any(rom[fo(NB, 0x4000):fo(NB, 0x8000)])
    ws = list(ev['warps'])
    i = ws.index((35, 16, 2) + GATE); assert (35, 17) not in [(w[0], w[1]) for w in ws]
    ws[i] = (35, 16, 1) + GATE
    ws.insert(i + 1, (35, 17, 2) + GATE)
    r = rom
    blob = bytes(r[ev['off']:ev['off'] + 2]) + bytes([len(ws)]) + b''.join(bytes(w) for w in ws) + \
        bytes(r[fo(ob, a['events']) + 3 + 5 * len(ev['warps']):ev['end']])
    # $69 の ほかの マップの イベントで、2ばんどうろの イベント・スクリプトと 重ならない 大きな 場所
    mine = (ev['off'], ev['end'])
    best = None
    for k in SM.hdr:
        if k == ROUTE2: continue
        try: ak = SM.attributes(k)
        except Exception: continue
        if ak['scripts_bank'] != ob: continue
        e2 = SM.events(k); n = e2['end'] - e2['off']
        if n >= len(blob) and not (e2['off'] < mine[1] and mine[0] < e2['end']):
            if best is None or n < best[1]: best = (e2['off'], n, k)
    assert best, '場所が ない'
    rom[fo(NB, 0x4000):fo(NB, 0x8000)] = rom[fo(ob, 0x4000):fo(ob, 0x8000)]
    dst = best[0] - fo(ob, 0x4000) + fo(NB, 0x4000)
    rom[dst:dst + len(blob)] = blob
    ao = a['off']
    rom[ao + 6] = NB
    na = best[0] - fo(ob, 0x4000) + 0x4000
    rom[ao + 9] = na & 0xFF; rom[ao + 10] = na >> 8
    # ゲートの 中：北の 出入口 2つ（(0,4)(0,5)）を それぞれ 2ばんどうろの 左・右へ
    gt = fo(0x25, 0x40ED); hp = fo(0x25, r16(rom, gt + 2 * (GATE[0] - 1))) + 9 * (GATE[1] - 1)
    gao = fo(rom[hp], r16(rom, hp + 3)); go = fo(rom[gao + 6], r16(rom, gao + 9)) + 2
    ng = rom[go]; go += 1
    ge = dict(warps=[tuple(rom[go + 5 * j:go + 5 * j + 5]) for j in range(ng)])
    gw = list(ge['warps'])
    for j, w in enumerate(gw):
        if (w[0], w[3], w[4]) == (0,) + ROUTE2:
            nw = i + 1 + (1 if w[1] == 5 else 0)          # 1 から 数える ワープの 番号
            rom[go + 5 * j + 2] = nw
    # 右の マス（ブロック $86 の 右下、2ばんどうろ だけで 使う）の 当たりも 左と 同じ ワープの じゅうたん（$70）に
    hp2 = fo(0x25, r16(rom, gt + 2 * (ROUTE2[0] - 1))) + 9 * (ROUTE2[1] - 1); ts = rom[hp2 + 1]
    te = fo(0xE1, 0x4000) + 15 * ts; c = fo(rom[te + 6], r16(rom, te + 7))
    W = rom[ao + 2]; bl = fo(rom[ao + 3], r16(rom, ao + 4))
    b = rom[bl + (35 // 2) * W + 17 // 2]; assert b == 0x86 and rom[c + 4 * b:c + 4 * b + 4] == bytes([0, 0, 0x70, 0])
    rom[c + 4 * b + 3] = 0x70
    log.append('2ばんどうろの ゲートの 北の 入口：右の マスにも ワープ（スクリプトの バンク $69 → $%02X、イベント %s の 場所へ）'
               % (NB, best[2]))
    return rom
