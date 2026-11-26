; ポケモンセンター（赤のキット「ポケモンセンターの回復」から）：
;  1) 回復したあと（「またの ごりようを おまちしてます！」のあと）、主人公が下を向く
;     （A ボタンを連打しても、もう一度話しかけない）。「やめる」のときは今までどおり。
;  2) 「せってい」の「かいふくの アニメーション」が「とばす」なら、回復のきかいのアニメーション（と音楽の切りかえ）をしない。
;     （wOptions のビット4。0 = みる・1 = とばす。前のレポートは 0 なので「みる」）
;
; 青のジョーイさんの処理（01:7056〜。赤は 01:6EE1〜で、青は +$172）の
;   01:708F  farcall AnimateHealingMachine（1C:4975。8バイト）＋ 音楽をもどす所（01:7097〜70AC）
;   01:70BC  jr .done（01:70C1：「またの…」→ jp UpdateSprites）
; をかえる。01:7099〜70AC のあいた所に、回復したときの終わりを置く。どの版も同じ番地。

IF HAS_HEAL_OPT

DEF wOptions EQU $D2D4
DEF BIT_SKIP_HEAL_ANIM EQU 4
DEF wSpritePlayerFacing EQU $C109 ; 主人公の向き（0 = 下）
DEF AnimateHealingMachine EQU $4975 ; バンク $1C
DEF UpdateSprites EQU $23BD
DEF PokemonCenterFarewellText EQU $714A ; バンク $01

SECTION "ポケモンセンター：回復のアニメーション", ROMX[$708F], BANK[$01]
	ld b, BANK(KitHealAnim)
	ld hl, KitHealAnim
	call Bankswitch
	jr KitHealAfterMusic       ; 音楽をもどす所は KitHealAnim でした

; 01:7099〜70AC（20バイト）：回復したときの終わり
KitHealDone:
	ld hl, PokemonCenterFarewellText
	call PrintText
	xor a ; 下
	ld [wSpritePlayerFacing], a
	jp UpdateSprites
	ds $70AD - @, 0
KitHealAfterMusic:
	assert @ == $70AD

SECTION "ポケモンセンター：回復のあと", ROMX[$70BC], BANK[$01]
	jr KitHealDone

FreeBankA
KitHealAnim:
	ld a, [wOptions]
	bit BIT_SKIP_HEAL_ANIM, a
	jr nz, .skip
	ld b, $1C
	ld hl, AnimateHealingMachine
	call Bankswitch
	; 元の 01:7097〜70AC（音楽をもとにもどす）
	xor a
	ld [$CFAE], a ; wAudioFadeOutControl
	ld a, [$C0F0] ; wAudioSavedROMBank
	ld [$C0EF], a ; wAudioROMBank
	ld a, [$D2DA] ; wMapMusicSoundID
	ld [$CFB1], a ; wLastMusicSoundID
	ld [$C0EE], a ; wNewSoundID
	jp PlaySound
.skip
	; アニメーションをとばす：音楽はそのまま。少しだけ間をあける
	ld c, 8
	jp DelayFrames

ENDC
