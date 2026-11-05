; つかえるわざの命中：銀 日本版（後期版）の値（PlaceMoveData の フック $04:$76a8・Moves $10:$5c6c・wCurSpecies $ce54 は 金と 同じ。置き場所だけ ちがう）
DEF MA_HOOK            EQU $76a8      ; バンク$04 PlaceMoveData の hlcoord 1, 14 / ld a, PRINTMOVEDESCRIPTION / call Predef
DEF MA_HOOK_BANK       EQU $04
DEF MA_Predef          EQU $2e05
DEF MA_PREDEF_DESC     EQU $11        ; PrintMoveDescription
DEF MA_DESC_COORD      EQU $c4b9      ; hlcoord 1, 14
DEF MA_MOVES_BANK      EQU $10
DEF MA_Moves           EQU $5c6c      ; 1つ 7バイト（+4 命中）
DEF MA_GetFarByte      EQU $30e4
DEF MA_PlaceString     EQU $0f46
DEF MA_PrintNum        EQU $31f9
DEF MA_wCurSpecies     EQU $ce54      ; わざの 番号
DEF MA_wBuffer         EQU $d143      ; wTextDecimalByte（元の いりょく と 同じ）
DEF MA_COORD           EQU $c3a0 + 11 * 20 + 9   ; hlcoord 9, 11
DEF MA_BANK            EQU $48
DEF MA_ADDR            EQU $7000
INCLUDE "src/moveacc.asm"
