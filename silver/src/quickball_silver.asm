; 前のボールをすぐ投げる：銀 日本版（後期版）の値（アドレスは 金と 同じ。WRAM・置き場所だけ ちがう）
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
DEF wLastBall          EQU $def9      ; 使われていない WRAM（ダウジングの $def5〜$def8 の 次）
DEF wQuickBall         EQU $defa
DEF QB_BANK            EQU $48
DEF QB_ADDR            EQU $5e00
INCLUDE "src/quickball.asm"
