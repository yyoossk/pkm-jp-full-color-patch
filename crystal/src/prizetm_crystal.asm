; ゲームコーナーの 景品の わざマシンに わざの 名前を 出す（クリスタル 日本版）
;   「わざマシン25　5500」→「25　かみなり　　　5500」（ピカチュウ版フルカラーと 同じ）
;   コガネ（$15）・タマムシの 景品交換所（$1a）の メニューの 見出し（MenuHeader）の 右はしを 15 → 17 に 広げ、
;   メニューの 中身（MenuData）を 同じ バンクの 空き（元の ROM の 終わりの 0 の 所）に 新しく 置く。
;   わざの 名前と 値段は 元の ゲームと 同じ（値段は スクリプトの checkcoins・takecoins が 元の まま）。
INCLUDE "src/charmap_jp.inc"

DEF PT_GOLDENROD_HEADER EQU $625c   ; バンク$15 MenuHeader（40 02 00 0b 0f 64 62 01）
DEF PT_CELADON_HEADER   EQU $7491   ; バンク$1a MenuHeader（40 02 00 0b 0f 99 74 01）

SECTION "prizetm goldenrod header", ROMX[PT_GOLDENROD_HEADER + 4], BANK[$15]
	db 17
	dw PrizeTM_Goldenrod
SECTION "prizetm goldenrod", ROMX[$7f00], BANK[$15]
PrizeTM_Goldenrod:
	db $80 ; STATICMENU_CURSOR
	db 4
	db $f8, $fb, "　かみなり　　　　", $fb, $fb, $f6, $f6, "@"   ; わざマシン25 かみなり 5500
	db $f7, $fa, "　ふぶき　　　　　", $fb, $fb, $f6, $f6, "@"   ; わざマシン14 ふぶき 5500
	db $f9, $fe, "　だいもんじ　　　", $fb, $fb, $f6, $f6, "@"   ; わざマシン38 だいもんじ 5500
	db "やめる@"

SECTION "prizetm celadon header", ROMX[PT_CELADON_HEADER + 4], BANK[$1a]
	db 17
	dw PrizeTM_Celadon
SECTION "prizetm celadon", ROMX[$7f80], BANK[$1a]
PrizeTM_Celadon:
	db $80 ; STATICMENU_CURSOR
	db 4
	db $f9, $f8, "　かげぶんしん　　", $f7, $fb, $f6, $f6, "@"   ; わざマシン32 かげぶんしん 1500
	db $f8, $ff, "　サイコキネシス　", $f9, $fb, $f6, $f6, "@"   ; わざマシン29 サイコキネシス 3500
	db $f7, $fb, "　はかいこうせん　", $fd, $fb, $f6, $f6, "@"   ; わざマシン15 はかいこうせん 7500
	db "やめる@"
