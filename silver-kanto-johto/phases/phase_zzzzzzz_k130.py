"""ポケモンセンターの 直し（第130弾。phase_zzzzzz_k128 の あと。クリスタル版 カントー＆ジョウトの キットから。銀の アドレスで）
 1 ポケモンセンターで 回復したら（「いいえ」でも）主人公が 下を 向く（A の 連打で また 話しかけない ように）。
   ジョーイさんの スクリプト（std の PokecenterNurseScript、バンク $36）の 最後
   「pause 10 / waitbutton / closetext / end」（$36:$40F8）の はじめ 4バイトを $49 への farsjump に。
   そこで 同じ ことを したあと closetext の あとに turnobject PLAYER, DOWN（75 00 00）。ポケルスの 話の あとは 元のまま。
 2 「せってい」の「プリントの こさ」の 行を「かいふく アニメ」（みる／みない）に。
   wOptions2（$D1B0。bit 0 は メニューせつめい、bit 1〜2 は 電話の 回数）の bit 3（セーブに 入る。0 ＝ みる）。
   せっていの 表（$39:$4AF5）の 5番目（$4C41 の プリントの こさ）の 所を 新しい 処理で 書きかえる（$4CA4 からは 元のまま）。
   プリンタの こさ（wGBPrinterBrightness）は 前の 値の まま。
   「みない」の ときは、回復の「turnobject 左 〜 pause 10」（$36:$40BE〜$40D7）を「special HealParty」だけに
   （$36:$40BE を $49 への farsjump に。callasm で bit 3 を wScriptVar に 入れて iftrue で 分ける。どちらも $36:$40D8 へ）。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
from gsc import fo
from jptext import enc

FB = 0x49
STD = 0x36
OPT = 0x39
OPTIONS2, HEAL_BIT = 0xD1B0, 3
SCRIPT_VAR = 0xD165
HJOY = 0xA9
PLACE_STRING = 0x0F46
VALUE_POS = 0xC45F            # 「プリントの こさ」の 値の 場所（clockopt で 1行 上げた あと）


def w16(v): return bytes([v & 0xFF, v >> 8])


def expect(rom, o, hexs):
    b = bytes.fromhex(hexs.replace(' ', ''))
    assert rom[o:o + len(b)] == b, (hex(o), rom[o:o + len(b)].hex(' '), hexs)


class Free:
    def __init__(s, rom, bank):
        s.rom, s.bank = rom, bank
        b = rom[fo(bank, 0x4000):fo(bank, 0x8000)]; i = 0x3FFF
        while i >= 0 and b[i] == 0: i -= 1
        s.a = 0x4000 + i + 3
    def put(s, data):
        o = fo(s.bank, s.a); assert s.a + len(data) <= 0x8000 and not any(s.rom[o:o + len(data)])
        s.rom[o:o + len(data)] = data; a = s.a; s.a += len(data); return a


def nurse(rom, log):
    expect(rom, fo(STD, 0x40B9), '4c 5f 46 8a 14 75 fe 02 8a 0a 0f 1b 00 7e 00 00 15 00 0f 3d 00 8a 1e 0f 3c 00 75 fe 00 8a 0a 9c')
    expect(rom, fo(STD, 0x40ED), '4c 9a 46 75 fe 01 8a 0a 75 fe 00 8a 0a 53 49 90')
    f = Free(rom, FB)
    get_var = f.put(bytes([0xFA]) + w16(OPTIONS2) + bytes([0xE6, 1 << HEAL_BIT, 0xEA]) + w16(SCRIPT_VAR) + b'\xC9')
    anim = bytes(rom[fo(STD, 0x40BE):fo(STD, 0x40D8)])
    assert len(anim) == 26
    base = f.a
    body_len = 4 + 3 + len(anim) + 4
    fast = base + body_len
    heal = (bytes([0x0E, FB]) + w16(get_var) + bytes([0x09]) + w16(fast) + anim + bytes([0x04, STD]) + w16(0x40D8))
    assert len(heal) == body_len and f.put(heal) == base
    f.put(bytes([0x0F, 0x1B, 0x00, 0x04, STD]) + w16(0x40D8))           # .fast: special HealParty
    rom[fo(STD, 0x40BE):fo(STD, 0x40BE) + 4] = bytes([0x04, FB]) + w16(base)
    end = f.put(bytes([0x8A, 0x0A, 0x53, 0x49, 0x75, 0x00, 0x00, 0x90]))   # pause 10 / waitbutton / closetext / 下を 向く / end
    rom[fo(STD, 0x40F8):fo(STD, 0x40F8) + 4] = bytes([0x04, FB]) + w16(end)
    log.append('第130弾 1：ジョーイさん 回復 $%02X:$%04X（みない なら HealParty だけ）、さいごに 下を 向く $%02X:$%04X'
               % (FB, base, FB, end))


def options(rom, log):
    old, new = enc('プリントの　こさ'), enc('かいふく　アニメ')
    assert len(old) == len(new)
    o = fo(OPT, 0x4AC6); assert rom[o:o + len(old)] == old
    rom[o:o + len(old)] = new
    tb = fo(OPT, 0x4AF5) + 2 * 4
    assert rom[tb:tb + 2] == w16(0x4C41)
    h = 0x4C41
    expect(rom, fo(OPT, h), 'cd a4 4c f0 a9 cb 6f 20 0f cb 67 28 17')
    s_on = enc('みる　　　　') + b'\x50'
    s_off = enc('みない　　　') + b'\x50'
    n_code = 3 + 2 + 2 + 2 + 1 + 2 + 1 + 3 + 2 + 2 + 3 + 3 + 3 + 2
    a_on = h + n_code; a_off = a_on + len(s_on)
    code = (bytes([0x21]) + w16(OPTIONS2) +                        # ld hl, wOptions2
            bytes([0xF0, HJOY, 0xE6, 0x30, 0x28, 0x04,              # ldh a,[hJoyPressed] / and 左右 / jr z,.show
                   0x7E, 0xEE, 1 << HEAL_BIT, 0x77]) +              # ld a,[hl] / xor 8 / ld [hl],a
            bytes([0x11]) + w16(a_on) +                             # .show ld de, みる
            bytes([0xCB, 0x46 | (HEAL_BIT << 3), 0x28, 0x03]) +     # bit 3,[hl] / jr z,+3
            bytes([0x11]) + w16(a_off) +                            # ld de, みない
            bytes([0x21]) + w16(VALUE_POS) + bytes([0xCD]) + w16(PLACE_STRING) + bytes([0xA7, 0xC9]))
    assert len(code) == n_code
    blob = code + s_on + s_off
    assert h + len(blob) <= 0x4CA4                                  # $4CA4 からは 元の まま
    rom[fo(OPT, h):fo(OPT, h) + len(blob)] = blob
    log.append('第130弾 2：せっていの「かいふく アニメ」（$39:$4C41。wOptions2 bit 3）')


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    nurse(rom, log)
    options(rom, log)
    return rom
