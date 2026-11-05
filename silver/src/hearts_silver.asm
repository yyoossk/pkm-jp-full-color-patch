; なつき度のハート：銀 日本版（後期版）の値（アドレスは 金と 同じ。置き場所だけ ちがう）
DEF HT_HOOK            EQU $4f8e      ; バンク$14 LoadPinkPage の call WaitBGMap
DEF HT_HOOK_BANK       EQU $14
DEF HT_STUB            EQU $7fc8      ; バンク$14 の 空き（9バイト）
DEF HT_WaitBGMap       EQU $33ae
DEF HT_PlaceString     EQU $0f46
DEF HT_wTempMonHappiness EQU $d020
DEF HT_TILE            EQU $5e        ; ぬりつぶし（$5f は わく だけ）
DEF HT_VRAM            EQU $9000 + HT_TILE * 16
DEF HT_COORD           EQU $c3a0 + 8 * 20 + 9   ; hlcoord 9, 8
DEF HT_ATTR            EQU $cccd + 8 * 20 + 9   ; wAttrmap の 同じ 所
DEF HT_BANK            EQU $48
DEF HT_ADDR            EQU $6000
INCLUDE "src/hearts.asm"
