; ポケモンセンターの 回復
;  1) 回復した あと（「またの ごりようを おまちしてます！」の あと）、主人公が 下を 向く
;     （A ボタンを 連打しても、もう一度 ジョーイさんに 話しかけない。「やめる」の ときは 今までどおり）。
;  2) 「せってい」に「かいふくの アニメーション」（みる／とばす）を 足す。「とばす」なら 回復の きかいの
;     アニメーション（ボールが 並んで 光る・回復の 音楽）を しない（町の 音楽は そのまま）。
;     値は wOptions（$D2D4）の ビット4（0 = みる・1 = とばす）。前の レポートは 0 なので「みる」。
;     ビット0〜3 は 文字の 速さ（and $0f）、5 は わすれさせる ときの カーソル、6・7 は しあいの ルール・せんとう アニメーション。
;
; 緑の DisplayPokemonCenterDialogue_（01:6FC0 付近〜。8つの 版で 同じ バイト）の
;   01:7016  farcall AnimateHealingMachine（8バイト）＋ 01:701E〜7033 音楽を もどす 所
;   01:7043  jr .done（「またの…」→ jp UpdateSprites）
; を かえる。01:7020〜7033 の あいた 所に 回復した ときの 終わりを 置く。
; 「せってい」は 土台で バンク $35（35:4000〜）に 作り直されて いる（項目 4つ・ラベルの 行 1・5・9・13、
;   えらぶ 行 3・7・11・15、おわり 17）。項目を 5つ（ラベル 1・4・7・10・13、えらぶ 行 3・6・9・12・15、
;   おわり 17）に する。ラベルの 字に だくてんが ないので、前の 項目の えらぶ 行の すぐ 下に 置ける。

DEF wOptions_PH          EQU $d2d4
DEF BIT_SKIP_HEAL_ANIM   EQU 4
DEF wPlayerFacing_PH     EQU $c109 ; 主人公の 向き（0 = 下）
DEF AnimateHealingMachine_PH EQU $4984 ; バンク $1C
DEF PlaySound_PH         EQU $0da2
DEF UpdateSprites_PH     EQU $0e1a
DEF PrintText_PH         EQU $3b59
DEF DelayFrames_PH       EQU $3661
DEF Bankswitch_PH        EQU $3500
DEF PokecenterFarewell_PH EQU $70d1 ; バンク $01

SECTION "ポケセン 回復の アニメ 呼ぶ所", ROMX[$7016], BANK[$01]
	ld b, BANK(KitHealAnim)
	ld hl, KitHealAnim
	call Bankswitch_PH
	jr @ + 2 + ($7034 - $7020) ; 音楽を もどす 所は KitHealAnim で した

; 01:7020〜7033（20バイト）：回復した ときの 終わり
KitHealDone:
	ld hl, PokecenterFarewell_PH
	call PrintText_PH
	xor a ; 下
	ld [wPlayerFacing_PH], a
	jp UpdateSprites_PH

SECTION "ポケセン 回復の あと", ROMX[$7043], BANK[$01]
	jr KitHealDone

SECTION "ポケセン 回復の アニメ", ROMX[$4300], BANK[$35]
KitHealAnim:
	ld a, [wOptions_PH]
	bit BIT_SKIP_HEAL_ANIM, a
	jr nz, .skip
	ld b, $1c
	ld hl, AnimateHealingMachine_PH
	call Bankswitch_PH
	; 元の 01:701E〜7033（音楽を もとに もどす）
	xor a
	ld [$cfae], a ; wAudioFadeOutControl
	ld a, [$c0f0] ; wAudioSavedROMBank
	ld [$c0ef], a ; wAudioROMBank
	ld a, [$d2da] ; wMapMusicSoundID
	ld [$cfb1], a ; wLastMusicSoundID
	ld [$c0ee], a ; wNewSoundID
	jp PlaySound_PH
.skip
	; アニメーションを とばす：音楽は そのまま。少しだけ 間を あける
	ld c, 8
	jp DelayFrames_PH

; ---------------------------------------------------------------- せってい
DEF wTopMenuItemY_PH   EQU $cc24
DEF wTopMenuItemX_PH   EQU $cc25
DEF wCurrentMenuItem_PH EQU $cc26
DEF wLastMenuItem_PH   EQU $cc2a
DEF wOptTextSpeedX     EQU $cd3d
DEF wOptBattleAnimX    EQU $cd3e
DEF wOptBattleStyleX   EQU $cd3f
DEF wOptCancelX        EQU $cd40
DEF wOptForgetX        EQU $cd41
DEF wOptHealAnimX      EQU $cd42 ; 新しい 項目（せっていの 画面の あいだだけ）
DEF hJoy5_PH           EQU $ffb5
DEF PlaceString_PH     EQU $0405
DEF Delay3_PH          EQU $3ce7
DEF OptPlaceCursor     EQU $3aa6 ; 元の 35:4059 と 同じ
DEF JoypadLowSens_PH   EQU $3759
DEF OptCursorX         EQU $3b09 ; 元の 35:40D0 と 同じ
DEF OptCursorY         EQU $3afc ; 元の 35:4107 と 同じ
DEF ROW EQUS "$c3a0 + 20 *"

; ラベルの 場所（行 4・7・10 に つめる）
SECTION "せってい ラベル2", ROMX[$4012 + 1], BANK[$35]
	dw ROW 4 + 1
SECTION "せってい ラベル3", ROMX[$401b + 1], BANK[$35]
	dw ROW 7 + 1
SECTION "せってい ラベル4", ROMX[$4024 + 1], BANK[$35]
	dw ROW 10 + 1

SECTION "せってい 入口", ROMX[$4036], BANK[$35]
	jp KitOptMain

