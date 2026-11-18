"""殿堂入り・スタッフロール（第54弾）と つづきから・主人公の 後ろ姿（第71弾）。
   クリスタル版の $35:$6240〜$7491（カントーの 殿堂入りと スタッフロールは 赤どおり、ジョウトの 四天王の あとは
   クリスタル（銀）の もの）を 銀の $B5 の 同じ アドレスへ 写して asmport で 読みかえる。
     ・銀の HallOfFame（$21:$6604 の call AnimateHallOfFame / pop af / jp Credits）→ pop af / ld b,a / jp $00F6
       （ROM0 の 空き：farcall $B5:$6240）。ジョウトの 四天王の あと（EVENT_BEAT_ELITE_FOUR）は 銀の
       AnimateHallOfFame・Credits へ。
   つづきから（$35:$6262）：セーブを 読んだ あと、ライバルの 名前が まだ なければ「シゲル」を 入れる（前の セーブ）。
     銀の Continue（$01:$5DCF の farcall TryLoadSaveFile）→ farcall $B5:$6262。
   殿堂入りの あと つづきから はじめる 場所：クリスタル版と 同じく カントーの 殿堂入りの あとは マサラ、
     ジョウトの 殿堂入りの あとは ワカバ（$01:$5E38 → $B5 の 小さな 処理）。
   主人公の 後ろ姿（戦い・殿堂入り）：銀の $0F:$7A2B（2か所）→ クリスタル版の レッドの 絵 $71:$7AD1。"""
import os, sys, pickle
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
import cmaps, port, asmport
from gsc import fo, r16
sys.path.insert(0, os.path.join(H, 'phases'))
import phase_opening as PO

