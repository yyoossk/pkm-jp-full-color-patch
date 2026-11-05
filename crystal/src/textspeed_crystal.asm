; 文字の 速さ さいこう … クリスタル（日本版）用の 値（本体は src/textspeed.asm）
; クリスタルの せっていも 金と 同じ 作り（Options_TextSpeed・GetTextSpeed）
DEF TS_HOOK          EQU $42a9     ; Options_TextSpeed（call GetTextSpeed / ldh a, [hJoyPressed] / bit 5, a）
DEF TS_HOOK_BANK     EQU $39
DEF TS_COORD         EQU $c4bf     ; はなしの はやさの 文字（元は $c4d3。clockopt で 1行 上の $c4bf）
DEF TS_wOptions      EQU $cfc0
DEF TS_hJoyPressed   EQU $ffa7
DEF TS_PlaceString   EQU $1057
DEF TS_BANK          EQU $76       ; ボックスの 自動切りかえ・マスターボール・むしよけの あと
DEF TS_ADDR          EQU $4400

INCLUDE "src/textspeed.asm"
