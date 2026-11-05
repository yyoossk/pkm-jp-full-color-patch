; ポケギアの文字の後ろを白に … クリスタル（日本版）用の 値（本体は src/pokegearwhite.asm）
; クリスタルは 男の子（PokegearPals）と 女の子（PokegearFPals。町の 色だけ ちがう）の 2つの 色が あり、どちらも 6組・色0 は RGB 28,31,20
DEF PG_PALS      EQU $76e6      ; バンク$02 PokegearPals（「fc 53 b5 56 ad 35 00 00 fc 53 e0 03 …」）
DEF PG_PALS2     EQU $7716      ; バンク$02 PokegearFPals（すぐ あと）
DEF PG_PALS_BANK EQU $02

INCLUDE "src/pokegearwhite.asm"
