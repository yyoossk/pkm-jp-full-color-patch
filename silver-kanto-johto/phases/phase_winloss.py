"""戦いの あとの セリフ（第54・74弾）：winlosstext の 文は その スクリプトの バンクから 読む
   （銀・クリスタルは いつも マップの スクリプトの バンク → カントーの スクリプト（MOD の バンク）の 文が こわれる）。
     ・Script_winlosstext（$25:$702F の ld hl,wWinTextPointer）→ スクリプトの バンク（wScriptBank $D152）を
       WINLOSS（クリスタル $DA5C → 銀 $D768）に おぼえる。
     ・PrintWinLossText（$38C0）：WINLOSS が あれば その バンク、なければ マップの バンク（GetMapScriptsBank）。1回で 消す。
     ・reloadmapafterbattle（命令の 表 $25:$6CA2）：はじめに WINLOSS を 消す（負けて 文が 出なかった とき、次の トレーナーの
       文を その バンクから 読んで リセットされる 不具合。第74弾）。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
from gsc import fo, r16

WINLOSS = 0xD768
wScriptBank, wWinTextPointer, wLossTextPointer, wBattleResult = 0xD152, 0xCF5C, 0xCF5E, 0xCFE3
GetMapScriptsBank = 0x2CEC
FREE = 0x7FE1


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    w = lambda a: bytes([a & 0xff, a >> 8])
    q = FREE; o = fo(0x25, q); assert not any(rom[o:o + 17])
    hw = bytes([0xFA]) + w(wScriptBank) + bytes([0xEA]) + w(WINLOSS) + bytes([0x21]) + w(wWinTextPointer) + bytes([0xC9])
    hr = bytes([0xAF, 0xEA]) + w(WINLOSS) + bytes([0xC3, 0xEF, 0x72])
    rom[o:o + len(hw)] = hw; rom[o + len(hw):o + len(hw) + len(hr)] = hr
    o = fo(0x25, 0x702F); assert rom[o:o + 3] == bytes([0x21]) + w(wWinTextPointer); rom[o:o + 3] = bytes([0xCD]) + w(q)
    o = fo(0x25, 0x6CA2); assert rom[o:o + 2] == w(0x72EF); rom[o:o + 2] = w(q + len(hw))
    o = 0x38C0                        # 追加機能パッチは call GetMapScriptsBank を 再戦の バンク $43 を みる $3F8A に して いる
    assert rom[o:o + 30] in (bytes.fromhex('fa0bd1fe011805215ccf180cfae3cf215ccfa72803215ecf2a666fcdec2c'),
                             bytes.fromhex('fa0bd1fe011805215ccf180cfae3cf215ccfa72803215ecf2a666fcd8a3f'))
    code = (bytes([0xFA]) + w(wBattleResult) + bytes([0x21]) + w(wWinTextPointer) + bytes([0xA7, 0x28, 0x03, 0x21]) +
            w(wLossTextPointer) + bytes([0x2A, 0x66, 0x6F, 0xFA]) + w(WINLOSS) + bytes([0xA7, 0x20, 0x03, 0xCD]) +
            w(GetMapScriptsBank) + bytes([0xF5, 0xAF, 0xEA]) + w(WINLOSS) + bytes([0xF1]))
    assert len(code) == 30, len(code)
    rom[o:o + 30] = code
    log.append('戦いの あとの セリフ：スクリプトの バンクから（$25:$%04X）' % q)
    return rom
