; なつき度のハート … クリスタル（日本版）用（金銀の src/hearts.asm と 同じ ことを する）
; クリスタルの つよさの 画面は 作りが ちがう：
;   ・ポケモンの 絵と うごきは VRAM バンク1 の タイルを 使う（色の 表の ビット3）。バンク0 の $42〜$5f は 町の 絵の のこり
;     （3ページ どれでも 使って いない。マップに もどる とき 読みなおされる）ので、ハートは バンク0 の $5e・$5f に 書く。
;     そのため 金の ような 色の 表の ビット3・文字の 写しは いらない。
;   ・1ページめの 右がわは 8・9行めが あいて いる（タイプ の 下、けいけんちの わくの 上）。hlcoord 9, 8 に「なつきど」、14, 8 から ハート 5こ。
;   ・LoadPinkPage（$13:$5ea9）は WaitBGMap で おわらず「ld hl, $c5f2 / ld [hl], $41 / ret」（$13:$5f5e）で おわるので、
;     その 前の「ld hl, $c5e9 / ld [hl], $40」から 10バイトを Hearts への farcall に し（ret は そのまま）、Hearts で $c5e9・$c5f2 に 書く。
INCLUDE "src/charmap_jp.inc"

DEF HT_HOOK            EQU $5f59      ; バンク$13 LoadPinkPage の さいごの 10バイト（ld hl, $c5e9 / ld [hl], $40 / ld hl, $c5f2 / ld [hl], $41）
DEF HT_HOOK_BANK       EQU $13
DEF HT_PlaceString     EQU $1057
DEF HT_wTempMonHappiness EQU $d0e9    ; wTempMon（$d0ce）＋ MON_HAPPINESS（$1b）
DEF HT_TILE            EQU $5e        ; ぬりつぶし（$5f は わく だけ）
DEF HT_VRAM            EQU $9000 + HT_TILE * 16
DEF HT_COORD           EQU $c4a0 + 8 * 20 + 9   ; hlcoord 9, 8
DEF HT_BANK            EQU $76
DEF HT_ADDR            EQU $6a00

SECTION "hearts hook", ROMX[HT_HOOK], BANK[HT_HOOK_BANK]
	ld a, BANK(Hearts)
	ld hl, Hearts
	rst $08
	nop
	nop
	nop
	nop                               ; つぎの ret（$5f63）は 元の まま

SECTION "hearts", ROMX[HT_ADDR], BANK[HT_BANK]
Hearts:
	ld a, $40                         ; 元の 命令（けいけんちの わくの 下の かど）
	ld [$c5e9], a
	ld a, $41
	ld [$c5f2], a
	; ハートの 絵を VRAM バンク0 の タイル $5e・$5f に（画面が ついて いるので STAT を 見て 1バイトずつ）
	di
	xor a
	ldh [$ff4f], a                    ; rVBK
	ld de, HeartsGFX
	ld hl, HT_VRAM
	ld c, 2 * 16
.copy
	ldh a, [$ff41]                    ; rSTAT
	and 2
	jr nz, .copy
	ld a, [de]
	ld [hli], a
	inc de
	dec c
	jr nz, .copy
	ei
	ld hl, HT_COORD
	ld de, .Label
	call HT_PlaceString
	; ハートの 数 ＝（なつき度 ＋ 50）÷ 51
	ld a, [HT_wTempMonHappiness]
	ld l, a
	ld h, 0
	ld de, 50
	add hl, de
	ld c, 0
	ld de, -51
.div
	ld a, h
	and a
	jr nz, .sub
	ld a, l
	cp 51
	jr c, .divdone
.sub
	add hl, de
	inc c
	jr .div
.divdone
	ld hl, HT_COORD + 5
	ld b, 5
.loop
	ld a, HT_TILE + 1                 ; わく だけ
	dec c
	bit 7, c
	jr nz, .put
	ld a, HT_TILE                     ; ぬりつぶし
.put
	ld [hli], a
	dec b
	jr nz, .loop
	ret

.Label db "なつきど@"

HeartsGFX:
	; ぬりつぶし（色3）
	db %01101100, %01101100
	db %11111110, %11111110
	db %11111110, %11111110
	db %11111110, %11111110
	db %01111100, %01111100
	db %00111000, %00111000
	db %00010000, %00010000
	db %00000000, %00000000
	; わく だけ
	db %01101100, %01101100
	db %10010010, %10010010
	db %10000010, %10000010
	db %10000010, %10000010
	db %01000100, %01000100
	db %00101000, %00101000
	db %00010000, %00010000
	db %00000000, %00000000
