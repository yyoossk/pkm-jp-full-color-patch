"""第130弾（ポケモンセンターの 直し）の 金版。apply(g, log, FB)。
 1 ジョーイさんの スクリプト（std、金は バンク $36）の 最後「pause 10 / waitbutton / closetext / end」（36:40F8）の はじめ 4バイトを
   FB への farsjump に：同じ ことの あと turnobject PLAYER, DOWN（75 00 00）。「いいえ」も ここを 通る。ポケルスの 話の あとは 元どおり。
 2 せっていの「プリントの こさ」（39:4C40）を「かいふく アニメ」（みる／みない）に。せっていの 飛び先の 表（39:4C6F）の 5番目
   （0x4DBB）を、バンク $39 の 空き（7FF8〜、8バイト）の 入口 → バンク $42（せっていの 追加機能の バンク）の 処理に。
   左右で wOptions2（$D1B0。bit 1・2 は 電話の 回数）の bit 3 を 切りかえ、「みる」「みない」を 出す（C45F）。セーブに 入る。
   プリンタの こさ（D1AF）は 前の 値の まま。
   「みない」：ジョーイさんの「turnobject 左 / pause 10 / special HealParty / playmusic なし / setval / special HealMachineAnim /
   pause 30 / special RestartMapMusic / turnobject 下 / pause 10」（36:40BE〜40D7）を「special HealParty」だけに。
"""
import gold_tutor
def fo(b, a): return b * 0x4000 + a - 0x4000
def w16(v): return bytes([v & 0xFF, v >> 8])
def expect(g, o, h):
    b = bytes.fromhex(h.replace(' ', '')); assert bytes(g[o:o + len(b)]) == b, (hex(o), g[o:o + len(b)].hex(' '), h)
enc = gold_tutor.enc

STD, OPT_BANK, FAR = 0x36, 0x39, 0x42
OPTIONS2, HEAL_BIT, SCRIPT_VAR = 0xD1B0, 3, 0xD165
HJOY, PLACE_STRING, ROW = 0xFFA9, 0x0F46, 0xC45F


def tail(g, b):
    B = g[b * 0x4000:(b + 1) * 0x4000]; e = len(B)
    while e and B[e - 1] == 0: e -= 1
    return 0x4000 + e + 2


class Free:
    def __init__(s, g, bank, start=None): s.g, s.bank, s.a = g, bank, start or tail(g, bank)
    def put(s, data):
        o = fo(s.bank, s.a); assert s.a + len(data) <= 0x8000 and not any(s.g[o:o + len(data)]), (hex(s.bank), hex(s.a))
        s.g[o:o + len(data)] = data; r = s.a; s.a += len(data); return r


def nurse(g, log, f):
    expect(g, fo(STD, 0x40BE), '75 fe 02 8a 0a 0f 1b 00 7e 00 00 15 00 0f 3d 00 8a 1e 0f 3c 00 75 fe 00 8a 0a 9c')
    expect(g, fo(STD, 0x40F8), '8a 0a 53 49 90 4c c2 46')
    get_var = f.put(bytes([0xFA]) + w16(OPTIONS2) + bytes([0xE6, 1 << HEAL_BIT, 0xEA]) + w16(SCRIPT_VAR) + b'\xC9')
    anim = bytes(g[fo(STD, 0x40BE):fo(STD, 0x40D8)])
    base = f.a; n = 4 + 3 + len(anim) + 4; fast = base + n
    heal = bytes([0x0E, f.bank]) + w16(get_var) + bytes([0x09]) + w16(fast) + anim + bytes([0x04, STD]) + w16(0x40D8)
    assert len(heal) == n and f.put(heal) == base
    f.put(bytes([0x0F, 0x1B, 0x00, 0x04, STD]) + w16(0x40D8))
    g[fo(STD, 0x40BE):fo(STD, 0x40BE) + 4] = bytes([0x04, f.bank]) + w16(base)
    end = f.put(bytes([0x8A, 0x0A, 0x53, 0x49, 0x75, 0x00, 0x00, 0x90]))
    g[fo(STD, 0x40F8):fo(STD, 0x40F8) + 4] = bytes([0x04, f.bank]) + w16(end)
    log.append('第130弾 1 ジョーイさん：回復 %02X:%04X（みない なら HealParty だけ）・おわりに 下を 向く %02X:%04X' % (f.bank, base, f.bank, end))


def options(g, log):
    old, new = enc('プリントの　こさ'), enc('かいふく　アニメ'); assert len(old) == len(new)
    o = fo(OPT_BANK, 0x4C40); assert bytes(g[o:o + len(old)]) == old
    g[o:o + len(new)] = new
    tb = fo(OPT_BANK, 0x4C6F) + 2 * 4; assert bytes(g[tb:tb + 2]) == w16(0x4DBB)
    fr = Free(g, FAR)
    s_on = fr.put(enc('みる　　　') + b'\x50'); s_off = fr.put(enc('みない　　') + b'\x50')
    h = fr.put(bytes([0x21]) + w16(OPTIONS2) + bytes([0xF0, HJOY & 0xFF, 0xE6, 0x30, 0x28, 0x04, 0x7E, 0xEE, 1 << HEAL_BIT, 0x77,
               0x11]) + w16(s_on) + bytes([0xCB, 0x46 | (HEAL_BIT << 3), 0x28, 0x03, 0x11]) + w16(s_off) +
               bytes([0x21]) + w16(ROW) + bytes([0xCD]) + w16(PLACE_STRING) + bytes([0xA7, 0xC9]))
    stub = Free(g, OPT_BANK, 0x7FF8).put(bytes([0x3E, FAR, 0x21]) + w16(h) + bytes([0xCF, 0xC9]))
    g[tb:tb + 2] = w16(stub)
    log.append('第130弾 2 せってい「かいふく アニメ」：39:%04X → 42:%04X' % (stub, h))


def apply(g, log, FB):
    nurse(g, log, Free(g, FB, 0x4000))
    options(g, log)
