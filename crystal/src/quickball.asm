; 戦闘で、前に 使った ボールを SELECT で すぐ 投げる（金 日本版）
;
; ・野生の ポケモンとの 戦闘の メニュー（たたかう・リュック・ポケモン・にげる）で SELECT を おすと、
;   リュックを ひらかずに、前に 使った ボールと 同じ ボールを 投げる。
;   前に 使った ボールが もう ない とき・まだ 使って いない ときは、ふつうに リュックを ひらく。
;   トレーナーとの 戦闘では なにも しない。
;   （むしとり大会・サファリは メニューが ちがうので かわらない）
; ・「前に 使った ボール」は リュックの ボールの ポケットに ある どうぐを 戦闘で 使った とき に おぼえる
;   （使われていない WRAM。電源を 切ると わすれる）。
;
; しくみ
;   ・戦闘の メニューの MenuData（$09:$4e9f）の flags に STATICMENU_ENABLE_SELECT を 足す
;     （_2DMenu は SELECT で キャリーを かえす）。
;   ・CommonBattleMenu の「call _2DMenu」を QB_Menu（バンク$09 の 空き）に：キャリーなら wQuickBall = 1。
;     カーソルの 場所は かわらない。
;   ・BattleMenu .next の「ld a, 1 / ldh [hBGMapMode], a」を QB_Next（バンク$0f の 空き）の call に：
;     wQuickBall なら QB_Decide で ボールを きめて、BattleMenu_Pack の むしとり大会と 同じ ながれ
;     （LoadStandardMenuHeader → wCurItem → DoItemEffect → .got_item）で 投げる（ボールは PokeBallEffect が へらす）。
;   ・BattleMenu_Pack .got_item の「call .UseItem」を QB_Used に：使った どうぐが ボールの ポケットに あれば おぼえる。
;
; 銀・クリスタルに 入れるとき：下の DEF を その ROM の 値に する
;   （クリスタルは 戦闘の メニューの 作りが 同じか、BattleMenu の ならび（1 たたかう・2 リュック…）を 確かめる）

IF !DEF(QB_MENUDATA)
DEF QB_MENUDATA        EQU $4e9f      ; バンク$09 BattleMenuHeader の MenuData（flags $81）
DEF QB_MENU_BANK       EQU $09
DEF QB_MENU_CALL       EQU $4e8a      ; CommonBattleMenu の call _2DMenu
DEF QB_MENU_FREE       EQU $7fcf      ; バンク$09 の 空き
DEF QB_2DMenu          EQU $1e40
DEF QB_BATTLE_BANK     EQU $0f
DEF QB_NEXT_HOOK       EQU $5fe5      ; BattleMenu .next の ld a, 1 / ldh [hBGMapMode], a
DEF QB_BattleMenu      EQU $5fb6
DEF QB_BattleMenu_Pack EQU $600b
DEF QB_GOT_ITEM        EQU $6046      ; BattleMenu_Pack .got_item の call .UseItem
DEF QB_UseItem         EQU $6071
DEF QB_BATTLE_FREE     EQU $7fc8      ; バンク$0f の 空き
DEF QB_LoadStandardMenuHeader EQU $1b8d
DEF QB_DoItemEffect    EQU $3011
DEF QB_CheckItem       EQU $304b
DEF QB_TossItem        EQU $3025
DEF QB_wItemEffectSucceeded EQU $cfde
DEF QB_wItemQuantityChange EQU $d003
DEF QB_wBattleMode     EQU $d108
DEF QB_wCurItem        EQU $cffc
DEF QB_wNumBalls       EQU $d5ef
DEF QB_hBGMapMode      EQU $ffd6
DEF wLastBall          EQU $defa      ; 使われていない WRAM（ダウジングの $def6〜$def9 の 次）
DEF wQuickBall         EQU $defb
DEF QB_BANK            EQU $45
DEF QB_ADDR            EQU $6a00
ENDC

SECTION "quickball menudata", ROMX[QB_MENUDATA], BANK[QB_MENU_BANK]
	db $81 | %10                      ; STATICMENU_CURSOR | STATICMENU_DISABLE_B | STATICMENU_ENABLE_SELECT
SECTION "quickball menu call", ROMX[QB_MENU_CALL], BANK[QB_MENU_BANK]
	call QB_Menu
SECTION "quickball menu", ROMX[QB_MENU_FREE], BANK[QB_MENU_BANK]
QB_Menu:
	call QB_2DMenu
	ret nc
	ld a, 1
	ld [wQuickBall], a
	ret

SECTION "quickball next hook", ROMX[QB_NEXT_HOOK], BANK[QB_BATTLE_BANK]
	call QB_Next
	nop
SECTION "quickball got item", ROMX[QB_GOT_ITEM], BANK[QB_BATTLE_BANK]
	call QB_Used
SECTION "quickball battle", ROMX[QB_BATTLE_FREE], BANK[QB_BATTLE_BANK]
QB_Next:
	ld a, 1
	ldh [QB_hBGMapMode], a
	ld a, [wQuickBall]
	and a
	ret z
	xor a
	ld [wQuickBall], a
	pop hl                            ; BattleMenu に もどらない
	ld a, BANK(QB_Decide)
	ld hl, QB_Decide
	rst $08                           ; b = ボール（0 ＝ リュックを ひらく・$ff ＝ なにも しない）
	ld a, b                           ; （farcall は a を かえさない）
	inc a
	jp z, QB_BattleMenu
	dec a
	jp z, QB_BattleMenu_Pack
	ld [QB_wCurItem], a
	call QB_LoadStandardMenuHeader
	call QB_DoItemEffect             ; ボールは PokeBallEffect が 1こ へらす
	jp QB_GOT_ITEM
QB_Used:
	ld a, BANK(QB_Remember)
	ld hl, QB_Remember
	rst $08
	jp QB_UseItem

SECTION "quickball", ROMX[QB_ADDR], BANK[QB_BANK]
QB_Decide:                            ; → b
	ld b, $ff
	ld a, [QB_wBattleMode]
	dec a
	ret nz                            ; トレーナー
	ld b, 0
	ld a, [wLastBall]
	and a
	ret z
	ld [QB_wCurItem], a
	ld hl, QB_wNumBalls
	call QB_CheckItem
	ld b, 0
	ret nc                            ; もう ない
	ld a, [wLastBall]
	ld b, a
	ret

QB_Remember:
	ld a, [QB_wCurItem]
	push af
	ld hl, QB_wNumBalls
	call QB_CheckItem
	pop bc
	ret nc
	ld a, b
	ld [wLastBall], a
	ret
