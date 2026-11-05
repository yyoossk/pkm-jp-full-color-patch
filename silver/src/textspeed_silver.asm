; 文字の速さ さいこう：銀 日本版（後期版）の値
DEF TS_HOOK          EQU $4b05     ; Options_TextSpeed（銀。金は $4c7f）。call GetTextSpeed から 7バイト 以上
DEF TS_HOOK_BANK     EQU $39
DEF TS_COORD         EQU $c3d3 - 20 ; はやさの 文字の 場所（銀も hlcoord 11, 3 = $c3d3。せっていの とけいで 1行 上）
DEF TS_wOptions      EQU $d1ab
DEF TS_hJoyPressed   EQU $ffa9
DEF TS_PlaceString   EQU $0f46
DEF TS_BANK          EQU $47
DEF TS_ADDR          EQU $4200
INCLUDE "src/textspeed.asm"
