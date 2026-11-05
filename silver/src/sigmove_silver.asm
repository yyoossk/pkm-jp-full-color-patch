INCLUDE "src/sigmove_silver.inc"
INCLUDE "src/sigmove.asm"

; セレビィの表を うつす（中身は 元と同じ）
SECTION "sigmove celebi ptr", ROMX[SIG_CELEBI_PTR], BANK[SIG_BANK]
	dw SigMove_CelebiEvosAttacks
SECTION "sigmove celebi list", ROMX[SIG_CELEBI_NEW], BANK[SIG_BANK]
SigMove_CelebiEvosAttacks:
	db 0
	db 1, $49    ; やどりぎのタネ
	db 1, $5d    ; ねんりき
	db 1, $69    ; じこさいせい
	db 1, $d7    ; いやしのすず
	db 10, $db   ; しんぴのまもり
	db 20, $f6   ; げんしのちから
	db 30, $f8   ; みらいよち
	db 40, $e2   ; バトンタッチ
	db 50, $c3   ; ほろびのうた
	db 0
	ASSERT SIG_FREE + 48 <= SIG_CELEBI_NEW
	ASSERT @ <= $8000
