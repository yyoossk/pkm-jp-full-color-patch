; わざマシンの わざ名・サファリの 歩数（ピカチュウの キット）
;
; 1. ゲームコーナーの 景品交換所：わざマシンの 一覧を「２３　りゅうのいかり　３３００」（番号・わざ・コインの 数）に、
;    確認の 文を「わざマシン２３　りゅうのいかりで　いいんだね？」に する。
;    緑の 景品の わくも ピカチュウと 同じ（hlcoord 0, 2・lb bc, 8, 16）。景品も 同じ（23・15・50）。
;    GetPrizeMenuId（bank $14）の わざマシンの 所を farcall KitPrizeTMNames / ret に、
;    HandlePrizeChoice の わざマシンの call GetItemName を KitPrizeTMName に した。
;    わざは TechnicalMachines（bank 4。kit11.py が 番地を わたす）と GetMoveName で 出す。
DEF wPrize1_K       EQU $d102
DEF wPrize1Price_K  EQU $d106
DEF wNamedObjectIndex_K EQU $d0e3
DEF TM01_K          EQU $c9
DEF NAME_BUFFER_LENGTH_K EQU 20

KitPrizeTMNames::
	ld hl, wPrize1_K
	ld de, wPrize1Price_K
	ld c, 4 ; row
.loop
	push bc
	push de
	push hl
	; hl = coord (2, row)
	ld hl, wTileMap + 2
	ld b, 0
	ld a, c
.row
	push bc
	ld bc, SCREEN_WIDTH
	add hl, bc
	pop bc
	dec a
	jr nz, .row
	pop de ; the prize
	push de
	push hl
	ld a, [de]
	ld [wNamedObjectIndex_K], a
	sub TM01_K - 1 ; TM number (10-50)
	ld b, CHARVAL("０") - 1
.tens
	inc b
	sub 10
	jr nc, .tens
	add 10
	add CHARVAL("０")
	ld [hl], b
	inc hl
	ld [hl], a
	inc hl
	inc hl ; (5, row)
	push hl
	call KitPrizeGetMoveName
	pop hl
	call PlaceString
	pop hl
	ld bc, 11
	add hl, bc
	pop bc ; the prize
	pop de ; its price
	push bc
	push de
	ld c, $82 ; 2 bytes, leading zeroes
	call PrintBCDNumber
	pop de
	inc de
	inc de
	pop hl
	inc hl
	pop bc
	inc c
	inc c
	ld a, c
	cp 10
	jr c, .loop
	hlcoord 2, 10
	ld de, KitPrizeNoThanksText
	jp PlaceString

KitPrizeNoThanksText:
	db "いらない@"

; [wNamedObjectIndex] = わざマシン → wNameBuffer ＝「わざマシン２３　りゅうのいかり」（[wNamedObjectIndex] は そのまま）
KitPrizeTMName::
	call GetItemName
	ld hl, wNameBuffer
	ld de, wStringBuffer
	ld bc, NAME_BUFFER_LENGTH_K
	call CopyData
	call KitPrizeGetMoveName ; wNameBuffer = the move
	ld hl, wStringBuffer
.findEnd
	ld a, [hli]
	cp $50
	jr nz, .findEnd
	dec hl
	ld [hl], CHARVAL("　")
	inc hl
	ld de, wNameBuffer
.copy
	ld a, [de]
	inc de
	ld [hli], a
	cp $50
	jr nz, .copy
	ld hl, wStringBuffer
	ld de, wNameBuffer
	ld bc, NAME_BUFFER_LENGTH_K
	jp CopyData

; [wNamedObjectIndex] = わざマシン → de = wNameBuffer = わざの 名前（[wNamedObjectIndex] は そのまま）
KitPrizeGetMoveName:
	ld a, [wNamedObjectIndex_K]
	push af
	sub TM01_K ; 0-
	ld c, a
	ld b, 0
	ld hl, TechnicalMachines
	add hl, bc
	ld de, wBuffer
	ld bc, 1
	ld a, TechnicalMachines_BANK
	call FarCopyData
	ld a, [wBuffer]
	ld [wNamedObjectIndex_K], a
	call GetMoveName
	pop af
	ld [wNamedObjectIndex_K], a
	ld de, wNameBuffer
	ret

