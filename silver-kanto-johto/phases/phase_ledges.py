"""赤の マップの 段差（第69弾）：タイルセット 40（1ばんどうろ・トキワ・22ばんどうろ など）では、段差の タイルの 1つ 手前から
   その 向きに 歩くと とびこえ（2マス）、ほかの 向きからは かべ。ジョウトは そのまま。
   銀は クリスタルと 同じ アドレス（バンク$04：TryStep $416B の call CheckLandPerms $4176、.TryJump の 音の 所 $420D）。
     $04:$7FEB（空き 21 バイト）：call CheckLandPerms / ret c / farcall しらべる 処理（$E8:$4100）/
       c ＝ 0 歩く・1 かべ・2 とびこえ（pop hl して .TryJump の 音から：TryStep には もどらない）"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
from gsc import fo, r16

TB, CHK = 0xE8, 0x4100
TRAMP = 0x7FEB
RED_OVERWORLD_TS = 40
wTileset, wWalkingTileCollision, wFacingDirection = 0xD074, 0xCF5C, 0xCF59


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    o = fo(4, 0x4176); assert rom[o:o + 3] == bytes([0xCD, 0x9E, 0x43])
    o = fo(4, 0x420D); assert rom[o:o + 9] == bytes([0x11, 0x16, 0x00, 0xCD, 0x45, 0x3D, 0x3E, 0x03, 0xCD])
    lt = bytes(rom[fo(4, 0x421E):fo(4, 0x421E) + 8]); assert lt == bytes([1, 2, 4, 8, 9, 0x0A, 5, 6])
    w = lambda a: bytes([a & 0xff, a >> 8])
    tab = CHK + 40
    chk = (bytes([0x0E, 0x00, 0xFA]) + w(wTileset) + bytes([0xFE, RED_OVERWORLD_TS, 0xC0,     # ld c,0 / タイルセット 40 だけ
                                                           0xFA]) + w(wWalkingTileCollision) +
           bytes([0x5F, 0xE6, 0xF0, 0xFE, 0xA0, 0xC0,                                     # 段差（$A0〜）でなければ 歩く
                  0x7B, 0xE6, 0x07, 0x5F, 0x16, 0x00, 0x21]) + w(tab) +
           bytes([0x19, 0xFA]) + w(wFacingDirection) +
           bytes([0xA6, 0x0E, 0x01, 0xC8, 0x0E, 0x02, 0xC9]))                             # 向きが 合えば とびこえ
    assert len(chk) <= 40
    o = fo(TB, CHK); assert not any(rom[o:o + 48]); rom[o:o + len(chk)] = chk; rom[fo(TB, tab):fo(TB, tab) + 8] = lt
    tr = (bytes([0xCD, 0x9E, 0x43, 0xD8, 0x3E, TB, 0x21]) + w(CHK) +
          bytes([0xCF, 0x79, 0xA7, 0xC8, 0x3D, 0x37, 0xC8, 0xE1, 0xC3, 0x0D, 0x42]))
    assert len(tr) <= 21
    o = fo(4, TRAMP); assert not any(rom[o:o + 21]); rom[o:o + len(tr)] = tr
    o = fo(4, 0x4176); rom[o + 1:o + 3] = w(TRAMP)
    log.append('段差：赤の マップ（タイルセット 40）は 赤と 同じに')
    return rom
