"""追加の 直し 第123弾（クリスタル版 カントー＆ジョウト Ver.1.2.1・1.2.2 の 直しを 銀へ。キット「追加の直し_第123弾_キット」）。
   1 出口マット（DoPlayerMovement .CheckWarp）：銀の bugfix.asm の 67 は 向きの 読みなおしを 残して いるので 起きない（直さない）。
   2・3 さいしょから：赤と 同じ 部屋の ゲーム機の 前（3,6）で 上を 向いて 始まり、パソコンに キズぐすり 1こ。
       SpawnPoints（$05:$5286）の 0番の y を 6 に。NewGame の「ld a, SPAWN_HOME / ld [wDefaultSpawnpoint], a /
       ld a, MAPSETUP_WARP / ldh [hMapEntryMethod], a」（$5C2A、9バイト）を farcall に（$FB：wPlayerSpriteSetupFlags ＝ $21、
       wNumPCItems ＝ 1, POTION, 1, $FF）。
   4 1行 19文字 以上の 文（おかあさん・ふなのり 3つ・コジロウ（2か所））：改行の 場所を 動かす（同じ バイト数）。
   5 オーキドが 来る 前の 研究所の シゲル：赤の「なんだー　<PLAYER>か！／オーキドの　じいさんなら　いねーよ」（$62）。
   6 マサラの 草むらで 追いかけて きた オーキドが 主人公の ほう（上）を 向いて 話す（$71:$4C45・$4C9D）。
   7 トキワジムの 扉：主人公が 上を 向いてから 読む（$6F）。
   8 研究所の 助手：女の子（1,9 上下に 歩く）と 助手 2人（2,10）（8,10）（イベントの 表を $62 の 空きへ 作りなおす）。
     文は 赤の 文が 手もとに ないので、赤の 意味（はかせは みんなに そんけい されて いる・はかせの じょしゅ）で 書いた。
   9 つかまえ方を 見せる おじいさんの 絵：この 版は MOD の おじいさんの 絵を 使って いない（銀の 絵）ので 直さない。
  10 段差の あとの 連れ歩き：src/follow.asm（.far で wPlayerStepDirection ＝ $FF なら 主人公の 場所）。
  11 カントーで「そらをとぶ」：FlyMap（$24:$5D5B）の HasVisitedSpawn を SPAWN_INDIGO → SPAWN_PALLET、カーソルの はじめを
     カントーの 最初（マサラタウン）に。
  12 つよさの 画面の ハート：src/hearts_silver.asm・src/hearts.asm で 9行め に。
  14 タイムカプセルでしか 手に 入らない 道具を 野生の ポケモンが 持つ（基本データ $14:$5AA9、もちもの 1 ＝ 23%・2 ＝ 2%）。"""
import os, sys, importlib.util
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
import asmpatch, jptext
from gsc import fo, r16

CODE_BANK = 0xFB
KIT = os.path.join(H, 'build', 'kit')
_spec = importlib.util.spec_from_file_location('tutor', os.path.join(H, 'phases', 'phase_zzzz_tutor.py'))
TU = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(TU)


def expect(rom, o, hexs):
    b = bytes.fromhex(hexs.replace(' ', ''))
    assert rom[o:o + len(b)] == b, (hex(o), rom[o:o + len(b)].hex(' '), hexs)


def tail_free(rom, bank):
    d = rom[fo(bank, 0x4000):fo(bank, 0x8000)]
    n = len(d) - len(d.rstrip(b'\x00'))
    return 0x8000 - n + 2, n - 2          # 空きの はじめ（2バイト あける）と 大きさ


