; 場所の名前の看板をクリスタルと同じ見た目・色にし、下からスッと出て、スッと引っこむようにする
; （その１の「場所の名前に人物が重なる」の直しも、ここで作りなおす）
;
; キットの看板の処理（バンク $13）をそのまま使い、次の所をかえる。
;  1. 枠のタイル13まいを、看板を出すたびに VRAM バンク1 のタイル $51〜$5D に読みこむ
;  2. 看板のバッファ（20x4）に、白黒の枠のかわりにクリスタルの枠を書く。空白は中のタイルにする
;  3. 名前を3行めの真ん中に置く（左はし = (20 - 文字数) / 2）
;  4. ウインドウへ書く時、どのマスも属性 $0F（VRAM バンク1・パレット7）にし、
;     名前の字形は「地を色1、字を色3」で読みこむ
;  5. 看板を出す時に BG パレット7 の色1・2を看板の色にかえ、引っこんだら元にもどす
;  6. VBlank で、hWY が $70 なら上へ、$90 なら下へ、ウインドウを1フレーム2ドットずつうごかす
;     （hWY はさわらず rWY に書く）。看板のあいだは、看板の行にかかるスプライトをかくす

IF HAS_PLACE_SIGN

DEF SIGN_TILE_BASE EQU $50          ; 枠のタイル k（1〜13）は SIGN_TILE_BASE + k
DEF SIGN_TILE_INSIDE EQU SIGN_TILE_BASE + 13
DEF SIGN_ATTR EQU $0F               ; VRAM バンク1・パレット7
DEF SIGN_TOP_Y EQU $70              ; 看板が出きった時のウインドウの位置
DEF SIGN_HIDDEN_Y EQU $90
DEF SIGN_SPEED EQU 2

; キットの看板の処理と、バンク0の処理（どの版も同じ番地）
DEF wSignBuffer EQU $CD7C           ; 看板のバッファ 20x4
DEF wSignName EQU $CD68             ; 名前の文字列（$50 まで）
DEF KitSignToWindow EQU $4D27       ; バッファをウインドウ（$9C00）へ書く
DEF KitWaitVRAM EQU $4DB1           ; VRAM に書ける時まで待つ
DEF KitGlyphLoopEnd EQU $4DAF
DEF rVBK EQU $FF4F
DEF rWY EQU $FF4A
DEF wDisableVBlankWYUpdate EQU $D07D

; 看板の動きの RAM（使っていない WRAM バンク7）
DEF SIGN_WRAM_BANK EQU 7
DEF wSignMark EQU $D000             ; しるし $A5,$5A
DEF wSignY EQU $D002                ; 今のウインドウの高さ
DEF wSignActive EQU $D003           ; 看板が出ている（出入りの途中もふくむ）
DEF wSignOrigSVBK EQU $D004         ; VBlank に入った時の WRAM バンク
DEF wSignSavedPal EQU $D005         ; パレット7 の色1・2 の元の色（4バイト）

; カラー化のパレット（WRAM バンク2）
DEF W2_BgPals EQU $D000             ; もとの色
DEF W2_PalReload EQU $D788          ; 1 にすると、もとの色から今の色を作りなおす
DEF SIGN_PAL_OFFSET EQU 7 * 8 + 2   ; パレット7 の色1

DEF SIGN_COLOR1 EQU 31 | (31 << 5) | (16 << 10)   ; うすい黄色
DEF SIGN_COLOR2 EQU 14 | (9 << 5) | (0 << 10)     ; 茶色

; --- 看板を書く所（キットの処理の中）-------------------------------------------

; 名前を置いてウインドウへ書く所（ld hl, $CDA6 / ld de, $CD68 / call PlaceString / call $4D27）
SECTION "看板 名前とウインドウ", ROMX[$4CC4], BANK[$13]
	call SignDrawCrystal
	ds 9, 0   ; nop

; ウインドウへ書く時の属性：どのマスも SIGN_ATTR（di / ld c, SIGN_ATTR / jr $4D4F）
SECTION "看板 属性", ROMX[$4D3C], BANK[$13]
	di
	ld c, SIGN_ATTR
	jr @ + 2 + ($4D4F - ($4D3F + 2))

; 名前の字形を読みこむ所：地を色1・字を色3 にする
SECTION "看板 字形", ROMX[$4D99], BANK[$13]
	jp SignGlyphLoop

FreeBank13
SignDrawCrystal:
; クリスタルの枠をバッファに書く
	ld hl, SignFrameMap
	ld de, wSignBuffer
	ld c, 20 * 4
.copy
	ld a, [hli]
	ld [de], a
	inc de
	dec c
	jr nz, .copy
