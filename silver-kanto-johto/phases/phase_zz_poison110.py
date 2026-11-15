"""第110弾 3・4：
 3 どくで 歩くと 背景が 紫 一色に なる → 赤と 同じ（背景パレット 8つの 色0 に 色2 を 写す）。
   銀の LoadPoisonBGPals（$32:$7C4D 付近、ld hl, wBGPals $C280 / ld c, $20 / 紫を 書く 輪）を 呼び出しに。
 4 ボックスが いっぱいに なった とき マサキから 電話が くる → PokeBallEffect .SendToPC で
   BATTLERESULT_BOX_FULL（wBattleResult の bit 7）を 立てない。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
from gsc import fo

PB, PAD = 0x32, 0x7E00
POISON_OLD = bytes.fromhex('21 80 c2 0e 20 3e bc 22 3e 7e 22 0d 20 f7')
POISON_NEW = bytes.fromhex('21 80 c2 0e 08'                 # ld hl, wBGPals / ld c, 8
                           '23 23 23 23 2a 46'              # hl+4：a, b ＝ 色2
                           '11 fb ff 19 22 70'              # hl-5 → 色0 ＝ a, b
                           '11 07 00 19 0d 20 ed c9')       # 次の パレット
BOX_PAT = bytes.fromhex('fa 10 ad fe 1e 20 05 21 e3 cf cb fe')


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    bank = bytes(rom[fo(PB, 0x4000):fo(PB, 0x8000)])
    i = bank.find(POISON_OLD); assert i >= 0 and bank.find(POISON_OLD, i + 1) < 0
    assert not any(rom[fo(PB, PAD):fo(PB, PAD) + len(POISON_NEW)])
    rom[fo(PB, PAD):fo(PB, PAD) + len(POISON_NEW)] = POISON_NEW
    o = fo(PB, 0x4000) + i
    rom[o:o + len(POISON_OLD)] = bytes([0xCD, PAD & 0xFF, PAD >> 8]) + bytes(len(POISON_OLD) - 3)
    b3 = bytes(rom[fo(3, 0x4000):fo(3, 0x8000)])
    j = b3.find(BOX_PAT); assert j >= 0 and b3.find(BOX_PAT, j + 1) < 0
    o2 = fo(3, 0x4000) + j + 10
    rom[o2:o2 + 2] = b'\x00\x00'                              # set 7, [hl] → nop nop
    log.append('どくの 点滅を 赤と 同じに（%X:%04X）、ボックスが いっぱいの 電話なし（03:%04X）' % (PB, PAD, 0x4000 + j + 10))
    return rom
