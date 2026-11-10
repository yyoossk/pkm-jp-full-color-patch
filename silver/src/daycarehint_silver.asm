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

; あずけた ポケモンの 今の レベル（DH_LEVEL。クリスタル追加機能キットの 54）
DEF DH_LEVEL EQU 1
DEF DH_LADY_HOOK     EQU $6d5a       ; DayCareLady .AskWithdrawMon（ld a, $03 / ld hl, $6989 / rst $08）
DEF DH_GetBreedMon2LevelGrowth EQU $6989
DEF DH_wBreedMon1Nickname EQU $dbd5  ; wDayCareMan ＋ 1
DEF DH_wBreedMon2Nickname EQU $dc04  ; wDayCareLady ＋ 3（英語版と 同じ ならび）
DEF DH_wLevelTemp    EQU $cf99       ; wStringBuffer2（$cf92）＋ 7
DEF DH_LEVEL_ADDR    EQU $5780
INCLUDE "src/daycarehint.asm"
