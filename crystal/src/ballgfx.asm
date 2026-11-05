; 戦闘で投げる モンスターボール・スーパーボール・ハイパーボール・マスターボール（と サファリボール）を それぞれの絵にする（クリスタル日本版）
; ・サファリボール：サファリゾーンの 戦いでは 投げる前に wCurItem を $b3（使われていない ITEM_B3）にするので、それを 印に
;   サファリボールの 絵（gfxdata・ballgfx_gfx.inc の 5つめ）と 色（ROM0 $3f7f の BallPal_Safari）を読む。
;
; ・絵と色は ピカチュウ版フルカラーの 投げるボールの絵から作った（src/ballgfx_data.inc、gfxdata/balls_crystal.2bpp）。
;   投げる・ゆれる・開く・トレーナーにはじかれる の全部で その絵になる。ほかのボールは元のまま。
; ・しくみ
;   1. LoadBattleAnimGFX：ボールの絵（BATTLE_ANIM_GFX_POKE_BALL）を読むとき、使ったボール（wCurItem）の絵を読む。
;      元のボールの絵は 10タイルで、9・10番目は使っていないので、閉じたボールの右半分を そこに入れる。
;   2. GetBallAnimPal：上半分の色を OBJ パレット5、下半分の色を 6 に入れ（wOBPals1・wOBPals2 の両方）、
;      ボールの「パレット」を 5 | $80（$80 = この4つのボールの印）にする。
;   3. BattleAnimOAMUpdate の属性を作る所：印があれば、下の段・開いたボール は パレット6、上の段は 5。
;      閉じたボールの 左右反転で描く右半分は、反転せずに 9・10番目のタイルを使う（左右ちがう絵にできる）。
;   4. _PlayBattleAnim のはじめ：パレット5・6（みどり・あお）を 元の色にもどす（つかまえたあとのボールは そのままの色で残る）。

DEF ANIM_BANK              EQU $33
DEF LoadBattleAnimGFX      EQU $681b
DEF GetBallAnimPal         EQU $521e
DEF BallColors             EQU $5241
DEF BattleAnimAssignPals   EQU $4895
DEF DecompressRequest2bpp  EQU $0e5d
DEF wCurItem               EQU $d0c6     ; WRAM バンク1
DEF wBattleAnimTempPalette EQU $d421
DEF wOBPals1               EQU $d040     ; WRAM バンク5
DEF wOBPals2               EQU $d0c0
DEF hCGBPalUpdate          EQU $ffe5
DEF rWBK                   EQU $ff70
DEF BattleObjectPals_ROM   EQU $02 * $4000 + $5759 - $4000   ; グレー・きいろ・あか・みどり・あお・ちゃいろ
DEF BATTLE_ANIM_GFX_POKE_BALL EQU $0b
DEF BATTLEANIMSTRUCT_PALETTE  EQU 5
DEF BALL_PAL_TOP           EQU 5
DEF BALL_PAL_BOTTOM        EQU 6
DEF BALL_MARK              EQU $80
DEF MASTER_BALL EQU 1
DEF ULTRA_BALL  EQU 2
DEF GREAT_BALL  EQU 4
DEF POKE_BALL   EQU 5
DEF SAFARI_BALL_MARK EQU $b3   ; サファリゾーンの 戦いで wCurItem に入れる印（使われていない ITEM_B3）
DEF BALLGFX_BANK EQU $70

SECTION "ballgfx load hook", ROMX[LoadBattleAnimGFX], BANK[ANIM_BANK]
	jp BallGFX_Load
	nop
SECTION "ballgfx pal hook", ROMX[GetBallAnimPal], BANK[ANIM_BANK]
	jp BallGFX_Pal
SECTION "ballgfx attr hook", ROMX[$4a7c], BANK[ANIM_BANK]
	call BallGFX_Attr
	nop
	nop
	nop
SECTION "ballgfx assign hook", ROMX[$40fb], BANK[ANIM_BANK]
	call BallGFX_AssignPals

