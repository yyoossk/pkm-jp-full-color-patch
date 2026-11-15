"""第110弾 6：タマムシマンション・ゲームコーナーの 名人の 家（タイルセット 50）の 絵と タイルごとの パレット。
   クリスタル版の もとに した 写し（pk_mansion.pkl）が ポケモン屋敷で 写した もの だった ため、絵が くずれて いた。
   キットの 赤フルカラーの VRAM の 写し（タマムシマンション 1F〜屋上・名人の家）から akapalmap.py の やり方で 作った
   data/mansion110_gfx.bin（$9000 の タイル $00-$5F）・data/mansion110_palmap.bin（多数決。見えなかった タイルは もとの まま）
   を 入れる。色（背景パレット 0〜6）は すでに 赤フルカラーと 同じ。
   絵は 圧縮 なし（LZ の そのまま 書く 命令だけ）で $EF に。palmap は もとの 場所（$93）に 上書き。
第110弾 7：タマムシマンションの 裏の 階段（1F〜3F の (2,1)、2F・3F の (4,1)）の 当たり $70（乗って 下を 押すと 移る）
   → $73（乗れば すぐ 移る。サントアンヌごうの 階段と 同じ）。ブロック $49 $4D $4E $50 $51 の 左下。
   どの ブロックも この 1か所 だけで 使われ、その 位置は ワープ（たしかめた）。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gsc import fo, r16
from phase_vgymdoor import unlz, lz_literal

TS, GB, GA = 50, 0xEF, 0x4000
STAIR_BLOCKS = (0x49, 0x4D, 0x4E, 0x50, 0x51)


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    gfx = open(os.path.join(H, 'data', 'mansion110_gfx.bin'), 'rb').read()
    pm = open(os.path.join(H, 'data', 'mansion110_palmap.bin'), 'rb').read()
    assert len(gfx) == 0x600 and len(pm) == 0x70
    te = fo(0xE1, 0x4000); e = te + 15 * TS
    assert len(unlz(rom, fo(rom[e], r16(rom, e + 1)))) == 0x600
    assert [i for i in range(54) if r16(rom, te + 15 * i + 13) == r16(rom, e + 13)] == [TS]   # palmap は ほかと 共有 しない
    lz = lz_literal(gfx); o = fo(GB, GA)
    assert not any(rom[o:o + len(lz)])
    rom[o:o + len(lz)] = lz
    rom[e] = GB; rom[e + 1] = GA & 0xFF; rom[e + 2] = GA >> 8
    p = fo(0x93, r16(rom, e + 13))
    assert rom[p + 0x30:p + 0x40] == b'\xff' * 16
    rom[p:p + 0x70] = pm
    c = fo(rom[e + 6], r16(rom, e + 7))
    for b in STAIR_BLOCKS:
        assert rom[c + 4 * b + 2] == 0x70, (hex(b), rom[c + 4 * b:c + 4 * b + 4].hex())
        rom[c + 4 * b + 2] = 0x73
    assert sum(1 for i in range(54) if (rom[te + 15 * i + 6], r16(rom, te + 15 * i + 7)) == (rom[e + 6], r16(rom, e + 7))) == 1
    log.append('タマムシマンションの 裏の 階段：ブロック %s の 左下 $70→$73' % ' '.join('%02X' % b for b in STAIR_BLOCKS))
    log.append('タマムシマンションの タイルセット %d：赤フルカラーの 絵（%X:%04X）・タイルごとの パレット' % (TS, GB, GA))
    return rom
