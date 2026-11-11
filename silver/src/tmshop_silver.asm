; わざマシンの 店：銀 日本版（後期版）の値（src/tmshop.asm より前に読みこむ）
; 店員の スクリプト・MART_CELADON_3F・wScriptVar は 金と 同じ。置き場所だけ ちがう（銀は $4b を ほかの 機能が 使う）
DEF TS_CLERK        EQU $639a      ; バンク$27 CeladonDeptStore3FClerkScript（6a 47 93 00 19 00 49 90）
DEF TS_CLERK_BANK   EQU $27
DEF TS_MART_ID      EQU $19        ; MART_CELADON_3F
DEF TS_wScriptVar   EQU $d165
DEF TS_BANK         EQU $5e        ; 空きの バンク
DEF TS_ADDR         EQU $4000
INCLUDE "src/tmshop.asm"
