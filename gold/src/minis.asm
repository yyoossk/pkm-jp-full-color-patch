; ポケットモンスター 金（日本版）手持ちのポケモンの見た目（Polished Crystal のミニアイコン）
; （クリスタル追加機能キットの minis.asm を移植）
;
; ・アイコンの絵：約40種類の使い回しではなく、ポケモンごとの絵（16×16 ×2コマ）。
;   手持ち・名前入力・わざの画面・交換など、GetIconGFX でアイコンを読みこむ所はぜんぶこの絵になる。
; ・アイコンの色：手持ちの画面では 1匹ずつ専用の OBJ パレット（2〜7番）にして、そのポケモンの色
;   （色ちがいは色ちがいの色）。どうぐ・メールの印は元のまま。
;
; 金銀クリスタルとのちがい
; ・ROM が 1MB でいっぱいなので、2MB にして 絵をバンク $40・$41 に置いた（ヘッダーは rgbfix -p で直す）。
; ・色と色の処理はバンク $3f の空き。
; ・金銀の色のデータ（wOBPals1/2）は WRAM0 にあるので、WRAM のバンクの切りかえはいらない。
; ・アイコンの種類番号は WRAM の空き（$dee8）に覚えておく（前は $de3b で、わざの ならびかえ（statsmove）と かさなって いた）。

INCLUDE "bf/pg.inc"

DEF wIconSpecies       EQU $dee8      ; 使われていない WRAM（$de3b は つよさをみる の わざの ならびかえ が 使う。$de40〜$dee7 は 60fps）
DEF ICON_EGG_JP        EQU $1c
DEF MINI_BANK          EQU $40       ; $40・$41（1バンクに128匹）
DEF ICONPAL_FIRST      EQU 2         ; 手持ちの1匹目 = OBJ パレット2
DEF OTHERICON_PAL      EQU 7         ; 名前入力・わざの画面のアイコン
DEF wPartyMon1DVs_JP   EQU $da05

;---------------------------------------------------------------------
; バンク $23（アイコンの処理）
;---------------------------------------------------------------------
; ReadMonMenuIcon：種類番号を覚えておく（cp EGG / jr z, .egg の所）
SECTION "minis ReadMonMenuIcon", ROMX[J_ReadMonMenuIcon], BANK[JB_ReadMonMenuIcon]
	call Minis_SaveSpecies
	nop

; GetIconGFX：絵の読みこみ元をポケモンごとの絵にする（ld a,[wCurIcon] … lb bc, BANK(Icons), 8）
SECTION "minis GetIconGFX", ROMX[J_GetIconGFX + 12], BANK[JB_GetIconGFX]
	call Minis_GetIconSource
	jr @ + 2 + 14
	ASSERT @ + 14 == J_GetIconGFX + 31   ; call Request2bpp

; 手持ちの画面のアイコン：色を決める（call .SpawnItemIcon の所）
SECTION "minis party icon", ROMX[$660e], BANK[$23]
	call Minis_InitPartyMenuIcon

; 名前入力・わざの画面のアイコン：色を決める
SECTION "minis naming icon", ROMX[J_NamingScreen_InitAnimatedMonIcon + 25], BANK[JB_NamingScreen_InitAnimatedMonIcon]
	jp Minis_InitOtherIcon       ; ld [hl], SPRITE_ANIM_FUNC_NULL / ret
SECTION "minis moves icon", ROMX[J_MoveList_InitAnimatedMonIcon + 26], BANK[JB_MoveList_InitAnimatedMonIcon]
	jp Minis_InitOtherIcon

; アニメの1コマを作るとき：色の番号を wCurSpriteOAMFlags の下の3ビットに入れる
SECTION "minis frame", ROMX[J_UpdateAnimFrame + 3], BANK[JB_UpdateAnimFrame]
	call Minis_GetSpriteAnimFrame

; OAM の属性：色の番号があれば使う
SECTION "minis oam attr", ROMX[J_GetSpriteOAMAttr], BANK[JB_GetSpriteOAMAttr]
	jp Minis_GetSpriteOAMAttr

SECTION "minis bank 23", ROMX[$7d00], BANK[$23]
Minis_SaveSpecies:
	ld [wIconSpecies], a
	cp EGG
	ret nz
	pop hl                       ; ReadMonMenuIcon からぬける
	ld a, ICON_EGG_JP
	ret

; de = 絵の場所、b = バンク、c = 8（hl はそのまま）
Minis_GetIconSource:
	push hl
	ld a, [wIconSpecies]
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
	ld c, 8
	pop hl
	ret

Minis_InitPartyMenuIcon:
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
	jp J_PartyMenu_InitAnimatedMonIcon__SpawnItemIcon

; 名前入力・わざの画面のアイコン：色の番号を入れて、そのポケモンの色を OTHERICON_PAL に入れる
; （NamingScreen_InitAnimatedMonIcon・MoveList_InitAnimatedMonIcon の最後の ld [hl], SPRITE_ANIM_FUNC_NULL / ret）
Minis_InitOtherIcon:
	ld [hl], 0                   ; SPRITE_ANIM_FUNC_NULL
	ld hl, SPRITEANIMSTRUCT_VAR4
	add hl, bc
	ld [hl], $80 | OTHERICON_PAL
	push bc
	ld a, BANK(Minis_LoadOtherIconPal)
	ld hl, Minis_LoadOtherIconPal
	rst $08
	pop bc
	ret

