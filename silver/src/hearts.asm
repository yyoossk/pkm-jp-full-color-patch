; つよさの 画面に なつき度を ハートで 出す（金 日本版）
;
; ・つよさの 画面の 1ページめ（ピンク）の「タイプ」の 下に「なつきど　♥♥♡♡♡」のように 5この ハートで 出す。
;   ハートの 数 ＝（なつき度 ＋ 50）÷ 51（0〜255 → 0〜5。つかまえた ばかり（70）は 2、さいだい（255）は 5）。
; ・ハートの 絵は 2まい（ぬりつぶし・わく だけ）。VRAM の バンク1 の タイル $5e・$5f に 読みこむ。
;
; しくみ
;   ・LoadPinkPage の さいごの「call WaitBGMap」を バンク$14 の 空きの Hearts_Stub に（Hearts を farcall して から WaitBGMap）。
;   ・Hearts：ハートの 絵を VRAM バンク1 の タイル $5e・$5f（$95e0）に 書き（画面が ついて いるので STAT を 見て 1バイトずつ）、
;     hlcoord 9, 8 に「なつきど」、hlcoord 14, 8 から ハート 5こ（その 5ますの 色の 表（VRAM バンク1 の $9800〜 と wAttrmap）の ビット3 ＝ バンク1 の タイル）。
;     バンク0 の $42〜$5f は ポケモンの 絵の うごき（アニメ）に 使われるので バンク1 に した。
;     ページを かえても その 5ますの ビット3 は のこるので、ほかの ページで そこに 出る 文字（のうりょくの 数字・濁点）を
;     バンク1 の 同じ 番号にも 写して おく（空白 $7f は バンク1 も 空白）。
;   ・なつき度は wTempMonHappiness（$d020）。
;
; 銀・クリスタルに 入れるとき：下の DEF を その ROM の 値に する
;   （使って いない タイルは つよさの 画面の 3ページ ぜんぶで 使って いない もの を えらぶ。
;     クリスタルは つよさの 画面の 作りが ちがうので 空いて いる 行と 場所を 見なおす）

INCLUDE "src/charmap_jp.inc"

IF !DEF(HT_HOOK)
DEF HT_HOOK            EQU $4f8e      ; バンク$14 LoadPinkPage の call WaitBGMap
DEF HT_HOOK_BANK       EQU $14
DEF HT_STUB            EQU $7fc8      ; バンク$14 の 空き（9バイト）
DEF HT_WaitBGMap       EQU $33ae
DEF HT_PlaceString     EQU $0f46
DEF HT_wTempMonHappiness EQU $d020
DEF HT_TILE            EQU $5e        ; ぬりつぶし（$5f は わく だけ）
DEF HT_VRAM            EQU $9000 + HT_TILE * 16
DEF HT_COORD           EQU $c3a0 + 8 * 20 + 9   ; hlcoord 9, 8
DEF HT_ATTR            EQU $cccd + 8 * 20 + 9   ; wAttrmap の 同じ 所
DEF HT_BANK            EQU $45
DEF HT_ADDR            EQU $6b00
ENDC

SECTION "hearts hook", ROMX[HT_HOOK], BANK[HT_HOOK_BANK]
	call Hearts_Stub
SECTION "hearts stub", ROMX[HT_STUB], BANK[HT_HOOK_BANK]
Hearts_Stub:
	ld a, BANK(Hearts)
	ld hl, Hearts
	rst $08
	jp HT_WaitBGMap

SECTION "hearts", ROMX[HT_ADDR], BANK[HT_BANK]
Hearts:
	; ハートの 絵を VRAM の バンク1 に（バンク0 の $42〜$5f は ポケモンの 絵の うごきに 使われる）
	; 画面が ついて いるので、1バイトずつ VRAM に 書ける とき（STAT の モード 0・1）を まって 書く
	di
	ld a, 1
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
	; ほかの ページで この 5ますに 出る 文字（数字 $f6〜$ff・濁点 $e4・$e5）を バンク1 にも 写す
	; （ページを かえても 色の 表の ビット3 は のこるので、のうりょくの 数字 などが バンク1 から 出る）
	ld hl, $8800 + ($e4 - $80) * 16
	ld c, 2 * 16
	call .Mirror
	ld hl, $8800 + ($f6 - $80) * 16
	ld c, 10 * 16
	call .Mirror
	xor a
	ldh [$ff4f], a
	ei
	; ハートの 5ますは バンク1 の タイル：画面の 色の 表（VRAM バンク1 の $9800〜）の ビット3 を たてる。
	; wAttrmap にも たてる（あとで 画面を かきなおす ときの ため）
	ld hl, HT_ATTR + 5
	ld b, 5
.attr
	set 3, [hl]
	inc hl
	dec b
	jr nz, .attr
	di
	ld a, 1
	ldh [$ff4f], a
	ld hl, $9800 + 8 * 32 + 9 + 5
	ld b, 5
.vattr
	ldh a, [$ff41]
	and 2
	jr nz, .vattr
	ld a, [hl]
	or 8
	ld c, a
.vattr2
	ldh a, [$ff41]
	and 2
	jr nz, .vattr2
	ld [hl], c
	inc hl
	dec b
	jr nz, .vattr
	xor a
	ldh [$ff4f], a
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

; hl から c バイト：バンク0 の 中身を バンク1 の 同じ 所へ（rVBK = 1 で 呼ぶ）
.Mirror
	xor a
	ldh [$ff4f], a
.mwait1
	ldh a, [$ff41]
	and 2
	jr nz, .mwait1
	ld b, [hl]
	ld a, 1
	ldh [$ff4f], a
.mwait2
	ldh a, [$ff41]
	and 2
	jr nz, .mwait2
	ld [hl], b
	inc hl
	dec c
	jr nz, .Mirror
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
