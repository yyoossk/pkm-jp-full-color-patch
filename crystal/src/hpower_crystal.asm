; めざめるパワー … クリスタル（日本版）用の 値（本体は src/hpower.asm）
; クリスタルの LoadGreenPage（$13:$5fcc）は わざの 名前が 金と 同じ hlcoord 9, 6 から 3行 ずつ。
; LoadStatsScreenPals を 呼ばない ので、さいごの「ld hl, $c537 / ld a, $3c / ld [$d21b], a / ld a, $23 / call Predef」
; （$13:$600a。13バイト。predef ListMovePP）を HPower_Draw への farcall（＋ nop 7つ）に して、HPower_Draw で その 3つを する。
DEF HP_HOOK            EQU $600a
DEF HP_HOOK_BANK       EQU $13
DEF HP_HOOK_NOPS       EQU 7
DEF HP_PP_COORD        EQU $c537      ; hlcoord 11, 7（PP）
DEF HP_wListMovesLineSpacing EQU $d21b
DEF HP_PP_PREDEF       EQU $23        ; ListMovePP
DEF HP_Predef          EQU $2d55
DEF HP_GetTypeName     EQU $4a54      ; バンク$14
DEF HP_GetTypeName_BANK EQU $14
DEF HP_PlaceString     EQU $1057
DEF HP_PrintNum        EQU $3164
DEF HP_wTempMonMoves   EQU $d0d0
DEF HP_wTempMonDVs     EQU $d0e3
DEF HP_wNamedObjectIndex EQU $d296
DEF HP_wStringBuffer1  EQU $d05b
DEF HP_wBuffer         EQU $d066      ; wStringBuffer2（威力 1バイト）
DEF HP_COORD           EQU $c4a0 + 6 * 20 + 9   ; hlcoord 9, 6
DEF HIDDEN_POWER       EQU $ed
DEF HP_BANK            EQU $76
DEF HP_ADDR            EQU $6d00

INCLUDE "src/hpower.asm"
