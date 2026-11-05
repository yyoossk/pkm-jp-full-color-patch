; Polished Crystal の 手持ちのポケモンの見た目（ミニアイコン）を移植
;
; ・アイコンの絵：ポケモンごとの絵（Polished Crystal の gfx/minis、16×16 ×2コマ）
;   元の「アイコンの種類（約40種類を使い回し）」の代わりに、種類ごとの絵を出す。
;   手持ち・名前入力・わざの画面など、アイコンを読みこむ所はぜんぶこの絵になる。
; ・アイコンの色：手持ちの画面では、1匹ずつ専用の OBJ パレット（2〜7番）を使い、
;   （名前入力・わざの画面のアイコンは OBJ パレット7）
;   そのポケモンの色（Polished Crystal のポケモンの色。色ちがいは色ちがいの色）にする。
;   どうぐ・メールを持っているときの印は 元のまま（パレット0）。
;
; データ（build.py ではなく tools で作る）
;   gfxdata/minis.2bpp    … 0 = タマゴ、1〜251 = 図鑑番号順。1匹 8タイル（128バイト）
;   gfxdata/minipals.bin  … 0〜251、1匹 8バイト（ふつうの 明るい色・暗い色、色ちがいの 明るい色・暗い色）

INCLUDE "src/crystal_jp.inc"

DEF rWBK               EQU $ff70
DEF hObjectStructIndex EQU $ffb0
DEF hCGBPalUpdate      EQU $ffe5
DEF wCurSpriteOAMFlags EQU $c3b8
DEF wPartySpecies      EQU $dc9e
DEF wPartyMon1DVs      EQU $dca5 + 21
DEF wBGPals1           EQU $d000     ; WRAM バンク5
DEF wBGPals2           EQU $d080
DEF wOBPals1           EQU $d040
DEF wOBPals2           EQU $d0c0
DEF wIconSpecies       EQU $dfb0     ; WRAM バンク2（使われていない所）
DEF EGG                EQU $fd
DEF ICON_EGG           EQU $1c
DEF SPRITEANIMSTRUCT_VAR4 EQU $0f
DEF SPRITEANIMSTRUCT_FRAMESET_ID EQU $01
DEF MINI_BANK          EQU $71       ; $71・$72（1バンクに128匹）
DEF MINIPAL_BANK       EQU $73
DEF ICONPAL_FIRST      EQU 2         ; 手持ちの1匹目 = OBJ パレット2
DEF MINIS_SINGLE_PAL   EQU 7         ; 名前入力・わざの画面のアイコン
DEF wTempIconSpecies   EQU $d296

;---------------------------------------------------------------------
; バンク $23（アイコンの処理）
;---------------------------------------------------------------------
; ReadMonMenuIcon：種類番号を覚えておく
SECTION "minis ReadMonMenuIcon", ROMX[$6ab3], BANK[$23]
	call Minis_SaveSpecies
	nop

; GetIcon：アイコンの絵の読みこみ先をポケモンごとの絵にする
SECTION "minis GetIcon", ROMX[$6a27], BANK[$23]
	jp Minis_GetIcon

; 手持ちの画面のアイコン：色を決める
SECTION "minis party icon", ROMX[$68d5], BANK[$23]
	call Minis_InitPartyMenuIcon

; 名前入力・わざの画面のアイコン：そのポケモンの色（LoadMenuMonIcon.Jumptable の2・3番目）
SECTION "minis icon jumptable", ROMX[$6854 + 2], BANK[$23]
	dw Minis_NamingScreenIcon
	dw Minis_MoveListIcon

; アニメの1コマを作るとき：色の番号を wCurSpriteOAMFlags の下の3ビットに入れる
SECTION "minis frame", ROMX[$504f], BANK[$23]
	call Minis_GetSpriteAnimFrame

; OAM の属性：色の番号があれば使う
SECTION "minis oam attr", ROMX[$50de], BANK[$23]
	jp Minis_GetSpriteOAMAttr

SECTION "minis bank 23", ROMX[$7f10], BANK[$23]
Minis_SaveSpecies:
	ld d, a
	ldh a, [rWBK]
	ld e, a
	ld a, 2
	ldh [rWBK], a
	ld a, d
	ld [wIconSpecies], a
	ld a, e
	ldh [rWBK], a
	ld a, d
	cp EGG
	ret nz
	pop hl                       ; ReadMonMenuIcon からぬける
	ld a, ICON_EGG
	ret

