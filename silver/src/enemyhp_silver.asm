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
INCLUDE "src/enemyhp.asm"
