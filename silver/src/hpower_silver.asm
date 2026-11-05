; めざめるパワー：銀 日本版（後期版）の値（アドレスは 金と 同じ。置き場所だけ ちがう）
DEF HP_HOOK            EQU $5089      ; バンク$14 LoadGreenPage の farcall LoadStatsScreenPals
DEF HP_HOOK_BANK       EQU $14
DEF HP_Pals_BANK       EQU $02
DEF HP_Pals            EQU $5241      ; LoadStatsScreenPals
DEF HP_GetTypeName     EQU $4a87      ; バンク HP_HOOK_BANK（wNamedObjectIndex → wStringBuffer1）
DEF HP_PlaceString     EQU $0f46
DEF HP_PrintNum        EQU $31f9
DEF HP_wTempMonMoves   EQU $d007
DEF HP_wTempMonDVs     EQU $d01a
DEF HP_wNamedObjectIndex EQU $d143
DEF HP_wStringBuffer1  EQU $cf87
DEF HP_wBuffer         EQU $cf92      ; wStringBuffer1 の あと（威力 1バイト）
DEF HP_COORD           EQU $c3a0 + 6 * 20 + 9   ; 1つめの わざの 名前（hlcoord 9, 6）
DEF HIDDEN_POWER       EQU $ed
DEF HP_BANK            EQU $48
DEF HP_ADDR            EQU $6b00
INCLUDE "src/hpower.asm"
