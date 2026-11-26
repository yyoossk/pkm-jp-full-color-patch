; 第128弾 11：たいあたり など（SCX で 片方の 絵を ずらす 演出）で、こちらの 背の 高い 絵の 上の 部分が 動かない
;（第126弾の 続き。クリスタル版 カントー＆ジョウトの キット asm/tackle_tiles.asm を 銀の アドレスに した もの）。
; 2匹の 絵は タイルの 6段目（48〜55行目）を 共有する。6段目は 両方とも SCX の 範囲から はずし、攻撃する 側の 6段目の タイルを
; 毎コマ 同じ だけ ずらして かきなおす（元の タイルは WRAM に とって おき、HBlank DMA で、6段目を かいて いない 間に）。
; はみ出す 分は となりの 空きマスに 予備の タイル（VRAM バンク1 の $70）。演出が おわれば もとに もどす。
; 銀：BattleBGEffect_SetLCDStatCustoms1 は $32:$4E1E の 1つだけ（第126弾の TS_Customs1 $32:$7E20 へ とぶ）。
;   rSCX の ときだけ ここ（NT_Customs1）、ほか（rSCY など）は 第126弾の まま。
;   アニメの 1コマ（$33:$4166 の call PushLYOverrides / call BattleAnimRequestPals）→ farcall TT_Hook。
;   銀は WRAM の バンクを 切りかえない（wLYOverrides $C700・wLYOverridesBackup $C800 は WRAM0）。
; CODE32・CODEM・BANKM・OLD1 は phase_zzzzzz_k128.py が 先頭に DEF する。

DEF hLCDCPointer  EQU $FFC8
DEF hLYOverStart  EQU $FFC9
DEF hLYOverEnd    EQU $FFCA
DEF rLCDC         EQU $FF40
DEF rSTAT         EQU $FF41
DEF rSCX_         EQU $FF43
DEF rLY           EQU $FF44
DEF rVBK          EQU $FF4F
DEF rHDMA1        EQU $FF51
DEF rHDMA2        EQU $FF52
DEF rHDMA3        EQU $FF53
DEF rHDMA4        EQU $FF54
DEF rHDMA5        EQU $FF55
DEF rSVBK         EQU $FF70
DEF wTilemap      EQU $C3A0
DEF wAttrmap      EQU $CCCD
DEF wBackup       EQU $C800          ; wLYOverridesBackup
DEF wAnimFlags    EQU $CA0F          ; wBattleAnimFlags, bit 0: stop
DEF PushLYOverrides EQU $3C2E
DEF CheckTurn     EQU $4F63          ; bank $32: nz = the player's side
DEF RequestPals   EQU $41B1          ; bank $33: BattleAnimRequestPals
DEF SPILL_TILE    EQU $70

; WRAM0（戦いの 間だけ 使う すき間）：wLYOverrides（$C700〜$C78F）の あとの $C791〜$C7FF（intro の wLYOverrides2 と
; wLYOverridesBackup の 前の ds 112）と、wLYOverridesBackup（$C800〜$C88F）の あとの $C891〜$C8FF（ds 112）。
; ClearLYOverrides（$32:$4E0A）は $C790・$C890 まで 消すので その 1バイトは 使わない。$C900 からは 戦いの アニメの 物。
; slots (16-aligned): the original tiles of strip index k: k < 6: $C7A0 + 16k, k >= 6: $C8A0 + 16(k - 6)
DEF wTTQBlank     EQU $C791
DEF wTTOutBlank   EQU $C792
DEF wTTState      EQU $C793          ; 0: off, 1: player attacks, 2: enemy attacks; bit 7: first frame
DEF wTTLast       EQU $C794
DEF wTTR          EQU $C795          ; r' (kernel)
DEF wTTQ          EQU $C796
DEF wTTDir        EQU $C797
DEF wTTK          EQU $C798
DEF wTTNZ         EQU $C799          ; bit k: slot k is not blank
DEF wTTPrevZ      EQU $C79A          ; bit k: the tile now in VRAM is blank
DEF wTTSpillSave  EQU $C8C0
DEF wTTOut        EQU $C8D0          ; (HDMA の 元：16 の 倍数)
DEF wTTDest       EQU $C8E0          ; 8 x VRAM address of strip tile k
DEF wTTBank       EQU $C8F0          ; 8 x its VRAM bank