; スタック：[絵を置く VRAM の場所]、hl も同じ
Minis_GetIcon:
	ldh a, [rWBK]
	ld e, a
	ld a, 2
	ldh [rWBK], a
	ld a, [wIconSpecies]
	ld d, a
	ld a, e
	ldh [rWBK], a
	ld a, d
	cp EGG
	jr nz, .species
	xor a                        ; タマゴ = 0番
.species
	ld b, MINI_BANK
	bit 7, a
	jr z, .low
	inc b
.low
	and $7f
	ld l, a
	ld h, 0
rept 7
	add hl, hl                   ; × 128
endr
	ld de, $4000
	add hl, de
	ld d, h
	ld e, l
	pop hl
	push hl
	ld c, 8
	call $6a3f                   ; GetGFXUnlessMobile
	pop hl
	ret

Minis_InitPartyMenuIcon:
	call $6908                   ; InitPartyMenuIcon（bc = アニメの構造体）
	ldh a, [hObjectStructIndex]
	add ICONPAL_FIRST
	or $80
	ld hl, SPRITEANIMSTRUCT_VAR4
	add hl, bc
	ld [hl], a                   ; 印：$80 | パレット番号
	push bc
	ld a, BANK(Minis_LoadPartyIconPal)
	ld hl, Minis_LoadPartyIconPal
	rst $08
	pop bc
	ret

Minis_NamingScreenIcon:
	call $6961                   ; NamingScreen_InitAnimatedMonIcon
	ld e, 0
	jr Minis_SingleIcon
Minis_MoveListIcon:
	call $697d                   ; MoveList_InitAnimatedMonIcon
	ld e, 1
Minis_SingleIcon:
	ld hl, SPRITEANIMSTRUCT_VAR4
	add hl, bc
	ld [hl], $80 | MINIS_SINGLE_PAL
	push bc
	ld a, BANK(Minis_LoadSingleIconPal)
	ld hl, Minis_LoadSingleIconPal
	rst $08
	pop bc
	ret

Minis_GetSpriteAnimFrame:
	call $5132                   ; GetSpriteAnimFrame
	push af
	push hl
; 手持ちのアイコンのアニメ（フレームセット 1〜6）だけ。ほかのアニメ（セレビィ・そらをとぶ など）も
; VAR4 を使っているので、フレームセットで見分ける
	ld hl, SPRITEANIMSTRUCT_FRAMESET_ID
	add hl, bc
	ld a, [hl]
	dec a
	cp 6
	jr nc, .done
	ld hl, SPRITEANIMSTRUCT_VAR4
	add hl, bc
	ld a, [hl]
	bit 7, a
	jr z, .done
	and %111
	ld l, a
	ld a, [wCurSpriteOAMFlags]
	and ~%111
	or l
	ld [wCurSpriteOAMFlags], a
.done
	pop hl
	pop af
	ret

; hl = OAM データの属性の所（その1つ前がタイルの番号）
Minis_GetSpriteOAMAttr:
	ld a, [wCurSpriteOAMFlags]
	ld b, a
	ld a, [hl]
	xor b
	and $e0
	ld b, a
	ld a, [hl]
	and $1f
	or b
	ld b, a
	ld a, [wCurSpriteOAMFlags]
	and %111
	jr z, .keep
	dec hl
	ld a, [hl]
	inc hl
	cp 8
	jr nc, .keep                 ; どうぐ・メールの印は元の色
	ld a, b
	and ~%111
	ld b, a
	ld a, [wCurSpriteOAMFlags]
	and %111
	or b
	ret
.keep
	ld a, b
	ret

;---------------------------------------------------------------------
; 絵（バンク $71・$72）
;---------------------------------------------------------------------
SECTION "minis gfx 1", ROMX[$4000], BANK[MINI_BANK]
	INCBIN "gfxdata/minis.2bpp", 0, 128 * 128
SECTION "minis gfx 2", ROMX[$4000], BANK[MINI_BANK + 1]
	INCBIN "gfxdata/minis.2bpp", 128 * 128

;---------------------------------------------------------------------
; 色（バンク $73）
;---------------------------------------------------------------------
SECTION "minis pals", ROMX[$4000], BANK[MINIPAL_BANK]
MiniIconPals:
	INCBIN "gfxdata/minipals.bin"

