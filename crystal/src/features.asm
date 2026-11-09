; ポケットモンスター クリスタル（日本版）追加機能
;  1. Bボタンダッシュ（ランニングシューズ。なみのりも速く）
;  2. メニューに「パソコン」
;  3. 手持ちのポケモンを選ぶと「なまえ」（ニックネーム変更）
;  4. 手持ちのポケモンを選ぶと「わすれる」（ひでんわざも忘れられる）
;  ※ ひでんマシンを全ポケモンに… は build.py で基本データを書きかえる
;  ※ 60fps は fps60.asm（別の版）

INCLUDE "src/crystal_jp.inc"
INCLUDE "src/charmap_jp.inc"

DEF BASEROM EQUS "\"base.gbc\""

;=====================================================================
; 1. Bボタンダッシュ
;=====================================================================
SECTION "Run walk", ROMX[DoPlayerMovement_walk], BANK[BANK_PLAYERMOVE]
	jp RunOrWalkStep          ; ld a, STEP_WALK / call .DoStep / scf / ret

SECTION "Run surf", ROMX[DoPlayerMovement_surf], BANK[BANK_PLAYERMOVE]
	jp RunOrWalkStep

SECTION "Run code", ROMX[$5f40], BANK[BANK_PLAYERMOVE]
RunOrWalkStep:
	ldh a, [hJoyDown]
	and B_BUTTON
	ld a, STEP_WALK
	jr z, .go
	ld a, STEP_BIKE           ; B を押している間は自転車と同じ速さ
.go
	call DoPlayerMovement_DoStep
	scf
	ret

;=====================================================================
; 2. スタートメニューに「パソコン」
;    ならび：ずかん・ポケモン・リュック・ポケギア・パソコン・（主人公の名前）・レポート・せってい
;    （ポケギアの あと、主人公の名前の 前に 入れる。とじる は 出さない。B／START で閉じられる。
;      むしとり大会中は パソコンは 出さず、さいごに とじる）
;=====================================================================
SECTION "StartMenu items ptr", ROMX[StartMenu_MenuDataItemsPtr], BANK[BANK_STARTMENU]
	dw StartMenuItemsNew

SECTION "StartMenu pc/status", ROMX[StartMenu_StatusAppend], BANK[BANK_STARTMENU]
	call StartMenu_PCAndStatus  ; 5バイト（ld a,3 / call .AppendMenuList）
	nop
	nop

SECTION "StartMenu exit/pc", ROMX[StartMenu_ExitAppend], BANK[BANK_STARTMENU]
	call StartMenu_ExitInContest ; 5バイト（ld a,6 / call .AppendMenuList）
	nop
	nop

SECTION "StartMenu new", ROMX[$7f10], BANK[BANK_STARTMENU]
StartMenuItemsNew:
	INCBIN BASEROM, BANK_STARTMENU * $4000 + StartMenu_Items - $4000, 9 * 6
	dw StartMenu_PC, .PCString, .PCDesc   ; STARTMENUITEM_PC = 9
.PCString:
	db "パソコン@"
.PCDesc:
	db "どこでも<NEXT>パソコンを　つかう@"

StartMenu_PCAndStatus:        ; パソコン（むしとり大会中は なし）→ 主人公の名前
	ld hl, wStatusFlags2
	bit STATUSFLAGS2_BUG_CONTEST_TIMER_F, [hl]
	jr nz, .status
	ld a, STARTMENUITEM_PC
	call StartMenu_AppendMenuList
.status
	ld a, STARTMENUITEM_STATUS
	jp StartMenu_AppendMenuList

StartMenu_ExitInContest:      ; とじる は むしとり大会中だけ
	ld hl, wStatusFlags2
	bit STATUSFLAGS2_BUG_CONTEST_TIMER_F, [hl]
	ret z
	ld a, STARTMENUITEM_EXIT
	jp StartMenu_AppendMenuList

StartMenu_PC:
	ld a, PCScript_Bank
	ld hl, PCScript
	call FarQueueScript
	ld a, 4                   ; メニューを閉じてスクリプトを動かす
	ret

