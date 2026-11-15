"""フレンドリィショップの 品物：クリスタル版で 変えた 店（タマムシデパート・シオン など）を 銀へ。
   銀の Marts（$05:$65EA、34 店）の 中身を ぜんぶ $E5:$4000〜 に 並べなおす。追加機能キットの MasterBallMart
   （GetMart の あとに farcall。b ＝ バンク、タマムシ3F と セキエイの 表の 場所で わざマシン売り・マスターボールに かえる）の
   ld b,$05 を $E5 に、くらべる 場所を 新しい 場所に。
   クリスタル版で もとの クリスタルと 同じ 店は 銀の 品物の まま、変えた 店は クリスタル版の 品物（道具の 番号は 銀へ）。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
import cmaps, xlat
from gsc import fo, r16

MB = 0xE5
S_MARTS, C_MARTS, N = 0x65EA, 0x64C3, 34
GETMART_PAT = bytes([0x21, 0xEA, 0x65, 0x19, 0x19, 0x5E, 0x23, 0x56, 0x3E])   # GetMart の ld hl, Marts …（キットが farcall）


# 第110弾：ニビ・ハナダは 赤と 同じ。グレン（ヤマブキの 表を 使って いた）は どの スクリプトも 使わない 表 33 を
# 赤の グレンの 品物に して 使う（表 25 は 追加機能キットが わざマシン売りの 印に して いるので 使わない）
RED_MARTS = {19: ('POKE_BALL', 'POTION', 'ESCAPE_ROPE', 'ANTIDOTE', 'BURN_HEAL', 'AWAKENING', 'PARLYZ_HEAL'),
             20: ('POKE_BALL', 'POTION', 'REPEL', 'ANTIDOTE', 'BURN_HEAL', 'AWAKENING', 'PARLYZ_HEAL'),
             28: ('HP_UP', 'PROTEIN', 'IRON', 'CARBOS', 'CALCIUM'),     # タマムシ5F（赤は マックスアップも 売る）
             33: ('ULTRA_BALL', 'GREAT_BALL', 'HYPER_POTION', 'MAX_REPEL', 'ESCAPE_ROPE', 'FULL_HEAL', 'REVIVE')}
CINNABAR_MART, MART_SAFFRON, MART_CINNABAR = (26, 52), 30, 33


def lst(r, b, p):
    o = fo(b, p); e = o + 1
    while r[e] != 0xFF: e += 1
    return bytes(r[o:e + 1])                  # 数, 品物…, -1（クリスタル版は 数を 0 に した 店も ある）


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    cmod = open(cmaps.CMOD, 'rb').read(); corig = open(cmaps.CORIG, 'rb').read()
    T = xlat.Tables(); ci = xlat.inv(T.c_item)
    GETMART = bytes(rom[fo(5, 0x4000):fo(5, 0x8000)]).index(GETMART_PAT) + fo(5, 0x4000)
    g = rom[GETMART:GETMART + 14]
    assert g[:8] == bytes([0x21, 0xEA, 0x65, 0x19, 0x19, 0x5E, 0x23, 0x56]) and g[8] == 0x3E and g[10] == 0x21 and g[13] == 0xCF
    kb, ka = g[9], r16(g, 11); k = fo(kb, ka)
    assert rom[k:k + 2] == bytes([0x06, 0x05]) and rom[k + 2:k + 4] == bytes([0x7B, 0xFE]) and rom[k + 5:k + 8] == bytes([0x20, 0x0C, 0x7A]) \
        and rom[k + 19:k + 21] == bytes([0x7B, 0xFE]) and rom[k + 22:k + 25] == bytes([0xC0, 0x7A, 0xFE])
    old = {r16(rom, fo(5, S_MARTS) + 2 * i): i for i in range(N)}
    i_tm = old[rom[k + 9] << 8 | rom[k + 4]]; i_mb = old[rom[k + 25] << 8 | rom[k + 21]]
    assert not any(rom[fo(MB, 0x4000):fo(MB, 0x8000)])
    q = 0x4000; changed = []
    assert MART_CINNABAR not in (i_tm, i_mb)
    for i in range(N):
        cl = lst(cmod, 5, r16(cmod, fo(5, C_MARTS) + 2 * i))
        ol = lst(corig, 5, r16(corig, fo(5, C_MARTS) + 2 * i))
        sl = lst(rom, 5, r16(rom, fo(5, S_MARTS) + 2 * i))
        if cl != ol:
            items = []
            for v in cl[1:-1]:
                if v >= 0xBF: items.append(v); continue          # わざマシン・ひでんマシン（同じ 番号）
                n = ci.get(v)
                assert n in T.g_item, (i, hex(v), n)
                items.append(T.g_item[n])
            sl = bytes([cl[0]] + items + [0xFF]); changed.append(i)
        if i in RED_MARTS:                                       # 第110弾：赤と 同じ 品物・順
            sl = bytes([len(RED_MARTS[i])] + [T.g_item[n] for n in RED_MARTS[i]] + [0xFF]); changed.append('赤%d' % i)
        o = fo(MB, q); rom[o:o + len(sl)] = sl
        rom[fo(5, S_MARTS) + 2 * i] = q & 0xff; rom[fo(5, S_MARTS) + 2 * i + 1] = q >> 8
        q += len(sl)
    new = {i: r16(rom, fo(5, S_MARTS) + 2 * i) for i in range(N)}
    rom[k + 1] = MB
    rom[k + 4] = new[i_tm] & 0xff; rom[k + 9] = new[i_tm] >> 8
    rom[k + 21] = new[i_mb] & 0xff; rom[k + 25] = new[i_mb] >> 8
    # グレンの ショップの 店員：pokemart 0, MART_SAFFRON → MART_CINNABAR
    import port, gsc
    P = port.Port.__new__(port.Port); P.CM = cmaps.CMaps(cmod); P.SM = gsc.Maps(bytes(rom[:0x100000]), gsc.PG + '/constants/map_constants.asm'); P.todo = {}
    gg, mm = P.x_map(*CINNABAR_MART); gt = fo(0x25, 0x40ED); hh = fo(0x25, r16(rom, gt + 2 * (gg - 1))) + 9 * (mm - 1)
    ao = fo(rom[hh], r16(rom, hh + 3)); sb = rom[ao + 6]; p = fo(sb, r16(rom, ao + 9)) + 2
    kk = rom[p]; p += 1 + 5 * kk; kk = rom[p]; p += 1 + 8 * kk; kk = rom[p]; p += 1 + 5 * kk; kk = rom[p]; p += 1
    hits = 0
    for j in range(kk):
        sp_ = r16(rom, p + 13 * j + 9)
        if sp_ < 0x4000: continue
        so = fo(sb, sp_); i2 = bytes(rom[so:so + 12]).find(bytes([0x93, 0x00, MART_SAFFRON, 0x00]))
        if i2 >= 0: rom[so + i2 + 2] = MART_CINNABAR; hits += 1
    assert hits == 1, hits
    log.append('ショップ：%d 店を $%02X へ、クリスタル版で 変えた 店 %s、グレン %d-%d は 表 %d' % (N, MB, changed, gg, mm, MART_CINNABAR))
    return rom