SECTION "ballgfx code", ROMX[$7ee0], BANK[ANIM_BANK]
; a = 0 マスター・1 ハイパー・2 スーパー・3 モンスター・4 サファリ、キャリー = ほかのボール
BallGFX_Which:
	ldh a, [rWBK]
	push af
	ld a, 1
	ldh [rWBK], a
	ld a, [wCurItem]
	ld e, a
	pop af
	ldh [rWBK], a
	ld a, e
	cp MASTER_BALL
	jr z, .m
	cp ULTRA_BALL
	jr z, .u
	cp GREAT_BALL
	jr z, .g
	cp POKE_BALL
	jr z, .p
	cp SAFARI_BALL_MARK
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

; hl = 絵を置く VRAM、a = 絵の番号
BallGFX_Load:
	cp BATTLE_ANIM_GFX_POKE_BALL
	jr nz, .orig
	push hl
	call BallGFX_Which
	pop hl
	jr c, .orig_ball
	push hl
	ld e, a
	ld d, 0
	ld hl, .gfx
	add hl, de
	add hl, de
	ld a, [hli]
	ld h, [hl]
	ld l, a
	pop de
	ld bc, (BALLGFX_BANK << 8) | 10
	push bc
	call DecompressRequest2bpp
	pop bc
	ret
.orig_ball
	ld a, BATTLE_ANIM_GFX_POKE_BALL
.orig
	push hl
	ld l, a
	ld h, 0
	jp LoadBattleAnimGFX + 4
.gfx
	dw BallGFX_Master, BallGFX_Ultra, BallGFX_Great, BallGFX_Poke, BallGFX_Safari

; bc = ボールの アニメの構造体
BallGFX_Pal:
	push bc
	call BallGFX_Which
	pop bc
	jr nc, .ours
	ld hl, BallColors
	jp GetBallAnimPal + 3
.ours
	ld hl, BATTLEANIMSTRUCT_PALETTE
	add hl, bc
	ld [hl], BALL_PAL_TOP | BALL_MARK
	ld de, BallPal_Safari        ; サファリボールの色は ROM0 の 別の空き
	cp 4
	jr z, .got_pal
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
.got_pal
	ld hl, wOBPals1 + BALL_PAL_TOP * 8
	call .copy
	ld hl, wOBPals2 + BALL_PAL_TOP * 8
	call .copy
	ld a, 1
	ldh [hCGBPalUpdate], a
	ret
; de の16バイトを hl へ（WRAM バンク5）
.copy
	ldh a, [rWBK]
	push af
	ld a, 5
	ldh [rWBK], a
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
	pop af
	ldh [rWBK], a
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
	ldh a, [rWBK]
	push af
	ld a, 5
	ldh [rWBK], a
	ld hl, .orig_pals
	ld de, wOBPals1 + BALL_PAL_TOP * 8
	ld c, 16
.loop
	ld a, [hli]
	ld [de], a
	inc de
	dec c
	jr nz, .loop
	pop af
	ldh [rWBK], a
	jp BattleAnimAssignPals

; 色のデータは ROM0 の空き（$0070〜、バンク$33 の空きが足りないため）
SECTION "ballgfx safari pal", ROM0[$3f7f]   ; ROM0 の空き（$0070〜 の 4つの色の あとには 空きがない）
BallPal_Safari:                       ; サファリボール（ピカチュウ版）：上・下
	db $ff, $7f, $52, $2b, $c5, $15, $42, $08, $ff, $7f, $9e, $5b, $52, $2b, $42, $08

SECTION "ballgfx pals", ROM0[$0070]
BallGFX_AssignPals.orig_pals
	INCBIN "base.gbc", BattleObjectPals_ROM + 3 * 8, 16      ; みどり・あお
BallPals:
	INCLUDE "src/ballgfx_pals.inc"

SECTION "ballgfx gfx", ROMX[$5800], BANK[BALLGFX_BANK]
	INCLUDE "src/ballgfx_gfx.inc"
