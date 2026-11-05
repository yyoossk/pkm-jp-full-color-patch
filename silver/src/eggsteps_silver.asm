; タマゴの歩数：銀 日本版（後期版）の値（EggStatsScreen の フック $14:$51bf などは 金と 同じ。置き場所だけ ちがう）
DEF ES_HOOK            EQU $51bf      ; バンク$14 EggStatsScreen .picked の あと の call WaitBGMap / ld a, 1 / ldh [hBGMapMode], a
DEF ES_HOOK_BANK       EQU $14
DEF ES_WaitBGMap       EQU $33ae
DEF ES_PlaceString     EQU $0f46
DEF ES_PrintNum        EQU $31f9
DEF ES_wTempMonHappiness EQU $d020
DEF ES_wStepCount      EQU $d983
DEF ES_wBuffer         EQU $cf87      ; wStringBuffer1（2バイト）
DEF ES_hBGMapMode      EQU $ffd6
DEF ES_COORD           EQU $c3a0 + 15 * 20 + 9   ; hlcoord 9, 15
DEF ES_BANK            EQU $48
DEF ES_ADDR            EQU $6400
INCLUDE "src/eggsteps.asm"
