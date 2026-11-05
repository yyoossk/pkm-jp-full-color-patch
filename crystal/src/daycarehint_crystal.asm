; 育て屋の話 … クリスタル（日本版）用の 値（本体は src/daycarehint.asm）
; DayCareMan（$05:$6bb7）は 金と 同じ 形。.AskWithdrawMon の 頭が「ld a, $03 / ld hl, $6946 / rst $08」（6バイト）
DEF DH_HOOK          EQU $6bdf       ; バンク$05 DayCareMan .AskWithdrawMon
DEF DH_HOOK_BANK     EQU $05
DEF DH_GetBreedMon1LevelGrowth EQU $6946
DEF DH_GetBreedMon1LevelGrowth_BANK EQU $03
DEF DH_CheckBreedmonCompatibility EQU $766b
DEF DH_CheckBreedmonCompatibility_BANK EQU $05
DEF DH_PrintText     EQU $1041
DEF DH_wDayCareMan   EQU $de89       ; wBreedMon1Species $de96・wBreedMon2Species $dec5
DEF DH_wDayCareLady  EQU $deb6
DEF DH_wStepsToEgg   EQU $deb7
DEF DH_wBreedingCompatibility EQU $d296   ; DayCare_InitBreeding（$05:$723b）で 読む 所
DEF DH_BANK          EQU $76
DEF DH_ADDR          EQU $6000

INCLUDE "src/daycarehint.asm"
