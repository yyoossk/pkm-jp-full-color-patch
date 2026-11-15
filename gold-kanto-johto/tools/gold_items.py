"""クリスタル版で 足した 大事な どうぐ（ポケモンのふえ・シルフスコープ・リフトキー・カードキー・カセキ・ひみつのカギ・ひきかえけん・
   きんのいれば・とどけもの）の 名前・属性・説明を 金に。番号は クリスタル版と 同じ（金でも 空いている 番号）。
   ・名前の 表：金 の ホーム $3559（バンク・住所）が 指す 表を 新しい バンクへ（1 こ ずつ 長さが ちがうので 表ごと）
   ・属性：金 01:$6B93（7 バイトずつ）を その場で
   ・説明：金 0B:$402D の ポインター。文は バンク 0B の 使わなくなった トレーナーの 種類の 名前の 表（0B:$52D6〜、480 バイト）に
"""
def fo(b, a): return b * 0x4000 + a - 0x4000
ITEMS = [0x38, 0x87, 0x88, 0x89, 0x8D, 0x8E, 0x91, 0x93, 0x94, 0x95, 0x99]

def names(r, ptr):
    o = fo(r[ptr], r[ptr + 1] | r[ptr + 2] << 8); L = []
    for i in range(256):
        e = r.index(0x50, o); L.append(bytes(r[o:e + 1])); o = e + 1
    return L

def apply(g, M, E, log):
    gn = names(g, 0x3559); mn = names(M, 0x3380)
    for i in ITEMS: gn[i - 1] = mn[i - 1]
    blob = b''.join(gn)
    NB = E.next_bank; E.next_bank += 1
    g[fo(NB, 0x4000):fo(NB, 0x4000) + len(blob)] = blob
    g[0x3559] = NB; g[0x355A] = 0x00; g[0x355B] = 0x40
    for i in ITEMS:
        o = fo(1, 0x6B93) + 7 * (i - 1); assert g[o:o + 7] == bytes.fromhex('99990000000100')
        g[o:o + 7] = M[0x69FA + 7 * (i - 1):0x69FA + 7 * i]
    a = 0x52D6
    for i in ITEMS:
        p = M[0x2C02D + 2 * (i - 1)] | M[0x2C02D + 2 * (i - 1) + 1] << 8
        s = fo(0x0B, p); e = M.index(0x50, s); t = M[s:e + 1]
        assert a + len(t) <= 0x54B6
        g[fo(0x0B, a):fo(0x0B, a) + len(t)] = t
        o = fo(0x0B, 0x402D) + 2 * (i - 1); g[o] = a & 0xFF; g[o + 1] = a >> 8
        a += len(t)
    log.append('どうぐ %d こ（名前の 表 %02X:4000、説明 0B:52D6〜%04X）' % (len(ITEMS), NB, a))
