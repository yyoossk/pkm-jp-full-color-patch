; 相手のHPの数字 … クリスタル（日本版）用の 値（本体は src/enemyhp.asm）
; DrawEnemyHUD（$0f:$6038）の farcall DrawEnemyHUDBorder（$0f:$6044：ld a, $0b / ld hl, $51ef / rst $08）。
; HPBarAnim_UpdateHPRemaining（$03:$5a01）は 金と 同じ 形（ld a, [wWhichHPBar] / and a / ret z / cp 1 / jr z, .load_15 / ld de, 1 …）。
; 相手の HUD も 金と 同じ（名前 1行め、HP バー hlcoord 2, 2、わくの 線 3行め）なので 数字は hlcoord 3, 3。
DEF EH_HUD_HOOK        EQU $6044
DEF EH_HUD_BANK        EQU $0f
DEF EH_Border_BANK     EQU $0b
DEF EH_Border          EQU $51ef
DEF EH_ANIM_HOOK       EQU $5a04
DEF EH_ANIM_BANK       EQU $03
DEF EH_PrintNum        EQU $3164
DEF EH_wEnemyMonHP     EQU $d247      ; wEnemyMon（英語版 ＋ $31。wEnemyMonType1 $d255 と 同じ ずれ）
DEF EH_wEnemyMonMaxHP  EQU $d249
DEF EH_COORD           EQU $c4a0 + 3 * 20 + 3   ; hlcoord 3, 3
DEF EH_BANK            EQU $76
DEF EH_ADDR            EQU $6f00

INCLUDE "src/enemyhp.asm"
