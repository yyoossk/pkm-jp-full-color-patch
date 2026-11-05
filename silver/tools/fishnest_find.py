"""src/fishnest.asm の「ROM ごとにちがう所」を ROM から調べる（金・銀・クリスタル、日本版・海外版）。
   python3 tools/fishnest_find.py ROM.gbc
   Pokedex_GetArea.GetAndPlaceNest と FindNest の命令の並びで探して、その中のアドレスを読む。
   色のアドレス（wOBPals1・wOBPals2・hCGB・hCGBPalUpdate）と KANTO_LANDMARK は出せないので、
   ひとつ前の値（金銀）か、src/fishnest.asm の説明（クリスタル）を使う。"""
import sys
d = open(sys.argv[1], 'rb').read()

def find(pat):
    hits = []
    i = d.find(bytes(pat[:1]))
    while i != -1:
        if all(v is None or d[i + k] == v for k, v in enumerate(pat)): hits.append(i)
        i = d.find(bytes(pat[:1]), i + 1)
    return hits

def ptr(o): return o // 0x4000, o % 0x4000 + (0x4000 if o >= 0x4000 else 0)
_ = None
# .GetAndPlaceNest:
#  ld [wTownMapCursorLandmark],a / ld e,a / farcall FindNest / decoord 0,0 / ld hl,wShadowOAMSprite00
#  .nestloop: ld a,[de] / and a / jr z,.done_nest / push de / ld e,a / push hl / farcall GetLandmarkCoords / pop hl
#  ld a,d / sub 4 / ld [hli],a / ld a,e / sub 4 / ld [hli],a / ld a,$7f / ld [hli],a / xor a / ld [hli],a
#  pop de / inc de / jr .nestloop
#  .done_nest: ld hl,wShadowOAM / decoord 0,0 / ld bc,$a0 / call CopyBytes
pat = [0xea, _, _, 0x5f, 0x3e, _, 0x21, _, _, 0xcf, 0x11, _, _, 0x21, _, _,
       0x1a, 0xa7, 0x28, _, 0xd5, 0x5f, 0xe5, 0x3e, _, 0x21, _, _, 0xcf, 0xe1,
       0x7a, 0xd6, 0x04, 0x22, 0x7b, 0xd6, 0x04, 0x22, 0x3e, 0x7f, 0x22, 0xaf, 0x22, 0xd1, 0x13, 0x18, _,
       0x21, _, _, 0x11, _, _, 0x01, 0xa0, 0x00, 0xcd]
h = find(pat)
if len(h) != 1: sys.exit('GetAndPlaceNest が %d か所見つかった（1か所のはず）' % len(h))
o = h[0]
w = lambda k: d[o + k] | d[o + k + 1] << 8
b, a = ptr(o)
print('DEF FISHNEST_HOOK              EQU $%04x' % (a + 4))
print('DEF FISHNEST_HOOK_BANK         EQU $%02x' % b)
print('DEF FISHNEST_DONE_NEST         EQU $%04x' % (a + 47))
print('DEF FISHNEST_FindNest          EQU $%04x' % w(7))
print('DEF FISHNEST_FindNest_BANK     EQU $%02x' % d[o + 5])
print('DEF FISHNEST_GetLandmarkCoords EQU $%04x' % w(26))
print('DEF FISHNEST_GetLandmarkCoords_BANK EQU $%02x' % d[o + 24])
print('DEF FISHNEST_wTilemap          EQU $%04x' % w(11))
print('DEF FISHNEST_wShadowOAM        EQU $%04x' % w(14))
# FindNest.ScanMapLoop: push af / ld a,[wNamedObjectIndex] / cp [hl] / jr z / inc hl / inc hl / pop af / dec a / jr nz
h = find([0xf5, 0xfa, _, _, 0xbe, 0x28, _, 0x23, 0x23, 0xf1, 0x3d, 0x20])
fn = (d[o + 5], w(7))
fo = fn[1] if fn[1] < 0x4000 else fn[0] * 0x4000 + fn[1] - 0x4000
h = [x for x in h if fo <= x < fo + 0x100]
if len(h) != 1: sys.exit('FindNest の wNamedObjectIndex が %d か所見つかった' % len(h))
print('DEF FISHNEST_wNamedObjectIndex EQU $%04x' % (d[h[0] + 2] | d[h[0] + 3] << 8))
