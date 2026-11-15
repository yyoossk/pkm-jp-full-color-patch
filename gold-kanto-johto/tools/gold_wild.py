"""野生の ポケモン：金の バンク 0A の 野生の コードと 表（$65EF〜$7FFF）を 新しい バンク WB の 同じ 住所に うつし
   （バンク 0A の のこり ＝ 通信・ふしぎなおくりもの は そのまま）、WB の 使わない 前半（$4000〜）に クリスタル版の
   カントーの 草むら・水の 表を 置く。ジョウトの 表と 大量発生の 表は 金の まま（同じ 住所）。
   よび出し：farcall 8か所・特別処理などの dba 7か所 を WB に。
"""
import re
def fo(b, a): return b * 0x4000 + a - 0x4000
def r16(r, o): return r[o] | r[o + 1] << 8
def w16(r, o, v): r[o] = v & 0xFF; r[o + 1] = v >> 8

CODE_LO, CODE_HI = 0x65EF, 0x6C1B
G_KG, G_KW = 0x78A6, 0x7E29
FARCALLS = [0x5E17, 0x507E6, 0x507F0, 0x91EC4, 0x97B26, 0x97B7F, 0x97BC5, 0x97BCB]   # 3e 0a 21 lo hi cf
FARCALLS2 = [0x3F742]                                                                  # 21 lo hi 3e 0a cf
DBAS = [0xC347, 0xC34A, 0xC34D, 0xC371, 0x15501, 0x1553D, 0x15540]
M_KG, M_KW = (0x0A, 0x7140), (0x0A, 0x7D05)

def apply(g, MOD, E, X, log):
    WB = E.next_bank; E.next_bank += 1
    g[fo(WB, 0x4000):fo(WB + 1, 0x4000)] = g[fo(0x0A, 0x4000):fo(0x0B, 0x4000)]
    g[fo(WB, 0x4000):fo(WB, CODE_LO)] = bytes(CODE_LO - 0x4000)
    for o in FARCALLS:
        assert g[o:o + 3] == b'\x3e\x0a\x21' and g[o + 5] == 0xCF and CODE_LO <= r16(g, o + 3) < CODE_HI; g[o + 1] = WB
    for o in FARCALLS2:
        assert g[o + 3:o + 6] == b'\x3e\x0a\xcf' and CODE_LO <= r16(g, o + 1) < CODE_HI; g[o + 4] = WB
    # dba（特別処理・マップの 準備の 命令）は バンクの 上の ビットを 別の 意味に 使う 所が あるので、バンク 0A の まま にして、
    # バンク 0A の 元の 入口（もう 使わない）に WB への farcall を 置く
    for o in DBAS:
        assert g[o] == 0x0A and CODE_LO <= r16(g, o + 1) < CODE_HI
        a = r16(g, o + 1)
        g[fo(0x0A, a):fo(0x0A, a) + 7] = bytes([0x3E, WB, 0x21, a & 0xFF, a >> 8, 0xCF, 0xC9])
    # クリスタル版の カントーの 表
    def table(bank, a, sz):
        o = fo(bank, a); out = bytearray()
        while MOD[o] != 0xFF:
            e = bytearray(MOD[o:o + sz]); gg, nn = X.mapid((e[0], e[1]), 'wild'); e[0], e[1] = gg, nn
            out += e; o += sz
        return out + b'\xff'
    kg = table(*M_KG, 47); kw = table(*M_KW, 9)
    a_kg = 0x4000; a_kw = a_kg + len(kg); end = a_kw + len(kw); assert end <= CODE_LO
    g[fo(WB, a_kg):fo(WB, a_kg) + len(kg)] = kg; g[fo(WB, a_kw):fo(WB, a_kw) + len(kw)] = kw
    n = 0
    seg = bytes(g[fo(WB, CODE_LO):fo(WB, CODE_HI)])
    for m in re.finditer(rb'[\x21\x11\x01](..)', seg, re.S):
        v = m.group(1)[0] | m.group(1)[1] << 8
        if v in (G_KG, G_KW):
            w16(g, fo(WB, CODE_LO) + m.start() + 1, a_kg if v == G_KG else a_kw); n += 1
    log.append('野生：バンク %02X（カントー 草むら %d・水 %d、表を 指す 所 %d）' % (WB, len(kg) // 47, len(kw) // 9, n))
    return WB
