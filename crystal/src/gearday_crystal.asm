; ポケギアの今日のできごと … クリスタル（日本版）用の 値（本体は src/gearday.asm）
; 曜日きょうだい・むしとりたいかい・ラプラスの 曜日と 場所は 金と 同じ（pret/pokecrystal の マップの スクリプトで 確かめた）
DEF GD_HOOK            EQU $4e92      ; バンク$24 PokegearClock_Init（$4e8f）の ld hl, $5486 / call PrintText
DEF GD_HOOK_BANK       EQU $24
DEF GD_GetWeekday      EQU $3342
DEF GD_PrintText       EQU $1041
DEF GD_BANK            EQU $76
DEF GD_ADDR            EQU $6800

INCLUDE "src/gearday.asm"
