; タマゴの歩数 … クリスタル（日本版）用の 値（本体は src/eggsteps.asm）
; クリスタルの EggStatsScreen（$13:$61bf）は WaitBGMap を 呼ばない ので、タマゴの 文を かいた あとの
; 「ld hl, $cf58 / set 5, [hl] / call $32c5」（$13:$6215。8バイト）を EggSteps への farcall（＋ nop 2つ）に して、
; EggSteps で 歩数を かいて から その 3つを する（ES_AFTER_NOPS）。
; （タマゴの 文を かく 所を フックに すると、文が バンク$13 に あるので farcall の 先から 読めない）
; 文は 6〜12行め なので、歩数は 金と 同じ hlcoord 9, 15。
DEF ES_HOOK            EQU $6215
DEF ES_HOOK_BANK       EQU $13
DEF ES_AFTER_NOPS      EQU 2
DEF ES_wStatsScreenFlags EQU $cf58
DEF ES_AfterCall       EQU $32c5
DEF ES_WaitBGMap       EQU 0          ; （使わない）
DEF ES_PlaceString     EQU $1057
DEF ES_PrintNum        EQU $3164
DEF ES_wTempMonHappiness EQU $d0e9
DEF ES_wStepCount      EQU $dc39      ; CountStep（$25:$6b79）の ld hl, $dc39
DEF ES_wBuffer         EQU $d05b      ; wStringBuffer1
DEF ES_hBGMapMode      EQU $ffd4
DEF ES_COORD           EQU $c4a0 + 15 * 20 + 9   ; hlcoord 9, 15
DEF ES_BANK            EQU $76
DEF ES_ADDR            EQU $6b00

INCLUDE "src/eggsteps.asm"
