; ずかんの タイプ・わざを 忘れさせる ときの わざの 情報・ショップの 説明（ピカチュウの キット）

; 1. ずかんの 説明の ページ（ShowPokedexDataInternal、bank 9 の A か B を 待つ ループの かわり）：
;    つかまえた ポケモンなら（説明の 1行めの 字 (1, 11) が 空白で ない）、右下に「▼」を 出して、A で
;    説明の ところを「タイプ１／ほのお」「タイプ２／ひこう」に する（殿堂入りと 同じ predef PrintMonType）。
;    もう いちど A か B で とじる。B なら 最初から とじる。緑の 説明の 場所も ピカチュウと 同じ（(1, 11) から）。
KitDexWaitButton::
	ld a, [wTileMap + 11 * SCREEN_WIDTH + 1]
	cp CHARVAL("　")
	jr z, KitDexWaitAB
	ld a, CHARVAL("▼")
	ldcoord_a 18, 16
	call KitDexWaitAB
	bit B_PAD_B, a
	ret nz
	hlcoord 1, 10
	lb bc, 7, 18
	call ClearScreenArea
	hlcoord 2, 11
	ld de, KitDexTypeText
	call PlaceString
	hlcoord 7, 11
	predef PrintMonType
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

; 2. わざを 忘れさせる 画面（どの わざを わすれさせたい？）：カーソルの ある わざの タイプ・いりょく・めいちゅうを
;    一覧（hlcoord 10, 8）の 上の わく（hlcoord 10, 2・lb bc, 4, 8）に 出す。いりょくが 0・1 なら「ー」。
;    緑では LearnMove の 一覧（bank 1）と、つよさを みる の「わすれさせる」の 一覧（bank $3F、forgetmove）の
;    call HandleMenuInput を、bank の 小さい 処理（farcall KitForgetMenuInput / ld a, e / ret）に した。
DEF KIT_FMI_X EQU 10
DEF KIT_FMI_Y EQU 2
DEF wMoves_K  EQU $d0b9
DEF wMenuWatchedKeys_F EQU $cc29

KitForgetMenuInput::
	hlcoord KIT_FMI_X, KIT_FMI_Y
	lb bc, 4, 8
	call TextBoxBorder
.loop
	call KitForgetDrawInfo
	ld a, PAD_A | PAD_B | PAD_UP | PAD_DOWN
	ld [wMenuWatchedKeys_F], a
	call HandleMenuInput
	ld e, a
	and PAD_A | PAD_B
	jr z, .loop
	ld a, PAD_A | PAD_B
	ld [wMenuWatchedKeys_F], a
	ret

KitForgetDrawInfo:
	hlcoord KIT_FMI_X + 1, KIT_FMI_Y + 1
	lb bc, 4, 8
	call ClearScreenArea
	ld a, [wCurrentMenuItem]
	ld e, a
	ld d, 0
	ld hl, wMoves_K
	add hl, de
	ld a, [hl]
	and a
	ret z
	dec a
	ld hl, Moves
	ld bc, 6 ; MOVE_LENGTH
	call AddNTimes
	ld de, wBuffer
	ld bc, 6
	ld a, Moves_BANK
	call FarCopyData
	; タイプ（PrintMoveType は wPlayerMoveType を 見る：バトルの 値を とって おく）
	ld a, [wPlayerMoveType]
	push af
	ld a, [wBuffer + 3] ; MOVE_TYPE
	ld [wPlayerMoveType], a
	hlcoord KIT_FMI_X + 1, KIT_FMI_Y + 2
	predef PrintMoveType
	pop af
	ld [wPlayerMoveType], a
	hlcoord KIT_FMI_X + 1, KIT_FMI_Y + 3
	ld de, KitFmiPowerText
	call PlaceString
	hlcoord KIT_FMI_X + 1, KIT_FMI_Y + 4
	ld de, KitFmiAccuracyText
	call PlaceString
	ld a, [wBuffer + 2] ; MOVE_POWER
	cp 2
	jr nc, .power
	ld a, CHARVAL("ー")
	ldcoord_a KIT_FMI_X + 8, KIT_FMI_Y + 3
	jr .accuracy
.power
	hlcoord KIT_FMI_X + 6, KIT_FMI_Y + 3
	ld de, wBuffer + 2
	lb bc, 1, 3
	call PrintNumber
.accuracy
	ld a, [wBuffer + 4] ; MOVE_ACC
	call KitAccuracyPercent
	ld [wBuffer + 6], a
	hlcoord KIT_FMI_X + 6, KIT_FMI_Y + 4
	ld de, wBuffer + 6
	lb bc, 1, 3
	jp PrintNumber

KitFmiPowerText:
	db "いりょく@"
KitFmiAccuracyText:
	db "めいちゅう@"

; 3. フレンドリィショップで 買う とき：カーソルの ある 道具の 説明を 画面の 下に（リュックと 同じ 説明。
;    MartPrintDescription は bagscreen の バンク）。
;    緑の DisplayListMenuIDLoop は 一覧を かく たびに ホームの 小さい 処理（00bd）を 呼ぶ
;   （PrintListMenuEntries と、bagpockets の ポケットの 見出し）。その 小さい 処理を farjp KitListPrint に した。
;    ・ショップの 一覧（PRICEDITEMLISTMENU）では wMenuWatchedKeys に 上下も 足して、カーソルを 動かす たびに
;      HandleMenuInput が もどる ように する（説明を かきかえる ため）。
;    ・すると DisplayListMenuIDLoop は 上下を スクロールと して あつかうので、カーソルが 動いた のに
;      スクロールが かわった ときは、ここで もとの スクロールに もどす（カーソルが 動いて いない（いちばん 上・下で
;      押した）ときは 今までどおり スクロール する）。前の カーソルと スクロールは wMenuItemToSwap に おぼえる
;     （ショップの 一覧では ならびかえを 使わない。DisplayListMenuID が 0 に して から 始まる。
;      PrintListMenuEntries の 間だけ 0 に もどす）。
DEF wMenuItemToSwap_K EQU $cc35
DEF wListScrollOffset_K EQU $cc36
DEF wListMenuID_K EQU $cf7b
DEF PRICEDITEMLISTMENU_K EQU 2

KitListPrint::
	ld a, [wListMenuID_K]
	cp PRICEDITEMLISTMENU_K
	jr nz, .print
	ld a, [wMenuItemToSwap_K]
	and a
	jr z, .print
	dec a
	ld b, a
	and 3
	ld c, a ; the cursor before
	ld a, [wCurrentMenuItem]
	cp c
	jr z, .print ; not moved: a real scroll (or nothing)
	ld a, b
	srl a
	srl a
	ld [wListScrollOffset_K], a ; moved: keep the scroll
.print
	xor a
	ld [wMenuItemToSwap_K], a
	call PrintListMenuEntries
	ld b, ListHook3F_BANK
	ld hl, ListHook3F
	call Bankswitch
	ld a, [wListMenuID_K]
	cp PRICEDITEMLISTMENU_K
	ret nz
	ld a, [wMenuWatchedKeys_F]
	or PAD_UP | PAD_DOWN
	ld [wMenuWatchedKeys_F], a
	ld b, MartPrintDescription_BANK
	ld hl, MartPrintDescription
	call Bankswitch
	ld a, [wListScrollOffset_K]
	add a
	add a
	ld b, a
	ld a, [wCurrentMenuItem]
	add b
	inc a
	ld [wMenuItemToSwap_K], a
	ret
