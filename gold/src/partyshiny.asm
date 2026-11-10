; 手持ちの 画面で、色ちがいの ポケモンに ★を 出す（金 日本版）
;
; ・手持ちの 画面（戦闘の 入れかえ・交換・そだてや など 手持ちを えらぶ 画面 ぜんぶ）で、色ちがいの ポケモンの
;   名前の 右上（「：Ｌ」の 上）に ★を 出す。タマゴには 出さない。
; ・色ちがいかは 個体値で みる（ぼうぎょ・すばやさ・とくしゅ が 10、こうげきが 2・3・6・7・10・11・14・15）。
;
; しくみ
;   ・PlacePartyNicknames の さいご（「やめる」を かく「ld de, .CancelString / call PlaceString / ret」7バイト）を
;     新しい バンクの PartyShiny への farcall に。PartyShiny は「やめる」を かいて から ★を かく。
;   ・★の 絵は 背景の タイル $5e（$95e0）に 書く（画面が ついて いる ことが あるので STAT を 見て 1バイトずつ）。
;     $5e は 戦闘では 使われて いない（あいての 絵 $00〜$30・自分の 絵 $31〜$54・けいけんちの バー と つかまえた 印 $55〜$5d）。
;     町では 地図の タイルだが、手持ちの 画面を とじる ときは かならず 地図の タイルを 読みなおす（ReloadTilesetAndPalettes）ので
;     もとに もどる。VRAM の バンク1 を 使うと、手持ちの 画面の 上に 出る メニュー（いあいぎり・つよさを みる など）で
;     その ますの 文字が きえるので 使わない。
;
; 銀・クリスタルに 入れるとき：下の DEF を その ROM の 値に する
;   （銀は 金と 同じ 作り。クリスタルは 手持ちの 画面の 名前の 場所と、戦闘で タイル $5e が 空いて いるかを 確かめる）

INCLUDE "src/charmap_jp.inc"

DEF PS_FOLLOW_MARK EQU 1             ; 連れ歩き（follow_gold.asm）を 入れて いる
IF !DEF(PS_HOOK)
DEF PS_HOOK            EQU $40be      ; バンク$14 PlacePartyNicknames .end の ld de, .CancelString / call PlaceString / ret
DEF PS_HOOK_BANK       EQU $14
DEF PS_PlaceString     EQU $0f46
DEF PS_wPartyCount     EQU $d9e8
DEF PS_wPartySpecies   EQU $d9e9
DEF PS_wPartyMon1DVs   EQU $da05
DEF PS_MONLEN          EQU $30
DEF PS_EGG             EQU $fd
DEF PS_TILE            EQU $5e
DEF PS_VRAM            EQU $9000 + PS_TILE * 16
DEF PS_COORD           EQU $c3a0 + 8      ; hlcoord 8, 0（1ぴきめ。2行 ごと）
DEF PS_BANK            EQU $45
DEF PS_ADDR            EQU $6e00
ENDC

SECTION "partyshiny hook", ROMX[PS_HOOK], BANK[PS_HOOK_BANK]
	ld a, BANK(PartyShiny)
	ld hl, PartyShiny
	rst $08
	ret

SECTION "partyshiny", ROMX[PS_ADDR], BANK[PS_BANK]
PartyShiny:
	; 「やめる」（hlcoord 1, 1 ＋ 2行 × 手持ちの 数）
	ld hl, $c3a0 + 20 + 1
	ld de, 2 * 20
	ld a, [PS_wPartyCount]
	and a
	jr z, .cancel
.cancel_row
	add hl, de
	dec a
	jr nz, .cancel_row
.cancel
	ld de, .Cancel
	call PS_PlaceString
	; ★の 絵
	ld de, StarGFX
	ld hl, PS_VRAM
	ld c, 16
.copy
	di
.wait
	ldh a, [$ff41]                    ; rSTAT
	and 2
	jr nz, .wait
	ld a, [de]
	ld [hli], a
	ei
	inc de
	dec c
	jr nz, .copy
	; 色ちがいの ポケモンの 行に ★
	ld hl, PS_COORD
	ld b, 0
.slot
	push hl
	call .IsShiny
	pop hl
	jr nc, .next
	ld [hl], PS_TILE
.next
	ld de, 2 * 20
	add hl, de
	inc b
	ld a, b
	cp 6
	jr c, .slot
IF DEF(PS_FOLLOW_MARK)
	; 連れ歩く ポケモンの ★（follow_gold.asm）
	ld a, BANK(Fw_PartyMark)
	ld hl, Fw_PartyMark
	rst $08
ENDC
	ret

; b ばんめ が 色ちがい なら キャリー（b は かえない）
.IsShiny
	ld a, [PS_wPartyCount]
	cp b
	jr c, .no                         ; 手持ちの 外
	jr z, .no
	ld hl, PS_wPartySpecies
	ld e, b
	ld d, 0
	add hl, de
	ld a, [hl]
	cp PS_EGG
	jr z, .no
	ld hl, PS_wPartyMon1DVs
	ld de, PS_MONLEN
	ld a, b
	and a
	jr z, .dv
.dvloop
	add hl, de
	dec a
	jr nz, .dvloop
.dv
	ld a, [hli]
	ld e, a                           ; こうげき・ぼうぎょ
	ld a, [hl]
	cp $aa                            ; すばやさ・とくしゅ
	jr nz, .no
	ld a, e
	and $0f
	cp $0a
	jr nz, .no
	bit 5, e
	jr z, .no
	scf
	ret
.no
	and a
	ret

.Cancel db "やめる@"

StarGFX:
	db %00010000, %00010000
	db %00010000, %00010000
	db %00111000, %00111000
	db %11111110, %11111110
	db %01111100, %01111100
	db %00111000, %00111000
	db %01101100, %01101100
	db %01000100, %01000100
