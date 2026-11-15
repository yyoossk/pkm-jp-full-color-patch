"""セレビィ（第61・63弾。キット「御三家・セレビィキット」の src/legends.asm を 銀の 値で、伝説の 鳥は なし）：
   殿堂入り（ジョウトの。EVENT_BEAT_ELITE_FOUR）の あと、ウバメのもりの ほこらを しらべると セレビィ Lv70（クリスタル版と 同じ）。
   1回だけ（まけた ときは また 会える）。しるしは クリスタル版の $D836 ビット0（銀では ctx['amap'][$D836]）。
   つかまえずに おわった（たおした・にげた）ときは、つぎの 殿堂入り（ワタルの スクリプト $2C:$7475）で もう一度 会える。
   本体 $E8:$4400。ほこらの bg_event の スクリプトの 場所 $28:$60D3 → $28:$7FFB の farsjump。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
import asmpatch
from gsc import fo

KIT = os.environ.get('KIT_STARTERS', '/home/claude/in/kit/金銀移植キット/ソース/kitgs/御三家・セレビィキット')
BANK, ADDR = 0xE8, 0x4400
CELEBI, CELEBI_LV = 251, 70
W_DEX_CAUGHT = 0xDB78      # 銀の wPokedexCaught（見た は $DB98）


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    flags = ctx['amap'][0xD836]
    assert not any(rom[fo(BANK, ADDR):fo(BANK, ADDR) + 0x100])
    assert rom[fo(0x28, 0x60D3):fo(0x28, 0x60D5)] == bytes([0xD7, 0x5D]) and rom[fo(0x28, 0x5DD7):fo(0x28, 0x5DDA)] == bytes([0x52, 0x8D, 0x60])
    assert not any(rom[fo(0x28, 0x7FFB):fo(0x28, 0x8000)])
    src = '''
INCLUDE "src/safari/crystal_includes.asm"
DEF LG_NO_INCLUDES EQU 1
DEF LG_NO_BIRDS EQU 1
DEF LG_BANK            EQU $%02x
DEF LG_ADDR            EQU $%04x
DEF LG_wEventFlags     EQU $d7aa
DEF LG_EVENT_BEAT_E4   EQU $0044
DEF wLegendFlags       EQU $%04x
DEF LG_wScriptVar      EQU $d165
DEF LG_ILEX_BANK       EQU $28
DEF LG_ILEX_SHRINE_PTR EQU $60d3
DEF LG_ILEX_FREE       EQU $7ffb
DEF LG_ILEX_SHRINE_TEXT EQU $608d
DEF LG_SPRITE_BANK     EQU $05        ; 鳥なし なので 使わない（Legend_PutObject）
DEF LG_RefreshSprites  EQU $0000
''' % (BANK, ADDR, flags)
    s = open(os.path.join(KIT, 'src', 'legends.asm'), encoding='utf-8').read().replace('INCBIN "base.gbc"', 'INCBIN "{ROM}"')
    asmpatch.overlay(rom, src + s, inc=[os.path.join(KIT, 'pokecrystal')], cwd=KIT)
    k = bytes([0x5C, CELEBI, 30]); i = rom.find(k, fo(BANK, ADDR), fo(BANK, ADDR) + 0x100)
    assert i > 0 and rom.find(k, i + 1, fo(BANK, ADDR) + 0x100) < 0; rom[i + 2] = CELEBI_LV
    # 第63弾：ワタルの setevent EVENT_BEAT_ELITE_FOUR / setevent $077C → farscall（2つ と checkscene ×2）
    site = fo(0x2C, 0x7475); old = bytes(rom[site:site + 6]); assert old == bytes([0x33, 0x44, 0x00, 0x33, 0x7C, 0x07])
    t = fo(BANK, ADDR + 0x100); assert not any(rom[t:t + 0x20])
    i = CELEBI - 1; a = ADDR + 0x100
    code = old + bytes([0x0E, BANK, (a + 11) & 0xFF, (a + 11) >> 8, 0x90])          # callasm / end
    code += bytes([0xFA, (W_DEX_CAUGHT + i // 8) & 0xFF, (W_DEX_CAUGHT + i // 8) >> 8, 0xCB, 0x47 | ((i % 8) << 3), 0xC0,
                   0x21, flags & 0xFF, flags >> 8, 0xCB, 0x86, 0xC9])
    rom[t:t + len(code)] = code
    rom[site:site + 6] = bytes([0x01, BANK, a & 0xFF, a >> 8, 0x13, 0x13])
    log.append('セレビィ（Lv%d。しるし $%04X ビット0）$%02X:$%04X・殿堂入りで もどす $2C:$7475' % (CELEBI_LV, flags, BANK, ADDR))
    return rom