SECTION "tackle tiles 32", ROMX[CODE32], BANK[$32]

NT_Customs1::
	cp LOW(rSCX_)
	jp nz, OLD1
	ldh [hLCDCPointer], a
	jr NT_Common
NT_Common:
	push bc
	call CheckTurn
	jr nz, .player
	xor a
	ldh [hLYOverStart], a
	ld a, $2f
	ldh [hLYOverEnd], a
	ld b, 2
	jr .setup
.player
	ld a, $37
	ldh [hLYOverStart], a
	ld a, $5e
	ldh [hLYOverEnd], a
	ld b, 1
.setup
	ld a, BANK(TT_Setup)
	ld hl, TT_Setup
	rst $08
	pop bc
	call CheckTurn
	ldh a, [hLYOverStart]
	ld d, a
	ldh a, [hLYOverEnd]
	ld e, a
	ret

SECTION "tackle tiles main", ROMX[CODEM], BANK[BANKM]

; b = 1 (player) / 2 (enemy)
TT_Setup::
	push bc
	ld a, [wTTState]
	and 3
	call nz, TT_Restore
	pop bc
	ld a, b
	or $80
	ld [wTTState], a
	xor a
	ld [wTTLast], a
	ld [wTTK], a
	ld [wTTNZ], a
	ld [wTTPrevZ], a
.loop
	call SideInfo
	ld a, [wTTK]
	cp b
	jp nc, .cells
	call TileDest                     ; hl = VRAM, a = bank
	call SetDest
	ld a, [wTTK]
	cp c
	jr z, .spill
	call SlotPtr
	ld d, h
	ld e, l
	call GetDest
	call ReadTile
	; blank?
	ld a, [wTTK]
	call SlotPtr
	ld c, 16
	xor a
.or
	or [hl]
	inc hl
	dec c
	jr nz, .or
	ld e, a
	ld a, [wTTK]
	call TTBit                          ; a = 1 << k
	ld c, a
	ld a, e
	and a
	ld a, c
	ld hl, wTTNZ
	jr nz, .nz
	ld hl, wTTPrevZ
.nz
	or [hl]
	ld [hl], a
	jr .next
.spill
	call GetDest
	ld de, wTTSpillSave
	call ReadTile
	call SideInfo
	ld a, [wTTK]
	call SlotPtr
	ld c, 16
	xor a
.zero
	ld [hli], a
	dec c
	jr nz, .zero
	ld hl, wTTOut
	ld c, 16
.zero2
	ld [hli], a
	dec c
	jr nz, .zero2
	call GetDest
	call HDMAOut                      ; the spare tile: blank
	ld a, [wTTK]
	call TTBit
	ld hl, wTTPrevZ
	or [hl]
	ld [hl], a
.next
	ld hl, wTTK
	inc [hl]
	jp .loop
.cells
	; the spill cell: tile SPILL_TILE (bank 1), the palette of the picture's tile beside it
	call SpillCell                    ; hl = wTilemap cell, de = wAttrmap of the neighbour, bc = VRAM cell
	ld a, [de]
	or 8
	push af
	ld h, b
	ld l, c
	ld a, SPILL_TILE
	ld b, 0
	call PutByte
	pop af
	ld b, 1
	call PutByte
	ret

; a = k -> a = 1 << k (bc, de, hl kept)
TTBit:
	push bc
	ld b, a
	ld a, 1
	inc b
.loop
	dec b
	jr z, .done
	add a
	jr .loop
.done
	pop bc
	ret

; hl = VRAM, a = bank -> the entry of wTTK (bc, hl kept)
SetDest:
	push bc
	ld b, a
	ld a, [wTTK]
	add a
	add LOW(wTTDest)
	ld e, a
	ld d, HIGH(wTTDest)
	ld a, l
	ld [de], a
	inc de
	ld a, h
	ld [de], a
	ld a, [wTTK]
	add LOW(wTTBank)
	ld e, a
	ld a, b
	ld [de], a
	pop bc
	ret

