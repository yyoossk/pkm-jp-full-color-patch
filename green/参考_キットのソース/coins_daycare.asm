; コイン500まい・そだてやのレベル（ピカチュウの キット）
; ・タマムシの ゲームコーナーの カウンター：コインを「５０まい（１０００円）」か「５００まい（１００００円）」で 買える
;   （金・銀と 同じ。B で やめる）。緑の カウンターの 人の 文（bank $12 の text_asm）を
;   farcall KitGameCornerClerk / jp TextScriptEnd に した。コインの まどは 緑の GameCornerDrawCoinBox
;   （hlcoord 11, 0・7行。ピカチュウと 同じ）。選ぶ わくは hlcoord 12, 7・lb bc, 3, 6（下の 文の わくの 上）。
;   緑の 色は タイルごとの パレットなので、わくを かいた あとの 色の 直しは いらない。
; ・そだてや：「〜くらい　そだってるな」の あとに「いまは　レベル○○だ！」、まだの ときは
;   「いまも　レベル○○の　ままだ」。緑の そだてやの 文（bank $15）を 出す call PrintText を
;   farjp KitDaycareText に した（文は ここ。緑の 文を 写して 1文 足した もの）。
DEF wDayCareNumLevelsGrown_K EQU $cd3e
DEF wDayCareMonBoxLevel_K    EQU $d994 ; ここには 今の レベル（CalcLevelFromExperience の d）が 入って いる
DEF COIN_CASE_K   EQU $45
DEF SFX_PURCHASE_K EQU $b2
DEF hMoney_K      EQU $ff9f ; 3 バイト（BCD）
DEF hCoins_K      EQU $ffa0 ; 2 バイト（BCD）
DEF hUnusedCoinsByte_K EQU $ff9f
DEF wPlayerMoney_K EQU $d2cb
DEF wPlayerCoins_K EQU $d523
DEF wStatusFlags5_K EQU $d6af
DEF BIT_NO_TEXT_DELAY_K EQU 6
DEF wTopMenuItemY_K EQU $cc24
DEF wTopMenuItemX_K EQU $cc25
DEF wMaxMenuItem_K EQU $cc28
DEF wMenuWatchedKeys_K EQU $cc29
DEF wLastMenuItem_K EQU $cc2a
DEF wMenuWatchMovingOutOfBounds_K EQU $cc37
DEF SubBCDPredef_PREDEF EQU $0c
DEF AddBCDPredef_PREDEF EQU $0b

KitGameCornerClerk::
	ld b, GameCornerDrawCoinBox_BANK
	ld hl, GameCornerDrawCoinBox
	call Bankswitch
	ld hl, KitCoinsAskText
	call PrintText
	call SaveScreenTilesToBuffer1
	hlcoord 12, 7
	lb bc, 3, 6
	call TextBoxBorder
	hlcoord 14, 8
	ld de, KitCoinsMenuText
	call PlaceString
	ld a, 8
	ld [wTopMenuItemY_K], a
	ld a, 13
	ld [wTopMenuItemX_K], a
	xor a
	ld [wCurrentMenuItem], a
	ld [wLastMenuItem_K], a
	ld [wMenuWatchMovingOutOfBounds_K], a
	inc a
	ld [wMaxMenuItem_K], a
	ld a, PAD_A | PAD_B
	ld [wMenuWatchedKeys_K], a
	ld hl, wStatusFlags5_K
	res BIT_NO_TEXT_DELAY_K, [hl]
	call HandleMenuInput
	push af
	ld c, 15
	call DelayFrames
	call LoadScreenTilesFromBuffer1
	pop af
	ld hl, KitCoinsDeclinedText
	bit B_PAD_B, a
	jp nz, .print
	ld a, [wCurrentMenuItem]
	ld e, a ; 0: 50 coins, 1: 500 coins
	; コインケースが ある
	ld b, COIN_CASE_K
	push de
	call IsItemInBag
	pop de
	ld hl, KitCoinsNoCaseText
	jp z, .print
	; コインケースに 入る（9990 / 9500 まいまで）
	ld a, $99
	ldh [hCoins_K], a
	ld a, $90
	ldh [hCoins_K + 1], a
	ld a, e
	and a
	jr z, .gotRoom
	ld a, $95
	ldh [hCoins_K], a
	xor a
	ldh [hCoins_K + 1], a