; 名前の文字数（$50 まで、18 まで）
	ld hl, wSignName
	ld b, 0
.len
	ld a, [hli]
	cp $50 ; 文字列のおわり
	jr z, .gotLen
	inc b
	ld a, b
	cp 18
	jr c, .len
.gotLen
	ld a, 20
	sub b
	srl a
	add LOW(wSignBuffer + 2 * 20)
	ld l, a
	ld a, HIGH(wSignBuffer + 2 * 20)
	adc 0
	ld h, a
	ld de, wSignName
	call PlaceString
; 空白は看板の中のタイルにする
	ld hl, wSignBuffer
	ld c, 20 * 4
.blank
	ld a, [hl]
	cp $7F
	jr nz, .next
	ld [hl], SIGN_TILE_INSIDE
.next
	inc hl
	dec c
	jr nz, .blank
; 枠のタイルを VRAM バンク1 に読みこむ
	ld hl, SignFrameGfx
	ld de, $9000 + (SIGN_TILE_BASE + 1) * 16
	ld c, 13 * 8
.gfx
	di
	ld a, 1
	ldh [rVBK], a
	call KitWaitVRAM
	ld a, [hli]
	ld [de], a
	inc de
	ld a, [hli]
	ld [de], a
	inc de
	xor a
	ldh [rVBK], a
	ei
	dec c
	jr nz, .gfx
	jp KitSignToWindow

; 名前の字形（1bpp を 8 バイト読みこんだもの $CEE4〜）を、地を色1・字を色3 で書く
; hl = 字形, de = VRAM, c = 8（キットの処理のつづき）
SignGlyphLoop:
	ld a, [hli]
	ld b, a
	di
	ld a, 1
	ldh [rVBK], a
	call KitWaitVRAM
	ld a, $FF
	ld [de], a
	inc de
	ld a, b
	ld [de], a
	inc de
	xor a
	ldh [rVBK], a
	ei
	dec c
	jr nz, SignGlyphLoop
	jp KitGlyphLoopEnd

SignFrameMap:
	db $51, $53,$53,$52,$52,$53,$53,$52,$52,$53,$53,$52,$52,$53,$53,$52,$52,$53,$53, $54
	db $55, $5D,$5D,$5D,$5D,$5D,$5D,$5D,$5D,$5D,$5D,$5D,$5D,$5D,$5D,$5D,$5D,$5D,$5D, $5B
	db $56, $5D,$5D,$5D,$5D,$5D,$5D,$5D,$5D,$5D,$5D,$5D,$5D,$5D,$5D,$5D,$5D,$5D,$5D, $5C
	db $57, $59,$59,$58,$58,$59,$59,$58,$58,$59,$59,$58,$58,$59,$59,$58,$58,$59,$59, $5A

; クリスタルの場所の名前の看板の枠（pokecrystal gfx/frames/map_entry_sign.png のタイル1〜13）
SignFrameGfx:
	db $ff, $ff, $e0, $ff, $cf, $f0, $9f, $e0, $91, $ee, $97, $ee, $97, $ee, $9f, $e0 ; 1
	db $ff, $ff, $00, $ff, $aa, $55, $ff, $00, $ff, $00, $ff, $00, $ff, $00, $ff, $00 ; 2
	db $ff, $ff, $00, $ff, $ff, $00, $ff, $00, $ff, $00, $ff, $00, $ff, $00, $ff, $00 ; 3
	db $ff, $ff, $07, $ff, $f3, $0f, $f9, $07, $89, $77, $e9, $77, $e9, $77, $f9, $07 ; 4
	db $cf, $f0, $e1, $fe, $cf, $f0, $cf, $f0, $cf, $f0, $cf, $f0, $e0, $ff, $cf, $f0 ; 5
	db $9f, $e0, $9f, $e0, $9f, $e0, $9f, $e0, $cf, $f0, $e1, $fe, $cf, $f0, $9f, $e0 ; 6
	db $91, $ee, $97, $ee, $97, $ee, $8f, $f0, $80, $ff, $c0, $ff, $e0, $ff, $ff, $ff ; 7
	db $ff, $00, $ff, $00, $ff, $00, $ff, $00, $aa, $55, $00, $ff, $00, $ff, $ff, $ff ; 8
	db $ff, $00, $ff, $00, $ff, $00, $ff, $00, $00, $ff, $00, $ff, $aa, $ff, $ff, $ff ; 9
	db $89, $77, $e9, $77, $e9, $77, $f1, $0f, $81, $7f, $03, $ff, $07, $ff, $ff, $ff ; 10
	db $f3, $0f, $87, $7f, $f3, $0f, $f3, $0f, $f3, $0f, $f3, $0f, $07, $ff, $f3, $0f ; 11
	db $f9, $07, $f9, $07, $f9, $07, $f9, $07, $f3, $0f, $87, $7f, $f3, $0f, $f9, $07 ; 12
	db $ff, $00, $ff, $00, $ff, $00, $ff, $00, $ff, $00, $ff, $00, $ff, $00, $ff, $00 ; 13

