"""オープニング・タイトル（第53弾）：クリスタル版の 赤の オープニング（コピーライト・ゲームフリーク・ゲンガーと ニドリーノ・
   赤の タイトル）を 銀へ。
   クリスタル版は 赤の 音の 処理（バンク$9D・$9E）を 入れて、オープニングの 間は それで 曲・効果音を 鳴らす
   （wMusicPlaying ＝ $A5 の あいだ、音の 処理の 毎フレームの 所から 赤の 処理を よぶ）。
     ・$9D → $E7、$9E → $E8 へ 写す。赤の 処理の WRAM（クリスタル $C100〜$C1EC）は 銀の 音の WRAM（$C000〜）へ（−$100）。
     ・銀の 毎フレームの 所（$3A:$405C）→ ROM0 の 空き（$39・$43・$4B・$53・$5B）の 小さな 分かれ道 → $E8:$4080。
   オープニングの 処理（$36:$5B70〜$75AD）と 絵（$2C:$5B43〜）は 銀の $B6・$AC の 同じ アドレスへ 写して 読みかえる。
     ・クリスタルの wShadowOAM $C400・タイルマップ $C4A0〜（MOD は 色の 作業にも 使う）→ −$100
     ・wBGPals2（WRAM5 $D080）→ $C280、wLYOverrides（WRAM5 $D100）→ $C700、展開先 $C800 は そのまま
   銀の IntroSequence（$01:$63EF）を farcall $B6:$7FD0（$5B70 と 画面の 後しまつ）/ jp $6416 に。"""
import os, sys, pickle
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
import cmaps, port, asmport
from gsc import fo, r16

RB1, RB2 = 0xE7, 0xE8                   # 赤の 音の 処理
STUB = 0x4080                           # $E8 の 空き
TITLE = (0x36, 0x5B70, 0x75AE)
GFX = (0x2C, 0x5B43, 0x7134)        # タイトルの ポケモンの 絵 16（$36:$757B の 表）。$7134〜 は カントーの テキスト
S_INTRO, S_AFTER = 0x63EF, 0x6416
WRAP = 0x7FC0                           # $B6 の 空き：タイトルの あと クリスタルと 同じく 画面を 消して BG マップへ 送る
HOME = {0x0B2A: 0x0AD9, 0x3ADB: 0x3C70}
HRAM = {0xFF9E: 0xFFA0, 0xFFCF: 0xFFD1, 0xFFD0: 0xFFD2, 0xFFD1: 0xFFD3, 0xFFD2: 0xFFD4, 0xFFD4: 0xFFD6}


