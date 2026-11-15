; 第65弾（金）：サファリゾーンで 歩いて いる あいだ、画面の 下に のこりの 歩数と ボールを 出す。
; クリスタル版の 9C:4000（キットの safarihud.asm）を 金に あわせた もの。
; 金には 町の 名前の 看板が ないので、HandleMapBackground（25:6726）の farcall ScrollScreen（25:672C）を
; この 処理への farcall に して、はじめに ScrollScreen を よぶ。
; SAF_BANK・HUD_ADDR は gold_safari.py から -D で わたす。
DEF wStatusFlags2         EQU $d565
DEF wSafariBallsRemaining EQU $d989
DEF wSafariTimeRemaining  EQU $d98a
DEF IN_SAFARI             EQU $7140      ; 同じ バンク（gold_safari）
DEF hWY             EQU $ffd4
DEF hCGBPalUpdate   EQU $ffe7
DEF wBGPals1_7      EQU $c238
DEF wBGPals2_7      EQU $c2b8
DEF HUD_WY          EQU $80
DEF ROW0            EQU $9c00
DEF ROW1            EQU $9c20
DEF ATTR            EQU $8f      ; 優先・VRAM バンク1・パレット7（金は つたの 絵・字を バンク0の $f8〜 に 読むので、字は バンク1 に 写す）

SECTION "safari hud", ROMX[HUD_ADDR], BANK[1]
SafariHUD:
	ld a, $03
	ld hl, $57a9
	rst $08                          ; ScrollScreen（もとの 処理）
	ld a, [wStatusFlags2]
	bit 1, a                         ; サファリゲーム中
	jr z, .off
	call IN_SAFARI                   ; キャリー ＝ サファリの 中
	jr nc, .off
	call .Pal
	ldh a, [$ff4f]
	push af
	ldh a, [hWY]
	cp HUD_WY
	call nz, .Full
	call .Digits
	pop af
	ldh [$ff4f], a
	ld a, HUD_WY
	jr .set
.off
	ldh a, [hWY]
	cp HUD_WY
	ret nz                           ; 出していなければ なにも しない
	ld a, $90
.set
	ldh [$ff4a], a
	ldh [hWY], a
	ret

.Pal
	ld hl, wBGPals2_7
	ld de, .Colors
	ld b, 8
.cmp
	ld a, [de]
	cp [hl]
	jr nz, .write
	inc de
	inc hl
	dec b
	jr nz, .cmp
	ret
.write
	ld hl, wBGPals1_7
	call .CopyPal
	ld hl, wBGPals2_7
	call .CopyPal
	ld a, 1
	ldh [hCGBPalUpdate], a
	ret
.CopyPal
	ld de, .Colors
	ld b, 8
.copy
	ld a, [de]
	inc de
	ld [hli], a
	dec b
	jr nz, .copy
	ret
.Colors
	dw $7fff, $7fff, $35ad, $0000

.Full
	ld a, 1
	ldh [$ff4f], a
	ld de, .Glyphs
.g_loop
	ld a, [de]
	inc de
	and a
	jr z, .g_done
	ld c, $90                        ; a < $80 → $9000 + a*16、a ≥ $80 → $8000 + a*16
	cp $80
	jr c, .g_lo
	ld c, $80
.g_lo
	ld l, a
	ld h, 0
	add hl, hl
	add hl, hl
	add hl, hl
	add hl, hl
	ld a, h
	add c
	ld h, a
	ld b, 8
.g_row
	ld a, [de]
	call .Put
	ld a, [de]
	call .Put
	inc de
	dec b
	jr nz, .g_row
	jr .g_loop
.g_done
	xor a
	ldh [$ff4f], a
	ld hl, ROW0
	ld de, .Row0
	call .Put20
	ld hl, ROW1
	ld de, .Row1
	call .Put20
	ld a, 1
	ldh [$ff4f], a
	ld hl, ROW0
	call .Attr20
	ld hl, ROW1
.Attr20
	ld b, 20
.attr_loop
	ld a, ATTR
	call .Put
	dec b
	jr nz, .attr_loop
	ret
.Put20
	ld b, 20
.put_loop
	ld a, [de]
	inc de
	call .Put
	dec b
	jr nz, .put_loop
	ret

.Digits
	xor a
	ldh [$ff4f], a
	ld a, [wSafariTimeRemaining]
	ld h, a
	ld a, [wSafariTimeRemaining + 1]
	ld l, a
	ld c, 0
.hundreds
	ld a, l
	sub 100
	ld e, a
	ld a, h
	sbc 0
	jr c, .hundreds_done
	ld h, a
	ld l, e
	inc c
	jr .hundreds
.hundreds_done
	ld a, l
	call .Split
	ld hl, ROW1 + 4
	ld a, c
	and a
	ld a, $7f
	jr z, .h_blank
	ld a, c
	add $f6
.h_blank
	call .Put
	ld a, c
	or d
	ld a, $7f
	jr z, .t_blank
	ld a, d
	add $f6
.t_blank
	call .Put
	ld a, e
	add $f6
	call .Put
	ld a, [wSafariBallsRemaining]
	call .Split
	ld hl, ROW1 + 14
	ld a, d
	and a
	ld a, $7f
	jr z, .b_blank
	ld a, d
	add $f6
.b_blank
	call .Put
	ld a, e
	add $f6
.Put
	push bc
	ld c, a
	di
.wait
	ldh a, [$ff41]
	and %10
	jr nz, .wait
	ld [hl], c
	ei
	inc hl
	pop bc
	ret

.Split
	ld d, 0
.split_loop
	sub 10
	jr c, .split_done
	inc d
	jr .split_loop
.split_done
	add 10
	ld e, a
	ret

.Glyphs
	INCLUDE "glyphs.inc"
	db 0
.Row0
	db $7f, $7f, $7f, $7f, $7f, $7f, $7f, $7f, $7f, $7f, $e5, $7f, $7f, $7f, $7f, $7f, $7f, $7f, $7f, $7f
.Row1
	db $7f, $b1, $c4, $7f, $7f, $7f, $7f, $ce, $7f, $7f, $9c, $e3, $a6, $7f, $7f, $7f, $ba, $7f, $7f, $7f