MonActionsNew:
	INCBIN BASEROM, BANK_MONMENU * $4000 + PokemonActionSubmenu_Actions - $4000, 20 * 3
	db MONMENUITEM_NAME
	dw MonMenu_Name
	db MONMENUITEM_FORGET
	dw MonMenu_Forget
	db -1

MonMenu_Name:
	farcall_jp MonMenu_NameBody
	ld a, c                   ; 戻り値は c で受け取る
	ret

MonMenu_Forget:
	farcall_jp MonMenu_ForgetBody
	ld a, c
	ret


;=====================================================================
; 3・4. 手持ちのメニューに「なまえ」「わすれる」
;=====================================================================
; --- 項目のリスト（バンク9）
SECTION "MonMenu ptr1", ROMX[GetMonMenuString_Ptr], BANK[BANK_MONSUBMENU]
	dw MonMenuOptionsNew + 1
SECTION "MonMenu ptr2", ROMX[GetMonMenuString_StrPtr], BANK[BANK_MONSUBMENU]
	dw MonMenuOptionStringsNew
SECTION "MonMenu ptr3", ROMX[IsFieldMove_Ptr], BANK[BANK_MONSUBMENU]
	dw MonMenuOptionsNew

SECTION "MonMenu items", ROMX[GetMonSubmenuItems_Cancel], BANK[BANK_MONSUBMENU]
	call AddExtraMonMenuItems
	jr GetMonSubmenuItems_Term

SECTION "MonMenu header", ROMX[MonSubmenu_LoadHeader], BANK[BANK_MONSUBMENU]
	call MonSubmenu_LoadHeaderNew
	nop
	nop
	nop
SECTION "MonMenu select", ROMX[MonMenuLoop_Select], BANK[BANK_MONSUBMENU]
	jp MonMenuLoop_SelectNew
SECTION "MonMenu top", ROMX[MonSubmenu_GetTopCoordCall], BANK[BANK_MONSUBMENU]
	call MonSubmenu_GetTopCoordNew
SECTION "MonMenu populate", ROMX[MonSubmenu_PopulateCall], BANK[BANK_MONSUBMENU]
	call PopulateMonMenuNew
SECTION "MonMenu cursor", ROMX[MonMenuLoop_InitCursorCall], BANK[BANK_MONSUBMENU]
	call InitMonMenuCursorNew

SECTION "MonMenu new", ROMX[$7de0], BANK[BANK_MONSUBMENU]
MonMenuOptionStringsNew:
	INCBIN BASEROM, BANK_MONSUBMENU * $4000 + MonMenuOptionStrings - $4000, MonMenuOptions - MonMenuOptionStrings
	db "なまえ@"     ; 8
	db "わすれる@"   ; 9

MonMenuOptionsNew:
	INCBIN BASEROM, BANK_MONSUBMENU * $4000 + MonMenuOptions - $4000, 21 * 3
	db MONMENU_MENUOPTION, MONMENUITEM_NAME,   8
	db MONMENU_MENUOPTION, MONMENUITEM_FORGET, 9
	db -1

AddExtraMonMenuItems:
	ld a, [wLinkMode]
	and a
	jr nz, .cancel
	ld a, MONMENUITEM_NAME
	call AddMonMenuItem
	ld a, MONMENUITEM_FORGET
	call AddMonMenuItem
; 「もどる」を入れると 9つ以上で奇数になるときは入れない（横2列で 空いた所ができないように。B で もどれる）
	ld a, [wMonSubmenuCount]
	cp MONMENU_WIDE - 1
	jr c, .cancel
	bit 0, a
	ret z
.cancel
	ld a, MONMENUITEM_CANCEL
	jp AddMonMenuItem

; 9項目以上になったら、横に2列で並べる
; （日本版は濁点が上の行に出るので1行ずつには詰められない）
DEF MONMENU_WIDE EQU 9
DEF MONMENU_WIDE_LEFT EQU 4
DEF MONMENU_COL_WIDTH EQU 7

