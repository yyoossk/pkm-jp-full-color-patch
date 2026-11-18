; カントーの ジムの 案内の 人の わざ教え（phases/phase_zzzz_tutor.py が 組む）
; wScriptVar ＝ わざの 番号（0〜5）で KT_Offer へ。教える 処理は キットの MoveTutor_Teach と 同じ。

KT_Offer:
	callasm KT_SetMove
	writetext KT_OfferText
	yesorno
	iffalse .no
	writetext KT_WhoText
	promptbutton
.choose
	callasm KT_Teach
	ifequal 0, .no
	ifequal 2, .cannot
	ifequal 3, .again
	writetext KT_DoneText
	waitbutton
	closetext
	end
.cannot
	writetext KT_CannotText
	promptbutton
.again
	writetext KT_WhoText
	promptbutton
	sjump .choose
.no
	writetext KT_LaterText
	waitbutton
	closetext
	end

; wScriptVar（0〜5）→ wPutativeTMHMMove と わざの 名前（wStringBuffer2）
KT_SetMove:
	ld a, [wScriptVar]
	ld [wKTWhich], a
	ld c, a
	ld b, 0
	ld hl, KT_Moves
	add hl, bc
	ld a, [hl]
	ld [wPutativeTMHMMove], a
	ld [wNamedObjectIndex], a
	call J_GetMoveName
	jp J_CopyName1

KT_Moves:
	db BIDE, BUBBLEBEAM, THUNDERBOLT, MEGA_DRAIN, PSYWAVE, FISSURE

; 手もちを えらんで おしえる。wScriptVar：0 = やめた、1 = おぼえた、2 = おぼえられない、3 = もう おぼえている・やめた
KT_Teach:
	ld a, [wPutativeTMHMMove]
	push af
	ld a, KT_SELECTMON_BANK
	ld hl, KT_SELECTMON
	rst $08
	pop bc
	ld a, b
	ld [wPutativeTMHMMove], a
	ld a, 0
	jp c, .set
	ld a, [wCurPartyMon]
	ld hl, wPartyMonNicknames
	call J_GetNickname
	ld a, [wCurPartySpecies]
	cp EGG
	ld a, 2
	jr z, .set
	ld a, [wKTWhich]
	swap a
	add a                            ; × 32
	ld e, a
	ld d, 0
	ld hl, KT_Compat
	add hl, de
	ld a, [wCurPartySpecies]
	dec a
	ld c, a
	srl a
	srl a
	srl a
	ld e, a
	ld d, 0
	add hl, de
	ld a, c
	and 7
	ld b, a
	ld a, [hl]
	inc b
.shift
	dec b
	jr z, .bit
	rrca
	jr .shift
.bit
	and 1
	ld a, 2
	jr z, .set
	ld a, KT_KNOWSMOVE_BANK
	ld hl, KT_KNOWSMOVE
	rst $08
	ld a, 3
	jr c, .set
	call J_FadeToMenu
	call J_ClearBGPalettes
	call J_ClearScreen
	call J_DelayFrame
	ld b, SCGB_MOVE_LIST
	call J_GetSGBLayout
	ld a, KT_LEARNMOVE_BANK
	ld hl, KT_LEARNMOVE
	rst $08
	push bc
	call J_CloseSubmenu
	pop bc
	ld a, b
	and a
	ld a, 3
	jr z, .set
	ld a, 1
.set
	ld [wScriptVar], a
	ret

KT_WaitText:
	db $00, "おーい！", $4f
	db "ちょっと　まってくれ！", $57
KT_IntroText:
	db $00, "ジムリーダーに　かった", $4f
	db "きみに　とっておきの", $55
	db "わざを　おしえて　あげよう！", $57
KT_OfferText:
	db $01
	dw wStringBuffer2
	db $00, "を", $4f
	db "おしえて　あげようか？", $57
KT_WhoText:
	db $00, "どの　ポケモンに", $4f
	db "おしえようか？", $57
KT_CannotText:
	db $00, "その　ポケモンには", $4f
	db "おしえられない　みたいだ", $57
KT_DoneText:
	db $00, "また　おぼえさせたく　なったら", $4f
	db "いつでも　はなしかけてくれ！", $57
KT_LaterText:
	db $00, "そうか！", $4f
	db "おぼえさせたく　なったら", $55
	db "いつでも　はなしかけてくれ！", $57
KT_CeladonGuideText:
	db $00, "おーす！", $4f
	db "みらいの　チャンピオン！", $51
	db "ここの　リーダー　エリカは", $4f
	db "くさタイプの　つかいてだ！", $51
	db "ほのおや　ひこうの　わざで", $4f
	db "せめて　いけ！", $57
