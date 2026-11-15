"""交換進化（第57・62弾。御三家・セレビィ・交換進化キットの 交換進化）：
   ・交換で 進化する 9ひき（ユンゲラー・ゴーリキー・ゴローン・ゴースト・ニョロゾ・イワーク・シードラ・ストライク・ポリゴン）は
     Lv37 で 進化（どうぐ いらない）。表の EVOLVE_TRADE（03, どうぐ, しゅるい）→ EVOLVE_LEVEL（01, 37, しゅるい）。
   ・ヤドン：おうじゃのしるし（交換）→ ヤドキング を 先に、Lv37 → ヤドラン を あとに。しるしを もたせて Lv37 いじょうで
     レベルが あがると ヤドキング。
   ・EvolveAfterBattle の .trade（$10:$641F）：「つうしん中、または（どうぐで しんか では なく）Lv37 いじょう」で すすむ。
     銀の バンク$10 は 空きが ない ので、しらべる 処理（と もとの かわらずのいしの しらべ $65CB）は $E8:$4300 へ。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
from gsc import fo, r16

PTRS = 0x695F                       # 銀の EvosAttacksPointers（$10）
TRADE9 = (61, 64, 67, 75, 93, 95, 117, 123, 137)
SLOWPOKE, SLOWBRO, SLOWKING, KINGS_ROCK = 79, 80, 199, 0x52
LV = 37
FB, FN = 0xE8, 0x4300
wLinkMode, wForceEvolution, wTempMonLevel = 0xD03C, 0xD0C4, 0xD024
wCurPartyMon, wPartyMon1Item, AddNTimes = 0xCFFF, 0xD9F1, 0x315F
EVERSTONE = 0x70


def evo_at(rom, sp):
    o = fo(0x10, r16(rom, fo(0x10, PTRS) + 2 * (sp - 1))); out = []
    while rom[o]:
        L = 4 if rom[o] == 5 else 3; out.append(o); o += L
    return out


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    for sp in TRADE9:
        n = 0
        for o in evo_at(rom, sp):
            if rom[o] == 3: rom[o + 1] = LV; rom[o] = 1; n += 1
        assert n == 1, sp
    a, b = evo_at(rom, SLOWPOKE)
    assert rom[a:a + 3] == bytes([1, LV, SLOWBRO]) and rom[b:b + 3] == bytes([3, KINGS_ROCK, SLOWKING])
    rom[a:a + 3] = bytes([3, KINGS_ROCK, SLOWKING]); rom[b:b + 3] = bytes([1, LV, SLOWBRO])
    w = lambda v: bytes([v & 0xff, v >> 8])
    fn = (b'\xfa' + w(wLinkMode) + b'\xa7\x20\x0d' +                          # つうしん中 なら .go
          b'\xfa' + w(wForceEvolution) + b'\xa7\x20\x17' +                    # どうぐで しんか → .no
          b'\xfa' + w(wTempMonLevel) + bytes([0xFE, LV, 0x38, 0x10]) +       # Lv37 より 下 → .no
          b'\xfa' + w(wCurPartyMon) + b'\x21' + w(wPartyMon1Item) + b'\x01\x30\x00\xcd' + w(AddNTimes) +
          bytes([0x7E, 0xFE, EVERSTONE, 0xC9, 0xAF, 0xC9]))                 # z ＝ しんかしない
    o = fo(FB, FN); assert not any(rom[o:o + len(fn)]); rom[o:o + len(fn)] = fn
    s = fo(0x10, 0x641F); assert rom[s:s + 13] == bytes.fromhex('fa3cd0a7ca6365cdcb65ca6365')
    rom[s:s + 13] = bytes([0xE5, 0x3E, FB, 0x21]) + w(FN) + bytes([0xCF, 0xE1, 0xCA, 0x63, 0x65, 0x00, 0x00])
    log.append('交換進化：9ひき Lv37、ヤドキングは おうじゃのしるし ＋ Lv37（$%02X:$%04X）' % (FB, FN))
    return rom
