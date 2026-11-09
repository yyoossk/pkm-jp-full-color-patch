; ずかんの 説明の ページの つづき（タイプ・進化・種族値）
; キットの dex_types.asm を 緑の 番地に 合わせた もの。前の タイプの ページ（37:54d1）の かわり。
;
;   1ページめ: 説明（今までどおり）。つかまえた ポケモンなら 右下に「▼」、A で 次へ（B で とじる）
;   2ページめ: 下の わく = 「タイプ１／ほのお」「タイプ２／ひこう」（今までどおり）
;              右上（たかさ・おもさの 所。このページから かわる）= 「しんか」と その 条件
;                レベル16 ／ かみなりのいし（道具の 名前）／ つうしんこうかん ／ なし
;                進化が いくつも ある時（イーブイ）は、右上の 3行に 1つずつ
;              右下に「▼」、A で 次へ（B で とじる）
;   3ページめ: 下の わく = 種族値（名前は 略さない）。A か B で とじる
;   つかまえて いない ポケモンは 今までどおり。
;
; 緑の 名前と 番地
DEF SCREEN_WIDTH      EQU 20
DEF wTileMap          EQU $c3a0
DEF wCurPartySpecies  EQU $cf78   ; ずかんで 見て いる ポケモン（内部の 番号）
DEF wCurSpecies       EQU $d092   ; GetMonHeader が 読む 番号（GetItemName でも 書きかわる）
DEF wMonHeader        EQU $d095   ; 緑では ここから（番号・種族値5つ・タイプ2つ …）
DEF wMonHBaseHP       EQU wMonHeader + 1
DEF wMonHBaseAttack   EQU wMonHeader + 2
DEF wMonHBaseDefense  EQU wMonHeader + 3
DEF wMonHBaseSpeed    EQU wMonHeader + 4
DEF wMonHBaseSpecial  EQU wMonHeader + 5
DEF wNamedObjectIndex EQU $d0e3   ; = wPokedexNum
DEF wKitDexBuf        EQU $cd7c   ; 看板の バッファ（ずかんでは 使わない）を 借りる
DEF hJoy5             EQU $ffb5
DEF FarCopyData       EQU $028c
DEF ClearScreenArea   EQU $0374
DEF PlaceString       EQU $0405
DEF GetItemName       EQU $19e5
DEF DelayFrames       EQU $3661
DEF JoypadLowSensitivity EQU $3759
DEF GetMonHeader      EQU $2e1f
DEF PrintNumber       EQU $3b6f
DEF Predef            EQU $3d7d
DEF PREDEF_PRINTMONTYPE EQU $4b
DEF EvosMovesPointerTable EQU $70d7
DEF EVOS_BANK         EQU $0e
DEF EVOLVE_LEVEL      EQU 1
DEF EVOLVE_ITEM       EQU 2
DEF LEFT_ALIGN        EQU 1 << 6
DEF B_PAD_B           EQU 1
DEF PAD_A             EQU 1
DEF PAD_B             EQU 2

MACRO hlcoord
	ld hl, wTileMap + (\2) * SCREEN_WIDTH + (\1)
ENDM
MACRO ldcoord_a
	ld [wTileMap + (\2) * SCREEN_WIDTH + (\1)], a
ENDM
MACRO lb
	ld \1, ((\2) & $ff) << 8 | ((\3) & $ff)
ENDM

SECTION "ずかん 呼ぶ所", ROMX[$4d04], BANK[$09]
	ld hl, KitDexWaitButton   ; （ld b, $37 / call Bankswitch は そのまま）

SECTION "ずかん タイプ・進化・種族値", ROMX[$5c00], BANK[$37]
KitDexWaitButton:
	; つかまえた ポケモン: 説明が 出て いる（1行めの 1文字め）
	ld a, [wTileMap + 11 * SCREEN_WIDTH + 1]
	cp CHARVAL("　")
	jr z, KitDexWaitAB
	ld a, CHARVAL("▼")
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
	ld a, PREDEF_PRINTMONTYPE
	call Predef              ; wMonHeader も 読まれる
	call KitDexEvolution
	ld a, CHARVAL("▼")
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
	db "タイプ１／<NEXT>"
	db "タイプ２／@"

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
	ld hl, wKitDexBuf
	ld a, d
	ld [hli], a
	ld [hl], e
	hlcoord 11, 15
	ld de, .TotalText
	call PlaceString
	hlcoord 16, 15
	ld de, wKitDexBuf
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
	; 進化の データ（最大 3つ × 4バイト ＋ 0）を wKitDexBuf に
	ld a, [wCurPartySpecies]
	dec a
	ld l, a
	ld h, 0
	add hl, hl
	ld de, EvosMovesPointerTable
	add hl, de
	ld de, wKitDexBuf
	ld bc, 2
	ld a, EVOS_BANK
	call FarCopyData
	ld hl, wKitDexBuf
	ld a, [hli]
	ld h, [hl]
	ld l, a
	ld de, wKitDexBuf
	ld bc, 13
	ld a, EVOS_BANK
	call FarCopyData
	call .Print
	; GetItemName が $d092〜 を 書きかえるので、ヘッダーを 読みなおして おく
	ld a, [wCurPartySpecies]
	ld [wCurSpecies], a
	jp GetMonHeader

.Print:
	; いくつ あるか
	ld hl, wKitDexBuf
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
	ld de, wKitDexBuf
	jp .Condition
.many
	; いくつも（イーブイ）: 4・6・8行めに 1つずつ
	hlcoord 9, 4
	ld de, wKitDexBuf
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
.LevelText: db "レべル@"   ; 緑の 字では 「ベ」は 「べ」と 同じ
.TradeText: db "つうしんこうかん@"
