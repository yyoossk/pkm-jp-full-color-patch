; ポケギアの 文字の 後ろ（うすい 黄緑）を 白に する（金 日本版）
;
; ・PokegearPals（6つの 色の 組。どれも 色0 が うすい 黄緑 RGB 28,31,20）の 色0 を 白（RGB 31,31,31）に する。
;   文字の 後ろ（時計・電話帳・ラジオ・下の 文の わく・地図の 地名の わく）が 白に なる。
;   地図の 道（同じ 色0）も 白に なる（色の 組ごとに 色0 が あるので、1つだけ かえると 黄緑と 白が まざるため ぜんぶ かえる）。
; ・PokegearPals は ポケギアの ほか、ずかんの「ぶんぷ」・そらをとぶ の 地図でも 使うので、そこも 同じに なる。
;
; 銀・クリスタルに 入れるとき：PG_PALS を その ROM の PokegearPals に する
;   （「fc 53 b5 56 ad 35 00 00 fc 53 e0 03 …」を さがす）

IF !DEF(PG_PALS)
DEF PG_PALS      EQU $7af4      ; バンク$02 PokegearPals
DEF PG_PALS_BANK EQU $02
ENDC

FOR PG_I, 6
SECTION "pokegear white {d:PG_I}", ROMX[PG_PALS + PG_I * 8], BANK[PG_PALS_BANK]
	dw $7fff                     ; 色0：白
ENDR
IF DEF(PG_PALS2)                 ; クリスタル：女の子の ポケギアの 色（PokegearFPals）も
FOR PG_I, 6
SECTION "pokegear white f {d:PG_I}", ROMX[PG_PALS2 + PG_I * 8], BANK[PG_PALS_BANK]
	dw $7fff
ENDR
ENDC
