; 育て屋の話：銀 日本版（後期版）の値（アドレス・WRAM は 金と 同じ。置き場所だけ ちがう）
DEF DH_HOOK          EQU $6d06       ; バンク$05 DayCareMan .AskWithdrawMon
DEF DH_HOOK_BANK     EQU $05
DEF DH_GetBreedMon1LevelGrowth EQU $696e
DEF DH_GetBreedMon1LevelGrowth_BANK EQU $03
DEF DH_CheckBreedmonCompatibility EQU $78e9
DEF DH_CheckBreedmonCompatibility_BANK EQU $05
DEF DH_PrintText     EQU $0f30
DEF DH_wDayCareMan   EQU $dbd4
DEF DH_wDayCareLady  EQU $dc01
DEF DH_wStepsToEgg   EQU $dc02
DEF DH_wBreedingCompatibility EQU $d143
DEF DH_BANK          EQU $48
DEF DH_ADDR          EQU $5600
INCLUDE "src/daycarehint.asm"