; the entry of wTTK -> hl = VRAM, a = bank (bc, de kept)
GetDest:
	push de
	ld a, [wTTK]
	add a
	add LOW(wTTDest)
	ld e, a
	ld d, HIGH(wTTDest)
	ld a, [de]
	ld l, a
	inc de
	ld a, [de]
	ld h, a
	ld a, [wTTK]
	add LOW(wTTBank)
	ld e, a
	ld a, [de]
	pop de
	ret

; called every animation frame instead of PushLYOverrides + BattleAnimRequestPals
TT_Hook::
	call PushLYOverrides
	ld a, [wTTState]
	and a
	jr z, .done
	ldh a, [hLCDCPointer]
	cp LOW(rSCX_)
	jr nz, .restore
	ld a, [wAnimFlags]
	bit 0, a
	jr nz, .restore
	ld a, [wTTState]
	bit 7, a
	jr z, .notfirst
	res 7, a
	ld [wTTState], a
	; the callers may have moved the range (Tackle: end + 1): keep row 6 out of it
	cp 1
	jr nz, .efirst
	ld a, $37
	ldh [hLYOverStart], a
	jr .notfirst
.efirst
	ld a, $2f
	ldh [hLYOverEnd], a
.notfirst
	ld a, [wTTState]
	cp 1
	jr nz, .enemy
	ld a, [wBackup + $37]             ; line 56's SCX
	jr .got
.enemy
	ld a, [wBackup + $2e]             ; line 47's SCX
.got
	cpl
	inc a                             ; pixels to the right
	ld hl, wTTLast
	cp [hl]
	jr z, .done
	ld [hl], a
IF DEF(DEBUG)
	ldh a, [rLY]
	ld [$d196], a
	ld a, [hl]
ENDC
IF !DEF(NOUPD)
	call TT_Update
ENDC
IF DEF(DEBUG)
	ldh a, [rLY]
	ld [$d197], a
	ld hl, $d198
	inc [hl]
ENDC
	jr .done
.restore
	call TT_Restore
.done
	ld a, $33
	ld hl, RequestPals
	rst $08
	ret

TT_Restore:
	xor a
	call TT_Update
	; the spare tile and the cell
	ld hl, wTTSpillSave
	ld de, wTTOut
	ld c, 16
.copy
	ld a, [hli]
	ld [de], a
	inc de
	dec c
	jr nz, .copy
	ld hl, $9000 + SPILL_TILE * 16
	ld a, 1
	call HDMAOut
	call SpillCell
	push de
	ld de, wAttrmap - wTilemap
	push hl
	add hl, de
	ld a, [hl]
	pop hl
	ld e, a                           ; attribute
	ld a, [hl]                        ; tile
	pop hl                            ; (unused)
	ld h, b
	ld l, c
	push de
	ld b, 0
	call PutByte
	pop de
	ld a, e
	ld b, 1
	call PutByte
	xor a
	ld [wTTState], a
	ret

; -> hl = wTilemap cell of the spill column, de = wAttrmap cell of the picture tile beside it, bc = VRAM BG map cell
SpillCell:
	call SideInfo                     ; c = spill k, d = first column
	ld a, d
	add c
	ld e, a                           ; the spill column
	ld a, c
	and a
	ld a, e
	jr z, .left
	dec a
	jr .nb
.left
	inc a
.nb
	push af
	ld d, 0
	ld hl, wTilemap + 6 * 20
	add hl, de
	push hl
	ld hl, $98c0
	add hl, de
	ld b, h
	ld c, l
	pop hl
	pop af
	push hl
	ld e, a
	ld d, 0
	ld hl, wAttrmap + 6 * 20
	add hl, de
	ld d, h
	ld e, l
	pop hl
	ret

; -> b = strip tiles, c = spill index, d = first column
SideInfo:
	ld a, [wTTState]
	and 3
	cp 1
	jr nz, .enemy
	ld b, 7
	ld c, 6
	ld d, 2
	ret
.enemy
	ld b, 8
	ld c, 0
	ld d, 11
	ret

; a = strip index (signed; outside 0 .. b-1: the spill slot, all 0) -> hl = its slot, a = the index used; b, c, de kept
SlotPtr:
	bit 7, a
	jr nz, .oob
	cp b
	jr c, .ok
