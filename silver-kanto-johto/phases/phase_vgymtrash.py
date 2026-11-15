"""クチバジムの ゴミばこ（第110弾 1 の 銀版）：
   赤の 文を 写した とき 1バイト 前から 写して いて、2つめの ロック・まちがい の 文の 先頭が 0F（アイテム入手の 曲を 鳴らす
   文の 命令）、1つめの 文の 先頭が 余分な 00 だった → 文の はじまりを 1バイト 後ろに。
   音を 赤と 同じに：1つめ＝SFX_PUSH_BUTTON（赤の SFX_SWITCH）、まちがい＝SFX_WRONG（赤の SFX_DENIED）、
   2つめが 開く＝扉の 音（赤の SFX_GO_INSIDE）を 文の あと・ボタン待ちの 前に。
   スクリプトは $63:$72F9（callasm / ifequal 1・2・3 / jumptext）。まちがい・2つめ は $63 の あきに 作りなおす。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
from gsc import fo, r16

B, CAN = 0x63, 0x72F9
SFX_PUSH_BUTTON, SFX_ENTER_DOOR, SFX_WRONG = 0x11, 0x1F, 0x19


def w(v): return bytes([v & 0xFF, v >> 8])


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    o = fo(B, CAN); s = rom[o:o + 19]
    assert s[0:2] == b'\x0e\x63' and s[4:6] == b'\x06\x01' and s[8:10] == b'\x06\x02' and s[12:14] == b'\x06\x03' and s[16] == 0x52
    c1, c2, c3 = r16(rom, o + 6), r16(rom, o + 10), r16(rom, o + 14)
    p1 = fo(B, c1); assert rom[p1:p1 + 2] == b'\x47\x4c' and rom[p1 + 4:p1 + 7] == bytes([0x84, SFX_PUSH_BUTTON, 0])
    t1 = r16(rom, p1 + 2); assert rom[fo(B, t1):fo(B, t1) + 2] == b'\x00\x00'
    p2 = fo(B, c2); assert rom[p2] == 0x52; tf = r16(rom, p2 + 1); assert rom[fo(B, tf)] == 0x0F
    p3 = fo(B, c3); assert rom[p3:p3 + 2] == b'\x47\x4c'; t3 = r16(rom, p3 + 2); assert rom[fo(B, t3)] == 0x0F
    assert rom[p3 + 4:p3 + 15] == bytes([0x53, 0x49, 0x79, 4, 4, 1, 0x84, SFX_ENTER_DOOR, 0, 0x7B, 0x85])
    rom[p1 + 2:p1 + 4] = w(t1 + 1)
    s_ = rom[fo(B, 0x4000):fo(B, 0x8000)]; a = 0x4000 + len(s_.rstrip(b'\0')) + 2
    n2 = bytes([0x47, 0x4C]) + w(tf + 1) + bytes([0x84, SFX_WRONG, 0, 0x85, 0x53, 0x49, 0x90])
    n3 = bytes([0x47, 0x4C]) + w(t3 + 1) + bytes([0x84, SFX_ENTER_DOOR, 0, 0x85, 0x53, 0x49, 0x79, 4, 4, 1, 0x7B, 0x90])
    assert a + len(n2) + len(n3) <= 0x8000
    rom[fo(B, a):fo(B, a) + len(n2)] = n2; rom[fo(B, a + len(n2)):fo(B, a + len(n2)) + len(n3)] = n3
    rom[o + 10:o + 12] = w(a); rom[o + 14:o + 16] = w(a + len(n2))
    log.append('クチバジムの ゴミばこ：文の 先頭 +1・音を 赤と 同じに（$%02X:$%04X）' % (B, a))
    return rom
