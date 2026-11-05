; つりざおで、かならず 何かが かかる ように する（金 日本版）
;
; ・つりざお（ボロ・いい・すごい）を 水に むかって 使うと、元は「…… つれない」に なる ことが あるが、
;   かならず ポケモンが かかる ように する（つれる ポケモンの しゅるい・わりあいは 元の まま）。
;   水に むいて いない・つれる 場所で ない ときは 今までどおり。
;
; しくみ
;   ・Fish.Fish の「call Random / cp [hl] / jr nc, .no_bite」（つりの 場所ごとの かかる 確率）の jr nc を nop 2つに。
;
; 銀・クリスタルに 入れるとき：Fish.Fish の 場所（call Random / cp [hl] / jr nc の jr nc）を その ROM で さがして DEF を かえる
;   （クリスタルも 作りは 同じ）

IF !DEF(FB_ADDR)
DEF FB_ADDR            EQU $68e5      ; バンク$24 Fish.Fish の jr nc, .no_bite（30 1f）
DEF FB_BANK            EQU $24
ENDC

SECTION "fishbite", ROMX[FB_ADDR], BANK[FB_BANK]
	nop
	nop