SECTION "せってい 新しい 処理", ROMX[$4400], BANK[$35]
KitOptMain:
	ld hl, ROW 13 + 1
	ld de, KitOptHealText
	call PlaceString_PH
	xor a
	ld [wCurrentMenuItem_PH], a
	ld [wLastMenuItem_PH], a
	inc a
	ld [$d2d7], a
	ld [wOptCancelX], a
	ld a, 3
	ld [wTopMenuItemY_PH], a
	call KitOptLoad
	ld a, [wOptTextSpeedX]
	ld [wTopMenuItemX_PH], a
	ld a, 1
	ldh [$ffba], a
	call Delay3_PH
.loop
	call OptPlaceCursor
	call KitOptSave
.joy
	call JoypadLowSens_PH
	ldh a, [hJoy5_PH]
	ld b, a
	and $fb
	jr z, .joy
	bit 1, b ; B
	jr nz, .exit
	bit 3, b ; START
	jr nz, .exit
	bit 0, b ; A
	jr z, .dir
	ld a, [wTopMenuItemY_PH]
	cp $11
	jr nz, .loop
.exit
	ld a, $90
	jp PlaySound_PH
.dir
	ld a, [wTopMenuItemY_PH]
	bit 7, b
	jr nz, .down
	bit 6, b
	jr nz, .up
	cp $11
	jr z, .loop
	cp 3
	jr z, .speed
	ld hl, wOptBattleAnimX
	cp 6
	jr z, .toggle
	ld hl, wOptBattleStyleX
	cp 9
	jr z, .toggle
	ld hl, wOptForgetX
	cp 12
	jr z, .toggle
	ld hl, wOptHealAnimX
.toggle
	ld a, [hl]
	xor $0b
	ld [hl], a
	jr .setx
.speed
	ld a, [wOptTextSpeedX]
	bit 5, b
	jr nz, .left
	cp $0e
	jr z, .store
	add 4
	cp 5
	jr nz, .store
	inc a
	jr .store
.left
	cp 1
	jr z, .store
	sub 4
	cp 2
	jr nz, .store
	dec a
.store
	ld [wOptTextSpeedX], a
.setx
	ld [wTopMenuItemX_PH], a
	call OptCursorX
	jp .loop
.down
	ld c, 1
	jr .move
.up
	ld c, KitOptRows.end - KitOptRows - 1
.move
	ld hl, KitOptRows
	ld b, 0
.find
	cp [hl]
	jr z, .found
	inc hl
	inc b
	jr .find
.found
	ld a, b
	add c
	cp KitOptRows.end - KitOptRows
	jr c, .ok
	sub KitOptRows.end - KitOptRows
.ok
	ld c, a
	ld b, 0
	ld hl, KitOptRows
	add hl, bc
	ld a, [hl]
	ld [wTopMenuItemY_PH], a
	ld hl, KitOptXPtrs
	add hl, bc
	add hl, bc
	ld a, [hli]
	ld h, [hl]
	ld l, a
	ld a, [hl]
	ld [wTopMenuItemX_PH], a
	call OptCursorY
	jp .loop

KitOptRows:
	db 3, 6, 9, 12, 15, $11
.end
KitOptXPtrs:
	dw wOptTextSpeedX, wOptBattleAnimX, wOptBattleStyleX, wOptForgetX, wOptHealAnimX, wOptCancelX

; 画面の カーソルの 場所 → wOptions（元の 35:411C に 新しい ビットを 足した もの）
KitOptSave:
	ld a, [wOptTextSpeedX]
	ld d, 0
	cp 1
	jr z, .speed
	ld d, 1
	cp 6
	jr z, .speed
	ld d, 3
	cp $0a
	jr z, .speed
	ld d, 5
.speed
	ld a, [wOptBattleAnimX]
	dec a
	jr z, .anim
	set 7, d
.anim
	ld a, [wOptBattleStyleX]
	dec a
	jr z, .style
	set 6, d
.style
	ld a, [wOptForgetX]
	dec a
	jr z, .forget
	set 5, d
.forget
	ld a, [wOptHealAnimX]
	dec a
	jr z, .heal
	set 4, d
.heal
	ld a, d
	ld [wOptions_PH], a
	ret

; wOptions → 画面の カーソルの 場所と ▷（元の 35:4150 に 新しい 行を 足した もの）
KitOptLoad:
	ld a, [wOptions_PH]
	and $0f
	ld b, 1
	jr z, .t
	ld b, 6
	cp 1
	jr z, .t
	ld b, $0e
	cp 5
	jr z, .t
	ld b, $0a
.t
	ld a, b
	ld [wOptTextSpeedX], a
	ld hl, ROW 3
	call .mark
	ld c, 7
	call .bit
	ld [wOptBattleAnimX], a
	ld hl, ROW 6
	call .mark
	ld c, 6
	call .bit
	ld [wOptBattleStyleX], a
	ld hl, ROW 9
	call .mark
	ld c, 5
	call .bit
	ld [wOptForgetX], a
	ld hl, ROW 12
	call .mark
	ld c, 4
	call .bit
	ld [wOptHealAnimX], a
	ld hl, ROW 15
	call .mark
	ld hl, ROW 17
	ld a, 1
.mark
	ld e, a
	ld d, 0
	add hl, de
	ld [hl], $ec ; ▷
	ret
.bit
	ld a, [wOptions_PH]
.rot
	rrca
	dec c
	jr nz, .rot
	rrca
	ld a, 1
	ret nc
	ld a, $0a
	ret

KitOptHealText:
	db "かいふくの アニメーション<NEXT>"
	db " みる", "       ", "とばす@" ; みる＝2〜3 けため・とばす＝11 けため（▷ は 1・10）
