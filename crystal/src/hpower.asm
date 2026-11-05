; つよさの 画面の わざの ページに、めざめるパワーの タイプと 威力を 出す（金 日本版）
;
; ・「つよさを みる」の 2ページめ（緑・つかえるわざ）で、めざめるパワーを おぼえて いれば、その わざの 名前の 所を
;       めざパ　ほのお65
;   の ように する（めざパ・タイプ・威力。PP の 行は 元の まま）。タイプと 威力は 個体値で きまる（戦闘と 同じ 計算）。
; ・わざの ならびかえ（17）の あとも 書きなおされる。
;
; しくみ
;   ・LoadGreenPage の「farcall LoadStatsScreenPals」（6バイト）を 新しい バンクの HPower_Draw への farcall に。
;     HPower_Draw は LoadStatsScreenPals を 呼んで から、wTempMonMoves で めざめるパワー（$ed）を さがして、
;     その わざの 行（hlcoord 9, 6 から 3行 ずつ。1行 上は 濁点の 行）を けして かく。
;   ・タイプ：（こうげきの 個体値 & 3）× 4 ＋（ぼうぎょ & 3）→ かくとう・ひこう・どく・じめん・いわ・むし・ゴースト・はがね・
;     ほのお・みず・くさ・でんき・エスパー・こおり・ドラゴン・あく。名前は GetTypeName（$14:$4a87）。
;   ・威力：こうげき・ぼうぎょ・すばやさ・とくしゅ の 個体値の 8 の ビットを 8・4・2・1 に ならべた 数 × 5 ＋（とくしゅ & 3）を
;     2で わって 31 を 足す（31〜70）。
;
; 銀・クリスタルに 入れるとき：下の DEF を その ROM の 値に する
;   （銀は 金と 同じ 作り。クリスタルは LoadGreenPage の わざの 場所・LoadStatsScreenPals の 呼び方を 確かめる）

INCLUDE "src/charmap_jp.inc"

IF !DEF(HP_HOOK)
DEF HP_HOOK            EQU $5089      ; バンク$14 LoadGreenPage の farcall LoadStatsScreenPals
DEF HP_HOOK_BANK       EQU $14
DEF HP_Pals_BANK       EQU $02
DEF HP_Pals            EQU $5241      ; LoadStatsScreenPals
DEF HP_GetTypeName     EQU $4a87      ; バンク HP_HOOK_BANK（wNamedObjectIndex → wStringBuffer1）
DEF HP_PlaceString     EQU $0f46
DEF HP_PrintNum        EQU $31f9
DEF HP_wTempMonMoves   EQU $d007
DEF HP_wTempMonDVs     EQU $d01a
DEF HP_wNamedObjectIndex EQU $d143
DEF HP_wStringBuffer1  EQU $cf87
DEF HP_wBuffer         EQU $cf92      ; wStringBuffer1 の あと（威力 1バイト）
DEF HP_COORD           EQU $c3a0 + 6 * 20 + 9   ; 1つめの わざの 名前（hlcoord 9, 6）
DEF HIDDEN_POWER       EQU $ed
DEF HP_BANK            EQU $45
DEF HP_ADDR            EQU $7200
ENDC
IF !DEF(HP_GetTypeName_BANK)
DEF HP_GetTypeName_BANK EQU HP_HOOK_BANK
ENDC

SECTION "hpower hook", ROMX[HP_HOOK], BANK[HP_HOOK_BANK]
	ld a, BANK(HPower_Draw)
	ld hl, HPower_Draw
	rst $08
IF DEF(HP_HOOK_NOPS)
	REPT HP_HOOK_NOPS
	nop
	ENDR
ENDC

SECTION "hpower", ROMX[HP_ADDR], BANK[HP_BANK]
HPower_Draw:
IF DEF(HP_PP_PREDEF)
	; クリスタル：フックで けした「hlcoord ○○ / ld a, $3c / ld [wListMovesLineSpacing], a / predef ListMovePP」を する
	ld hl, HP_PP_COORD
	ld a, $3c
	ld [HP_wListMovesLineSpacing], a
	ld a, HP_PP_PREDEF
	call HP_Predef
ELSE
	ld a, HP_Pals_BANK
	ld hl, HP_Pals
	rst $08
ENDC
	; めざめるパワーは 何ばんめ？
	ld hl, HP_wTempMonMoves
	ld c, 0
.find
	ld a, [hli]
	cp HIDDEN_POWER
	jr z, .found
	inc c
	ld a, c
	cp 4
	jr c, .find
	ret
.found
	; hl = その わざの 行
	ld hl, HP_COORD
	ld de, 3 * 20
	ld a, c
	and a
	jr z, .row
.rowloop
	add hl, de
	dec c
	jr nz, .rowloop
.row
	push hl
	; けす（濁点の 行 と 名前の 行。x 9〜18）
	ld de, -20
	add hl, de
	ld c, 10
	ld a, $7f
.clear1
	ld [hli], a
	dec c
	jr nz, .clear1
	ld de, 20 - 10
	add hl, de
	ld c, 10
.clear2
	ld [hli], a
	dec c
	jr nz, .clear2
	pop hl
	push hl
	ld de, .Label
	call HP_PlaceString
	; タイプ
	ld a, [HP_wTempMonDVs]
	and 3
	add a
	add a
	ld b, a
	ld a, [HP_wTempMonDVs]
	swap a
	and 3
	add a
	add a
	ld c, a
	ld a, [HP_wTempMonDVs]
	and 3
	or c                              ; （こうげき & 3）× 4 ＋（ぼうぎょ & 3）
	inc a                             ; ノーマル を とばす
	cp 6                              ; BIRD
	jr c, .type
	inc a
	cp 10                             ; UNUSED_TYPES
	jr c, .type
	add $14 - 10
.type
	ld [HP_wNamedObjectIndex], a
	ld a, HP_GetTypeName_BANK
	ld hl, HP_GetTypeName
	rst $08
	pop hl
	push hl
	ld de, 4
	add hl, de
	ld de, HP_wStringBuffer1
	call HP_PlaceString
	; 威力
	ld a, [HP_wTempMonDVs]            ; こうげき・ぼうぎょ
	ld b, a
	swap a
	and %1000                         ; こうげき → 8
	ld c, a
	ld a, b
	and %1000
	srl a                             ; ぼうぎょ → 4
	or c
	ld c, a
	ld a, [HP_wTempMonDVs + 1]        ; すばやさ・とくしゅ
	ld b, a
	swap a
	and %1000
	srl a
	srl a                             ; すばやさ → 2
	or c
	ld c, a
	ld a, b
	and %1000
	srl a
	srl a
	srl a                             ; とくしゅ → 1
	or c
	ld c, a
	add a
	add a
	add c                             ; × 5
	ld c, a
	ld a, b
	and 3
	add c
	srl a
	add 31
	ld [HP_wBuffer], a
	pop hl
	ld de, 8
	add hl, de
	ld de, HP_wBuffer
	ld bc, $0102                      ; 1バイト・2けた
	jp HP_PrintNum

.Label db "めざパ@"
