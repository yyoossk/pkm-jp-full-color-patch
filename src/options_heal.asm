; 「せってい」に「かいふくの アニメーション」（みる／とばす）を足す（赤のキット「ポケモンセンターの回復」から）。
; 青のせっていの画面はバンク $13（13:42FA〜）で、赤の土台と同じ作り・同じ番地（項目 4つ・ラベルの行 1・5・9・13、
; えらぶ行 3・7・11・15、おわり 17）。これを項目 5つ（ラベル 1・4・7・10・13、えらぶ行 3・6・9・12・15、おわり 17）にする。
; ラベルにはだくてんの字がないので、前の項目のえらぶ行のすぐ下に置ける。
; 値は wOptions のビット4（0 = みる・1 = とばす）。ビット0〜2 は文字の速さ（and $0f）、5 はわすれさせるときのカーソル、
; 6・7 はしあいのルール・せんとうアニメーション。青で wOptions を読む所を全部見て、ビット4 を使う所がないことを確かめた。
; 元の 13:4330〜4529 は、もう使わない（そのまま残る）。呼ぶ処理の番地は vars（151匹そろう版は +1）。

INCLUDE "charmap.inc"

IF HAS_HEAL_OPT

DEF wOptions EQU $D2D4
DEF wTopMenuItemY EQU $CC24
DEF wTopMenuItemX EQU $CC25
DEF wCurrentMenuItem EQU $CC26
DEF wLastMenuItem EQU $CC2A
DEF wOptTextSpeedX EQU $CD3D
DEF wOptBattleAnimX EQU $CD3E
DEF wOptBattleStyleX EQU $CD3F
DEF wOptCancelX EQU $CD40
DEF wOptForgetX EQU $CD41
DEF wOptHealAnimX EQU $CD42 ; 新しい項目（せっていの画面のあいだだけ）
DEF ROW EQUS "$C3A0 + 20 *"

; ラベルの場所（行 4・7・10 につめる）
SECTION "せってい：ラベル2", ROMX[$430C + 1], BANK[$13]
	dw ROW 4 + 1
SECTION "せってい：ラベル3", ROMX[$4315 + 1], BANK[$13]
	dw ROW 7 + 1
SECTION "せってい：ラベル4", ROMX[$431E + 1], BANK[$13]
	dw ROW 10 + 1

SECTION "せってい：入力の入口", ROMX[$4330], BANK[$13]
	jp KitOptMain

FreeBank13
KitOptMain:
	ld hl, ROW 13 + 1
	ld de, KitOptHealText
	call PlaceString
	xor a
	ld [wCurrentMenuItem], a
	ld [wLastMenuItem], a
	inc a
	ld [$d2d7], a
	ld [wOptCancelX], a
	ld a, 3
	ld [wTopMenuItemY], a
	call KitOptLoad
	ld a, [wOptTextSpeedX]
	ld [wTopMenuItemX], a
	ld a, 1
	ldh [$ffba], a
	call Delay3
.loop
	call PlaceMenuCursor
	call KitOptSave
.joy
	call JoypadLowSensitivity
	ldh a, [hJoy5]
	ld b, a
	and $fb
	jr z, .joy
	bit 1, b ; B
	jr nz, .exit
	bit 3, b ; START
	jr nz, .exit
	bit 0, b ; A
	jr z, .dir
	ld a, [wTopMenuItemY]
	cp $11
	jr nz, .loop
.exit
	ld a, $90
	jp PlaySound
.dir
	ld a, [wTopMenuItemY]
	bit 7, b
	jr nz, .down
	bit 6, b
	jr nz, .up
	cp $11
	jr z, .loop
	cp 3
	jr z, .speed
	ld hl, wOptBattleAnimX
	cp 6
	jr z, .toggle
	ld hl, wOptBattleStyleX
	cp 9
	jr z, .toggle
	ld hl, wOptForgetX
	cp 12
	jr z, .toggle
	ld hl, wOptHealAnimX
.toggle
	ld a, [hl]
	xor $0b
	ld [hl], a
	jr .setx
