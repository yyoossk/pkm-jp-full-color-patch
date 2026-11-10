; ゲームコーナーの 景品の わざマシンに わざの 名前を 出す（銀 日本版。クリスタル追加機能キットの 52）
;   「わざマシン25　5500」→「25　かみなり　　　5500」（ピカチュウ版フルカラーと 同じ）
;   クリスタルは 見出しと 中身を 同じ バンクの 空きに おいたが、銀は コガネ（$13）・タマムシ（$27）の バンクに 空きが ない。
;   そこで、スクリプトの「loadmenu 見出し / verticalmenu」（4バイト）を「callasm 新しい 処理」（4バイト）に かえ、
;   新しい バンクで 見出しを 読んで VerticalMenu を よぶ（Script_loadmenu・Script_verticalmenu と 同じ ことを する）。
;   わざの 名前と 値段は 元の ゲームと 同じ（値段は スクリプトの checkcoins・takecoins が 元の まま）。
INCLUDE "src/charmap_jp.inc"

DEF PT_BANK            EQU $43        ; RM_SCRIPT_BANK（新しい バンク）
DEF PT_ADDR            EQU $4f00
DEF PT_LoadMenuHeader  EQU $1b59
DEF PT_UpdateSprites   EQU $191c
DEF PT_VerticalMenu    EQU $1ba0
DEF PT_wMenuCursorY    EQU $cf14
DEF PT_wScriptVar      EQU $d165

; スクリプトの loadmenu（$4f）見出し / verticalmenu（$58）→ callasm（$0e）
SECTION "prizetm goldenrod script", ROMX[$5ccc], BANK[$13]
	db $0e, PT_BANK
	dw PrizeTM_GoldenrodMenu
SECTION "prizetm celadon script", ROMX[$746e], BANK[$27]
	db $0e, PT_BANK
	dw PrizeTM_CeladonMenu

SECTION "prizetm", ROMX[PT_ADDR], BANK[PT_BANK]
PrizeTM_GoldenrodMenu:
	ld hl, PrizeTM_GoldenrodHeader
	jr PrizeTM_Menu
PrizeTM_CeladonMenu:
	ld hl, PrizeTM_CeladonHeader
PrizeTM_Menu:
	call PT_LoadMenuHeader            ; このバンクから 読む（wMenuDataBank ＝ この バンク）
	call PT_UpdateSprites
	call PT_VerticalMenu
	ld a, [PT_wMenuCursorY]
	jr nc, .ok
	xor a
.ok
	ld [PT_wScriptVar], a
	ret

PrizeTM_GoldenrodHeader:
	db $40                            ; MENU_BACKUP_TILES
	db 2, 0                           ; 上・左
	db 11, 17                         ; 下・右（元は 15）
	dw .data
	db 1
.data
	db $80 ; STATICMENU_CURSOR
	db 4
	db $f8, $fb, "　かみなり　　　　", $fb, $fb, $f6, $f6, "@"   ; わざマシン25 かみなり 5500
	db $f7, $fa, "　ふぶき　　　　　", $fb, $fb, $f6, $f6, "@"   ; わざマシン14 ふぶき 5500
	db $f9, $fe, "　だいもんじ　　　", $fb, $fb, $f6, $f6, "@"   ; わざマシン38 だいもんじ 5500
	db "やめる@"

PrizeTM_CeladonHeader:
	db $40
	db 2, 0
	db 11, 17
	dw .data
	db 1
.data
	db $80 ; STATICMENU_CURSOR
	db 4
	db $f9, $f8, "　かげぶんしん　　", $f7, $fb, $f6, $f6, "@"   ; わざマシン32 かげぶんしん 1500
	db $f8, $ff, "　サイコキネシス　", $f9, $fb, $f6, $f6, "@"   ; わざマシン29 サイコキネシス 3500
	db $f7, $fb, "　はかいこうせん　", $fd, $fb, $f6, $f6, "@"   ; わざマシン15 はかいこうせん 7500
	db "やめる@"