; --- VBlank：出入りの動き、スプライトをかくす、パレット ------------------------------

; VBlank の中の空き（rst $10 のあとの nop）から呼ぶ
SECTION "看板 VBlank の呼び出し", ROM0[$1FE7]
IF HAS_FOLLOW
	ld b, BANK(VBlankHooks)
	ld hl, VBlankHooks
ELSE
	ld b, BANK(SignVBlank)
	ld hl, SignVBlank
ENDC
	call Bankswitch

IF HAS_FOLLOW
FreeBank13
VBlankHooks:                      ; 連れ歩きの VBlank（絵を VRAM へ）のあとに看板
	ld b, BANK(FollowerVBlank)
	ld hl, FollowerVBlank
	call Bankswitch
	jp SignVBlank
ENDC

; ★ WRAM バンクを VBlank に入った時のバンク以外にしているあいだは、
;   スタックが $DFxx にあるので call / push / pop を使わない。
FreeBank13
SignVBlank:
	ld a, [wDisableVBlankWYUpdate]
	and a
	ret nz
	ldh a, [rSVBK]
	ld e, a
	ld a, SIGN_WRAM_BANK
	ldh [rSVBK], a
	ld a, e
	ld [wSignOrigSVBK], a
; しるしがなければ、はじめの値にする
	ld a, [wSignMark]
	cp $A5
	jr nz, .init
	ld a, [wSignMark + 1]
	cp $5A
	jr z, .ready
.init
	ld a, $A5
	ld [wSignMark], a
	ld a, $5A
	ld [wSignMark + 1], a
	ld a, SIGN_HIDDEN_Y
	ld [wSignY], a
	xor a
	ld [wSignActive], a
.ready
	ldh a, [hWY]
	cp SIGN_TOP_Y
	jr z, .show
	cp SIGN_HIDDEN_Y
	jr z, .hide
; ほかの使いかた（話す・メニューなど）：看板はすぐやめる
	ld a, [wSignActive]
	and a
	jr z, .done
	jr .finish

.show
	ld a, [wSignActive]
	and a
	jr nz, .checkPal
	ld a, 1
	ld [wSignActive], a
	ld a, SIGN_HIDDEN_Y
	ld [wSignY], a
; パレット7 が看板の色でなければ（出はじめ・マップがかわって読みなおされた）、看板の色にする
.checkPal
	ld a, 2
	ldh [rSVBK], a
	ld hl, W2_BgPals + SIGN_PAL_OFFSET
	ld a, [hli]
	cp LOW(SIGN_COLOR1)
	jr nz, .needPal
	ld a, [hli]
	cp HIGH(SIGN_COLOR1)
	jr nz, .needPal
	ld a, [hli]
	cp LOW(SIGN_COLOR2)
	jr nz, .needPal
	ld a, [hl]
	cp HIGH(SIGN_COLOR2)
	jr nz, .needPal
	ld a, SIGN_WRAM_BANK
	ldh [rSVBK], a
	jr .up
.needPal
	ld a, SIGN_WRAM_BANK
	ldh [rSVBK], a
	jp .setPal              ; パレットをかえて .up へもどる
.up
	ld a, [wSignY]
	sub SIGN_SPEED
	cp SIGN_TOP_Y
	jr nc, .storeY
	ld a, SIGN_TOP_Y
	jr .storeY

.hide
	ld a, [wSignActive]
	and a
	jr z, .done
	ld a, [wSignY]
	add SIGN_SPEED
	cp SIGN_HIDDEN_Y
	jr c, .storeY
.finish
	ld a, SIGN_HIDDEN_Y
	ld [wSignY], a
	xor a
	ld [wSignActive], a
	jr .restorePal

.storeY
	ld [wSignY], a
	ldh [rWY], a
; 看板の行にかかるスプライトをかくす（OAM の Y が 高さ + 16 - 8 + 1 以上）
	add 16 - 8 + 1
	ld b, a
	ld hl, wShadowOAM
	ld c, 40
.oam
	ld a, [hl]
	cp b
	jr c, .oamNext
	ld [hl], $A0
.oamNext
	ld a, l
	add 4
	ld l, a
	dec c
	jr nz, .oam

