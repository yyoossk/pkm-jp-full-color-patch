; わざの威力と命中・効き目 … クリスタル（日本版）用の 値（本体は src/movepower.asm）
; MoveInfoBox（$0f:$66d7）は 金と 同じ 形・同じ 場所（わく hlcoord 9, 13・「わざタイプ」10, 15・「／」14, 16・タイプ 15, 16）
DEF MP_HOOK            EQU $6755      ; バンク$0f MoveInfoBox の ld hl, $c5ef / ld a, $2a / call Predef / ret
DEF MP_HOOK_BANK       EQU $0f
DEF MP_PREDEF_PRINTMOVETYPE EQU $2a
DEF MP_Predef          EQU $2d55
DEF MP_PlaceString     EQU $1057
DEF MP_PrintNum        EQU $3164
DEF MP_wPlayerMoveStruct EQU $c60f    ; MOVE_ANIM（MoveInfoBox の ld a, [$c60f] / ld b, a）
DEF MP_wStringBuffer1  EQU $d05b
DEF MP_COORD           EQU $c4a0      ; hlcoord 0, 0
DEF MP_wEnemyMonType1  EQU $d255
DEF MP_wEnemyMonType2  EQU $d256
DEF MP_TypeMatchups    EQU $4bb1      ; バンク$0d（英語版と 同じ 場所・同じ 中身）
DEF MP_TYPES_BANK      EQU $0d
DEF MP_GetFarByte      EQU $3019
DEF MP_BANK            EQU $76
DEF MP_ADDR            EQU $6200

INCLUDE "src/movepower.asm"
