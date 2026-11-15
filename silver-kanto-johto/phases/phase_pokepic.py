"""pokepic の ポケモンの 絵を カラーに（第94弾：オーキドの 研究所で ボールを えらぶ ときなど）。
   銀の _CGB_Pokepic（$02:$5938）の わくを うめる 所（ld a,PAL_BG_GRAY / call FillBoxCGB / call ApplyAttrmap / ret、$5966）
   → パレット 7 に その ポケモンの 色（白・色1・色2・黒）を wBGPals1・wBGPals2 に 入れて、わくを パレット 7 で うめる。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
from gsc import fo

FILL = 0x5966
GET_MON_PAL, LOAD_PAL, FILLBOX = 0x5BF1, 0x5A71, 0x5A87
W_CURPARTYSPECIES = 0xCFFE
BGPALS1_7, BGPALS2_7 = 0xC238, 0xC2B8
H_CGBPALUPDATE = 0xE7
FREE = 0x7FB0


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    o = fo(2, FILL); assert rom[o:o + 9] == bytes.fromhex('3e00cd875acdcb5ac9')
    assert rom[fo(2, GET_MON_PAL):fo(2, GET_MON_PAL) + 3] == bytes.fromhex('6f2600')
    w = lambda v: bytes([v & 0xFF, v >> 8])
    code = (b'\xe5\xc5' + b'\xfa' + w(W_CURPARTYSPECIES) + b'\xcd' + w(GET_MON_PAL)
            + b'\xe5\x11' + w(BGPALS1_7) + b'\xcd' + w(LOAD_PAL)
            + b'\xe1\x11' + w(BGPALS2_7) + b'\xcd' + w(LOAD_PAL)
            + b'\x3e\x01\xe0' + bytes([H_CGBPALUPDATE])
            + b'\xc1\xe1\x3e\x07\xc3' + w(FILLBOX))
    f = fo(2, FREE); assert not any(rom[f:f + len(code)]) and FREE + len(code) <= 0x8000
    rom[f:f + len(code)] = code
    rom[o:o + 5] = b'\xcd' + w(FREE) + b'\x00\x00'
    log.append('pokepic：ポケモンの 色（$02:$%04X）' % FREE)
    return rom