.speed
	ld a, [wOptTextSpeedX]
	bit 5, b
	jr nz, .left
	cp $0e
	jr z, .store
	add 4
	cp 5
	jr nz, .store
	inc a
	jr .store
.left
	cp 1
	jr z, .store
	sub 4
	cp 2
	jr nz, .store
	dec a
.store
	ld [wOptTextSpeedX], a
.setx
	ld [wTopMenuItemX], a
	call OptCursorX
	jp .loop
.down
	ld c, 1
	jr .move
.up
	ld c, KitOptRows.end - KitOptRows - 1
.move
	ld hl, KitOptRows
	ld b, 0
.find
	cp [hl]
	jr z, .found
	inc hl
	inc b
	jr .find
.found
	ld a, b
	add c
	cp KitOptRows.end - KitOptRows
	jr c, .ok
	sub KitOptRows.end - KitOptRows
.ok
	ld c, a
	ld b, 0
	ld hl, KitOptRows
	add hl, bc
	ld a, [hl]
	ld [wTopMenuItemY], a
	ld hl, KitOptXPtrs
	add hl, bc
	add hl, bc
	ld a, [hli]
	ld h, [hl]
	ld l, a
	ld a, [hl]
	ld [wTopMenuItemX], a
	call PlaceUnfilledArrowMenuCursor
	jp .loop

KitOptRows:
	db 3, 6, 9, 12, 15, $11
.end
KitOptXPtrs:
	dw wOptTextSpeedX, wOptBattleAnimX, wOptBattleStyleX, wOptForgetX, wOptHealAnimX, wOptCancelX

; 画面の カーソルの 場所 → wOptions（元の 13:4416 に 新しい ビットを 足した もの）
KitOptSave:
	ld a, [wOptTextSpeedX]
	ld d, 0
	cp 1
	jr z, .speed
	ld d, 1
	cp 6
	jr z, .speed
	ld d, 3
	cp $0a
	jr z, .speed
	ld d, 5
.speed
	ld a, [wOptBattleAnimX]
	dec a
	jr z, .anim
	set 7, d
.anim
	ld a, [wOptBattleStyleX]
	dec a
	jr z, .style
	set 6, d
.style
	ld a, [wOptForgetX]
	dec a
	jr z, .forget
	set 5, d
.forget
	ld a, [wOptHealAnimX]
	dec a
	jr z, .heal
	set 4, d
.heal
	ld a, d
	ld [wOptions], a
	ret

; wOptions → 画面の カーソルの 場所と ▷（元の 13:444A に 新しい 行を 足した もの）
KitOptLoad:
	ld a, [wOptions]
	and 7
	ld b, 1
	jr z, .t
	ld b, 6
	cp 1
	jr z, .t
	ld b, $0e
	cp 5
	jr z, .t
	ld b, $0a
.t
	ld a, b
	ld [wOptTextSpeedX], a
	ld hl, ROW 3
	call .mark
	ld c, 7
	call .bit
	ld [wOptBattleAnimX], a
	ld hl, ROW 6
	call .mark
	ld c, 6
	call .bit
	ld [wOptBattleStyleX], a
	ld hl, ROW 9
	call .mark
	ld c, 5
	call .bit
	ld [wOptForgetX], a
	ld hl, ROW 12
	call .mark
	ld c, 4
	call .bit
	ld [wOptHealAnimX], a
	ld hl, ROW 15
	call .mark
	ld hl, ROW 17
	ld a, 1
.mark
	ld e, a
	ld d, 0
	add hl, de
	ld [hl], $ec ; ▷
	ret
.bit
	ld a, [wOptions]
.rot
	rrca
	dec c
	jr nz, .rot
	rrca
	ld a, 1
	ret nc
	ld a, $0a
	ret

KitOptHealText:
	db "かいふくの アニメーション<NEXT>"
	db " みる", "       ", "とばす@" ; みる＝2〜3 けため・とばす＝11 けため（▷ は 1・10）

ENDC