Minis_GetSpriteAnimFrame:
	call J_GetSpriteAnimFrame
	push af
	push hl
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
; 絵（バンク $40・$41。ROM を 2MB にする）
;---------------------------------------------------------------------
SECTION "minis gfx 1", ROMX[$4000], BANK[MINI_BANK]
	INCBIN "gfxdata/minis.2bpp", 0, 128 * 128
SECTION "minis gfx 2", ROMX[$4000], BANK[MINI_BANK + 1]
	INCBIN "gfxdata/minis.2bpp", 128 * 128

;---------------------------------------------------------------------
; 色（バンク $3f の空き）
;---------------------------------------------------------------------
SECTION "minis pals", ROMX[$7000], BANK[$3f]
MiniIconPals:
	INCBIN "gfxdata/minipals.bin"

; [hObjectStructIndex] 番目の手持ちの色を OBJ パレット（2〜7）に入れる
Minis_LoadPartyIconPal:
	ldh a, [hObjectStructIndex]
	ld hl, wPartyMon1DVs_JP
	ld bc, PARTYMON_STRUCT_LENGTH
	call J_AddNTimes             ; hl = 個体値
	ldh a, [hObjectStructIndex]
	ld e, a
	ld d, 0
	add ICONPAL_FIRST
	ld c, a
	push hl
	ld hl, wPartySpecies
	add hl, de
	ld a, [hl]
	pop hl
	jr Minis_SetIconPal

; 名前入力・わざの画面のアイコンの色（OBJ パレット OTHERICON_PAL）。
; 手持ちの wCurPartyMon 番目が同じポケモンなら、その個体値で 色ちがい を見る（ちがえば ふつうの色）
Minis_LoadOtherIconPal:
	ld hl, 0
	ld a, [wPartyCount]
	ld b, a
	ld a, [wCurPartyMon]
	cp b
	jr nc, .go                   ; 手持ちの数より大きい
	ld e, a
	ld d, 0
	ld hl, wPartySpecies
	add hl, de
	ld a, [wTempIconSpecies]
	cp [hl]
	ld hl, 0
	jr nz, .go
	ld a, e
	ld hl, wPartyMon1DVs_JP
	ld bc, PARTYMON_STRUCT_LENGTH
	call J_AddNTimes
.go
	ld c, OTHERICON_PAL
	ld a, [wTempIconSpecies]
	; fallthrough

; a = ポケモン、hl = 個体値（0 = 色ちがいを見ない）、c = OBJ パレットの番号
; 画面が見えているとき（ならびかえ のあと など）は すぐに画面に出す。
; 金銀の VBlank は 色の更新をした回は 絵の転送（Request2bpp）をしないので、
; そのときは 更新が終わるまで待つ（待たないと次のポケモンの絵が読みこまれない）。
; 画面が消えているときは VBlank が来ないので待たない。
Minis_SetIconPal:
	ld b, a
	ldh a, [hCGB]
	and a
	ret z                        ; 白黒のゲームボーイでは色はいらない
	ld a, c
	add a
	add a
	add a                        ; × 8（1パレット）
	push af
	ld a, b
	cp EGG
	jr nz, .got
	xor a                        ; タマゴ = 0番
.got
	ld d, h
	ld e, l                      ; de = 個体値
	ld l, a
	ld h, 0
rept 3
	add hl, hl                   ; × 8
endr
	ld bc, MiniIconPals
	add hl, bc
; 色ちがい？（ぼうぎょ・すばやさ・とくしゅ が 10、こうげきが 2,3,6,7,10,11,14,15）
	ld a, d
	or e
	jr z, .normal
	ld a, [de]
	ld b, a
	inc de
	ld a, [de]
	cp $aa
	jr nz, .normal
	ld a, b
	and $0f
	cp $0a
	jr nz, .normal
	bit 5, b
	jr z, .normal
	ld bc, 4
	add hl, bc
.normal
	ld a, [hli]
	ld c, a
	ld a, [hli]
	ld b, a
	ld a, [hli]
	ld e, a
	ld d, [hl]                   ; bc = 明るい色、de = 暗い色
	pop af
	add LOW(wOBPals1)
	ld l, a
	ld h, HIGH(wOBPals1)
	push hl
	call .write
	pop hl
; 画面の色が消してある（ClearPalettes で wOBPals2 が全部 $ff）ときは、wOBPals1 だけにしておく。
; 手持ちの画面などは あとで SetDefaultBGPAndOBP（わざの画面は ApplyPals）が まとめて画面に出すので、
; ここで出すと アイコンだけが一覧より先に出てしまう（元のゲームは一覧といっしょに出る）
	ld a, [wOBPals2 + 1]
	cp $ff
	ret z
	ld a, l
	add LOW(wOBPals2 - wOBPals1)
	ld l, a
	ld h, HIGH(wOBPals2)
	call .write
	ld a, 1
	ldh [hCGBPalUpdate], a
	ldh a, [rLCDC]
	bit 7, a
	ret z                        ; 画面が消えている
.wait
	call J_DelayFrame
	ldh a, [hCGBPalUpdate]
	and a
	jr nz, .wait
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
