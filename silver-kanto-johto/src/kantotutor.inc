; 赤の わざマシンの わざを 教える（phases/phase_zzzz_tutor.py が 組む）
; クリスタルの MoveTutor・CheckCanLearnMoveTutorMove（engine/events/move_tutor.asm）を 銀 日本版へ 移した もの。
; callasm KT_MoveTutor：wScriptVar ＝ わざ番号。教えたら wScriptVar ＝ 0、やめたら $FF。

DEF KT_PREDEF_LEARNMOVE EQU $00
DEF KT_PREDEF_CANLEARN  EQU $0e
DEF KT_ChooseMonToLearnTMHM_NoRefresh EQU J_ChooseMonToLearnTMHM + 15   ; ClearBGPalettes の あと

KT_MoveTutor:
	call J_FadeToMenu
	call J_ClearBGPalettes
	call J_ClearScreen
	call J_DelayFrame
	ld b, SCGB_PACKPALS
	call J_GetSGBLayout
	xor a
	ld [wItemAttributeValue], a
	ld a, [wScriptVar]
	ld [wNamedObjectIndex], a
	ld [wPutativeTMHMMove], a
	call J_GetMoveName
	call J_CopyName1
	ld a, JB_ChooseMonToLearnTMHM
	ld hl, J_ChooseMonToLearnTMHM
	rst $08
	jr c, .cancel
	jr .enter_loop
.loop
	ld a, JB_ChooseMonToLearnTMHM
	ld hl, KT_ChooseMonToLearnTMHM_NoRefresh
	rst $08
	jr c, .cancel
.enter_loop
	call KT_CheckCanLearn
	jr nc, .loop
	xor a
	ld [wScriptVar], a
	jr .quit
.cancel
	ld a, -1
	ld [wScriptVar], a
.quit
	jp J_CloseSubmenu

KT_CheckCanLearn:
	ld hl, .MenuHeader
	call J_LoadMenuHeader
	ld a, KT_PREDEF_CANLEARN
	call J_Predef
	push bc
	ld a, [wCurPartyMon]
	ld hl, wPartyMonNicknames
	call J_GetNickname
	pop bc
	ld a, c
	and a
	jr nz, .can_learn
	push de
	ld de, SFX_WRONG
	call J_PlaySFX
	pop de
	ld hl, KT_NotCompatibleText
	call J_PrintText
	jr .didnt_learn
.can_learn
	ld a, JB_KnowsMove
	ld hl, J_KnowsMove
	rst $08
	jr c, .didnt_learn
	ld a, KT_PREDEF_LEARNMOVE
	call J_Predef
	ld a, b
	and a
	jr z, .didnt_learn
	ld c, HAPPINESS_LEARNMOVE
	ld a, JB_ChangeHappiness
	ld hl, J_ChangeHappiness
	rst $08
	jr .learned
.didnt_learn
	call J_ExitMenu
	and a
	ret
.learned
	call J_ExitMenu
	scf
	ret
.MenuHeader:
	db MENU_BACKUP_TILES
	menu_coords 0, 12, SCREEN_WIDTH - 1, SCREEN_HEIGHT - 1
	dw 0
	db 1

KT_NotCompatibleText:                    ; <名前>は <わざ>を おぼえられない！
	db $01
	dw wStringBuffer1
	db $00, "は　", $50
	db $01
	dw wStringBuffer2
	db $00, "を", $4f
	db "おぼえることが　できない！", $58

; predef CanLearnTMHMMove の 代わり：wScriptVar と わざが 同じ（わざを 教える 人から 来た）ときだけ 赤の 表で 答える
KT_Wrap:
	push de
	ld a, [wPutativeTMHMMove]
	ld d, a
	ld hl, KT_RedTable
.l1
	ld a, [hli]
	and a
	jr z, .orig
	cp d
	jr z, .found
	inc hl
	inc hl
	jr .l1
.found
	ld a, [wScriptVar]
	cp d
	jr nz, .orig
	ld a, [hli]
	ld h, [hl]
	ld l, a
	ld a, [wCurPartySpecies]
	ld d, a
.l2
	ld a, [hli]
	cp $ff
	jr z, .no
	cp d
	jr nz, .l2
	ld c, 1
	pop de
	ret
.no
	ld c, 0
	pop de
	ret
.orig
	pop de
	ld a, JB_CanLearnTMHMMove
	ld hl, J_CanLearnTMHMMove
	rst $08
	ret
