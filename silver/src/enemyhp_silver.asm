; 相手のHPの数字：銀 日本版（後期版）の値（アドレスは 金と 同じ。HPBarAnim_UpdateHPRemaining の バイトも 同じ。置き場所だけ ちがう）
DEF EH_HUD_HOOK        EQU $5eb1      ; バンク$0f DrawEnemyHUD の farcall DrawEnemyHUDBorder
DEF EH_HUD_BANK        EQU $0f
DEF EH_Border_BANK     EQU $0b
DEF EH_Border          EQU $51a9
DEF EH_ANIM_HOOK       EQU $5a57      ; バンク$03 HPBarAnim_UpdateHPRemaining の and a / ret z / cp 1 / jr z, .load_15
DEF EH_ANIM_BANK       EQU $03
DEF EH_PrintNum        EQU $31f9
DEF EH_wEnemyMonHP     EQU $d0f1
DEF EH_wEnemyMonMaxHP  EQU $d0f3
DEF EH_COORD           EQU $c3a0 + 3 * 20 + 3   ; hlcoord 3, 3
DEF EH_BANK            EQU $48
DEF EH_ADDR            EQU $6d00

; 相手の HP の 数字が わくの 下の 線に かさなって 線が とぎれて いた → 線を 1行 下（数字の 下）に うつす（自分の HUD と 同じ）
DEF EH_LINE_BELOW EQU 1

INCLUDE "src/enemyhp.asm"

; 相手の HUD を けす 所（hlcoord 1, 0 / lb bc, 4, 10 か 4, 11 / call ClearBox）を 5行に（うつした 線も けす）
; （銀の ROM で「21 a1 c3 01 0a 04 cd」「21 a1 c3 01 0b 04 cd」を さがした 8か所。クリスタルと 同じ 数）
MACRO EH_CLEAR5
	SECTION "enemyhp clear5 \1 \2", ROMX[\2 + 5], BANK[\1]
	db 5
ENDM
	EH_CLEAR5 $0d, $6995
	EH_CLEAR5 $0d, $7b39
	EH_CLEAR5 $0f, $4d71
	EH_CLEAR5 $0f, $4ec4
	EH_CLEAR5 $0f, $5660
	EH_CLEAR5 $0f, $73ac
	EH_CLEAR5 $33, $41db
	EH_CLEAR5 $0f, $5ea8                ; DrawEnemyHUD の さいしょ（lb bc, 4, 11）
