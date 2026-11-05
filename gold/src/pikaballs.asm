; 戦闘で投げる モンスターボール・スーパーボール・ハイパーボール・マスターボール（と サファリボール）を、それぞれ固有の絵にする（金 日本版）
; 絵と色は ポケットモンスターピカチュウフルカラー の投げるボール（12×12ドット、上半分と下半分で別の色）から取った。
;
; 元のゲーム：どのボールも同じ絵（gfx/battle_anims/pokeball.png、10タイル）で、色（OBJ パレット1つ）だけちがう。
;   まっすぐの絵は 左の2タイルを左右反転して右に使っている（OAMSET_0A = OAMData_04）。
; 変えたあと（この4種類と サファリボール（wCurItem = $b3。サファリゾーンの 戦い）だけ。ほかのボール（ヘビーボールなど）は元のまま）：
;   1. LoadBattleAnimGFX：ボールの絵（BATTLE_ANIM_GFX_POKE_BALL）を読むとき、wCurItem がこの4つなら、そのボールの絵を読む。
;      並びは元と同じ（0・1 まっすぐの左、2〜5 かたむき、6・7 開いたとき）に、8・9 = まっすぐの右 を足した 10タイル。
;   2. GetBallAnimPal：このボールの OBJ パレットを「BALL_PAL | $80」にして（$80 = 印）、
;      BALL_PAL（上半分）・BALL_PAL+1（下半分）に このボールの色を書く（wOBPals2 = 画面に出す色だけ。
;      アニメが終わると BattleAnim_RevertPals が wOBPals1 から もどすので、ほかのわざの色は変わらない）。
;   3. BattleAnimOAMUpdate の属性を作る所：印のあるもの（このボールだけ）は
;      ・下の段（データの Y が 0 以上）は パレット+1
;      ・まっすぐの絵（OAMData_04）の右の2つ（左右反転）は、反転をやめて タイル+8（右の絵）
;      ・開いたときの下の絵（タイル7。0D）は パレット+1
;      （ボールの絵は いつもアニメの最初の絵なので、タイル番号 = BATTLEANIM_BASE_TILE + 番号）

DEF BALL_BANK          EQU $33      ; 戦闘アニメのバンク
DEF BALL_FREE          EQU $7e20    ; バンク$33 の空き（$7e1d〜）
DEF BALL_GFX_BANK      EQU $42      ; 絵を置くバンク（ジムリーダー再戦・せっていのとけい と同じバンクの空き）
DEF BALL_GFX_ADDR      EQU $6000
DEF LoadBattleAnimGFX  EQU $675f    ; push hl / ld l, a / ld h, 0 / …
DEF GetBallAnimPal     EQU $516c    ; ld hl, BallColors / …
DEF OAMUpdate_Pal      EQU $49ca    ; ld a, [wBattleAnimTempPalette] / and $0f（このあと or b / ld [de], a）
DEF OAMData_04_Attr2   EQU $729f + 4 + 3   ; まっすぐの絵の 右上（左右反転）の属性
DEF OAMData_04_Attr4   EQU $729f + 12 + 3  ; 右下
DEF DecompressRequest2bpp EQU $0d9c
DEF wCurItem           EQU $cffc
DEF wBattleAnimTempPalette EQU $ca21
DEF wOBPals2           EQU $c2c0
DEF hCGBPalUpdate      EQU $ffe7
DEF hCGB               EQU $ffe8
DEF BATTLE_ANIM_GFX_POKE_BALL EQU $0b
DEF BATTLEANIM_BASE_TILE EQU 49
DEF BATTLEANIMSTRUCT_PALETTE EQU 5
DEF BALL_PAL           EQU 5        ; 上半分 = 5（GREEN）、下半分 = 6（BLUE）。ボールのアニメでは使っていない
DEF BALL_TILES         EQU 10
DEF OAM_XFLIP          EQU $20
DEF PIKABALL_LZ_SIZE   EQU 5 * 33 + 1   ; 32バイトずつ5回 ＋ おわり

; ---- 1. 絵を読む所
SECTION "pikaballs gfx hook", ROMX[LoadBattleAnimGFX], BANK[BALL_BANK]
	jp PikaBall_LoadGFX
	nop
LoadBattleAnimGFX_Cont:             ; ld h, 0 のつぎ（$6763）

; ---- 2. 色
SECTION "pikaballs pal hook", ROMX[GetBallAnimPal], BANK[BALL_BANK]
	jp PikaBall_Pal
GetBallAnimPal_Cont:                ; ld a, [wCurItem] から（$516f）

; ---- 3. 属性
SECTION "pikaballs oam hook", ROMX[OAMUpdate_Pal], BANK[BALL_BANK]
	call PikaBall_OAM
	nop
	nop

