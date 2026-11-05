; ルギア・ホウオウの 専用わざ（src/sigmove.asm）の クリスタル日本版の値
; tools/sigmove_find.py（パッチを入れる前の ROM）で出した値 ＋ 空きの場所
DEF SIG_BANK           EQU $10
DEF SIG_PTR_LUGIA      EQU $6943
DEF SIG_PTR_HOOH       EQU $6945
DEF SIG_FREE           EQU $7e40    ; バンク$10 の空き（表は $7dfc まで）
DEF SIG_LUGIA_WILD_BANK EQU $1c    ; うずまきじまの ルギア（loadwildmon LUGIA, 60 の レベルの所）
DEF SIG_LUGIA_WILD     EQU $4ad4
DEF SIG_HOOH_WILD_BANK EQU $1a     ; スズのとうの ホウオウ（loadwildmon HO_OH, 60 の レベルの所）
DEF SIG_HOOH_WILD      EQU $5f62
DEF SIG_WILD_LEVEL     EQU 40      ; 両方 レベル40 にする