; [hObjectStructIndex] 番目の手持ちの色を OBJ パレット（2〜7）に入れる
Minis_LoadPartyIconPal:
	ldh a, [hObjectStructIndex]
	ld hl, wPartyMon1DVs
	ld bc, PARTYMON_STRUCT_LENGTH
	call AddNTimes               ; hl = こたいち
	ldh a, [hObjectStructIndex]
	ld e, a
	ld d, 0
	push hl
	ld hl, wPartySpecies
	add hl, de
	ld a, [hl]
	pop hl
	ld d, a                      ; d = 種類
	ldh a, [hObjectStructIndex]
	add ICONPAL_FIRST
	ld e, a                      ; e = パレット
	jr Minis_SetIconPal

; わざの画面（e = 1、手持ちの [wCurPartyMon] 番目）・名前入力（e = 0）のアイコンの色 → OBJ パレット7
Minis_LoadSingleIconPal:
	ld a, [wTempIconSpecies]
	ld d, a
	ld hl, 0
	ld a, e
	and a
	jr z, .got
	ld a, [wCurPartyMon]
	ld hl, wPartyMon1DVs
	ld bc, PARTYMON_STRUCT_LENGTH
	call AddNTimes
.got
	ld e, MINIS_SINGLE_PAL
	; fallthrough

; d = 種類、hl = こたいち（0 なら ふつうの色）、e = パレット
Minis_SetIconPal:
	push de
	ld a, h
	or l
	jr z, .normal_dv
	ld a, [hli]
	ld b, a
	ld a, [hl]
	cp $aa
	jr nz, .normal_dv
	ld a, b
	and $0f
	cp $0a
	jr nz, .normal_dv
	bit 5, b
	jr z, .normal_dv
	ld c, 4                      ; 色ちがい
	jr .got_shiny
.normal_dv
	ld c, 0
.got_shiny
	pop de
	push de
	ld a, d
	cp EGG
	jr nz, .species
	xor a
.species
	ld l, a
	ld h, 0
rept 3
	add hl, hl                   ; × 8
endr
	ld b, 0
	add hl, bc
	ld bc, MiniIconPals
	add hl, bc
	ld a, [hli]
	ld c, a
	ld a, [hli]
	ld b, a
	ld a, [hli]
	ld e, a
	ld d, [hl]                   ; bc = 明るい色、de = 暗い色
	pop hl                       ; l = パレット
	ld a, l
	add a
	add a
	add a                        ; × 8（1パレット）
	add LOW(wOBPals1)
	ld l, a
	ld h, HIGH(wOBPals1)
	ldh a, [rWBK]
	push af
	ld a, 5
	ldh [rWBK], a
	push hl
	call .write
	pop hl
	; 画面に出ている色（wOBPals2）にも書くのは、画面が できあがって いる ときだけ。
	; 開くとき（ClearBGPalettes で 白に した あと）に 書くと、まだ 白い 画面の なかで
	; アイコン だけ 先に 色が ついて 見えた。できあがって いるか どうかは、
	; 画面に 出て いる BG パレット0（wBGPals2）の 色1 が 白（$7fff・$ffff）でも 黒（$0000）でも ないか で 見る
	; （白・黒の ときは、このあとの SetPalettes などが wOBPals1 から うつす）。
	; （前は wBGPals1 と wBGPals2 の BG パレット0 が 同じか で 見て いたが、ならびかえの とき wBGPals1 だけ
	;   一時 かわる ので、入れかえた アイコンが 少しの 間 前の 色（フィールドの 茶色など）で 見えた）
	push hl
	push de
	ld a, [wBGPals2 + 2]
	ld e, a
	ld a, [wBGPals2 + 3]
	ld d, a
	ld a, e
	cp $ff
	jr nz, .notwhite
	ld a, d
	and $7f
	cp $7f
	jr z, .notshown_np                ; 白（$7fff・ClearBGPalettes の $ffff）
.notwhite
	ld a, e
	or d
	jr z, .notshown_np
	pop de
	pop hl
	ld a, l
	add LOW(wOBPals2 - wOBPals1)
	ld l, a
	ld h, HIGH(wOBPals2)
	call .write
	pop af
	ldh [rWBK], a
	ld a, 1
	ldh [hCGBPalUpdate], a
	ret

.notshown_np
	pop de
	pop hl
	pop af
	ldh [rWBK], a
	ret

.write
	ld a, $ff                    ; 0：白（透明）
	ld [hli], a
	ld a, $7f
	ld [hli], a
	ld a, c                      ; 1：明るい色
	ld [hli], a
	ld a, b
	ld [hli], a
	ld a, e                      ; 2：暗い色
	ld [hli], a
	ld a, d
	ld [hli], a
	xor a                        ; 3：黒
	ld [hli], a
	ld [hl], a
	ret
