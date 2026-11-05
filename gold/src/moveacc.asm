; 手持ちの「つかえるわざ」の 画面で、わざの 命中も 出す（金 日本版）
;
; ・手持ちの メニューの「つかえるわざ」で、下の わくの「タイプ／ノーマル　いりょく／　50」の 上の 行に
;       めいちゅう／ 95
;   と 出す（いりょく と 右を そろえる。命中は 0〜255 を ％に。×100÷255 を 四捨五入。戦闘の わざの 画面（35）と 同じ）。
;   命中の ない わざ（データが 0）も その まま 0 と 出さず「ー」に する。
;
; しくみ
;   ・PlaceMoveData の「hlcoord 1, 14 / predef PrintMoveDescription」（8バイト）を 新しい バンクの MoveAcc への farcall に
;     （のこり 2バイトは nop）。MoveAcc は せつめいを かいて から、Moves（$10:$5c6c）の その わざの 命中を 読んで
;     hlcoord 9, 11 に「めいちゅう／」、hlcoord 15, 11 から 3けたで かく（11行めは 12行めの 濁点の 行だが、
;     タイプの 名前 は x 6〜9 で 濁点は x 8 まで なので かさならない）。
;
; 銀・クリスタルに 入れるとき：下の DEF を その ROM の 値に する
;   （クリスタルは PlaceMoveData の 作り・文字の 場所が 同じか 確かめる）

INCLUDE "src/charmap_jp.inc"

IF !DEF(MA_HOOK)
DEF MA_HOOK            EQU $76a8      ; バンク$04 PlaceMoveData の hlcoord 1, 14 / ld a, PRINTMOVEDESCRIPTION / call Predef
DEF MA_HOOK_BANK       EQU $04
DEF MA_Predef          EQU $2e05
DEF MA_PREDEF_DESC     EQU $11        ; PrintMoveDescription
DEF MA_DESC_COORD      EQU $c4b9      ; hlcoord 1, 14
DEF MA_MOVES_BANK      EQU $10
DEF MA_Moves           EQU $5c6c      ; 1つ 7バイト（+4 命中）
DEF MA_GetFarByte      EQU $30e4
DEF MA_PlaceString     EQU $0f46
DEF MA_PrintNum        EQU $31f9
DEF MA_wCurSpecies     EQU $ce54      ; わざの 番号
DEF MA_wBuffer         EQU $d143      ; wTextDecimalByte（元の いりょく と 同じ）
DEF MA_COORD           EQU $c3a0 + 11 * 20 + 9   ; hlcoord 9, 11
DEF MA_BANK            EQU $45
DEF MA_ADDR            EQU $7800
ENDC

SECTION "moveacc hook", ROMX[MA_HOOK], BANK[MA_HOOK_BANK]
	ld a, BANK(MoveAcc)
	ld hl, MoveAcc
	rst $08
	nop
	nop

SECTION "moveacc", ROMX[MA_ADDR], BANK[MA_BANK]
MoveAcc:
	ld hl, MA_DESC_COORD
	ld a, MA_PREDEF_DESC
	call MA_Predef
	; 命中
	ld a, [MA_wCurSpecies]
	dec a
	ld l, a
	ld h, 0
	ld d, h
	ld e, l
	add hl, hl
	add hl, hl
	add hl, hl
	ld a, l
	sub e
	ld l, a
	ld a, h
	sbc d
	ld h, a                           ; × 7
	ld de, MA_Moves + 4
	add hl, de
	ld a, MA_MOVES_BANK
	call MA_GetFarByte
	push af
	ld hl, MA_COORD
	ld de, .Label
	call MA_PlaceString
	pop af
	and a
	jr nz, .acc
	ld a, $e3                         ; ー
	ld [MA_COORD + 8], a
	ret
.acc
	; ×100÷255 を 四捨五入
	ld l, a
	ld h, 0
	add hl, hl
	add hl, hl
	push hl                           ; ×4
	add hl, hl
	add hl, hl
	add hl, hl
	push hl                           ; ×32
	add hl, hl                        ; ×64
	pop de
	add hl, de
	pop de
	add hl, de
	ld de, 127
	add hl, de
	ld c, 0
	ld de, -255
.div
	ld a, h
	and a
	jr nz, .sub
	ld a, l
	cp 255
	jr c, .done
.sub
	add hl, de
	inc c
	jr .div
.done
	ld a, c
	ld [MA_wBuffer], a
	ld hl, MA_COORD + 6
	ld de, MA_wBuffer
	ld bc, $0103
	jp MA_PrintNum

.Label db "めいちゅう", $f3, "@"
