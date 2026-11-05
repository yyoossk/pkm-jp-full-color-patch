; ボックスの数（ピカチュウの キット）：マサキの パソコン「ボックスを かえる」で、左上の「いまのボックス」の
; わくを 2行 のばして（lb bc, 2, 9 → 4, 9。0〜5行め）、カーソルの ある ボックスの ポケモンの 数を
; 「なかみ　１２／３０」のように 出す（カーソルを 動かすと かわる。空なら「０／３０」）。
; 緑の わくの 作りも ピカチュウと 同じ（左上 hlcoord 0, 0、一覧 hlcoord 11, 0・lb bc, 16, 7、
; 名前は 2・4・…・16行めで、その 上の 行は「ボ」の 濁点の 行）。一覧と ボールは 今までどおり
; （ボールは フォントの $78、色は boxball が パレット 7 に 入れる）。
; ・DisplayChangeBoxMenu（bank $1C）の GetMonCountsForAllBoxes の あとの ボールの ループの かわりに KitBoxCounts。
; ・ChangeBox の call HandleMenuInput の かわりに KitBoxMenuInput（押した ボタンは a で かえす。bank $1C の 小さい 処理から）。
DEF wBoxMonCounts_K EQU $cd3d
DEF NUM_BOXES_K     EQU 8
DEF MONS_PER_BOX_K  EQU 30
DEF wMenuWatchedKeys_B EQU $cc29

KitBoxCounts::
	ld hl, wTileMap + 2 * SCREEN_WIDTH + 18
	ld de, wBoxMonCounts_K
	ld bc, SCREEN_WIDTH * 2
	ld a, NUM_BOXES_K
.loop
	push af
	ld a, [de]
	and a ; is the box empty?
	jr z, .noBall
	ld [hl], $78 ; pokeball tile next to the box name
.noBall
	add hl, bc
	inc de
	pop af
	dec a
	jr nz, .loop
	hlcoord 1, 4
	ld de, KitBoxCountText
	jp PlaceString

; HandleMenuInput を 上下でも もどる ように して くりかえし、そのたびに 数を かく。e ＝ 押した ボタン（A か B）
KitBoxMenuInput::
.loop
	call KitBoxDrawCount
	ld a, PAD_A | PAD_B | PAD_UP | PAD_DOWN
	ld [wMenuWatchedKeys_B], a
	call HandleMenuInput
	ld e, a
	and PAD_A | PAD_B
	jr z, .loop
	ld a, PAD_A | PAD_B
	ld [wMenuWatchedKeys_B], a
	ret

; カーソルの ある ボックスの 数を (5, 4) に「１２／３０」
KitBoxDrawCount:
	ld a, [wCurrentMenuItem]
	ld e, a
	ld d, 0
	ld hl, wBoxMonCounts_K
	add hl, de
	ld d, h
	ld e, l
	hlcoord 5, 4
	ld a, CHARVAL("　")
	ld [hli], a
	ld [hld], a
	lb bc, 1, 2
	call PrintNumber
	ld a, CHARVAL("／")
	ld [hli], a
	ld a, CHARVAL("０") + MONS_PER_BOX_K / 10
	ld [hli], a
	ld [hl], CHARVAL("０") + MONS_PER_BOX_K % 10
	ret

KitBoxCountText:
	db "なかみ@"