def red_engine(rom, cmod, log):
    rom[fo(RB1, 0x4000):fo(RB1, 0x8000)] = cmod[fo(0x9D, 0x4000):fo(0x9D, 0x8000)]
    n2 = len(bytes(cmod[fo(0x9E, 0x4000):fo(0x9E, 0x8000)]).rstrip(b'\0'))
    rom[fo(RB2, 0x4000):fo(RB2, 0x4000) + n2] = cmod[fo(0x9E, 0x4000):fo(0x9E, 0x4000) + n2]
    # WRAM：$C100〜$C1FF → $C000〜（処理を たどった 所の 3バイト命令だけ）
    n = 0
    for b, rb, entries in ((0x9D, RB1, (0x43DB, 0x4417)), (0x9E, RB2, (0x4000, 0x406B))):
        seen = set()
        for e in entries:
            for pos, op, L in asmport.walk(cmod, b, e):
                if (pos, op) in seen: continue
                seen.add((pos, op)); o = fo(rb, pos)
                if L == 3:
                    v = r16(rom, o + 1)
                    if 0xC100 <= v < 0xC200 and op in (0x01, 0x11, 0x21, 0xEA, 0xFA): rom[o + 2] = 0xC0; n += 1
                    elif op in (0xCD, 0xC3) and v < 0x4000:
                        t = HOME.get(v); assert t, '%02X:%04X home %04X' % (b, pos, v)
                        rom[o + 1] = t & 0xff; rom[o + 2] = t >> 8
                elif op == 0x26 and rom[o + 1] in (0xC1, 0xD1): raise ValueError('ld h %02X:%04X' % (b, pos))
    o = fo(RB2, 0x4048); assert rom[o:o + 2] == bytes([0x3E, 0x9D]); rom[o + 1] = RB1
    # 毎フレーム：赤の 処理（音量 $77 を 入れて $E7:$4417）
    st = bytes([0x3E, 0x77, 0xE0, 0x24, 0x3E, RB1, 0x21, 0x17, 0x44, 0xCF, 0xC9])
    o = fo(RB2, STUB); assert not any(rom[o:o + len(st)]); rom[o:o + len(st)] = st
    # ROM0 の 空きに 分かれ道（$3A:$405C の ld a,[wMusicPlaying] / and a / ret z の かわり）
    parts = {0x39: bytes([0xFA, 0x00, 0xC0, 0xFE, 0xA5, 0x18, 0x03]),      # ld a,[$C000] / cp $A5 / jr $43
             0x43: bytes([0x20, 0x06, 0x18, 0x0C]),                          # jr nz,$4B / jr $53
             0x4B: bytes([0xA7, 0xC8, 0xC3, 0x61, 0x40]),                    # and a / ret z / jp $4061（銀の 処理）
             0x53: bytes([0x3E, RB2, 0x18, 0x04]),                           # ld a,$E8 / jr $5B
             0x5B: bytes([0x21, STUB & 0xff, STUB >> 8, 0xCF, 0xC9])}         # ld hl,STUB / rst $08 / ret
    for a, bs in parts.items():
        assert not any(rom[a:a + len(bs)]), hex(a); rom[a:a + len(bs)] = bs
    o = fo(0x3A, 0x405C); assert rom[o:o + 5] == bytes([0xFA, 0x00, 0xC0, 0xA7, 0xC8])
    rom[o:o + 5] = bytes([0xC3, 0x39, 0x00, 0x00, 0x00])
    log.append('赤の 音の 処理：$9D・$9E → $%02X・$%02X（WRAM %d か所）' % (RB1, RB2, n))


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    cmod = open(cmaps.CMOD, 'rb').read(); corig = open(cmaps.CORIG, 'rb').read()
    g1 = open(os.path.join(H, 'roms', 'gin1.gbc'), 'rb').read()
    red_engine(rom, cmod, log)
    for b, a, e in (TITLE, GFX):
        s = fo(b, a); d = fo(port.cb(b), a)
        assert not any(rom[d:d + e - a]), '%02X:%04X' % (b, a)
        rom[d:d + e - a] = cmod[s:s + e - a]
    Hm = asmport.Home(corig, g1)
    wm = dict(pickle.load(open(os.path.join(ctx['B'], 'wram_map.pkl'), 'rb')))
    wm.update(asmport.WRAM_EXTRA); wm.update(HRAM)
    for a in range(0xC400, 0xC608): wm[a] = a - 0x100              # wShadowOAM・タイルマップ（色の 作業にも 使う）
    for a in range(0xD000, 0xD100): wm[a] = 0xC200 + (a - 0xD000)  # 色（WRAM5）
    for a in range(0xD100, 0xD190): wm[a] = 0xC700 + (a - 0xD100)  # wLYOverrides（WRAM5）
    wm[0xC800] = 0xC800                                            # 展開先（銀でも タイトルの 間は あき）
    wm[0xCF58] = 0xCE58                                            # wTitleScreenSelectedOption
    asmport.HOME_EXTRA.update(HOME)
    TR = asmport.Translator(cmod, corig, g1, wm, Hm, log); TR.wm = wm; TR.nosvbk = True
    TR.routine(rom, 0x36, 0x5B70, '36:5B70')
    assert not TR.unres, TR.unres
    B = port.cb(0x36)
    for at, old, new in ((0x5CCC, (0x26, 0xD1), (0x26, 0xC7)),          # ld h,HIGH(wLYOverrides)
                         (0x62D4, (0x3E, 0x2C), (0x3E, port.cb(0x2C))),  # 絵の バンク
                         (0x62D9, (0x3E, 0x36), (0x3E, B)),
                         (0x5C7F, (0x3E, 0x9E), (0x3E, RB2)),           # 赤の 音
                         (0x75A4, (0x3E, 0x9E), (0x3E, RB2))):
        o = fo(B, at); assert tuple(rom[o:o + 2]) == old, hex(at); rom[o:o + 2] = bytes(new)
    # call $5B70 / ClearSprites / ClearBGPalettes / res 2,[rLCDC] / ClearTilemap / WaitBGMap2（クリスタル $31CC）/ ret
    # hBGMapAddress ＝ $9800（銀は はじめ $9C00。銀の タイトルが $9800 に して いた）
    # hLCDCPointer・hSCX・hSCY ＝ 0、hWX ＝ 7、hWY ＝ $90（クリスタル $01:$63B9〜 と 同じ。窓を 画面の 外へ）
    wr = bytes([0xCD, 0x70, 0x5B, 0xCD, 0xBB, 0x30, 0xCD, 0xAB, 0x33, 0x21, 0x40, 0xFF, 0xCB, 0x96,
                0xCD, 0xA1, 0x0E, 0xAF, 0xE0, 0xD8, 0x3E, 0x98, 0xE0, 0xD9, 0xCD, 0xB8, 0x33,
                0xAF, 0xE0, 0xC8, 0xE0, 0xD1, 0xE0, 0xD2, 0x3E, 0x07, 0xE0, 0xD3, 0x3E, 0x90, 0xE0, 0xD4, 0xC9])
    o = fo(B, WRAP); assert not any(rom[o:o + len(wr)]); rom[o:o + len(wr)] = wr
    o = fo(1, S_INTRO)
    assert rom[o:o + 9] == bytes([0x21, 0x96, 0x51, 0x3E, 0x39, 0xCF, 0x38, 0x06, 0x21])
    rom[o:o + 9] = bytes([0x3E, B, 0x21, WRAP & 0xff, WRAP >> 8, 0xCF, 0xC3, S_AFTER & 0xff, S_AFTER >> 8])
    log.append('オープニング：クリスタル版の もの（$%02X:$5B70）を 使う' % B)
    return rom
