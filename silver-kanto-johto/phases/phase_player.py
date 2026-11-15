"""主人公の 見た目（第71弾の のこり）：
   ・名前を きめる 画面の 主人公の アイコン（$24:$5F6D の ld de,ChrisSpriteGFX / ld b,BANK）→ 人の絵の 表の 主人公
     （phase_kanto で クリスタル版の レッドに した もの）。
   ・トレーナーカードの 絵（銀 $09:$5490、5×7 タイル）→ クリスタル版の ChrisCardPic（$22:$436E、レッド）。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
import cmaps
from gsc import fo


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    cmod = open(cmaps.CMOD, 'rb').read()
    e = rom[0x147B0:0x147B6]                       # 人の絵 1（主人公）
    o = fo(0x24, 0x5F6D); assert rom[o:o + 5] == bytes([0x11, 0x00, 0x40, 0x06, 0x30])
    rom[o + 1] = e[0]; rom[o + 2] = e[1]; rom[o + 4] = e[3]
    o = fo(9, 0x50AB); assert rom[o:o + 9] == bytes.fromhex('2190541100900190023e09')[:9]
    s = fo(0x22, 0x436E); d = fo(9, 0x5490)
    for r in range(7):                              # クリスタルは 列ごと（5 列 × 7）、銀は 行ごと
        for c in range(5):
            t = s + 16 * (c * 7 + r); rom[d + 16 * (r * 5 + c):d + 16 * (r * 5 + c) + 16] = cmod[t:t + 16]
    log.append('名前の 画面の アイコン（%02X:%04X）・トレーナーカードの 絵を レッドに' % (e[3], e[0] | e[1] << 8))
    return rom
