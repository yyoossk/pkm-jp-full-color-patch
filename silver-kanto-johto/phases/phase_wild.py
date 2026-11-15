"""野生の ポケモン（第57・60弾 など）：クリスタル版の 草むら・水の 表を 銀へ。
   ジョウトの 草むら・水、カントーの 水は 銀の バンク$0A の 同じ 場所へ（大きさが 同じか 小さい）。
   カントーの 草むら（60 マップ、銀の 2倍）は 入りきらないので $E3 へ：
     $E3 ＝ バンク$0A の 写し。$E3:$4000 に カントーの 草むらの 表、$E3:$4B10〜 に 読む 処理。
     見つけた 1つ分（47バイト）は wSGBPals（$CC9D。ゲームボーイカラーでは 使わない）へ 写して hl に する。
   バンク$0A の 3か所を $7FE4〜 の 中つぎ（farcall）へ。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
import cmaps, port, gsc
from gsc import fo, r16

WB = 0xE3
BUF = 0xCC9D
GL, WL = 47, 9


def table(rom, bank, addr, L):
    o = fo(bank, addr); n = 0
    while rom[o + L * n] != 0xFF: n += 1
    return bytearray(rom[o:o + L * n + 1]), n


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    cmod = open(cmaps.CMOD, 'rb').read()
    P = port.Port.__new__(port.Port)
    P.CM = cmaps.CMaps(cmod); P.SM = gsc.Maps(bytes(rom[:0x100000]), gsc.PG + '/constants/map_constants.asm'); P.todo = {}

    def fix(t, n, L):
        for i in range(n):
            g, m = P.x_map(t[L * i], t[L * i + 1]); t[L * i] = g; t[L * i + 1] = m
        return t

    jg, njg = table(cmod, 0x0A, 0x660C, GL); jw, njw = table(cmod, 0x0A, 0x7E3F, WL)
    kg, nkg = table(cmod, 0x0A, 0x7140, GL); kw, nkw = table(cmod, 0x0A, 0x7D05, WL)
    for t, n, L in ((jg, njg, GL), (jw, njw, WL), (kg, nkg, GL), (kw, nkw, WL)): fix(t, n, L)
    sjg, n1 = table(rom, 0x0A, 0x6C1B, GL); sjw, n2 = table(rom, 0x0A, 0x774F, WL); skw, n3 = table(rom, 0x0A, 0x7E29, WL)
    assert njg == n1 and njw == n2 and nkw <= n3, (njg, n1, njw, n2, nkw, n3)
    rom[fo(0x0A, 0x6C1B):fo(0x0A, 0x6C1B) + len(jg)] = jg
    rom[fo(0x0A, 0x774F):fo(0x0A, 0x774F) + len(jw)] = jw
    rom[fo(0x0A, 0x7E29):fo(0x0A, 0x7E29) + len(kw)] = kw

    # $E3 ＝ $0A の 写し ＋ カントーの 草むら
    rom[fo(WB, 0x4000):fo(WB, 0x8000)] = rom[fo(0x0A, 0x4000):fo(0x0A, 0x8000)]
    KT = 0x4000; rom[fo(WB, KT):fo(WB, KT) + len(kg)] = kg
    assert KT + len(kg) <= 0x4B10
    COPYBYTES, LOOKUP, NEST, CURMAP = 0x30D6, 0x6872, 0x664C, 0x6869
    assert rom[COPYBYTES:COPYBYTES + 3] == bytes([0x04, 0x0C, 0x18])
    a = 0x4B10
    def put(code):
        nonlocal a
        o = fo(WB, a); rom[o:o + len(code)] = code; r = a; a += len(code); return r
    def w(v): return bytes([v & 0xff, v >> 8])
    # 見つけた 1つ分を WRAM へ：push de ; ld de,BUF ; ld bc,47 ; call CopyBytes ; pop de ; ld hl,BUF ; scf ; ret
    tobuf = put(bytes([0xD5, 0x11]) + w(BUF) + bytes([0x01, GL, 0x00, 0xCD]) + w(COPYBYTES) + bytes([0xD1, 0x21]) + w(BUF) + bytes([0x37, 0xC9]))
    # G1：出会い（de = 表）。カントーなら $E3 の 表。ld bc,47 ; call CopyCurrentMapDE ; call LookUp ; ret nc ; jp tobuf
    g1 = put(bytes([0x7A, 0xFE, 0x78, 0x20, 0x08, 0x7B, 0xFE, 0xA6, 0x20, 0x03, 0x11]) + w(KT) +
             bytes([0x62, 0x6B, 0x01, GL, 0x00, 0xCD]) + w(CURMAP) + bytes([0xCD]) + w(LOOKUP) + bytes([0xD0, 0xC3]) + w(tobuf))
    # G2：マップ de で さがす
    g2 = put(bytes([0x21]) + w(KT) + bytes([0x01, GL, 0x00, 0xCD]) + w(LOOKUP) + bytes([0xD0, 0xC3]) + w(tobuf))
    # G3：ずかんの ぶんぷ
    g3 = put(bytes([0x21]) + w(KT) + bytes([0xC3]) + w(NEST))

    # バンク$0A の 中つぎ（$7FE4〜）
    t = 0x7FE4
    def tput(code):
        nonlocal t
        o = fo(0x0A, t); assert not any(rom[o:o + len(code)]); rom[o:o + len(code)] = code; r = t; t += len(code); return r
    tr1 = tput(bytes([0x54, 0x5D, 0x3E, WB, 0x21]) + w(g1) + bytes([0xCF, 0xC9]))
    tr2 = tput(bytes([0x3E, WB, 0x21]) + w(g2) + bytes([0xCF, 0xC9]))
    tr3 = tput(bytes([0x3E, WB, 0x21]) + w(g3) + bytes([0xCF, 0xC9]))
    assert t <= 0x8000
    # 出会い：0x2A826 "cd 44 68 | 01 2f 00 18 38" → jp tr1
    o = 0x2A827; assert rom[o:o + 5] == bytes([0x01, 0x2F, 0x00, 0x18, 0x38]); rom[o:o + 5] = bytes([0xC3]) + w(tr1) + bytes([0, 0])
    for o in (0x2AABD, 0x2AB64):
        assert rom[o:o + 6] == bytes([0x21, 0xA6, 0x78, 0xCD, 0x72, 0x68]), hex(o); rom[o:o + 6] = bytes([0xCD]) + w(tr2) + bytes(3)
    o = 0x2A640; assert rom[o:o + 6] == bytes([0x21, 0xA6, 0x78, 0xCD, 0x4C, 0x66]); rom[o:o + 6] = bytes([0xCD]) + w(tr3) + bytes(3)
    log.append('野生：ジョウト草 %d・水 %d、カントー草 %d（$E3）・水 %d' % (njg, njw, nkg, nkw))
    if P.todo: log.append('TODO ' + str({k: sorted(v)[:8] for k, v in P.todo.items()}))
    return rom
