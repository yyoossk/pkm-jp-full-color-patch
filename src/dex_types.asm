; ずかんの 説明の ページの つづき（タイプ・進化・種族値）  … ピカチュウ版から受けとった dex_types.asm
; 青では、前に入れた タイプの ページ（バンク $13:5A13、ROM の中）の かわりに、これを よぶ。
; よび出し：ShowPokedexDataInternal（バンク $10:4400 の ld b, $13 / ld hl, KitDexWaitButton / call Bankswitch）
; 青の ラベル・番地は src/common.inc と vars/<版>.inc にある。
; wBuffer の かわりに wKitDexBuffer（$CEF0〜、30バイトの wBuffer の中。先頭 $CEE4 は FarCopyData が こわすので さける）を 使う。

INCLUDE "charmap.inc"

IF HAS_KIT_HUD   ; キットを 入れて いる 版だけ（カラー化のみには 入れない）

DEF wKitDexBuffer EQU $CEF0

SECTION "ずかん タイプ・進化・種族値 よび出し", ROMX[$4402], BANK[$10]
	ld hl, KitDexWaitButton

FreeBank13
; ずかんの 説明の ページの つづき（タイプ・進化・種族値）
; 前の dex_types.asm（タイプの ページ）を、このファイルで まるごと 入れかえる。
;
;   1ページめ: 説明（今までどおり）。つかまえた ポケモンなら 右下に「▼」、A で 次へ（B で とじる）
;   2ページめ: 下の わく = 「タイプ１／ほのお」「タイプ２／ひこう」（今までどおり）
;              右上（たかさ・おもさの 所。このページから かわる）= 「しんか」と その 条件
;                レベル16 ／ かみなりのいし（道具の 名前）／ つうしんこうかん ／ なし
;                進化が いくつも ある時（イーブイ）は、右上の 3行に 1つずつ
;              右下に「▼」、A で 次へ（B で とじる）
;   3ページめ: 下の わく = 種族値（名前は 略さない）
;                たいりょく ○○○  こうげき ○○○
;                ぼうぎょ   ○○○  すばやさ ○○○
;                とくしゅ   ○○○  ごうけい ○○○
;              A か B で とじる
;   つかまえて いない ポケモンは 今までどおり。
;
; 進化の 条件は EvosMovesPointerTable の データを 読む（その 版で 条件を かえて いれば、それが 出る）。
; ShowPokedexDataInternal: A か B を まつ 所の かわりに よぶ（wCurSpecies が その ポケモン）。
; どの バンクに 置いても よい（ほかの バンクの データは FarCopyData・predef で 読む）。

KitDexWaitButton:
	; つかまえた ポケモン: 説明が 出て いる（1行めの 1文字め）
	ld a, [wTileMap + 11 * SCREEN_WIDTH + 1]
	cp "　"
	jr z, KitDexWaitAB
	ld a, "▼"
	ldcoord_a 18, 16
	call KitDexWaitAB
	bit B_PAD_B, a
	ret nz
; ---- 2ページめ: タイプと 進化
	hlcoord 1, 10
	lb bc, 7, 18
	call ClearScreenArea
	hlcoord 2, 11
	ld de, KitDexTypeText
	call PlaceString
	hlcoord 7, 11
	predef PRINT_MON_TYPE ; wMonHeader も 読まれる
	call KitDexEvolution
	ld a, "▼"
	ldcoord_a 18, 16
	ld c, 10
	call DelayFrames
	call KitDexWaitAB
	bit B_PAD_B, a
	ret nz
; ---- 3ページめ: 種族値
	hlcoord 1, 10
	lb bc, 7, 18
	call ClearScreenArea
	call KitDexStats
	ld c, 10
	call DelayFrames
KitDexWaitAB:
	call JoypadLowSensitivity
	ldh a, [hJoy5]
	and PAD_A | PAD_B
	jr z, KitDexWaitAB
	ret

KitDexTypeText:
	db   "タイプ１／"
	next "タイプ２／@"

; ---------------------------------------------------------------- 種族値
KitDexStats:
	hlcoord 1, 11
	ld de, .HPText
	ld bc, wMonHBaseHP
	call .StatLeft
	hlcoord 11, 11
	ld de, .AtkText
	ld bc, wMonHBaseAttack
	call .StatRight
	hlcoord 1, 13
	ld de, .DefText
	ld bc, wMonHBaseDefense
	call .StatLeft
	hlcoord 11, 13
	ld de, .SpdText
	ld bc, wMonHBaseSpeed
	call .StatRight
	hlcoord 1, 15
	ld de, .SpcText
	ld bc, wMonHBaseSpecial
	call .StatLeft
	; ごうけい（2バイト）
	ld hl, wMonHBaseHP
	ld b, 5
	xor a
	ld d, a
	ld e, a
