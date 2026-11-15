"""サントアンヌごうが 去る ところ（第107弾の 銀版。赤フルカラーと 同じに）：
   ・港の タイルセット（39）の 水（タイル $14）に 赤と 同じ アニメ：20フレームごとに 1ドット、右へ 4回・左へ 4回
     （銀の ReadTileToAnimBuffer $44BD／ScrollTileRightLeft $42B0／WriteTileFromAnimBuffer $44B1 と WaitTileAnimation $42A5 ×16、
     DoneTileAnimation $42A2）。表は $3F:$7C00（あき）。
   ・けむりの 色（$D9:$6DF2。OBJ パレット 7 を 白に して いた）を 赤フルカラーの OBJ パレット3（うすい オレンジ・茶色）に。
   （さいごに 組む：$3F の あきを ほかの フェーズの あとで つかう）"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
from gsc import fo

DOCK_TS = 39
T14, TILE_BUF = 0x9140, 0xCE35
READ, SCROLL_RL, WRITE, WAIT, DONE = 0x44BD, 0x42B0, 0x44B1, 0x42A5, 0x42A2
ANIM_AT = 0x7C00
SMOKE = (0xD9, 0x6DF2)
SMOKE_PAL = [(27, 31, 27), (31, 24, 17), (15, 10, 3), (0, 0, 0)]


def w(v): return bytes([v & 0xFF, v >> 8])


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    tab = w(T14) + w(READ) + w(TILE_BUF) + w(SCROLL_RL) + w(T14) + w(WRITE) + (bytes(2) + w(WAIT)) * 16 + bytes(2) + w(DONE)
    o = fo(0x3F, ANIM_AT); assert not any(rom[o - 16:o + len(tab) + 16]); rom[o:o + len(tab)] = tab
    e = fo(0xE1, 0x4000) + 15 * DOCK_TS; old = rom[e + 9] | rom[e + 10] << 8
    rom[e + 9:e + 11] = w(ANIM_AT)
    # けむり
    o = fo(*SMOKE); old2 = bytes.fromhex('21f8c20e0436ff23367f230d20f7'); assert rom[o:o + len(old2)] == old2
    s = rom[fo(SMOKE[0], 0x4000):fo(SMOKE[0], 0x8000)]; a2 = 0x4000 + len(s.rstrip(b'\0')) + 2
    pal = b''.join(w(r | g << 5 | b << 10) for r, g, b in SMOKE_PAL)
    code = bytes([0x21, 0xF8, 0xC2, 0x11]) + w(a2 + 15) + bytes([0x0E, 8, 0x1A, 0x22, 0x13, 0x0D, 0x20, 0xFA, 0xC9]) + pal
    assert a2 + len(code) <= 0x8000
    rom[fo(SMOKE[0], a2):fo(SMOKE[0], a2) + len(code)] = code
    rom[o:o + len(old2)] = bytes([0xCD]) + w(a2) + bytes(len(old2) - 3)
    log.append('サントアンヌの 港：水の アニメ（$3F:$%04X、もと $%04X）・けむりの 色（$%02X:$%04X）' % (ANIM_AT, old, SMOKE[0], a2))
    return rom
