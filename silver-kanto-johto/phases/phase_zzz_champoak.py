"""カントーの チャンピオンに 勝った あと：オーキドが 出る 場所（7,4）は 文字の わくに かくれる ので、
   はかせが 見えない まま 話して いた（GS は わくに かかる 人を 出さない）。
   出した あと 右・上に 1歩ずつ 歩かせて（6,5）（連れ歩きの となり）に 来させる。
   $78:$5952 の appear 4・opentext を scall に して、$78:$4BC0（MOD でも 使われて いない 空き）に 書く。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
from gsc import fo

B = 0x78
SITE = 0x5952
NEW = 0x4BC0
MV = NEW + 8


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    o = fo(B, SITE)
    assert rom[o:o + 6] == bytes.fromhex('6e04474c9a5b')
    n = fo(B, NEW)
    assert not any(rom[n - 0x20:n + 0x20])
    rom[n:n + 8] = bytes([0x6E, 0x04, 0x68, 0x04, MV & 0xff, MV >> 8, 0x47, 0x90])   # appear 4 / applymovement 4 / opentext / end
    rom[fo(B, MV):fo(B, MV) + 4] = bytes([0x0C | 3, 0x0C | 1, 0x00 | 1, 0x47])    # step RIGHT / step UP / turn_head UP / step_end
    rom[o:o + 3] = bytes([0x00, NEW & 0xff, NEW >> 8])
    log.append('  チャンピオンの あとの オーキド：（6,5）まで 歩いて くる')
    return rom
