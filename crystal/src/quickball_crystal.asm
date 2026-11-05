; 前のボールをすぐ投げる … クリスタル（日本版）用（金銀の src/quickball.asm と 同じ ことを する）
; クリスタルは バンク$0f の 空きが すくない（24バイト・9バイト）ので、きめる 所も 投げる 所も バンク$76 で して、
; バンク$0f には 小さな 入口だけ 置く。wLastBall・wQuickBall は WRAM バンク2（$dfc9・$dfca）。
;   ・戦闘の メニューの MenuData（$09:$4f44。flags $81）に STATICMENU_ENABLE_SELECT を 足す（$83）。
;   ・CommonBattleMenu（$09:$4f02）の「call $1ffc」（_2DMenu。$09:$4f0e）を QB_Menu に：キャリー（SELECT）なら wQuickBall = 1。
;   ・BattleMenu（$0f:$6149）.next の「ld a, 1 / ldh [hBGMapMode], a」（$0f:$6179）を QB_Next に。
;     日本版の ならびは 1 たたかう・2 リュック（$61cb）・3 ポケモン・4 にげる（金と 同じ）。
;   ・BattleMenu_Pack .got_item の「call .UseItem」（$0f:$620d → $6238）を QB_Used に。
INCLUDE "src/charmap_jp.inc"

DEF QB_MENUDATA        EQU $4f44
DEF QB_MENU_CALL       EQU $4f0e
DEF QB_2DMenu          EQU $1ffc
DEF QB_MENU_FREE       EQU $7f50      ; バンク$09 の 空き（$7f4e〜）
DEF QB_NEXT_HOOK       EQU $6179
DEF QB_BattleMenu      EQU $6149
DEF QB_BattleMenu_Pack EQU $61cb
DEF QB_GOT_ITEM        EQU $620d
DEF QB_UseItem         EQU $6238
DEF QB_NEXT_FREE       EQU $7fe8      ; バンク$0f の 空き（24バイト）
DEF QB_USED_FREE       EQU $7fd7      ; バンク$0f の 空き（9バイト）
DEF QB_RETURN_HOOK     EQU $74b5      ; _ReturnToBattle_UseBall（$09:$74b5）の 頭の call ClearBGPalettes
DEF QB_ClearBGPalettes EQU $31bf
DEF QB_RETURN_FREE     EQU $7f70      ; バンク$09 の 空き
DEF QB_LoadStandardMenuHeader EQU $1d39
DEF QB_DoItemEffect    EQU $2f11
DEF QB_CheckItem       EQU $2f4b
DEF QB_wBattleMode     EQU $d25e
DEF QB_wCurItem        EQU $d0c6
DEF QB_wNumBalls       EQU $d8ca
DEF QB_hBGMapMode      EQU $ffd4
DEF wLastBall          EQU $dfc9      ; WRAM バンク2（$dfc7・$dfc8 は ぶんぷの 時間帯）
DEF wQuickBall         EQU $dfca
DEF QB_BANK            EQU $76
DEF QB_ADDR            EQU $6900

MACRO qb_load ; a ＝ WRAM バンク2 の \1
	ld a, 2
	ldh [$ff70], a
	ld a, [\1]
	push af
	ld a, 1
	ldh [$ff70], a
	pop af
ENDM
MACRO qb_store ; WRAM バンク2 の \1 ＝ a
	push af
	ld a, 2
	ldh [$ff70], a
	pop af
	ld [\1], a
	push af
	ld a, 1
	ldh [$ff70], a
	pop af
ENDM

SECTION "quickball menudata", ROMX[QB_MENUDATA], BANK[$09]
	db $81 | %10                      ; STATICMENU_ENABLE_SELECT を 足す
SECTION "quickball menu call", ROMX[QB_MENU_CALL], BANK[$09]
	call QB_Menu
SECTION "quickball menu", ROMX[QB_MENU_FREE], BANK[$09]
QB_Menu:
	call QB_2DMenu
	ret nc
	ld a, 1
	qb_store wQuickBall
	ret

; SELECT で 投げる ときは、ボールの 処理（PokeBallEffect）の はじめの _ReturnToBattle_UseBall
; （リュックの 画面から 戦闘の 画面を 作りなおす：画面を 白くして 絵・文字・色を 読みなおす）を とばす。
; 戦闘の 画面は そのまま 出ているので、作りなおすと 画面ぜんたいが 一瞬 白く なって いた。
SECTION "quickball return hook", ROMX[QB_RETURN_HOOK], BANK[$09]
	call QB_Return
SECTION "quickball return", ROMX[QB_RETURN_FREE], BANK[$09]
QB_Return:
	qb_load wQuickBall
	cp $80
	jp nz, QB_ClearBGPalettes         ; ふつう（リュックから）は 元の まま
	pop hl                            ; _ReturnToBattle_UseBall の のこりを しない
	ret

SECTION "quickball next hook", ROMX[QB_NEXT_HOOK], BANK[$0f]
	call QB_Next
	nop
SECTION "quickball next", ROMX[QB_NEXT_FREE], BANK[$0f]
QB_Next:
	ld a, BANK(QB_Decide)
	ld hl, QB_Decide
	rst $08                           ; b：0 ＝ ふつう・1 ＝ メニューに もどる・2 ＝ リュック・3 ＝ 投げた
	ld a, b                           ; （farcall は a を かえさない）
	and a
	ret z
	pop hl                            ; BattleMenu に もどらない
	dec a
	jp z, QB_BattleMenu
	dec a
	jp z, QB_BattleMenu_Pack
	jp QB_GOT_ITEM
SECTION "quickball got item", ROMX[QB_GOT_ITEM], BANK[$0f]
	call QB_Used
SECTION "quickball used", ROMX[QB_USED_FREE], BANK[$0f]
QB_Used:
	ld a, BANK(QB_Remember)
	ld hl, QB_Remember
	rst $08
	jp QB_UseItem

SECTION "quickball", ROMX[QB_ADDR], BANK[QB_BANK]
QB_Decide:
	ld a, 1                           ; 元の 命令
	ldh [QB_hBGMapMode], a
	ld b, 0
	qb_load wQuickBall
	and a
	ret z
	xor a
	qb_store wQuickBall
	ld b, 1
	ld a, [QB_wBattleMode]
	dec a
	ret nz                            ; トレーナー → メニューに もどる
	ld b, 2
	qb_load wLastBall
	and a
	ret z                             ; まだ 使って いない → リュック
	ld [QB_wCurItem], a
	ld hl, QB_wNumBalls
	call QB_CheckItem
	ld b, 2
	ret nc                            ; もう ない → リュック
	qb_load wLastBall
	ld [QB_wCurItem], a
	call QB_LoadStandardMenuHeader
	ld a, $80                         ; 投げて いる あいだの 印（QB_Return）
	qb_store wQuickBall
	call QB_DoItemEffect             ; ボールは PokeBallEffect が 1こ へらす
	xor a
	qb_store wQuickBall
	ld b, 3
	ret

QB_Remember:
	ld a, [QB_wCurItem]
	push af
	ld hl, QB_wNumBalls
	call QB_CheckItem
	pop bc
	ret nc
	ld a, b
	qb_store wLastBall
	ret