MonSubmenu_LoadHeaderNew:
	ld hl, MonSubmenu_Header
	ld a, [wMonSubmenuCount]
	cp MONMENU_WIDE
	jr c, .go
	ld hl, MonSubmenuWideHeader
.go
	jp LoadMenuHeader

MonSubmenuWideHeader:
	db $40 ; MENU_BACKUP_TILES
	db 0, MONMENU_WIDE_LEFT, 17, 19
	dw 0
	db 1

; 2列のときの行数
GetMonMenuWideRows:
	ld a, [wMonSubmenuCount]
	inc a
	srl a
	ret

MonSubmenu_GetTopCoordNew:
	ld a, [wMonSubmenuCount]
	cp MONMENU_WIDE
	jp c, MonSubmenu_GetTopCoord
	call GetMonMenuWideRows
	add a
	ld b, a
	ld a, [wMenuBorderBottomCoord]
	sub b
	dec a
	ld [wMenuBorderTopCoord], a
	jp MenuBox

PopulateMonMenuNew:
	ld a, [wMonSubmenuCount]
	cp MONMENU_WIDE
	jp c, PopulateMonMenu
	call MenuBoxCoord2Tile
	ld bc, 2 * 20 + 2
	add hl, bc
	ld de, wMonSubmenuItems
.loop
	ld a, [de]
	inc de
	cp -1
	ret z
	push de
	push hl
	call GetMonMenuString
	pop hl
	push hl
	call PlaceString
	pop hl
	pop de
; 左の列 → 右の列、右の列 → 次の行の左
	ld a, e
	sub LOW(wMonSubmenuItems)
	bit 0, a
	ld bc, MONMENU_COL_WIDTH
	jr nz, .next
	ld bc, 2 * 20 - MONMENU_COL_WIDTH
.next
	add hl, bc
	jr .loop

InitMonMenuCursorNew:
	call InitVerticalMenuCursor
	ld a, [wMonSubmenuCount]
	cp MONMENU_WIDE
	ret c
	call GetMonMenuWideRows
	ld [w2DMenuNumRows], a
	ld a, 2
	ld [w2DMenuNumCols], a
	ld a, $20 | MONMENU_COL_WIDTH
	ld [w2DMenuCursorOffsets], a
	ret

; A を押したとき：何番目の項目か
MonMenuLoop_SelectNew:
	ld a, [wMenuCursorY]
	dec a
	ld c, a
	ld a, [wMonSubmenuCount]
	cp MONMENU_WIDE
	jr c, .got
	sla c
	ld a, [wMenuCursorX]
	dec a
	add c
	ld c, a
	ld a, [wMonSubmenuCount]
	dec a
	cp c
	jp c, MonMenuLoop_Joypad   ; 空いている所 → 何もしない
.got
	ld b, 0
	ld hl, wMonSubmenuItems
	add hl, bc
	ld a, [hl]
	ret

; --- 選んだときの動き（バンク4の表をつくり直す）
SECTION "MonActions ptr", ROMX[PokemonActionSubmenu_ActionsPtr], BANK[BANK_MONMENU]
	dw MonActionsNew



;=====================================================================
; 新しいバンク
;=====================================================================
SECTION "New bank", ROMX[$4000], BANK[BANK_NEW]

; --- なまえ（ニックネーム変更）
MonMenu_NameBody:
	call LoadStandardMenuHeader
	xor a
	ld [wMonType], a
	ld a, [wCurPartySpecies]
	ld [wNamedObjectIndex], a
	ld [wCurSpecies], a
	call GetBaseData
	ld b, NAME_MON
	ld de, wStringBuffer2
	ld a, BANK_MONMENU
	ld hl, NamingScreen
	rst $08
; 何も入れなかった（空白だけ）ときは今の名前のまま
	ld hl, wStringBuffer2
	ld c, MON_NAME_LENGTH - 1
