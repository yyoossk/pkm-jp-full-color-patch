; 手持ちの色ちがいの星：銀 日本版（後期版）の値（PlacePartyNicknames .end $14:$40be などは 金と 同じ。置き場所だけ ちがう）
DEF PS_HOOK            EQU $40be      ; バンク$14 PlacePartyNicknames .end の ld de, .CancelString / call PlaceString / ret
DEF PS_HOOK_BANK       EQU $14
DEF PS_PlaceString     EQU $0f46
DEF PS_wPartyCount     EQU $d9e8
DEF PS_wPartySpecies   EQU $d9e9
DEF PS_wPartyMon1DVs   EQU $da05
DEF PS_MONLEN          EQU $30
DEF PS_EGG             EQU $fd
DEF PS_TILE            EQU $5e
DEF PS_VRAM            EQU $9000 + PS_TILE * 16
DEF PS_COORD           EQU $c3a0 + 8      ; hlcoord 8, 0（1ぴきめ。2行 ごと）
DEF PS_BANK            EQU $48
DEF PS_ADDR            EQU $6600
INCLUDE "src/partyshiny.asm"
