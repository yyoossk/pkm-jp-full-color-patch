; ゲームコーナーの 景品の わざマシンに わざの 名前を 出す（金 日本版。クリスタル追加機能キットの 52）
;   「わざマシン25　5500」→「25　かみなり　　　5500」（ピカチュウ版フルカラーと 同じ）
;   コガネ（$13）・タマムシの 景品交換所（$27）の メニューの 見出し（MenuHeader。40 02 00 0b 0f ..）の 右はしを 15 → 17 に 広げ、
;   メニューの 中身（MenuData）を 同じ バンクに 新しく 置く。わざの 名前と 値段は 元の ゲームと 同じ。
; 金は どちらの バンクも 空きが ない（日本版 金の 文章には text_far が ない）ので、同じ バンクの 長い 文章を 1つずつ
; 空いた バンクに うつし、元の 場所の 頭を「text_asm（$08）→ うつした 文章を 出す」に して、のこりを 置き場所に した。
;   コガネ：$13:$68bd の 文章（252バイト。$13:$64f1 の writetext）
;   タマムシ：$27:$6dc0 の 文章（316バイト。$27:$6d5f の writetext）
INCLUDE "src/charmap_jp.inc"

DEF BASEROM EQUS "\"base.gbc\""
DEF PT_GOLDENROD_HEADER EQU $5d5c   ; バンク$13 MenuHeader（40 02 00 0b 0f 64 5d 01）
DEF PT_CELADON_HEADER   EQU $74fe   ; バンク$27 MenuHeader（40 02 00 0b 0f 06 75 01）
DEF PT_TEXT13           EQU $68bd
DEF PT_TEXT13_LEN       EQU 252
DEF PT_TEXT27           EQU $6dc0
DEF PT_TEXT27_LEN       EQU 316
DEF PT_DoTextUntilTerminator EQU $1286
DEF PT_BANK             EQU $45
DEF PT_ADDR             EQU $5c00

MACRO pt_head ; うつした 文章を 出す 頭（text_asm）
	db $08                            ; text_asm（jp hl）
	ld a, BANK(\1)
	ld hl, \1
	rst $08                           ; bc（文字の 場所）は そのまま もどる
	ld hl, PT_End\@
	ret
PT_End\@:
	db $50                            ; text_end
ENDM

SECTION "prizetm goldenrod header", ROMX[PT_GOLDENROD_HEADER + 4], BANK[$13]
	db 17
	dw PrizeTM_Goldenrod
SECTION "prizetm goldenrod", ROMX[PT_TEXT13], BANK[$13]
	pt_head PT_PrintText13
PrizeTM_Goldenrod:
	db $80 ; STATICMENU_CURSOR
	db 4
	db $f8, $fb, "　かみなり　　　　", $fb, $fb, $f6, $f6, "@"   ; わざマシン25 かみなり 5500
	db $f7, $fa, "　ふぶき　　　　　", $fb, $fb, $f6, $f6, "@"   ; わざマシン14 ふぶき 5500
	db $f9, $fe, "　だいもんじ　　　", $fb, $fb, $f6, $f6, "@"   ; わざマシン38 だいもんじ 5500
	db "やめる@"
	ASSERT @ <= PT_TEXT13 + PT_TEXT13_LEN

SECTION "prizetm celadon header", ROMX[PT_CELADON_HEADER + 4], BANK[$27]
	db 17
	dw PrizeTM_Celadon
SECTION "prizetm celadon", ROMX[PT_TEXT27], BANK[$27]
	pt_head PT_PrintText27
PrizeTM_Celadon:
	db $80 ; STATICMENU_CURSOR
	db 4
	db $f9, $f8, "　かげぶんしん　　", $f7, $fb, $f6, $f6, "@"   ; わざマシン32 かげぶんしん 1500
	db $f8, $ff, "　サイコキネシス　", $f9, $fb, $f6, $f6, "@"   ; わざマシン29 サイコキネシス 3500
	db $f7, $fb, "　はかいこうせん　", $fd, $fb, $f6, $f6, "@"   ; わざマシン15 はかいこうせん 7500
	db "やめる@"
	ASSERT @ <= PT_TEXT27 + PT_TEXT27_LEN

SECTION "prizetm texts", ROMX[PT_ADDR], BANK[PT_BANK]
PT_PrintText13:
	ld hl, PT_Text13
	jp PT_DoTextUntilTerminator
PT_PrintText27:
	ld hl, PT_Text27
	jp PT_DoTextUntilTerminator
PT_Text13:
	INCBIN BASEROM, $13 * $4000 + PT_TEXT13 - $4000, PT_TEXT13_LEN
PT_Text27:
	INCBIN BASEROM, $27 * $4000 + PT_TEXT27 - $4000, PT_TEXT27_LEN