.gotRoom
	push de
	call HasEnoughCoins
	pop de
	ld hl, KitCoinsCaseFullText
	jp nc, .print
	; お金が ある（1000 / 10000 円）
	push de
	call .setPrice
	call HasEnoughMoney
	pop de
	ld hl, KitCoinsCantAffordText
	jp c, .print
	push de
	call .setPrice
	ld hl, hMoney_K + 2
	ld de, wPlayerMoney_K + 2
	ld c, 3
	predef SubBCDPredef
	pop de
	; コインを もらう
	xor a
	ldh [hUnusedCoinsByte_K], a
	ld a, e
	and a
	ld a, $00
	ld b, $50
	ld hl, KitCoinsThanks50Text
	jr z, .gotCoins
	ld a, $05
	ld b, $00
	ld hl, KitCoinsThanks500Text
.gotCoins
	ldh [hCoins_K], a
	ld a, b
	ldh [hCoins_K + 1], a
	push hl
	ld de, wPlayerCoins_K + 1
	ld hl, hCoins_K + 1
	ld c, 2
	predef AddBCDPredef
	ld a, SFX_PURCHASE_K
	call PlaySoundWaitForCurrent
	ld b, GameCornerDrawCoinBox_BANK
	ld hl, GameCornerDrawCoinBox
	call Bankswitch
	pop hl
.print
	jp PrintText

.setPrice
; hMoney = 1000 (e = 0) / 10000 (e = 1) 円（BCD）
	xor a
	ldh [hMoney_K + 2], a
	ld a, e
	and a
	ld a, $10
	ld b, $00
	jr z, .gotPrice
	xor a
	ld b, $01
.gotPrice
	ldh [hMoney_K + 1], a
	ld a, b
	ldh [hMoney_K], a
	ret

KitCoinsMenuText:
	db   "５０まい"
	next "５００まい@"

KitCoinsAskText:
	text "いらっしゃいませ！"
	line "ロケット　ゲーム　コーナーです"
	para "ゲームよう　コイン　ですか？"
	para "５０まい　１０００円"
	line "５００まい　１００００円　です！"
	para "なんまい　かいますか？"
	done

KitCoinsThanks50Text:
	text "はい！　まいど　あり！"
	line "コイン　５０まい　どうぞ！"
	done

KitCoinsThanks500Text:
	text "はい！　まいど　あり！"
	line "コイン　５００まい　どうぞ！"
	done

KitCoinsDeclinedText:
	text "…　いりませんか！"
	line "それでは　また　どうぞ！"
	done

KitCoinsCantAffordText:
	text "おかね　たりないよ！"
	done

KitCoinsCaseFullText:
	text "おっと…！"
	line "コインケースが　まんたんだ！"
	done

KitCoinsNoCaseText:
	text "あれ？　コインを　いれる"
	line "コインケースが　ないよ！"
	done

; そだてや（緑の 文を 出す call PrintText の かわり）：そだった レベルが 0 なら「まだ」の 文
KitDaycareText::
	ld hl, KitDaycareGrownText
	ld a, [wDayCareNumLevelsGrown_K]
	and a
	jr nz, .print
	ld hl, KitDaycareNotYetText
.print
	jp PrintText

KitDaycareGrownText:
	text "おまえの　@"
	text_ram wNameBuffer
	text_start
	line "ずいぶんと　せいちょうしたぞ"
	para "そうだな　レベルで　いうと"
	line "@"
	text_decimal wDayCareNumLevelsGrown_K, 1, 3
	text "くらい　そだってるな"
	para "いまは　レベル@"
	text_decimal wDayCareMonBoxLevel_K, 1, 3
	text "だ！"
	para "やっぱり　わたしは　てんさいだ！"
	prompt

KitDaycareNotYetText:
	text "なんだ　もう　きたのか"
	line "おまえの　@"
	text_ram wNameBuffer
	text "は…"
	para "いまも　レベル@"
	text_decimal wDayCareMonBoxLevel_K, 1, 3
	text "の　ままだ"
	line "まだ　じかんが　かかるぞ"
	prompt
