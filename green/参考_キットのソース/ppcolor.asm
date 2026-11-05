; PPの 色（ピカチュウの キット）：バトルで わざを えらぶ とき、右下の わくの PP（今の 数）を、のこりが 少ない
; （今の PP × 4 ≦ 最大の PP）と 黄色、0 なら 赤で 出す。最大の 数と「／」は 黒の まま。
; 緑の バトルの BG パレットは 0〜7 ぜんぶ 使って いる ので、パレット 7（野生の バトルでは つかまえた しるしの
; ボール：白・赤・（使って いない）・黒。文字の 窓（namefix）は 白と 黒だけ）の 色1 を ボールと 同じ 赤、
; 色2 を 黄色に して 使う（トレーナーとの バトルでも 同じ 色を かく。色1・2 を 使う ものは ほかに ない）。
; ・数の 2ます（(14, 13)・(15, 13)）の 字を VRAM バンク1 の タイル $ec・$ed に 色1（赤）か 色2（黄）で 写し、
;   その ますの タイル（wTileMap と 両方の BG マップ）と 属性（バンク1・パレット 7。両方の BG マップと
;   W2_TilesetPaletteMap）を かきかえる。バンク1 の $ec・$ed は バトルでは 使われて いない。
; ・KitPrintMenuItemPP：PrintMenuItem（bank F）から farjp（KitPrintMenuItem の あと）。
;   KitPPColorOff：SelectMenuItem の HandleMenuInput の あと（bank F の 小さい 処理）：数を かきなおして 元の 属性に。
DEF KIT_PP_TILE EQU $ec
DEF KIT_PP_X    EQU 14
DEF KIT_PP_Y    EQU 13
DEF KIT_PP_PAL  EQU 7
DEF W2_PP_MAP   EQU W2_TilesetPaletteMap + KIT_PP_Y * SCREEN_WIDTH + KIT_PP_X

KitPrintMenuItemPP::
	call KitPrintMenuItem
	ld a, [wTileMap + KIT_PP_Y * SCREEN_WIDTH + 16]
	cp CHARVAL("／")
	ret nz ; ふうじられて いる：PP は 出て いない
	ld hl, wTileMap + KIT_PP_Y * SCREEN_WIDTH + KIT_PP_X + 3
	call KitPPReadNumber
	ld [wBuffer + 8], a ; 最大
	ld hl, wTileMap + KIT_PP_Y * SCREEN_WIDTH + KIT_PP_X
	call KitPPReadNumber
	ld c, 1 ; 赤
	and a
	jr z, .color
	add a
	add a
	ld hl, wBuffer + 8
	cp [hl]
	jr z, .low
	ret nc
.low
	ld c, 2 ; 黄
.color
	push bc
	call KitPPPalette
	pop bc
	ld hl, wTileMap + KIT_PP_Y * SCREEN_WIDTH + KIT_PP_X
	ld b, KIT_PP_TILE
	ld de, KIT_PP_Y * 32 + KIT_PP_X
.cell
	ld a, [hl]
	cp CHARVAL("　")
	jr z, .next
	push hl
	push bc
	push de
	call KitPPGlyph ; a = 字, b = バンク1 の タイル, c = 色
	pop de
	pop bc
	pop hl
	ld [hl], b
	push bc
	push hl
	ld a, b
	ld b, 8 | KIT_PP_PAL
	call KitPPWriteCell
	pop hl
	pop bc
.next
	inc hl
	inc de
	inc b
	ld a, b
	cp KIT_PP_TILE + 2
	jr nz, .cell
	ret

KitPPColorOff::
	ld a, [wTileMap + KIT_PP_Y * SCREEN_WIDTH + KIT_PP_X]
	cp KIT_PP_TILE
	jr z, .restore
	ld a, [wTileMap + KIT_PP_Y * SCREEN_WIDTH + KIT_PP_X + 1]
	cp KIT_PP_TILE + 1
	ret nz
