; 戦闘で投げる モンスターボール・スーパーボール・ハイパーボール・マスターボール（と サファリゾーンの サファリボール）を それぞれの絵・色にする（日本版 銀）
; （クリスタル追加機能キットの ballgfx.asm を移植。絵と色は ピカチュウ版フルカラーの 投げるボールから作ったもの）
;
; ・マスター＝むらさきに M、ハイパー＝黒に 黄色の H、スーパー＝青に 赤い もよう、モンスター＝赤。
;   投げる・あたって開く・ゆれる・つかまえたあと残るボール・トレーナーにはじかれる の全部で その絵になる。
;   ほかのボール（ぼんぐりのボールなど）は元のまま。
; ・1つのボールで色を2つ使う（上半分・下半分）。OBJ パレット5（みどり）・6（あお）に入れる。
;   ボールを投げるアニメには みどり・あお を使う物は出てこない（けむり＝グレー、マスターボールのキラキラ＝ちゃいろ）。
;   どの技のアニメも はじめに パレット5・6 を 元の色に もどす。
; ・しくみ（バンク$33）
;   1. LoadBattleAnimGFX の call DecompressRequest2bpp（$6772）：ボールの絵（$21:$531f）を読むとき、
;      wCurItem のボールの絵（バンク$43:$6000、10タイル、圧縮なし）を Request2bpp で読む。
;      元の絵の 9・10番目のタイルは使っていないので、閉じたボールの右半分を入れてある。
;   2. GetBallAnimPal（$516c）：色を wOBPals1・wOBPals2 の パレット5・6 に入れ、ボールのパレットを 5 | $80（印）にする。
;   3. BattleAnimOAMUpdate の属性を作る所（$49ca）：印があれば 上の段 = 5、下の段・開いたボール = 6。
;      閉じたボールの右半分（データでは左を反転）は 反転しないで +8 のタイルにする（左右ちがう絵にできる）。
;   4. PlayBattleAnim の はじめの call BattleAnimAssignPals（$40ed）：その前に パレット5・6 を BattleObjectPals の元の色にもどす。
; ・金銀の wOBPals1・wOBPals2 は WRAM バンク0 なので、クリスタルのような WRAM バンクの切りかえはいらない。

DEF ANIM_BANK              EQU $33
DEF GetBallAnimPal         EQU $516c
DEF BallColors             EQU $5185
DEF BattleAnimAssignPals   EQU $47f7
DEF DecompressRequest2bpp  EQU $0d9c
DEF Request2bpp            EQU $0de7
DEF wCurItem               EQU $cffc
DEF wBattleAnimTempPalette EQU $ca21
DEF wOBPals1               EQU $c240
DEF wOBPals2               EQU $c2c0
DEF hCGBPalUpdate          EQU $ffe7
DEF BattleObjectPals_ROM   EQU $02 * $4000 + $5b9f - $4000   ; グレー・きいろ・あか・みどり・あお・ちゃいろ
DEF POKEBALL_GFX_BANK      EQU $21
DEF POKEBALL_GFX           EQU $531f
DEF BATTLEANIMSTRUCT_PALETTE  EQU 5
DEF BALL_PAL_TOP           EQU 5
DEF BALL_PAL_BOTTOM        EQU 6
DEF BALL_MARK              EQU $80
DEF MASTER_BALL EQU 1
DEF ULTRA_BALL  EQU 2
DEF GREAT_BALL  EQU 4
DEF POKE_BALL   EQU 5
DEF SAFARI_BALL_ITEM EQU $b3    ; サファリゾーンの 戦いで 投げる前に wCurItem に入れる 印（使われていない ITEM_B3）
DEF BALLGFX_BANK EQU $43

SECTION "ballgfx load hook", ROMX[$6772], BANK[ANIM_BANK]
	call BallGFX_Load
SECTION "ballgfx pal hook", ROMX[GetBallAnimPal], BANK[ANIM_BANK]
	jp BallGFX_Pal
SECTION "ballgfx attr hook", ROMX[$49ca], BANK[ANIM_BANK]
	call BallGFX_Attr            ; 元は ld a, [wBattleAnimTempPalette] / and $0f / or b
	nop
	nop
	nop
SECTION "ballgfx assign hook", ROMX[$40ed], BANK[ANIM_BANK]
	call BallGFX_AssignPals

SECTION "ballgfx code", ROMX[$7e40], BANK[ANIM_BANK]
; a = 0 マスター・1 ハイパー・2 スーパー・3 モンスター・4 サファリ、キャリー = ほかのボール（e をこわす）
BallGFX_Which:
	ld a, [wCurItem]
	cp MASTER_BALL
	jr z, .m
	cp ULTRA_BALL
	jr z, .u
	cp GREAT_BALL
	jr z, .g
	cp POKE_BALL
	jr z, .p
	cp SAFARI_BALL_ITEM
	jr z, .s
	scf
	ret
