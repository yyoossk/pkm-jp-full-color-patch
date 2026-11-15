"""小さな 処理の 直し（クリスタル版の 第67・78弾 など）。
   第67弾：$80 より 上の バンクの スクリプトから サブスクリプトを よんで 正しく もどる。銀でも クリスタルの バンクから 写した
     スクリプトは みな $80〜 に ある。CallCallback（$25:$7389 の or $80 → or $00）、ExitScriptSubroutine（$25:$7A27 の
     and $7F → and $FF）。
   第78弾：カントーでは 野生の ポケモンが にげださない（赤と 同じ）。TryEnemyFlee（$0F:$44FA）の はじめの 2つの しらべを
     $E8:$4140 の 処理に（カントー なら nz ＝ にげない）。カントーかは クリスタルの IsInJohto と 同じ しかた
     （ランドマーク：$5E こうそくせん は ジョウト、0 なら もどる マップ、$2E マサラ 以上 は カントー）。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
from gsc import fo

FB, FLEE = 0xE8, 0x4140
GetWorldMapLocation = 0x2D44
wMapGroup, wBackupMapGroup = 0xD9C6, 0xD9BC
wBattleMode, wPlayerSubStatus5 = 0xD108, 0xCB3E
LM_KANTO, LM_FAST_SHIP = 0x2E, 0x5E


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    w = lambda v: bytes([v & 0xFF, v >> 8])
    o = fo(0x25, 0x7389); assert rom[o:o + 8] == bytes.fromhex('fa52d1f680ea52d1'); rom[o + 4] = 0x00
    o = fo(0x25, 0x7A27); assert rom[o:o + 7] == bytes.fromhex('2a47e67fea52d1'); rom[o + 3] = 0xFF
    # 第78弾
    ism = (b'\xfa' + w(wMapGroup) + b'\x47\xfa' + w(wMapGroup + 1) + b'\x4f\xcd' + w(GetWorldMapLocation) +
           bytes([0xFE, LM_FAST_SHIP, 0x28, 0x12, 0xA7, 0x20, 0x0B]) +
           b'\xfa' + w(wBackupMapGroup) + b'\x47\xfa' + w(wBackupMapGroup + 1) + b'\x4f\xcd' + w(GetWorldMapLocation) +
           bytes([0xFE, LM_KANTO, 0x30, 0x02, 0xAF, 0xC9, 0x3E, 0x01, 0xA7, 0xC9]))
    # cp $5E / jr z,.johto / and a / jr nz,.chk（0 の ときだけ もどる マップで）
    far = (b'\xfa' + w(wBattleMode) + b'\x3d\xc0' + b'\xfa' + w(wPlayerSubStatus5) + b'\xcb\x7f\xc0') + ism
    o = fo(FB, FLEE); assert not any(rom[o:o + len(far)]); rom[o:o + len(far)] = far
    site = fo(0x0F, 0x44FA)
    assert rom[site:site + 13] == bytes.fromhex('fa08d13d204dfa3ecbcb7f2046')
    stay = 0x44FA + 6 + 0x4D
    rom[site:site + 13] = bytes([0x3E, FB, 0x21]) + w(FLEE) + bytes([0xCF, 0x20, stay - (0x44FA + 8)]) + bytes(5)
    log.append('スクリプトの バンク $80〜、カントーの 野生は にげない')
    return rom