.oob
	ld a, c
.ok
	push af
	cp 6
	jr nc, .hi
	swap a
	add $a0
	ld l, a
	ld h, $c7
	pop af
	ret
.hi
	sub 6
	swap a
	add $a0
	ld l, a
	ld h, $c8
	pop af
	ret

; a = strip index, c = spill index, d = first column -> hl = VRAM tile, a = VRAM bank; bc, de kept
TileDest:
	cp c
	jr nz, .pic
	ld hl, $9000 + SPILL_TILE * 16
	ld a, 1
	ret
.pic
	add d
	push de
	ld e, a
	ld d, 0
	ld hl, wTilemap + 6 * 20
	add hl, de
	ld a, [hl]
	push af
	ld de, wAttrmap - wTilemap
	add hl, de
	ld a, [hl]
	and 8
	rrca
	rrca
	rrca
	ld e, a
	pop af
	ld l, a
	ld h, 0
	add hl, hl
	add hl, hl
	add hl, hl
	add hl, hl
	ld a, h
	cp 8
	jr nc, .high
	add $90
	jr .set
.high
	add $80
.set
	ld h, a
	ld a, e
	pop de
	ret

; hl = VRAM, a = bank, de = destination: 16 bytes; bc kept
ReadTile:
	push bc
	ld b, a
	ld c, 16
.loop
	di
	ldh a, [rVBK]
	push af
	ld a, b
	ldh [rVBK], a
.wait
	ldh a, [rSTAT]
	and 2
	jr nz, .wait
	ld a, [hli]
	ld [de], a
	pop af
	ldh [rVBK], a
	ei
	inc de
	dec c
	jr nz, .loop
	pop bc
	ret

; hl = VRAM, a = value, b = bank
PutByte:
	ld c, a
	di
	ldh a, [rVBK]
	push af
	ld a, b
	ldh [rVBK], a
.wait
	ldh a, [rSTAT]
	and 2
	jr nz, .wait
	ld [hl], c
	pop af
	ldh [rVBK], a
	ei
	ret

