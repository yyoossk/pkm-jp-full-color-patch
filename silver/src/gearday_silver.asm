; ポケギアの今日のできごと：銀 日本版（後期版）の値（アドレスは 金と 同じ。置き場所だけ ちがう）
DEF GD_HOOK            EQU $4e5f      ; バンク$24 PokegearClock_Init の ld hl, PokegearPressButtonText / call PrintText
DEF GD_HOOK_BANK       EQU $24
DEF GD_GetWeekday      EQU $351b
DEF GD_PrintText       EQU $0f30
DEF GD_BANK            EQU $48
DEF GD_ADDR            EQU $6200
INCLUDE "src/gearday.asm"