SECTION "pikaballs code", ROMX[BALL_FREE], BANK[BALL_BANK]
; a = wCurItem → キャリーあり：5種類のどれか（e = 0 マスター・1 ハイパー・2 スーパー・3 モンスター・4 サファリ）
PikaBall_Index:
	ld e, 0
	cp 1                         ; MASTER_BALL
	jr z, .yes
	inc e
	cp 2                         ; ULTRA_BALL
	jr z, .yes
	inc e
	cp 4                         ; GREAT_BALL
	jr z, .yes
	inc e
	cp 5                         ; POKE_BALL
	jr z, .yes
	inc e
	cp $b3                       ; サファリボール（サファリゾーンの 戦いで wCurItem に入れる。ITEM_B3 は 使われていない）
	jr z, .yes
	and a
	ret
.yes
	scf
	ret

PikaBall_LoadGFX:
	cp BATTLE_ANIM_GFX_POKE_BALL
	jr nz, .orig
	ld a, [wCurItem]
	call PikaBall_Index
	jr c, .ours
	ld a, BATTLE_ANIM_GFX_POKE_BALL
.orig
	push hl
	ld l, a
	ld h, 0
	jp LoadBattleAnimGFX_Cont
.ours
	; de = 絵のLZ（e × PIKABALL_LZ_SIZE）
	ld d, 0
	push hl                      ; 書く先（VRAM）
	ld hl, PikaBallGFXTable
	add hl, de
	add hl, de
	ld a, [hli]
	ld h, [hl]
	ld l, a
	pop de
	ld bc, (BALL_GFX_BANK << 8) | BALL_TILES
	push bc
	call DecompressRequest2bpp
	pop bc                       ; c = タイルの数（呼んだ所が使う）
	ret

PikaBall_Pal:
	ld a, [wCurItem]
	call PikaBall_Index
	jr c, .ours
	ld hl, $5185                 ; BallColors（元の ld hl, BallColors）
	jp GetBallAnimPal_Cont
.ours
	ld hl, BATTLEANIMSTRUCT_PALETTE
	add hl, bc
	ld [hl], BALL_PAL | $80
	ldh a, [hCGB]
	and a
	ret z
	push bc
	ld a, e
	swap a                       ; × 16（上・下 2つのパレット）
	ld e, a
	ld d, 0
	ld hl, PikaBallPals
	add hl, de
	ld de, wOBPals2 + BALL_PAL * 8
	ld c, 16
.copy
	ld a, [hli]
	ld [de], a
	inc de
	dec c
	jr nz, .copy
	pop bc
	ld a, 1
	ldh [hCGBPalUpdate], a
	ret

; 属性の パレットの部分を返す（hl = OAM データの属性、de = OAM の属性、[de-1] = タイル、b = 反転など）
PikaBall_OAM:
	ld a, [wBattleAnimTempPalette]
	bit 7, a
	jr nz, .ball
	and $0f
	ret
.ball
	and $07
	push af
	; まっすぐの絵の右の2つ：反転をやめて 右の絵（タイル+8）
	ld a, h
	cp HIGH(OAMData_04_Attr2)
	jr nz, .no_remap
	ld a, l
	cp LOW(OAMData_04_Attr2)
	jr z, .remap
	cp LOW(OAMData_04_Attr4)
	jr nz, .no_remap
.remap
	dec de
	ld a, [de]
	add 8
	ld [de], a
	inc de
	ld a, b
	xor OAM_XFLIP
	ld b, a
.no_remap
	; 開いたときの下の絵（タイル7）は 下半分の色
	dec de
	ld a, [de]
	inc de
	cp BATTLEANIM_BASE_TILE + 7
	jr z, .bottom
	; データの Y が 0 以上なら 下の段
	push hl
	dec hl
	dec hl
	dec hl
	bit 7, [hl]
	pop hl
	jr z, .bottom
	pop af
	ret
.bottom
	pop af
	inc a
	ret

PikaBallGFXTable:
FOR I, 5
	dw PikaBallLZ + I * PIKABALL_LZ_SIZE
ENDR

PikaBallPals:                       ; マスター・ハイパー・スーパー・モンスター・サファリ（上・下）
	INCBIN "gfxdata/pikaballs.pal"

; ---- 絵（LZ。そのままの並びのコマンドだけ。1つ 32バイトまで）
SECTION "pikaballs gfx", ROMX[BALL_GFX_ADDR], BANK[BALL_GFX_BANK]
PikaBallLZ:
FOR I, 5
FOR J, 5
	db $1f                       ; そのまま 32バイト
	INCBIN "gfxdata/pikaballs.2bpp", I * 160 + J * 32, 32
ENDR
	db $ff
ENDR
