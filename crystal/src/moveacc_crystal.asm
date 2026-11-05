; つかえるわざの命中 … クリスタル（日本版）用の 値（本体は src/moveacc.asm）
; PlaceMoveData（$04:$72xx）は 金と 同じ 形：タイプ hlcoord 5, 12、いりょく hlcoord 15, 12、せつめい hlcoord 1, 14。
DEF MA_HOOK            EQU $7301      ; バンク$04 PlaceMoveData の ld hl, $c5b9 / ld a, $11 / call Predef
DEF MA_HOOK_BANK       EQU $04
DEF MA_Predef          EQU $2d55
DEF MA_PREDEF_DESC     EQU $11        ; PrintMoveDescription
DEF MA_DESC_COORD      EQU $c5b9      ; hlcoord 1, 14
DEF MA_MOVES_BANK      EQU $10
DEF MA_Moves           EQU $5c69      ; 1つ 7バイト（+4 命中）。PlaceMoveData の ld hl, Moves + 2（$5c6b）から
DEF MA_GetFarByte      EQU $3019
DEF MA_PlaceString     EQU $1057
DEF MA_PrintNum        EQU $3164
DEF MA_wCurSpecies     EQU $cf54
DEF MA_wBuffer         EQU $d296      ; wTextDecimalByte（元の いりょく と 同じ）
DEF MA_COORD           EQU $c4a0 + 11 * 20 + 9   ; hlcoord 9, 11
DEF MA_BANK            EQU $76
DEF MA_ADDR            EQU $7200

INCLUDE "src/moveacc.asm"
