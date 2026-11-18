; 第66弾（金）：カントーの ジムの 案内の 人が、ジムリーダーに 勝った あと 赤の わざマシンの わざを 教える。
; クリスタルの MoveTutor（engine/events/move_tutor.asm）を 金に あわせた もの。
; スクリプトから callasm TUT_BANK, TutorN で よぶ。けっか：wScriptVar 0＝おぼえた／$FF＝やめた
; TUT_ADDR は gold_tutor.py から -D で わたす。compat.inc（わざの 表と おぼえられる ポケモンの ビットの 表）も そこで 作る。

DEF wScriptVar         EQU $d165
DEF wCurPartySpecies   EQU $cffe
DEF wCurPartyMon       EQU $cfff
DEF wNamedObjectIndex  EQU $d143
DEF wPutativeTMHMMove  EQU $d13f
DEF wPartyMonNicknames EQU $db34

DEF FadeToMenu         EQU $2bca
DEF CloseSubmenu       EQU $2bdd
DEF ClearBGPalettes    EQU $33ab
DEF ClearScreen        EQU $0eb4
DEF DelayFrame         EQU $032e
DEF GetMoveName        EQU $36a1
DEF CopyName1          EQU $3137
DEF LoadMenuHeader     EQU $1b59
DEF ExitMenu           EQU $1a51
DEF GetNickname        EQU $3a29
DEF PlaySFX            EQU $3d45
DEF FarPrintText       EQU $3366
DEF Predef             EQU $2e05
DEF SFX_WRONG          EQU $19
DEF PREDEF_LEARNMOVE   EQU $00
; 0B:592A ChooseMonToLearnTMHM・0B:5A2E TMHMNotCompatibleText・03:7F70 KnowsMove・01:7CEC ChangeHappiness

SECTION "tutor", ROMX[TUT_ADDR], BANK[1]
Tutor:
; wScriptVar ＝ 教える わざ（スクリプトの setval）
	call FadeToMenu
	call ClearBGPalettes
	call ClearScreen
	call DelayFrame
	ld a, [wScriptVar]
	ld [wNamedObjectIndex], a
	ld [wPutativeTMHMMove], a
	call GetMoveName
	call CopyName1
.loop
	ld a, $0b
	ld hl, $592a
	rst $08                          ; ChooseMonToLearnTMHM
	jr c, .cancel
	call CheckCanLearn
	jr nc, .loop
	xor a
	ld [wScriptVar], a
	jr .quit
.cancel
	ld a, -1
	ld [wScriptVar], a
.quit
	call CloseSubmenu
	ret

CheckCanLearn:
	ld hl, MenuHeader
	call LoadMenuHeader
	ld a, $0e
	call Predef                      ; CanLearnTMHMMove（CanLearnHook）
	push bc
	ld a, [wCurPartyMon]
	ld hl, wPartyMonNicknames
	call GetNickname
	pop bc
	ld a, c
	and a
	jr nz, .can_learn
	push de
	ld de, SFX_WRONG
	call PlaySFX
	pop de
	ld a, $0b
	ld hl, $5a2e
	call FarPrintText                ; TMHMNotCompatibleText
	jr .didnt_learn
.can_learn
	ld a, $03
	ld hl, $7f70
	rst $08                          ; KnowsMove
	jr c, .didnt_learn
	ld a, PREDEF_LEARNMOVE
	call Predef
	ld a, b
	and a
	jr z, .didnt_learn
	ld c, 5                          ; HAPPINESS_LEARNMOVE
	ld a, $01
	ld hl, $7cec
	rst $08                          ; ChangeHappiness
	jr .learned
.didnt_learn
	call ExitMenu
	and a
	ret
.learned
	call ExitMenu
	scf
	ret

CanLearnHook:
; predef CanLearnTMHMMove（02:4B5B の 表の $0E）の かわり。教え技の わざで、しかも wScriptVar が その わざ
; （わざを 教える 人から 来た とき）だけ 赤の 表で 答える。ほかは もとの 04:59BF。
	ld a, [wPutativeTMHMMove]
	ld b, a
	ld a, [wScriptVar]
	cp b
	jr nz, .orig
	ld hl, TutorMoves
	ld c, 0
.find
	ld a, [hli]
	and a
	jr z, .orig
	cp b
	jr z, .found
	inc c
	jr .find
.found
	ld a, c
	swap a                           ; ×16
	ld l, a
	ld h, 0
	add hl, hl                       ; ×32
	ld de, TutorCompat
	add hl, de
	ld a, [wCurPartySpecies]
	dec a
	ld b, a
	srl a
	srl a
	srl a
	ld e, a
	ld d, 0
	add hl, de
	ld a, b
	and 7
	ld b, a
	ld a, [hl]
	inc b
.shift
	dec b
	jr z, .got
	rrca
	jr .shift
.got
	and 1
	ld c, a
	ret
.orig
	ld a, $04
	ld hl, $59bf
	rst $08
	ret

MenuHeader:
	db $40                           ; MENU_BACKUP_TILES
	db 12, 0, 17, 19                 ; menu_coords 0,12,19,17
	dw 0
	db 1

INCLUDE "compat.inc"