; wTTOut -> hl (VRAM), a = bank; bc, de kept.  Interrupts stay on (the LCD handler's SCX writes must not be late).
HDMAOut:
IF DEF(NOHDMA)
	ret
ENDC
	push bc
	push de
	ld e, a
	ldh a, [rLCDC]
	bit 7, a
	jr z, .direct
	ld a, HIGH(wTTOut)
	ldh [rHDMA1], a
	ld a, LOW(wTTOut)
	ldh [rHDMA2], a
	ld a, h
	ldh [rHDMA3], a
	ld a, l
	ldh [rHDMA4], a
.guard
	; only at lines 2-43 / 58-139 (started at the end of a line, the transfer is at the next line's HBlank): not while row 6 is drawn, not at the lines where the SCX changes (the HBlank DMA
	; delays the LCD interrupt that writes it), not near VBlank (its handler expects VRAM bank 0)
	ldh a, [rLY]
	cp 2
	jr c, .guard
	cp 44
	jr c, .go
	cp 58
	jr c, .guard
	cp 140
	jr nc, .guard
.go
IF DEF(DEBUG)
	ldh a, [rLY]
	ld [$d19b], a
ENDC
	ldh a, [rVBK]
	ld d, a
	ld a, e
	ldh [rVBK], a
	ld a, $80
	ldh [rHDMA5], a
.wait
	ldh a, [rHDMA5]
	bit 7, a
	jr z, .wait
IF DEF(DEBUG)
	ldh a, [rLY]
	ld [$d19c], a
ENDC
	ld a, d
	ldh [rVBK], a
	pop de
	pop bc
	ret
.direct
	ldh a, [rVBK]
	ld d, a
	ld a, e
	ldh [rVBK], a
	ld bc, wTTOut
	ld e, 16
.copy
	ld a, [bc]
	ld [hli], a
	inc bc
	dec e
	jr nz, .copy
	ld a, d
	ldh [rVBK], a
	pop de
	pop bc
	ret

; a = pixels to the right (signed): redraw the attacker's row-6 strip
; out = (P << (8 - r')) | (Q >> r') per byte; right shift by r: P = left neighbour, Q = this, r' = r;
; left shift by r: P = this, Q = right neighbour, r' = 8 - r (q = whole tiles).  A tile that stays blank is skipped.
TT_Update:
	ld e, 0
	bit 7, a
	jr z, .pos
	cpl
	inc a
	ld e, 1
.pos
	ld c, a
	and 7
	ld b, a
	ld a, e
	and a
	ld a, b
	jr z, .rok
	ld a, 8
	sub b
.rok
	ld [wTTR], a
	ld a, c
	srl a
	srl a
	srl a
	ld [wTTQ], a
	ld a, e
	ld [wTTDir], a
	call WaitLY
	xor a
	ld [wTTK], a
.loop
	call SideInfo
	ld a, [wTTK]
	cp b
	ret nc
	ld a, [wTTQ]
	ld e, a
	ld a, [wTTDir]
	and a
	jr nz, .left
	ld a, [wTTK]
	sub e                             ; Q = k - q, P = k - q - 1
	jr .ptrs
.left
	ld a, [wTTK]
	add e                             ; P = k + q, Q = k + q + 1
	inc a
.ptrs
	push af
	call SlotPtr                      ; Q
	call IsBlank
	ld [wTTQBlank], a
	pop af
	push hl
	dec a
	call SlotPtr                      ; P
	call IsBlank                      ; a = 1: P blank
	ld d, h
	ld e, l
	pop bc
	; the result is blank: (r' = 0 or P blank) and (r' = 8 or Q blank)
	ld l, a
	ld a, [wTTR]
	and a
	jr nz, .p
	ld l, 1
.p
	cp 8
	ld a, [wTTQBlank]
	jr nz, .q
	ld a, 1
.q
	and l
	ld [wTTOutBlank], a
	jr z, .draw
	ld a, [wTTK]
	call TTBit
	ld hl, wTTPrevZ
	and [hl]
	jr nz, .next                      ; blank already
.draw
	call DoKernel
	ld a, [wTTK]
	call TTBit
	ld c, a
	cpl
	ld hl, wTTPrevZ
	and [hl]
	ld b, a
	ld a, [wTTOutBlank]
	and a
	ld a, b
	jr z, .setz
	or c
.setz
	ld [hl], a
	call GetDest
	call HDMAOut
.next
	ld hl, wTTK
	inc [hl]
	jp .loop

; a = the slot index (from SlotPtr) -> a = 1 if blank; bc, hl kept
IsBlank:
	push hl
	call TTBit
	ld hl, wTTNZ
	and [hl]
	ld a, 1
	jr z, .blank
	xor a
.blank
	pop hl
	ret

DoKernel:
	ld a, [wTTR]
	add a
	push de
	ld e, a
	ld d, 0
	ld hl, KTable
	add hl, de
	ld a, [hli]
	ld h, [hl]
	ld l, a
	pop de
	push hl
	ld hl, wTTOut
	ret

KTable:
	dw Kern0, Kern1, Kern2, Kern3, Kern4, Kern5, Kern6, Kern7, Kern8

Kern0:
REPT 16
	ld a, [bc]
	ld [hli], a
	inc bc
ENDR
	ret

Kern8:
REPT 16
	ld a, [de]
	ld [hli], a
	inc de
ENDR
	ret

MACRO KERNEL
Kern\1:
REPT 16
	ld a, [de]
	REPT \1
	rrca
	ENDR
	and ($FF << (8 - \1)) & $FF
	ld [hl], a
	ld a, [bc]
	REPT \1
	rrca
	ENDR
	and $FF >> \1
	or [hl]
	ld [hli], a
	inc de
	inc bc
ENDR
	ret
ENDM
	KERNEL 1
	KERNEL 2
	KERNEL 3
	KERNEL 4
	KERNEL 5
	KERNEL 6
	KERNEL 7

; wait until row 6 has been drawn (line 56), unless it already has this frame
WaitLY:
	ldh a, [rLCDC]
	bit 7, a
	ret z
.wait
	ldh a, [rLY]
	cp 56
	jr c, .wait
	ret