; 2. サファリゾーンの 中では、画面の 下 2行に「あと　４８２ほ　　ボール　２５こ」（上の 行は 濁点用）。
;    場所の 名前（sign.asm）と 同じ しくみ：ウィンドウ（vBGMap1 の 上の 2行）に かいて hWY を 128 に。
;    字は VRAM の バンク1 に 写し（KitSignCopyGlyph）、色は 緑の タイルごとの パレット（W2_TilesetPaletteMap）。
;    ・KitSafariHudTick：フィールドで 毎回（KitOverworldTick。場所の 名前の あと）。サファリゾーンの マップ
;      （SAFARI_ZONE_EAST 〜 CERULEAN_CAVE_2F の 前）で ウィンドウが あいて いれば（hWY が 144）出す。
;      話しかけ・メニュー・戦闘・場所の 名前の 間は ウィンドウが ほかに 使われて いるので 出さず、おわると また 出す。
;      サファリゾーンの 外で hWY が 128 なら 消す。
;    ・KitSafariHudStep：SafariZoneCheckSteps（bank 7。1歩 ごと）から。出て いる ときだけ 歩数を かきなおす。
DEF KIT_HUD_BUFFER  EQU wTileMapBackup2 ; 2行 × 20（かく ときだけ 使う。場所の 名前と 同じ）
DEF KIT_HUD_STEPS_X EQU 5
DEF KIT_HUD_BALLS_X EQU 15
DEF wSafariSteps_K    EQU $d68c ; 2 バイト
DEF wNumSafariBalls_K EQU $d983
DEF SAFARI_ZONE_EAST_K  EQU $d9
DEF CERULEAN_CAVE_2F_K  EQU $e2

KitSafariHudTick:
	call KitHudInSafari
	jr c, .inSafari
	ldh a, [hWY]
	cp KIT_HUD_WY
	ret nz
	ld a, 144
	ldh [hWY], a
	ret
.inSafari
	ldh a, [hWY]
	cp 144
	ret nz ; shown, or the window is used by something else (the map sign too)
	ld hl, KIT_HUD_BUFFER
	ld bc, 2 * SCREEN_WIDTH
	ld a, CHARVAL("　")
	call FillMemory
	ld hl, KIT_HUD_BUFFER + SCREEN_WIDTH + 2
	ld de, KitHudText
	call PlaceString
	call KitHudPrintNumbers
	ld hl, KIT_HUD_BUFFER
	ld de, vBGMap1
	ld c, 2 * SCREEN_WIDTH
	call KitHudToWindow
	ld a, KIT_HUD_WY
	ldh [hWY], a
	ret

KitSafariHudStep::
	ldh a, [hWY]
	cp KIT_HUD_WY
	ret nz
	call KitHudPrintNumbers
	ld hl, KIT_HUD_BUFFER + SCREEN_WIDTH + KIT_HUD_STEPS_X
	ld de, vBGMap1 + 32 + KIT_HUD_STEPS_X
	ld c, 3
	jp KitHudToWindow

; carry: サファリゾーンの 中
KitHudInSafari:
	ld a, [wCurMap]
	cp SAFARI_ZONE_EAST_K
	ccf
	ret nc
	cp CERULEAN_CAVE_2F_K
	ret

KitHudPrintNumbers:
	ld hl, KIT_HUD_BUFFER + SCREEN_WIDTH + KIT_HUD_STEPS_X
	ld a, CHARVAL("　")
	ld [hli], a
	ld [hli], a
	ld [hl], a
	ld hl, KIT_HUD_BUFFER + SCREEN_WIDTH + KIT_HUD_BALLS_X
	ld [hli], a
	ld [hl], a
	ld hl, KIT_HUD_BUFFER + SCREEN_WIDTH + KIT_HUD_STEPS_X
	ld de, wSafariSteps_K
	lb bc, 2, 3
	call PrintNumber
	ld hl, KIT_HUD_BUFFER + SCREEN_WIDTH + KIT_HUD_BALLS_X
	ld de, wNumSafariBalls_K
	lb bc, 1, 2
	jp PrintNumber

KitHudText:
	db "あと　　　　ほ　　ボール　　　こ@"

; c タイルを hl（バッファ）から de（ウィンドウの タイルマップ）へ。KitSignToWindow（sign.asm）と 同じ やり方
; （パレットは W2_TilesetPaletteMap の その タイルの もの。字（$80-$ff）は VRAM バンク1 に 写して 属性の bit 3）
KitHudToWindow:
.tile
	ld a, [hli]
	push hl
	push bc
	push de
	ld b, a
	cp $80
	call nc, KitSignCopyGlyph
	pop de
	di
	ld a, 2
	ldh [rWBK], a
	ld h, HIGH(W2_TilesetPaletteMap)
	ld l, b
	ld c, [hl] ; palette
	ld a, 1
	ldh [rWBK], a
	ld a, b
	cp $80
	jr c, .bank0
	set 3, c
.bank0
	call KitWaitHBlank
	ld a, b
	ld [de], a
	ld a, 1
	ldh [rVBK], a
	call KitWaitHBlank
	ld a, c
	ld [de], a
	xor a
	ldh [rVBK], a
	ei
	pop bc
	pop hl
	inc de
	ld a, e
	and 32 - 1
	cp SCREEN_WIDTH
	jr nz, .sameRow
	ld a, e
	add 32 - SCREEN_WIDTH
	ld e, a
	jr nc, .sameRow
	inc d
.sameRow
	dec c
	jr nz, .tile
	ret
