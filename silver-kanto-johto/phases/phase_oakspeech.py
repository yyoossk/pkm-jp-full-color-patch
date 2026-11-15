"""オーキドの 話（第52弾）：クリスタル版の 赤の オーキドの 話（赤の セリフ・ニドリーノ・赤の 曲）と
   ライバルの 名前を きめる 所を 銀へ。
   クリスタル版の 処理と データを 銀の 同じ アドレス（バンクは port.cb）へ 写して、asmport で 読みかえる：
     $36:$5867〜$5B6F  オーキドの 話（テキスト・ライバルの 名前の メニュー・text_asm の なきごえ $599A も）
     $01:$6208〜$6288  NamePlayer（主人公の 名前。きまった 名前は クリスタル版の もの）
     $22:$42AC〜$432F  ShowPlayerNamingChoices（えらぶ 名前の メニュー）
     $22:$487D〜$4BC1  DrawIntroPlayerPic と 主人公（レッド）の 絵（女の子の 絵は 使わない）
   銀の OakSpeech（$01:$5FB3）の 頭を farcall $B6:$5867 / ret に。"""
import os, sys, pickle
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
import cmaps, port, asmport, gsc
from gsc import fo, r16

REGIONS = [(0x36, 0x5867, 0x5B70), (0x01, 0x6208, 0x6289), (0x22, 0x42AC, 0x4330), (0x22, 0x487D, 0x4BC2)]
ROUTINES = [(0x36, 0x5867), (0x36, 0x599A), (0x01, 0x6208), (0x22, 0x42AC), (0x22, 0x487D)]
S_OAK = 0x5FB3                          # 銀の OakSpeech（farcall InitClock から）
HOME = {0x04A3: 0x0377, 0x04DD: 0x03B1, 0x0E49: 0x0D95, 0x1D00: 0x1B59, 0x3756: 0x391E}
WRAM = {0xD0E3: 0xD01A, 0xD0E4: 0xD01B}
for i in range(6): WRAM[0xD48E + i] = 0xD1B5 + i; WRAM[0xD4A6 + i] = 0xD1CD + i   # wPlayerName・wGreensName
for a in range(0xC4A0, 0xC608): WRAM[a] = a - 0x100                               # wTilemap


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    cmod = open(cmaps.CMOD, 'rb').read(); corig = open(cmaps.CORIG, 'rb').read()
    g1 = open(os.path.join(H, 'roms', 'gin1.gbc'), 'rb').read()
    for b, a, e in REGIONS:
        s = fo(b, a); d = fo(port.cb(b), a)
        assert not any(rom[d:d + e - a]), '%02X:%04X' % (b, a)
        rom[d:d + e - a] = cmod[s:s + e - a]
    Hm = asmport.Home(corig, g1)
    wm = dict(pickle.load(open(os.path.join(ctx['B'], 'wram_map.pkl'), 'rb')))
    wm.update(asmport.WRAM_EXTRA); wm.update(WRAM)
    asmport.HOME_EXTRA.update(HOME)
    for b, a in ((0x01, 0x6208), (0x22, 0x42AC), (0x22, 0x487D)):
        asmport.FAR_EXTRA[(b, a)] = (port.cb(b), a)
    TR = asmport.Translator(cmod, corig, g1, wm, Hm, log); TR.wm = wm
    for b, a in ROUTINES: TR.routine(rom, b, a, '%02X:%04X' % (b, a))
    # 女の子かどうか（wPlayerGender $D463）：銀は いつも 男の子 → ld a,[$D463] を xor a に
    n = 0
    for b, a, e in ((0x22, 0x42AC, 0x42CA), (0x22, 0x487D, 0x48B2)):             # 処理の 所だけ（絵の データは 見ない）
        for o in range(fo(port.cb(b), a), fo(port.cb(b), e) - 2):
            if rom[o:o + 3] == bytes([0xFA, 0x63, 0xD4]): rom[o:o + 3] = bytes([0xAF, 0x00, 0x00]); n += 1
    assert n == 3, n
    o = fo(port.cb(0x22), 0x489C)                                                 # 絵の バンク（ld b,$22 / ld c,$31 / call Get2bpp）
    assert rom[o:o + 4] == bytes([0x06, 0x22, 0x0E, 0x31]); rom[o + 1] = port.cb(0x22)
    un = {k: [x for x in v if x != 'wram D463'] for k, v in TR.unres.items()}; un = {k: v for k, v in un.items() if v}
    assert not un, un
    # 話の あとで 場所の 札の「前の 場所」（wMSPrev $DEFB）を レッドの いえ（マサラタウン）に：
    # クリスタル版は 新しい ゲームの はじめに 札を 出さない（_NewGame で wPrevLandmark を 入れる）
    SM = gsc.Maps(bytes(rom), gsc.PG + '/constants/map_constants.asm')
    lm = SM.header(SM.id['REDS_HOUSE_2F'])['landmark']
    W = 0x7FF0; wb = port.cb(0x36)                                               # $B6 の 終わり（空き）
    # 第100弾：ずかんの ならびは さいしょ 番号順（wLastDexMode $D671 = DEXMODE_OLD）
    code = bytes([0xCD, 0x67, 0x58, 0x3E, lm, 0xEA, 0xFB, 0xDE, 0x3E, 0x01, 0xEA, 0x71, 0xD6, 0xC9])
    assert not any(rom[fo(wb, W):fo(wb, W) + len(code)])
    rom[fo(wb, W):fo(wb, W) + len(code)] = code
    o = fo(1, S_OAK)
    assert rom[o:o + 6] == bytes([0x3E, 0x24, 0x21, 0x77, 0x46, 0xCF])
    rom[o:o + 7] = bytes([0x3E, wb, 0x21, W & 0xff, W >> 8, 0xCF, 0xC9])
    log.append('オーキドの 話：クリスタル版の もの（$%02X:$5867）を 使う' % port.cb(0x36))
    return rom