.restore
	hlcoord KIT_PP_X, KIT_PP_Y
	ld a, CHARVAL("　")
	ld [hli], a
	ld [hld], a
	; カーソルの わざの PP（wCurrentMenuItem：ここでは 1 が 1つめ）
	ld a, [wCurrentMenuItem]
	dec a
	ld e, a
	ld d, 0
	push hl
	ld hl, wBattleMonPP
	add hl, de
	ld a, [hl]
	pop hl
	and $3f ; PP_MASK
	ld [wBuffer + 8], a
	ld de, wBuffer + 8
	lb bc, 1, 2
	call PrintNumber
	; 元の 属性（「／」の ます (16, 13) と 同じ）
	di
	ld a, 2
	ldh [rWBK], a
	ld a, [W2_PP_MAP + 2]
	ld b, a
	ld a, 1
	ldh [rWBK], a
	ei
	ld hl, wTileMap + KIT_PP_Y * SCREEN_WIDTH + KIT_PP_X
	ld de, KIT_PP_Y * 32 + KIT_PP_X
	ld a, [hli]
	push bc
	push hl
	call KitPPWriteCell
	pop hl
	pop bc
	inc de
	ld a, [hl]
	jp KitPPWriteCell

; a = タイル, b = 属性, de = BG マップの 中の ます：両方の BG マップ（VRAM バンク0：タイル、1：属性）と
; W2_TilesetPaletteMap（20×18）の その ます
KitPPWriteCell:
	ld c, a
	ld hl, $9800
	add hl, de
	call .one
	ld hl, $9c00
	add hl, de
	call .one
	; W2：de（32 はば）→ 20 はば（13行めの ます）
	ld a, e
	and 31
	add LOW(W2_TilesetPaletteMap + KIT_PP_Y * SCREEN_WIDTH)
	ld l, a
	ld a, HIGH(W2_TilesetPaletteMap + KIT_PP_Y * SCREEN_WIDTH)
	adc 0
	ld h, a
	di
	ld a, 2
	ldh [rWBK], a
	ld [hl], b
	ld a, 1
	ldh [rWBK], a
	ei
	ret
.one
	di
	call KitWaitHBlank
	ld [hl], c
	ld a, 1
	ldh [rVBK], a
	call KitWaitHBlank
	ld [hl], b
	xor a
	ldh [rVBK], a
	ei
	ret

; a = 字（$80-$ff）, b = バンク1 の タイル（$80-$ff）, c = 色（1 か 2）
KitPPGlyph:
	push bc
	sub $80
	ld l, a
	ld h, 0
	add hl, hl
	add hl, hl
	add hl, hl
	ld de, FontGraphics
	add hl, de
	ld de, wBuffer
	ld bc, 8
	ld a, FontGraphics_BANK
	call FarCopyData
	pop bc
	ld l, b
	ld h, 0
	add hl, hl
	add hl, hl
	add hl, hl
	add hl, hl
	ld de, $8000
	add hl, de
	ld de, wBuffer
	ld b, 8
.row
	ld a, [de]
	inc de
	push de
	ld d, a
	ld e, 0
	ld a, c
	cp 1
	jr z, .gotBytes
	ld e, d ; 色2：上の バイト
	ld d, 0
.gotBytes
	di
	ld a, 1
	ldh [rVBK], a
	call KitWaitHBlank
	ld a, d
	ld [hli], a
	ld a, e
	ld [hli], a
	xor a
	ldh [rVBK], a
	ei
	pop de
	dec b
	jr nz, .row
	ret

; hl = 2ます（"　５"・"１５"）→ a = 数
KitPPReadNumber:
	ld a, [hli]
	call .digit
	ld b, a
	add a
	add a
	add b
	add a
	ld b, a
	ld a, [hl]
	call .digit
	add b
	ret
.digit
	sub CHARVAL("０")
	ret nc
	xor a
	ret

; パレット 7 の 色1 ＝ 赤（ボールと 同じ）、色2 ＝ 黄（WRAM バンク 2 の W2_BgPaletteData。V-blank で 送って もらう）
KitPPPalette:
	ld hl, KitPPColors
	ld de, W2_BgPaletteData + 8 * KIT_PP_PAL + 2
	di
	ld a, 2
	ldh [rWBK], a
	ld c, 4
.copy
	ld a, [hli]
	ld [de], a
	inc de
	dec c
	jr nz, .copy
	ld a, 1
	ld [W2_ForceBGPUpdate], a
	ldh [rWBK], a
	ei
	ret

KitPPColors:
	RGB 29,05,05, 31,22,00 ; 赤（つかまえた しるしの ボールと 同じ）、黄
