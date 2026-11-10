; ポケットモンスター 金・銀（日本版）追加機能（クリスタル追加機能キットから移植）
;  1. Bボタンダッシュ（ランニングシューズ。なみのりも速く）
;  2. メニューに「パソコン」（ならび：ずかん・ポケモン・リュック・ポケギア・パソコン・主人公・レポート・せってい）
;  3. 手持ちのポケモンを選ぶと「なまえ」（ニックネーム変更）
;  4. 手持ちのポケモンを選ぶと「わすれる」（ひでんわざも忘れられる）
;  ※ ひでんマシンを全ポケモンに… は build.py で基本データを書きかえる
;  ※ 60fps は fps60.asm（別の版）
;
; 金銀はバンク4・9の空きが少ないので、表（データ）だけをバンク4・9に置き、
; 処理はホーム（バンク0）の空きに置いた（ホームはどのバンクからでも呼べる）。

INCLUDE "src/version.inc"
INCLUDE "src/charmap_jp.inc"

DEF BASEROM EQUS "\"base.gbc\""

; 9項目以上になったら、横に2列で並べる
; （日本版は濁点が上の行に出るので1行ずつには詰められない）
DEF MONMENU_WIDE EQU 9
DEF MONMENU_WIDE_LEFT EQU 4
DEF MONMENU_COL_WIDTH EQU 7

;=====================================================================
; 1. Bボタンダッシュ
;=====================================================================
SECTION "Run walk", ROMX[DoPlayerMovement_walk], BANK[BANK_PLAYERMOVE]
	jp RunOrWalkStep          ; ld a, STEP_WALK / call .DoStep / scf / ret

SECTION "Run surf", ROMX[DoPlayerMovement_surf], BANK[BANK_PLAYERMOVE]
	jp RunOrWalkStep

;=====================================================================
; 2. スタートメニューに「パソコン」
;=====================================================================
SECTION "StartMenu items ptr", ROMX[StartMenu_MenuDataItemsPtr], BANK[BANK_STARTMENU]
	dw StartMenuItemsNew

; ならび：ずかん・ポケモン・リュック・ポケギア・パソコン・主人公の名前・レポート・せってい（「とじる」は 出さない。B／START で とじる）
;   むしとり大会中は パソコンを 出さず、さいごに「とじる」
SECTION "StartMenu pc/status", ROMX[StartMenu_StatusAppend], BANK[BANK_STARTMENU]
	call StartMenu_PCAndStatus ; 5バイト（ld a, STARTMENUITEM_STATUS / call .AppendMenuList）
	nop
	nop
SECTION "StartMenu exit", ROMX[StartMenu_ExitAppend], BANK[BANK_STARTMENU]
	call StartMenu_ExitInContest ; 5バイト（ld a, STARTMENUITEM_EXIT / call .AppendMenuList）
	nop
	nop

SECTION "Bank4 new", ROMX[BANK4_FREE], BANK[BANK_STARTMENU]
StartMenuItemsNew:
	INCBIN BASEROM, BANK_STARTMENU * $4000 + StartMenu_Items - $4000, 9 * 6
	dw StartMenu_PC, PCString, PCDesc   ; STARTMENUITEM_PC = 9
PCString:
	db "パソコン@"
PCDesc:
	db "どこでも<NEXT>パソコンを　つかう@"

MonActionsNew:
	INCBIN BASEROM, BANK_MONMENU * $4000 + PokemonActionSubmenu_Actions - $4000, 20 * 3
	db MONMENUITEM_NAME
	dw MonMenu_Name
	db MONMENUITEM_FORGET
	dw MonMenu_Forget
	db -1

SECTION "MonActions ptr", ROMX[PokemonActionSubmenu_ActionsPtr], BANK[BANK_MONMENU]
	dw MonActionsNew

;=====================================================================
; 3・4. 手持ちのメニューに「なまえ」「わすれる」
;=====================================================================
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

SECTION "Bank9 new", ROMX[BANK9_FREE], BANK[BANK_MONSUBMENU]
MonMenuOptionStringsNew:
	INCBIN BASEROM, BANK_MONSUBMENU * $4000 + MonMenuOptionStrings - $4000, MonMenuOptions - MonMenuOptionStrings
	db "なまえ@"     ; 8
	db "わすれる@"   ; 9

MonMenuOptionsNew:
	INCBIN BASEROM, BANK_MONSUBMENU * $4000 + MonMenuOptions - $4000, 21 * 3
	db MONMENU_MENUOPTION, MONMENUITEM_NAME,   8
	db MONMENU_MENUOPTION, MONMENUITEM_FORGET, 9
	db -1

MonSubmenuWideHeader:
	db $40 ; MENU_BACKUP_TILES
	db 0, MONMENU_WIDE_LEFT, 17, 19
	dw 0
	db 1


;=====================================================================
; ホーム（バンク0）の空き その1（$0068-$00ff）
;=====================================================================
SECTION "Home new 1", ROM0[HOME_FREE1]

; --- Bダッシュ（バンク4から呼ばれる）
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

; --- スタートメニュー（バンク4から呼ばれる）
StartMenu_ExitInContest:
	ld hl, wStatusFlags2
	bit STATUSFLAGS2_BUG_CONTEST_TIMER_F, [hl]
	ret z                     ; ふだんは「とじる」を 出さない
	ld a, STARTMENUITEM_EXIT
	jp StartMenu_AppendMenuList

StartMenu_PC:
	ld a, PCScript_Bank
	ld hl, PCScript
	call FarQueueScript
	ld a, 4                   ; メニューを閉じてスクリプトを動かす
	ret

; --- 手持ちのメニューの動き（バンク4から呼ばれる）
MonMenu_Name:
	farcall_jp MonMenu_NameBody
	ld a, c                   ; 戻り値は c で受け取る
	ret

MonMenu_Forget:
	farcall_jp MonMenu_ForgetBody
	ld a, c
	ret

; --- 以下はバンク9から呼ばれる
AddExtraMonMenuItems:
	ld a, [wLinkMode]
	and a
	jr nz, .cancel
	ld a, MONMENUITEM_NAME
	call AddMonMenuItem
	ld a, MONMENUITEM_FORGET
	call AddMonMenuItem
.cancel
	ld a, MONMENUITEM_CANCEL
	jp AddMonMenuItem

MonSubmenu_LoadHeaderNew:
	ld hl, MonSubmenu_Header
	ld a, [wMonSubmenuCount]
	cp MONMENU_WIDE
	jr c, .go
	ld hl, MonSubmenuWideHeader
.go
	jp LoadMenuHeader

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

;=====================================================================
; ホーム（バンク0）の空き その2（$3f10-$3fff）
;=====================================================================
SECTION "Home new 2", ROM0[HOME_FREE2]

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

;=====================================================================
; 新しい所（バンク$3f の空き）
;=====================================================================
SECTION "New bank", ROMX[NEW_ADDR], BANK[BANK_NEW]

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

; 使われて いない SetUnusedTwoDayTimer（$04:$5882、16バイト）に 置く（バンク4 の おわりの 空きは 使いきった）
SECTION "StartMenu pc/status body", ROMX[$5882], BANK[BANK_STARTMENU]
StartMenu_PCAndStatus:
	ld hl, wStatusFlags2
	bit STATUSFLAGS2_BUG_CONTEST_TIMER_F, [hl]
	ld a, STARTMENUITEM_PC
	call z, StartMenu_AppendMenuList ; むしとり大会中は パソコンを 出さない
	ld a, STARTMENUITEM_STATUS
	jp StartMenu_AppendMenuList
