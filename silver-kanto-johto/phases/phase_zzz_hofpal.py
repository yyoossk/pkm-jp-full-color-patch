"""殿堂入り（カントー・赤どおりの 画面）の ポケモンの 色：MOD の 表（$B5:$67A3）は 151ぴき まで で、
   それより 後の ポケモン（ジョウトの ポケモン）は ぜんぶ 0番（黄色）に なって いた。
   152〜251 は 銀の ポケモンの 色（$02:$6CC3、ふつうの 色 2つ）に 白と 黒を つけた 表（$B5:$7500）を 使う。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
from gsc import fo

B = 0xB5
SILVER_PAL = (0x02, 0x6CC3)
TAB = 0x7500
CODE = 0x7840


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    o = fo(B, 0x62FB)
    assert rom[o:o + 19] == bytes.fromhex('fa00cbfe983801af6f2600292929 11a36719c9'.replace(' ', ''))
    t = fo(B, TAB); n = 252 - 0x98
    assert not any(rom[t:t + 8 * n]) and not any(rom[fo(B, CODE):fo(B, CODE) + 32])
    sp = fo(*SILVER_PAL)
    for i in range(n):
        s = 0x98 + i
        rom[t + 8 * i:t + 8 * i + 8] = b'\xff\x7f' + bytes(rom[sp + 8 * s:sp + 8 * s + 4]) + b'\x00\x00'
    lo, hi = CODE & 0xff, CODE >> 8
    rom[o:o + 6] = bytes([0xFA, 0x00, 0xCB, 0xC3, lo, hi]) ; rom[o + 6:o + 19] = bytes(13)
    c = bytes([0xFE, 0x98, 0x30, 0x0B,                  # cp $98 / jr nc,.hi
               0x6F, 0x26, 0x00, 0x29, 0x29, 0x29, 0x11, 0xA3, 0x67, 0x19, 0xC9,   # 赤の 表
               0xFE, 0xFC, 0x38, 0x03, 0xAF, 0x18, 0xEE,  # .hi: cp $FC / jr c,.j / xor a / jr 赤の 表
               0xD6, 0x98, 0x6F, 0x26, 0x00, 0x29, 0x29, 0x29, 0x11, TAB & 0xff, TAB >> 8, 0x19, 0xC9])
    rom[fo(B, CODE):fo(B, CODE) + len(c)] = c
    log.append('  殿堂入りの 色：152〜251 は 銀の 色（$%02X:$%04X）' % (B, TAB))
    return rom