def T(s): return '\tdb $00, ' + ', '.join('$%02X' % x for x in jptext.enc(s)) + ', $57'


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    assert not any(rom[fo(CODE_BANK, 0x4000):fo(CODE_BANK, 0x8000)])

    # ---- 2・3 さいしょから
    so = fo(5, 0x5286); assert tuple(rom[so:so + 4]) == (13, 4, 3, 3); rom[so + 3] = 6
    expect(rom, 0x5C2A, '3e 00 ea 20 cf 3e f1 e0 a1 c3 7a 5e')
    ng = bytes([0xAF, 0xEA, 0x20, 0xCF, 0x3E, 0x21, 0xEA, 0x74, 0xD1,
                0x21, 0x09, 0xD6, 0x3E, 1, 0x22, 0x3E, 0x12, 0x22, 0x3E, 1, 0x22, 0x3E, 0xFF, 0x77,
                0x3E, 0xF1, 0xE0, 0xA1, 0xC9])
    o = fo(CODE_BANK, 0x4000); rom[o:o + len(ng)] = ng
    rom[0x5C2A:0x5C33] = bytes([0x3E, CODE_BANK, 0x21, 0x00, 0x40, 0xCF, 0, 0, 0])
    log.append('2・3 さいしょから (3,6) 上向き・パソコンに キズぐすり（$%02X:$4000）' % CODE_BANK)

    # ---- 4 長すぎる 行
    def retext(pre, old, new, n=1):
        pb = jptext.enc(pre[:-1]) + b'\x72'; a, b = pb + jptext.enc(old), pb + jptext.enc(new)
        assert len(a) == len(b) and rom.count(a) == n, (pre, old, rom.count(a))
        st = 0
        for _ in range(n):
            o = rom.find(a, st); rom[o:o + len(a)] = b; st = o + 1
    retext('おかあさん『', 'となりの　オーキドはかせが<LINE>あなたを　よんでたわよ', 'となりの<LINE>オーキドはかせが　あなたを<CONT>よんでたわよ')
    retext('ふなのり『', 'おお　きみが　<PLAYER>か！<LINE>', 'おお<LINE>きみが　<PLAYER>か！<CONT>')
    retext('ふなのり『', 'いあいぎりで　きを　きるには<LINE>ブルーバッジが　ひつようだよ',
           'いあいぎりで<LINE>きを　きるには　ブルーバッジが<CONT>ひつようだよ')
    retext('ふなのり『', 'きみが　<PLAYER>くんだね？<LINE>', 'きみが<LINE><PLAYER>くんだね？<CONT>')
    retext('コジロウ『', 'ジョウトの　ヤドンの　シッポは<LINE>ロケットだんが　いただくぜ！',
           'ジョウトの<LINE>ヤドンの　シッポは　ロケットだんが<CONT>いただくぜ！', n=2)
    log.append('4 長すぎる 行 5つ（コジロウは 2か所）')

    # ---- 6 オーキドの 向き
    for ad in (0x4C45, 0x4C9D):
        o = fo(0x71, ad); expect(rom, o, '75 00 00 47 4c 9a 4d'); rom[o + 1] = 2; rom[o + 2] = 1

    # ---- 5・8 研究所（$62）と 7 トキワジムの 扉（$6F）
    a62, n62 = tail_free(rom, 0x62); a6f, n6f = tail_free(rom, 0x6F)
    o = fo(0x62, 0x4A0A); expect(rom, o, '4c ec 4b 53 49 90')
    o2 = fo(0x6F, 0x4DFF); expect(rom, o2, '47 4c 3e 51 53 49 68 00 0a 4e 90')
    # 研究所の イベントの 表
    h, ao = TU.header(rom, 13, 6); sb = rom[ao + 6]; ep = r16(rom, ao + 9); assert sb == 0x62
    ev = TU.read_events(rom, sb, ep)
    S = ['INCLUDE "includes.asm"', 'INCLUDE "src/jp_all_silver.inc"',
         'SECTION "k123 62", ROMX[$%04X], BANK[$62]' % a62,
         'K_Shigeru:', '\tcheckevent $0908', '\tiffalse .early', '\twritetext $4BEC', '\twaitbutton', '\tclosetext', '\tend',
         '.early', '\twritetext .t', '\twaitbutton', '\tclosetext', '\tend',
         '.t', '\tdb $00, $39, $50', '\tdb $00, $72, ' + ', '.join('$%02X' % x for x in jptext.enc(
             'なんだー　<PLAYER>か！<LINE>オーキドの　じいさんなら　いねーよ')) + ', $57',
         'K_Girl:', '\tjumptextfaceplayer K_GirlText', 'K_Sci:', '\tjumptextfaceplayer K_SciText',
         'K_GirlText:', T('オーキドはかせは<LINE>ポケモン　けんきゅうの<CONT>だいいちにんしゃ　なのよ！<PARA>'
                          'おおくの　トレーナーから<LINE>そんけい　されて　いるわ'),
         'K_SciText:', T('わたしは<LINE>オーキドはかせの　じょしゅ　です<PARA>'
                         'ここで　ポケモンの<LINE>けんきゅうを　しています'),
         'K_Events:', '\tds %d' % (len(TU.build_events(ev)) + 3 * 13),
         'SECTION "k123 6f", ROMX[$%04X], BANK[$6F]' % a6f,
         'K_ViridianDoor:', '\tturnobject PLAYER, UP', '\topentext', '\twritetext $513E', '\twaitbutton', '\tclosetext',
         '\tapplymovement PLAYER, $4E0A', '\tend',
         'SECTION "k123 tbl", ROMX[$4080], BANK[$%02X]' % CODE_BANK,
         '\tdw K_Shigeru, K_Girl, K_Sci, K_Events, K_ViridianDoor']
    asmpatch.overlay(rom, '\n'.join(S) + '\n', inc=[os.path.join(KIT, 'pokegold'), KIT], cwd=KIT)
    t = fo(CODE_BANK, 0x4080)
    shig, girl, sci, evs, vdoor = [r16(rom, t + 2 * i) for i in range(5)]
    assert shig >= a62 and evs + len(TU.build_events(ev)) + 39 <= 0x8000 - 2 and vdoor >= a6f
    rom[o:o + 3] = bytes([0x03, shig & 0xFF, shig >> 8])          # sjump
    rom[o2:o2 + 3] = bytes([0x03, vdoor & 0xFF, vdoor >> 8])
    def obj(spr, x, y, mv, rng, sc):
        return bytes([spr, y + 4, x + 4, mv, rng, 0xFF, 0xFF, 0x00, 0x00, sc & 0xFF, sc >> 8, 0xFF, 0xFF])
    ev['objects'] += [obj(0x28, 1, 9, 0x04, 0x10, girl), obj(0x3C, 2, 10, 0x06, 0, sci), obj(0x3C, 8, 10, 0x06, 0, sci)]
    d = TU.build_events(ev); q = fo(0x62, evs); rom[q:q + len(d)] = d
    rom[ao + 9] = evs & 0xFF; rom[ao + 10] = evs >> 8
    log.append('5 シゲル $62:%04X・8 研究所の 助手（イベント $62:%04X）・6 オーキドの 向き・7 トキワジムの 扉 $6F:%04X' % (shig, evs, vdoor))

    # ---- 11 そらをとぶ
    o = 0x91D5B; expect(rom, o, 'f5 0e 0d cd e4 5c a7 28 18 3e 0c ea 24 cf 3e 17 ea 25 cf ea 21 cf')
    rom[o + 2] = 0x02                                                  # SPAWN_PALLET
    rom[o + 9:o + 22] = bytes.fromhex('3e0cea24cfea21cf3e17ea25cf')    # カーソルの はじめ ＝ マサラタウン
    log.append('11 カントーの そらをとぶ（マサラを 知って いれば カントーの 地図、はじめは マサラタウン）')

    # ---- 14 野生の もちもの
    BASE = 0x51AA9; assert rom[BASE:BASE + 7] == bytes([1, 45, 49, 49, 45, 65, 65])
    LIGHT_BALL, TWISTEDSPOON, METAL_POWDER, LUCKY_PUNCH, POLKADOT_BOW, BRICK_PIECE, GOLD_LEAF, SILVER_LEAF, BRIGHTPOWDER = \
        0xA3, 0x60, 0x23, 0x1E, 0xAA, 0xB4, 0x4B, 0x3C, 0x03
    HELD = {25: (None, LIGHT_BALL, (0, 0xAD)), 63: (None, TWISTEDSPOON, (0, 0)), 64: (None, TWISTEDSPOON, (0, 0)),
            132: (None, METAL_POWDER, (0, 0)), 113: (LUCKY_PUNCH, None, (0, 0x7E)), 39: (None, POLKADOT_BOW, (0, 0)),
            66: (None, BRICK_PIECE, (0, 0)), 43: (None, GOLD_LEAF, (0, 0)), 69: (None, SILVER_LEAF, (0, 0)),
            144: (BRIGHTPOWDER, None, (0, 0)), 145: (BRIGHTPOWDER, None, (0, 0)), 146: (BRIGHTPOWDER, None, (0, 0)),
            150: (BRIGHTPOWDER, None, (0, 0x98))}
    for dex, (i1, i2, was) in HELD.items():
        o = BASE + 32 * (dex - 1); assert rom[o] == dex and (rom[o + 11], rom[o + 12]) == was, (dex, rom[o + 11:o + 13].hex())
        if i1 is not None: rom[o + 11] = i1
        if i2 is not None: rom[o + 12] = i2
    log.append('14 野生の もちもの %d しゅるい' % len(HELD))
    return rom