REGION = (0x35, 0x6240, 0x7492)
WRAM = {0xD26E: 0xD119, 0xD26F: 0xD11A, 0xDA6D: 0xD7B2}            # wBaseType1・2、EVENT_BEAT_ELITE_FOUR の バイト
for i in range(6): WRAM[0xD48E + i] = 0xD1B5 + i; WRAM[0xD4A6 + i] = 0xD1CD + i
for a in range(0xCB00, 0xCB0D): WRAM[a] = a                          # MOD の 作業用（銀でも この 間は あき）
HOME = {0x0E3B: 0x0D87, 0x3164: 0x31F9}
FAR = {(0x14, 0x510D): (0x14, 0x577F), (0x14, 0x5202): (0x14, 0x57ED), (0x42, 0x58BF): (0x21, 0x6A9B),
       (0x21, 0x6695): (0x21, 0x6674), (0x05, 0x4E87): (0x05, 0x4E21)}


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    cmod = open(cmaps.CMOD, 'rb').read(); corig = open(cmaps.CORIG, 'rb').read()
    g1 = open(os.path.join(H, 'roms', 'gin1.gbc'), 'rb').read()
    B = port.cb(0x35); A2 = port.cb(0x22)
    b, a, e = REGION
    s = fo(b, a); d = fo(B, a); assert not any(rom[d:d + e - a]); rom[d:d + e - a] = cmod[s:s + e - a]
    # 主人公の 後ろ姿を 読む 所（$22:$482E）：銀の 予め 決まった 処理（predef $3F）で レッドの 絵を
    pb = bytes([0x21, 0xD1, 0x7A, 0x06, 0x71, 0x11, 0x10, 0x93, 0x0E, 0x31, 0x3E, 0x3F, 0xCD, 0x05, 0x2E, 0xC9])
    o = fo(A2, 0x482E); assert not any(rom[o:o + len(pb)]); rom[o:o + len(pb)] = pb
    asmport.FAR_EXTRA.update(FAR); asmport.FAR_EXTRA[(0x22, 0x482E)] = (A2, 0x482E)
    asmport.HOME_EXTRA.update(PO.HOME); asmport.HOME_EXTRA.update(HOME)
    Hm = asmport.Home(corig, g1)
    wm = dict(pickle.load(open(os.path.join(ctx['B'], 'wram_map.pkl'), 'rb')))
    wm.update(asmport.WRAM_EXTRA); wm.update(PO.HRAM); wm.update(WRAM)
    for x in range(0xC400, 0xC608): wm[x] = x - 0x100
    for x in range(0xD000, 0xD100): wm[x] = 0xC200 + (x - 0xD000)
    wm[0xD0C8] = 0xCFFE                       # wCurPartySpecies：殿堂入りで 出す ポケモンの 絵（ここを 作業用に すると 絵と タイプが 1ぴきめの まま）
    for x in range(0xD100, 0xD190): wm[x] = 0xC700 + (x - 0xD100)
    wm[0xC800] = 0xC800
    TR = asmport.Translator(cmod, corig, g1, wm, Hm, log); TR.wm = wm; TR.nosvbk = True
    TR.routine(rom, 0x35, 0x6240, '35:6240'); TR.routine(rom, 0x35, 0x6262, '35:6262')
    assert not TR.unres, TR.unres
    for at, old, new in ((0x63E5, (0x01, 0x31, 0x22), (0x01, 0x31, A2)),   # レッドの 絵（$22:$48B2）
                         (0x6687, (0x01, 0x19, 0x35), (0x01, 0x19, B))):    # 展開する 絵の バンク
        o = fo(B, at); assert tuple(rom[o:o + 3]) == old, hex(at); rom[o:o + 3] = bytes(new)
    # 銀の HallOfFame
    o = fo(0x21, 0x6604); assert rom[o:o + 7] == bytes([0xCD, 0x74, 0x66, 0xF1, 0xC3, 0x9B, 0x6A])
    rom[o:o + 7] = bytes([0xF1, 0x47, 0xC3, 0xF6, 0x00, 0x00, 0x00])
    st = bytes([0x3E, B, 0x21, 0x40, 0x62, 0xCF, 0xC9])
    assert not any(rom[0xF6:0xF6 + len(st)]); rom[0xF6:0xF6 + len(st)] = st
    # 銀の Continue
    o = fo(1, 0x5DCF); assert rom[o:o + 6] == bytes([0x3E, 0x05, 0x21, 0x21, 0x4E, 0xCF])
    rom[o:o + 6] = bytes([0x3E, B, 0x21, 0x62, 0x62, 0xCF])
    # 殿堂入りの あとの 場所（クリスタル版 $01:$7E83：フラグ $DACE の ビット4 で ワカバ $0E か マサラ $02）
    fb = ctx['amap'][0xDACE]
    sp = bytes([0xFA, fb & 0xff, fb >> 8, 0xCB, 0x67, 0x3E, 0x0E, 0x20, 0x02, 0x3E, 0x02, 0xEA, 0x20, 0xCF, 0xC9])
    SP = 0x7FE0; o = fo(B, SP); assert not any(rom[o:o + len(sp)]); rom[o:o + len(sp)] = sp
    o = fo(1, 0x5E38); assert rom[o:o + 11] == bytes([0x3E, 0x0E, 0xEA, 0x20, 0xCF, 0xCD, 0x48, 0x5E, 0xC3, 0x7A, 0x5E])
    rom[o:o + 11] = bytes([0x3E, B, 0x21, SP & 0xff, SP >> 8, 0xCF, 0xCD, 0x48, 0x5E, 0x18, 0x37])
    # 主人公の 後ろ姿
    for bk, at in ((0x0F, 0x79B8), (0x21, 0x69C0)):
        o = fo(bk, at); assert rom[o:o + 3] == bytes([0x21, 0x2B, 0x7A]); rom[o + 1:o + 3] = bytes([0xD1, 0x7A])
        q = o + 3
        while rom[q:q + 2] != bytes([0x06, 0x0F]): q += 1
        assert q - o <= 16; rom[q + 1] = 0x71
    log.append('殿堂入り・スタッフロール・つづきから：クリスタル版の もの（$%02X:$6240）、主人公の 後ろ姿は レッド' % B)
    return rom
