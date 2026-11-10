; わざの威力と命中・効き目：銀 日本版（後期版）の値（MoveInfoBox の さいごの 9バイトは 銀では $0f:$65df。TypeMatchups $0d:$4cfd・wEnemyMonType1・2 は 金と 同じ）
DEF MP_HOOK            EQU $65df      ; 銀（金は $65e4。銀は ここが 5バイト 前）。 バンク$0f MoveInfoBox の ld hl, $c4ef / ld a, PRINTMOVETYPE / call Predef / ret
DEF MP_HOOK_BANK       EQU $0f
DEF MP_PREDEF_PRINTMOVETYPE EQU $2a
DEF MP_Predef          EQU $2e05
DEF MP_PlaceString     EQU $0f46
DEF MP_PrintNum        EQU $31f9
DEF MP_wPlayerMoveStruct EQU $caef    ; MOVE_ANIM（+2 威力・+4 命中）
DEF MP_wStringBuffer1  EQU $cf87
DEF MP_wEnemyMonType1  EQU $d0ff
DEF MP_wEnemyMonType2  EQU $d100
DEF MP_TypeMatchups    EQU $4cfd      ; バンク$0d（こうげき・ぼうぎょ・ばいりつ（0／5／20）。$fe くぎり・$ff おわり）
DEF MP_TYPES_BANK      EQU $0d
DEF MP_GetFarByte      EQU $30e4
DEF MP_COORD           EQU $c3a0      ; hlcoord 0, 0
DEF MP_BANK            EQU $48
DEF MP_ADDR            EQU $5800
DEF MP_PPCOLOR EQU 1                  ; PP の のこりで 色（src/statuscolor_silver.asm）
INCLUDE "src/movepower.asm"
