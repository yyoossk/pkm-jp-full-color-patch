"""オーキドに 荷物を わたすと 落ちる 直し（第125弾。クリスタル版 カントー＆ジョウトの キットから）。
   起きて いた こと：$5D 以上の 新しい 曲（シゲルの 曲・研究所・ハナダ など。phase_sound3_shigeru / phase_sound4_red）を
     鳴らす とき、$3A の 曲の 表を 読む 所（$7FB7 → $7FDE）が「farcall $F1:$4100」して いた。
     曲の 切りかえで 前の 曲を 小さく して から 次の 曲に する とき（FadeMusic、$3A:$439A / $43B3）や、
     曲の 中の 命令（$3A:$4A39）は、VBlank の 割り込みの 中（_UpdateSound）から _PlayMusic（$3A:$4B30）を よぶ。
     銀の farcall（rst $08 → $2DE3）は、行き先の バンクを wD148 に、もどる ときの bc を wCFDA / wCFDB に 一時的に 置く。
     メインの 処理が farcall の 途中に いる ときに VBlank が 来て、割り込みの 中で また farcall すると、それが 書きかわり、
     メインの 処理が まちがった バンクに 飛んで 落ちる（タイミングしだい）。
   直し：$3A:$7FDE を farcall を 使わない 形に する。
     $3A:$7FDE  ldh a,[hROMBank] / push af / ld a,$F1 / rst Bankswitch   → そのまま $F1:$7FE4 に つづく
     $F1:$7FE4  call $4100 / pop af / rst Bankswitch                      → そのまま $3A:$7FE9 に つづく
     $3A:$7FE9  ret
     （hl = 曲の 3 バイトの 場所 は そのまま。よぶ 側は すぐ a を 読みかえるので a・bc は 気に しない。）"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
from gsc import fo

AB, TB, STUB = 0x3A, 0xF1, 0x7FDE


def expect(rom, o, hexs):
    b = bytes.fromhex(hexs.replace(' ', ''))
    assert rom[o:o + len(b)] == b, (hex(o), rom[o:o + len(b)].hex(' '), hexs)


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    # 曲の 表を 読む 所（phase_sound4_red が 書いた もの）：$5D 以上 → $7FDE
    expect(rom, fo(AB, 0x4B39), 'cd b7 7f')
    expect(rom, fo(AB, 0x7FB7), '7b fe 5d 30 22')
    expect(rom, fo(AB, STUB), '3e f1 21 00 41 cf c9 00 00 00 00 00 00 00 00')
    a = fo(AB, STUB)
    rom[a:a + 15] = bytes([0xF0, 0x9F, 0xF5, 0x3E, TB, 0xD7,        # $7FDE-$7FE3（$3A）
                           0, 0, 0, 0, 0,                          # $7FE4-$7FE8（$F1 で 動く）
                           0xC9, 0, 0, 0])                         # $7FE9 ret（$3A）
    b = fo(TB, 0x7FE4)
    assert not any(rom[b:b + 5])
    rom[b:b + 5] = bytes([0xCD, 0x00, 0x41, 0xF1, 0xD7])            # call $4100 / pop af / rst Bankswitch
    log.append('第125弾：$3A:$7FDE の farcall $F1:$4100 を、farcall を 使わない 形に（VBlank の 中で よばれても こわさない）')
    return rom