.sum
	ld a, [hli]
	add e
	ld e, a
	jr nc, .noCarry
	inc d
.noCarry
	dec b
	jr nz, .sum
	ld hl, wKitDexBuffer
	ld a, d
	ld [hli], a
	ld [hl], e
	hlcoord 11, 15
	ld de, .TotalText
	call PlaceString
	hlcoord 16, 15
	ld de, wKitDexBuffer
	lb bc, 2, 3
	jp PrintNumber

; de = ラベル、bc = 値、hl = 置く所。数字は 3けた 右よせ
;   左の 列（1〜9）: ラベルの 6マスあと、右の 列（11〜18）: 5マスあと
.StatRight:
	ld a, 5
	jr .stat
.StatLeft:
	ld a, 6
.stat
	push af
	push hl
	push bc
	call PlaceString
	pop de
	pop hl
	pop af
	ld c, a
	ld b, 0
	add hl, bc
	lb bc, 1, 3
	jp PrintNumber

.HPText:    db "たいりょく@"
.AtkText:   db "こうげき@"
.DefText:   db "ぼうぎょ@"
.SpdText:   db "すばやさ@"
.SpcText:   db "とくしゅ@"
.TotalText: db "ごうけい@"

; ---------------------------------------------------------------- 進化
KitDexEvolution:
	; 右上（たかさ・おもさ）を けす
	hlcoord 9, 3
	lb bc, 6, 10
	call ClearScreenArea
	; 進化の データ（最大 3つ × 4バイト ＋ 0）を wKitDexBuffer に
	ld a, [wCurSpecies]
	dec a
	ld l, a
	ld h, 0
	add hl, hl
	ld de, EvosMovesPointerTable
	add hl, de
	ld de, wKitDexBuffer
	ld bc, 2
	ld a, BANK_EvosMovesPointerTable
	call FarCopyData
	ld hl, wKitDexBuffer
	ld a, [hli]
	ld h, [hl]
	ld l, a
	ld de, wKitDexBuffer
	ld bc, 13
	ld a, BANK_EvosMovesPointerTable
	call FarCopyData
	; いくつ あるか
	ld hl, wKitDexBuffer
	ld c, 0
.count
	ld a, [hl]
	and a
	jr z, .counted
	inc c
	cp EVOLVE_ITEM
	ld de, 4
	jr z, .skip
	dec de
.skip
	add hl, de
	jr .count
.counted
	ld a, c
	cp 2
	jr nc, .many
	; 0こ・1こ: 「しんか」の 下に 条件
	push bc
	hlcoord 9, 6
	ld de, .EvoText
	call PlaceString
	pop bc
	ld a, c
	and a
	jr nz, .one
	hlcoord 9, 8
	ld de, .NoneText
	jp PlaceString
.one
	hlcoord 9, 8
	ld de, wKitDexBuffer
	jp .Condition
.many
	; いくつも（イーブイ）: 4・6・8行めに 1つずつ
	hlcoord 9, 4
	ld de, wKitDexBuffer
	ld b, 3
.manyLoop
	ld a, [de]
	and a
	ret z
	push bc
	push hl
	call .Condition ; de = 次の データ
	pop hl
	ld bc, 2 * SCREEN_WIDTH
	add hl, bc
	pop bc
	dec b
	jr nz, .manyLoop
	ret

; de = 進化の データ1つ、hl = 置く所。de = 次の データ
.Condition:
	ld a, [de]
	inc de
	cp EVOLVE_LEVEL
	jr z, .level
	cp EVOLVE_ITEM
	jr z, .item
	; つうしんこうかん
	inc de ; レベル
	inc de ; しんか後
	push de
	ld de, .TradeText
	call PlaceString
	pop de
	ret
.level
	push de
	push hl
	ld de, .LevelText
	call PlaceString
	ld h, b
	ld l, c
	pop af ; すてる
	pop de
	push de
	lb bc, LEFT_ALIGN | 1, 3
	call PrintNumber
	pop de
	inc de ; レベル
	inc de ; しんか後
	ret
.item
	ld a, [de]
	inc de
	inc de ; レベル
	inc de ; しんか後
	push de
	push hl
	ld b, a
	ld a, [wNamedObjectIndex] ; wPokedexNum と 同じ 所なので とっておく
	push af
	ld a, b
	ld [wNamedObjectIndex], a
	call GetItemName
	pop af
	ld [wNamedObjectIndex], a
	pop hl
	call PlaceString
	pop de
	ret

.EvoText:   db "しんか@"
.NoneText:  db "なし@"
.LevelText: db "レベル@"
.TradeText: db "つうしんこうかん@"

ENDC
