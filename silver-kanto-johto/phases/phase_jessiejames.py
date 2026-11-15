"""ムサシと コジロウ（トレーナーの 種類 72）の 戦いの 絵を 2つの 色に（第66弾。ピカチュウ・フルカラーと 同じ）：
   絵の 左3列（コジロウ）＝ 青紫の 髪（BG パレット 5）、右4列（ムサシ）＝ 赤紫の 髪（BG パレット 1）。
   銀の _CGB_FinishBattleScreenLayout の おわり（$02:$5429。追加機能パッチの farcall $3F:$6F40）→ $E8:$4200（それを よんで から）。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
import asmpatch
from gsc import fo

SRC = r'''
DEF wBattleMode          EQU $d108
DEF wTempEnemyMonSpecies EQU $d0df
DEF wOtherTrainerClass   EQU $d10a
DEF TRAINER_JJ           EQU 72
DEF wTilemap             EQU $c3a0
DEF wAttrmap             EQU $cccd
DEF wBGPals1             EQU $c200

SECTION "jj hook", ROMX[$5429], BANK[$02]
	ld a, BANK(JJColors)
	ld hl, JJColors
	rst $08

SECTION "jj colors", ROMX[$4200], BANK[$E8]
JJColors:
	ld a, $3f
	ld hl, $6f40
	rst $08
	ld a, [wBattleMode]
	cp 2
	ret nz
	ld a, [wTempEnemyMonSpecies]
	and a
	ret nz
	ld a, [wOtherTrainerClass]
	cp TRAINER_JJ
	ret nz
	ld hl, wAttrmap + 12
	ld b, 4
	ld a, [wTilemap + 13]
	cp 7
	jr z, .fill
	ld hl, wAttrmap + 14
	dec b
.fill
	ld c, 7
.row
	push hl
	push bc
	ld a, 5
	ld [hli], a
	ld [hli], a
	ld [hli], a
	ld a, 1
.musashi
	ld [hli], a
	dec b
	jr nz, .musashi
	pop bc
	pop hl
	ld de, 20
	add hl, de
	dec c
	jr nz, .row
	ld hl, JJPals
	ld de, wBGPals1 + 5 * 8
	call .copy8
	ld de, wBGPals1 + 1 * 8
.copy8
	ld c, 8
.copy
	ld a, [hli]
	ld [de], a
	inc de
	dec c
	jr nz, .copy
	ret

JJPals:
	dw $7fff, $46ff, $6d8d, $0c63
	dw $7fff, $46ff, $3cdb, $0c63
'''


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    o = fo(2, 0x5429); assert rom[o:o + 6] == bytes([0x3E, 0x3F, 0x21, 0x40, 0x6F, 0xCF])
    assert not any(rom[fo(0xE8, 0x4200):fo(0xE8, 0x4280)])
    asmpatch.overlay(rom, SRC)
    log.append('ムサシと コジロウの 絵を 2つの 色に（$E8:$4200）')
    return rom