.s
	ld a, 4
	and a
	ret
.m
	xor a
	ret
.u
	ld a, 1
	ret
.g
	ld a, 2
	ret
.p
	ld a, 3
	and a
	ret

; hl = 絵（圧縮）、de = VRAM、b = バンク、c = タイルの数
BallGFX_Load:
	ld a, b
	cp POKEBALL_GFX_BANK
	jr nz, .orig
	ld a, h
	cp HIGH(POKEBALL_GFX)
	jr nz, .orig
	ld a, l
	cp LOW(POKEBALL_GFX)
	jr nz, .orig
	call BallGFX_Which
	jr c, .orig
	ld l, a
	ld h, 0
	ld a, l
	add a
	add a
	add l                        ; × 5
	ld l, a
	add hl, hl
	add hl, hl
	add hl, hl
	add hl, hl
	add hl, hl                   ; × 160
	push bc
	ld bc, BallGFX
	add hl, bc
	pop bc
	push de
	ld d, h
	ld e, l                      ; de = 新しい絵
	pop hl                       ; hl = VRAM
	ld b, BALLGFX_BANK
	jp Request2bpp
.orig
	jp DecompressRequest2bpp

; bc = ボールの アニメの構造体
BallGFX_Pal:
	call BallGFX_Which
	jr nc, .ours
	ld hl, BallColors
	jp GetBallAnimPal + 3
.ours
	ld hl, BATTLEANIMSTRUCT_PALETTE
	add hl, bc
	ld [hl], BALL_PAL_TOP | BALL_MARK
	add a
	add a
	add a
	add a                        ; × 16
	ld e, a
	ld d, 0
	ld hl, BallPals
	add hl, de
	ld d, h
	ld e, l
	ld hl, wOBPals1 + BALL_PAL_TOP * 8
	call .copy
	ld hl, wOBPals2 + BALL_PAL_TOP * 8
	call .copy
	ld a, 1
	ldh [hCGBPalUpdate], a
	ret
; de の16バイトを hl へ
.copy
	push de
	push bc
	ld c, 16
.loop
	ld a, [de]
	inc de
	ld [hli], a
	dec c
	jr nz, .loop
	pop bc
	pop de
	ret

; 属性：b = 反転など、hl = OAM データの属性、de = 書く所（1つ前がタイル）
BallGFX_Attr:
	ld a, [wBattleAnimTempPalette]
	bit 7, a
	jr nz, .ball
	and $0f
	or b
	ret
.ball
	push hl
	dec hl
	dec hl
	dec hl
	ld a, [hl]                   ; OAM データの Y
	pop hl
	cp -4                        ; 開いたボール（1段）
	jr z, .bottom
	cp -8
	jr z, .top
	call .closed_right
.bottom
	ld a, BALL_PAL_BOTTOM
	or b
	ret
.top
	call .closed_right
	ld a, BALL_PAL_TOP
	or b
	ret
; 閉じたボールの右半分（データで左右反転）→ 反転しないで +8 のタイル
.closed_right
	bit 5, [hl]
	ret z
	res 5, b
	dec de
	ld a, [de]
	add 8
	ld [de], a
	inc de
	ret

BallGFX_AssignPals:
	ld hl, .orig_pals
	ld de, wOBPals1 + BALL_PAL_TOP * 8
	ld c, 16
.loop
	ld a, [hli]
	ld [de], a
	inc de
	dec c
	jr nz, .loop
	jp BattleAnimAssignPals
.orig_pals
	INCBIN "base.gbc", BattleObjectPals_ROM + 3 * 8, 16      ; みどり・あお

BallPals:   ; マスター・ハイパー・スーパー・モンスター（上の色・下の色）
	INCLUDE "src/ballgfx_pals.inc"
	INCBIN "gfxdata/pikaballs.pal", 4 * 16, 16   ; サファリ（ピカチュウ版の 色。金の サファリゾーンと 同じ）

SECTION "ballgfx gfx", ROMX[$6000], BANK[BALLGFX_BANK]
BallGFX:   ; マスター・ハイパー・スーパー・モンスター・サファリ の順に 10タイルずつ
	INCBIN "gfxdata/balls_crystal.2bpp"
	INCBIN "gfxdata/pikaballs.2bpp", 4 * 160, 160   ; サファリ（金の tools/pikaballs_make.py で 作った絵。並びは 同じ）
