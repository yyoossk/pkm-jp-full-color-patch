; 第128弾 7：状態異常の まま レベルアップすると、能力値の 箱（9,0）〜（19,10）が 状態異常の ますに かさなって 文字化け
;（自分の「まひ」などは VRAM バンク1 の $7c〜$7e の 文字＋属性 バンク1：箱の 数字が バンク1 の タイルで かかれた。
;  相手の 状態異常の 色の ます（5本目）に 箱の わくが かかると 黄色などに なった）。
; 箱を かく 前（$0F:$6EA0）：HP の 欄の 行（相手 1段目・自分 8段目）の 属性を ふつうに もどす。
; 箱を とじた あと（$0F:$6EC3）：StatusColor_BattleLayout（$48:$4C5E）で 状態異常の 色を つけなおす。
; どちらも VRAM へ じかに 書くのは 属性が かわる ますだけ（タイルを 先に、そのあと 属性。バンク1 は di〜ei の 中だけ）。
; クリスタル版 カントー＆ジョウトの キット（p128_status.py の BoxPre / BoxPost）を 銀の statuscolor に あわせた もの。
; BOX_ADDR は phase_zzzzzz_k128.py が 先頭に DEF する。

DEF TM                 EQU $C3A0
DEF AM                 EQU $CCCD
DEF wMonType           EQU $CE53
DEF Predef             EQU $2E05
DEF Textbox            EQU $0EC1
DEF WaitPressAorB      EQU $0A26
DEF SafeLoadTempTilemap EQU $3120
DEF BattleLayout       EQU $4C5E      ; StatusColor_BattleLayout（バンク $48）

SECTION "k128 levelup box", ROMX[BOX_ADDR], BANK[$48]

BoxPre::
	xor a
	ld [wMonType], a
	ld a, $1f                         ; CopyMonToTempMon
	call Predef
	ld hl, TM + 9
	ld b, 10
	ld c, 9
	call Textbox
	ld hl, AM + 1 * 20 + 3            ; 相手：3〜9 れつ 2本目、10〜11 れつ 1本目（SC_Enemy と 同じ）
	ld bc, $0702
	call Fill
	ld bc, $0201
	call Fill
	ld hl, AM + 8 * 20 + 10           ; 自分：10〜19 れつ 3本目（SC_Player と 同じ）
	ld bc, $0a03
	call Fill
	jr CopyRows

BoxPost::
	call WaitPressAorB
	call SafeLoadTempTilemap
	call BattleLayout
	; fallthrough

CopyRows:
	ld hl, TM + 1 * 20 + 3
	ld de, $9800 + 1 * 32 + 3
	ld b, 9
	call CopyCells
	ld hl, TM + 8 * 20 + 10
	ld de, $9800 + 8 * 32 + 10
	ld b, 10
	; fallthrough

; wTilemap の ます hl・VRAM de から b ます：wAttrmap と VRAM の 属性が ちがう ますだけ タイル（バンク0）・属性（バンク1）を 書く
CopyCells:
.cell
	push bc
	push hl
	ld bc, AM - TM
	add hl, bc
	ld c, [hl]
	call ReadV1
	cp c
	jr z, .same
	pop hl
	push hl
	ld a, [hl]
	call WriteV0
	ld a, c
	call WriteV1
.same
	pop hl
	pop bc
	inc hl
	inc de
	dec b
	jr nz, .cell
	ret

; [hl..] = c を b こ（hl は つぎへ）
Fill:
	ld [hl], c
	inc hl
	dec b
	jr nz, Fill
	ret

; a = [de]（VRAM バンク1）
ReadV1:
	di
	ld a, 1
	ldh [$ff4f], a
.w
	ldh a, [$ff41]
	and 2
	jr nz, .w
	ld a, [de]
	push af
	xor a
	ldh [$ff4f], a
	pop af
	ei
	ret

; [de] = a（VRAM バンク1）
WriteV1:
	push bc
	ld b, a
	di
	ld a, 1
	ldh [$ff4f], a
.w
	ldh a, [$ff41]
	and 2
	jr nz, .w
	ld a, b
	ld [de], a
	xor a
	ldh [$ff4f], a
	ei
	pop bc
	ret

; [de] = a（VRAM バンク0）
WriteV0:
	push bc
	ld b, a
	di
.w
	ldh a, [$ff41]
	and 2
	jr nz, .w
	ld a, b
	ld [de], a
	ei
	pop bc
	ret
