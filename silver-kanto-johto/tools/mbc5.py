"""MBC5 版（MBC30 → MBC5）。ふつうの 版を 組んだ あとに、ここで 写しを 作りかえる。
   MBC5 には 時計（RTC）が ない ので、時計を ソフトで 動かす：
     ・時計の 値は WRAM の $D690〜$D695（秒・分・時・日 下・日 上・フレーム）。銀の wTradeFlags の あとの 空き（ds 33）の 中で、
       セーブデータに 入る（レポートを 書くと 時計も 残る。電源を 切って いる 間は 時計は 止まる）。
     ・VBlank の 最後（GameTimer を よぶ 所 $0168）で、$FB の TICK を よぶ（1/60 秒ごと）。
     ・GetClock（$0477）・SetClock（$0551）は MBC3 の 時計の かわりに この 値を 読み書き する。
     ・LatchClock（$045C）・時計を 止める／動かす（$05:$4000・$4019）は 何も しない。
       SaveRTC（$05:$406A）は 時計の バンク（$0C）を 選ばない ように（MBC5 では RAM の バンク 0 を 書きかえて しまう）。
   ヘッダー：$0147 = $1B（MBC5＋RAM＋電池）。ROM 4MB・RAM 32KB は そのまま。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gsc import fo

RTC = 0xD690          # 秒・分・時・日下・日上・フレーム・まだ 足して いない 秒（2 バイト）
TICK_BANK, TICK = 0xFB, 0x4100
H = {'S': 0x93, 'M': 0x92, 'H': 0x91, 'DL': 0x90, 'DH': 0x8F}


def expect(rom, o, hexs):
    b = bytes.fromhex(hexs.replace(' ', ''))
    assert rom[o:o + len(b)] == b, (hex(o), rom[o:o + len(b)].hex(' '), hexs)


def w(v): return bytes([v & 0xFF, v >> 8])


def convert(rom):
    rom = bytearray(rom)
    assert rom[0x147] == 0x10 and rom[0x148] == 0x07 and rom[0x149] == 0x03
    lo = RTC & 0xFF
    # ---- LatchClock
    expect(rom, 0x045C, '3e 00 ea 00 60 3e 01 ea 00 60 c9')
    rom[0x045C:0x045C + 11] = bytes([0xC9]) + bytes(10)
    # ---- GetClock（$0477〜 の 49 バイト）・SetClock（$0551〜 の 51 バイト）は $FB の 本体を farcall する だけに して、
    #      あいた 所に バンク 0 の 直しと、VBlank の 小さな 時計（バンクを 切りかえない。VBlank で バンクを 切りかえると、
    #      $2000 に じかに 書いて hROMBank を 変えない 処理の とちゅうで もどす バンクを まちがえる）を 置く。
    expect(rom, 0x0477, '3e 0a ea 00 00 cd 5c 04 21 00 40 11 00 a0 36 08 1a e6 3f e0 93')
    expect(rom, 0x04A4, 'cd ad 30 c9')
    expect(rom, 0x0551, '3e 0a ea 00 00 cd 5c 04 21 00 40 11 00 a0 36 0c 1a cb 77 12')
    expect(rom, 0x0580, 'cd ad 30 c9')
    GET, SET = TICK, TICK + 0x80        # $FB の 本体
    g = bytearray([0x3E, TICK_BANK, 0x21]) + w(GET) + bytes([0xCF, 0xC9])          # farcall GetClock の 本体
    bs_at = 0x0477 + len(g)
    bs = bytes([0xF5, 0xA7, 0x20, 0x01, 0x3C, 0xEA, 0x00, 0x20, 0xF1, 0xC9])      # バンク 0 → 1
    g += bs
    vb_at = 0x0477 + len(g)
    # VBlank：フレームを 数えて、60 で「まだ 足して いない 秒」（16 ビット $D696）を 1 ふやす
    vb = bytearray([0xF0, 0x70, 0xF5, 0x3E, 0x01, 0xE0, 0x70,
                    0x21]) + w(RTC + 5) + bytes([0x34, 0x7E, 0xD6, 60, 0x38, 0x07, 0x77,
                    0x2C, 0x34, 0x20, 0x02, 0x2C, 0x34,
                    0xF1, 0xE0, 0x70, 0xC3, 0xA7, 0x1E])
    g += vb
    assert len(g) <= 49, len(g)
    rom[0x0477:0x0477 + 49] = bytes(g) + bytes(49 - len(g))
    sc = bytes([0x3E, TICK_BANK, 0x21]) + w(SET) + bytes([0xCF, 0xC9])
    rom[0x0551:0x0551 + 51] = sc + bytes(51 - len(sc))
    expect(rom, 0x0168, 'cd a7 1e')
    rom[0x0169:0x016B] = w(vb_at)
    # ---- Bankswitch（rst $10）：MBC3 では バンク 0 を 選ぶと バンク 1 に なるが、MBC5 では バンク 0 に なる。
    #      ゲームは ときどき 0 を 書く ので、MBC3 と 同じく 1 に する（フラグも そのまま）
    expect(rom, 0x0010, 'e0 9f ea 00 20 c9 00 00')
    rom[0x0010:0x0018] = bytes([0xE0, 0x9F, 0xC3]) + w(bs_at) + bytes(3)
    import re
    n = 0
    for m in list(re.finditer(rb'\xe0\x9f\xea\x00\x20', bytes(rom[:0x4000]))):
        h = m.start() + 2
        rom[h:h + 3] = bytes([0xCD]) + w(bs_at); n += 1
    assert n == 15, n
    # ---- 時計を 止める／動かす・SaveRTC
    o = fo(5, 0x4000); expect(rom, o, '3e 0a ea 00 00 cd 5c 04 3e 0c ea 00 40 fa 00 a0 cb f7 ea 00 a0 cd ad 30 c9')
    rom[o] = 0xC9
    o = fo(5, 0x4019); expect(rom, o, '3e 0a ea 00 00 cd 5c 04 3e 0c ea 00 40 fa 00 a0 cb b7 ea 00 a0 cd ad 30 c9')
    rom[o] = 0xC9
    o = fo(5, 0x406A); expect(rom, o, '3e 0a ea 00 00 cd 5c 04 21 00 a0 3e 0c ea 00 40 cb be 3e 00 ea 00 40')
    rom[o + 12] = 0x00                    # ld a,$0C → ld a,0
    rom[o + 16:o + 18] = bytes([0, 0])    # res 7,[hl] → nop nop
    # ---- $FB の 本体
    # GET：まだ 足して いない 秒（$D696）を 取り出して 0 に し、1 秒ずつ 秒・分・時・日に 足してから hRTC へ 写す
    G2 = bytearray([0xF0, 0x70, 0xF5, 0x3E, 0x01, 0xE0, 0x70,
                    0x21]) + w(RTC + 6) + bytes([0x5E, 0x36, 0x00, 0x2C, 0x56, 0x36, 0x00])   # de ＝ 秒（取り出して 0）
    loop = len(G2)
    G2 += bytes([0x7A, 0xB3, 0x28, 0])                     # ld a,d / or e / jr z,.copy
    jz = len(G2) - 1
    G2 += bytes([0x1B, 0x21]) + w(RTC)                       # dec de / ld hl,秒
    adds = []
    G2 += bytes([0x34, 0x7E, 0xD6, 60, 0x38, 0, 0x77]); adds.append(len(G2) - 2)
    G2 += bytes([0x2C, 0x34, 0x7E, 0xD6, 60, 0x38, 0, 0x77]); adds.append(len(G2) - 2)
    G2 += bytes([0x2C, 0x34, 0x7E, 0xD6, 24, 0x38, 0, 0x77]); adds.append(len(G2) - 2)
    G2 += bytes([0x2C, 0x34, 0x20, 0]); adds.append(len(G2) - 1)
    G2 += bytes([0x2C, 0xCB, 0xC6])
    back = len(G2)
    G2 += bytes([0x18, (loop - (back + 2)) & 0xFF])       # jr .loop
    for j in adds: G2[j] = (back - (j + 1)) & 0xFF
    copy = len(G2); G2[jz] = (copy - (jz + 1)) & 0xFF
    G2 += bytes([0x21]) + w(RTC)
    for k in ('S', 'M', 'H', 'DL'): G2 += bytes([0x2A, 0xE0, H[k]])
    G2 += bytes([0x7E, 0xE0, H['DH'], 0xF1, 0xE0, 0x70, 0xC9])
    S2 = bytearray([0xF0, 0x70, 0xF5, 0x3E, 0x01, 0xE0, 0x70, 0x21]) + w(RTC)
    for k in ('S', 'M', 'H', 'DL'): S2 += bytes([0xF0, H[k], 0x22])
    S2 += bytes([0xF0, H['DH'], 0xE6, 0x01, 0x22, 0xAF, 0x22, 0x22, 0x77, 0xF1, 0xE0, 0x70, 0xC9])   # フレーム・秒も 0
    a = fo(TICK_BANK, GET); assert not any(rom[a - 16:a + 0x80 + len(S2) + 16])
    assert len(G2) <= 0x80
    rom[a:a + len(G2)] = G2
    a = fo(TICK_BANK, SET); rom[a:a + len(S2)] = S2
    # ---- ヘッダー
    rom[0x147] = 0x1B
    c = 0
    for i in range(0x134, 0x14D): c = (c - rom[i] - 1) & 0xff
    rom[0x14D] = c
    sm = (sum(rom) - rom[0x14E] - rom[0x14F]) & 0xffff
    rom[0x14E], rom[0x14F] = sm >> 8, sm & 0xff
    return rom