.check
	ld a, [hli]
	cp $50
	jr z, .done
	cp $7f
	jr nz, .changed
	dec c
	jr nz, .check
	jr .done
.changed
	ld a, [wCurPartyMon]
	ld hl, wPartyMonNicknames
	ld bc, MON_NAME_LENGTH
	call AddNTimes
	ld d, h
	ld e, l
	ld hl, wStringBuffer2
	ld bc, MON_NAME_LENGTH
	call CopyBytes
.done
	call Call_ExitMenu
	ld c, 0                   ; 手持ちの画面を作り直す
	ret

; --- わすれる（ひでんわざも忘れられる）
MonMenu_ForgetBody:
	call GetMonMovesPtr
	inc hl
	ld a, [hl]
	and a
	jr nz, .choose
	ld hl, OnlyOneMoveText
	call MenuTextboxBackup
	ld c, 3
	ret

.choose
	ld a, BANK_MONMENU
	ld hl, ChooseMoveToDelete
	rst $08
	jr c, .cancel
	ld a, [wMenuCursorY]
	push af
; わざの名前 → wStringBuffer2、ニックネーム → wStringBuffer1
	call GetMonMovesPtr
	pop af
	push af
	dec a
	ld c, a
	ld b, 0
	add hl, bc
	ld a, [hl]
	ld [wNamedObjectIndex], a
	call GetMoveName
	call CopyName1
	call RedrawPartyMenu
	call GetCurNickname        ; 手持ちの画面を描くと buffer1 が変わるので後で
	ld hl, ConfirmForgetText
	call MenuTextbox
	call YesNoBox
	push af
	call ExitMenu
	pop af
	jr c, .no
	pop af
	call DeleteMove
	ld de, SFX_MOVE_DELETED
	call WaitPlaySFX
	ld hl, ForgotMoveText
	call MenuTextboxBackup
	ld c, 3
	ret

.no
	pop af
	ld c, 3
	ret

.cancel
	ld c, 0
	ret

GetMonMovesPtr:
	ld a, [wCurPartyMon]
	ld hl, wPartyMon1Moves
	ld bc, PARTYMON_STRUCT_LENGTH
	jp AddNTimes

; a = 何番目のわざか（1-4）
DeleteMove:
	ld e, a
	push de
	call GetMonMovesPtr
	pop de
	push de
	call .shift
	pop de
	ld a, [wCurPartyMon]
	ld hl, wPartyMon1PP
	ld bc, PARTYMON_STRUCT_LENGTH
	call AddNTimes
.shift
	ld a, e
	dec a
	ld c, a
	ld b, 0
	add hl, bc
	ld a, e
.loop
	cp NUM_MOVES
	jr z, .last
	inc hl
	ld b, [hl]
	dec hl
	ld [hl], b
	inc hl
	inc a
	jr .loop
.last
	ld [hl], 0
	ret

RedrawPartyMenu:
	ld a, BANK_PARTYMENU
	ld hl, LoadPartyMenuGFX
	rst $08
	ld a, BANK_PARTYMENU
	ld hl, InitPartyMenuWithCancel
	rst $08
	ld a, BANK_PARTYMENU
	ld hl, InitPartyMenuGFX
	rst $08
	ld a, BANK_PARTYMENU
	ld hl, WritePartyMenuTilemap
	rst $08
	ld a, BANK_PARTYMENU
	ld hl, PlacePartyMenuText
	rst $08
	call WaitBGMap
	jp SetDefaultBGPAndOBP

OnlyOneMoveText:
	db 0, "わざを　ひとつしか<LINE>おぼえていない！<PROMPT>"

ConfirmForgetText:
	db 1
	dw wStringBuffer1
	db 0, "の<LINE>@"
	db 1
	dw wStringBuffer2
	db 0, "を　わすれさせますか？<DONE>"

ForgotMoveText:
	db 1
	dw wStringBuffer1
	db 0, "は　@"
	db 1
	dw wStringBuffer2
	db 0, "を<LINE>きれいに　わすれた！<PROMPT>"