.done
	ld a, SIGN_WRAM_BANK
	ldh [rSVBK], a
	ld a, [wSignOrigSVBK]
	ldh [rSVBK], a
	ret

; パレット7 の色1・2 を看板の色にする（元の色はとっておく）。WRAM はバンク7 で来る
.setPal
	ld a, 2
	ldh [rSVBK], a
	ld hl, W2_BgPals + SIGN_PAL_OFFSET
	ld a, [hli]
	ld b, a
	ld a, [hli]
	ld c, a
	ld a, [hli]
	ld d, a
	ld e, [hl]
	ld a, SIGN_WRAM_BANK
	ldh [rSVBK], a
	ld hl, wSignSavedPal
	ld a, b
	ld [hli], a
	ld a, c
	ld [hli], a
	ld a, d
	ld [hli], a
	ld [hl], e
	ld a, 2
	ldh [rSVBK], a
	ld hl, W2_BgPals + SIGN_PAL_OFFSET
	ld a, LOW(SIGN_COLOR1)
	ld [hli], a
	ld a, HIGH(SIGN_COLOR1)
	ld [hli], a
	ld a, LOW(SIGN_COLOR2)
	ld [hli], a
	ld [hl], HIGH(SIGN_COLOR2)
	ld a, 1
	ld [W2_PalReload], a
	ld a, SIGN_WRAM_BANK
	ldh [rSVBK], a
	jp .up

; 元の色にもどす。ただし、マップがかわってパレットが読みなおされていたら、もどさない
.restorePal
	ld a, SIGN_HIDDEN_Y
	ldh [rWY], a
	ld hl, wSignSavedPal
	ld a, [hli]
	ld b, a
	ld a, [hli]
	ld c, a
	ld a, [hli]
	ld d, a
	ld e, [hl]
	ld a, 2
	ldh [rSVBK], a
	ld hl, W2_BgPals + SIGN_PAL_OFFSET
	ld a, [hli]
	cp LOW(SIGN_COLOR1)
	jr nz, .keep
	ld a, [hli]
	cp HIGH(SIGN_COLOR1)
	jr nz, .keep
	ld a, [hli]
	cp LOW(SIGN_COLOR2)
	jr nz, .keep
	ld a, [hl]
	cp HIGH(SIGN_COLOR2)
	jr nz, .keep
	ld hl, W2_BgPals + SIGN_PAL_OFFSET
	ld a, b
	ld [hli], a
	ld a, c
	ld [hli], a
	ld a, d
	ld [hli], a
	ld [hl], e
	ld a, 1
	ld [W2_PalReload], a
.keep
	jp .done


; PrepareOAMData（バンク1）の最後の「使わない OAM を消す」所からも、スプライトをかくす。
; （VBlank のあとに、ほかの所でスプライトが作りなおされることがあるため）
SECTION "看板 スプライトをかくす 呼び出し", ROMX[$49C4], BANK[$01]
	ld hl, PrepareOAM_HideUnderSign
	ld b, BANK(PrepareOAM_HideUnderSign)
	jp Bankswitch

FreeBank13
PrepareOAM_HideUnderSign:
IF HAS_FOLLOW
	ld b, BANK(FollowerTick)
	ld hl, FollowerTick
	call Bankswitch
ENDC
	ld d, $FF
	ldh a, [rSVBK]
	ld e, a
	ld a, SIGN_WRAM_BANK
	ldh [rSVBK], a
	ld a, [wSignMark]
	cp $A5
	jr nz, .bankBack
	ld a, [wSignMark + 1]
	cp $5A
	jr nz, .bankBack
	ld a, [wSignActive]
	and a
	jr z, .bankBack
	ld a, [wSignY]
	add 16 - 8 + 1
	ld d, a
.bankBack
	ld a, e
	ldh [rSVBK], a
	ld a, d
	inc a
	jr z, .clearUnused
	ld hl, wShadowOAM
	ld c, 40
.hideLoop
	ld a, [hl]
	cp d
	jr c, .next
	ld [hl], $A0
.next
	ld a, l
	add 4
	ld l, a
	dec c
	jr nz, .hideLoop

; ここから下は元の「使わない OAM を消す」処理と同じ
.clearUnused
	ldh a, [hOAMBufferOffset]
	ld l, a
	ld h, HIGH(wShadowOAM)
	ld de, 4
	ld b, $A0
	ld a, [wMovementFlags]
	bit 6, a
	ld a, $A0
	jr z, .clearLoop
	ld a, $90
.clearLoop
	cp l
	ret z
	ld [hl], b
	add hl, de
	jr .clearLoop

ENDC
