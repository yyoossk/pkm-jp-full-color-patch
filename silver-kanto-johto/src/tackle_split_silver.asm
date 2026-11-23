; 第126弾 1：たいあたり の 演出（BattleBGEffect_SetLCDStatCustoms1、銀は $32:$4E1E の 1つだけ）で、背の 高い ポケモンの とき
; 相手の 絵（こちらの 番）／こちらの 絵（相手の 番）も いっしょに ずれて いた。6段目の タイル（$30〜$37 行）で 2匹の 絵が
; 重なるので、動かされる 側の 絵に 点の ある 行を 範囲から はずす（クリスタル版 カントー＆ジョウトの キット asm/tackle_split.asm を
; 銀の アドレスに した もの）。VRAM は モード 0・1 の 間に 読む。タイルの VRAM の バンクは wAttrmap の bit3。

DEF wTilemap      EQU $C3A0
DEF wAttrmap      EQU $CCCD
DEF hLCDCPointer  EQU $FFC8
DEF hLYOverStart  EQU $FFC9
DEF hLYOverEnd    EQU $FFCA
DEF CheckTurn     EQU $4F63          ; BGEffect_CheckBattleTurn（nz：こちらの 番）

SECTION "tackle split", ROMX[$7E20], BANK[$32]

TS_Customs1::
	ldh [hLCDCPointer], a
	ld e, $2f
TS_Common:
	push bc                           ; bc = the effect's struct (the callers use it after this)
	push de
	call CheckTurn
	pop de
	jr nz, .player
	; the enemy's turn: lines 0 .. min($36, first dot line of the player's row 6)
	ld hl, wTilemap + 6 * 20 + 1
	ld c, 8
	call TS_RowMask                   ; d = bit 7: line $30 ... bit 0: line $37
	ld e, $30
.first
	sla d
	jr c, .gotfirst
	inc e
	ld a, e
	cp $38
	jr c, .first
.gotfirst
	ld a, e
	cp $36
	jr c, .endok
	ld a, $36
.endok
	ld e, a
	ld d, 0
	jr .store
.player
	; the player's turn: lines max(default, last dot line of the enemy's row 6 + 1) .. $5E
	push de
	ld hl, wTilemap + 6 * 20 + 11
	ld c, 9
	call TS_RowMask
	pop bc                            ; c = the default start
	ld b, $38
.last
	ld a, d
	and a
	jr z, .none
	srl d
	jr c, .gotlast
	dec b
	jr .last
.none
	ld b, 0
.gotlast
	ld a, b
	cp c
	jr nc, .startok
	ld a, c
.startok
	ld d, a
	ld e, $5e
.store
	ld a, d
	ldh [hLYOverStart], a
	ld a, e
	ldh [hLYOverEnd], a
	pop bc
	call CheckTurn                    ; as Crystal's: hl = the struct's turn byte, its flags
	ldh a, [hLYOverEnd]
	ret

; hl = wTilemap address of the first tile, c = tiles -> d = the lines with a dot (bit 7 = the tiles' line 0)
TS_RowMask:
	ldh a, [$ff4f]
	push af
	ld d, 0
.tile
	push bc
	push hl
	ld e, [hl]                        ; tile number
	ld bc, wAttrmap - wTilemap
	add hl, bc
	ld a, [hl]
	and 8
	rrca
	rrca
	rrca
	ldh [$ff4f], a                    ; VRAM bank of the tile
	ld l, e
	ld h, 0
	add hl, hl
	add hl, hl
	add hl, hl
	add hl, hl                        ; 16 × tile
	ldh a, [$ff40]
	bit 4, a
	jr nz, .low                       ; $8000 addressing
	ld a, e
	cp $80
	jr nc, .low                       ; $80-$FF: $8800-$8FFF
	ld a, h
	add $90
	ld h, a
	jr .addr
.low
	ld a, h
	add $80
	ld h, a
.addr
	ld bc, $0880                      ; b = 8 lines, c = the line's bit
.line
.wait
	ldh a, [$ff41]
	and 2
	jr nz, .wait                      ; mode 0 / 1 (then mode 2: VRAM still free for 80 dots)
	ld a, [hli]
	or [hl]
	inc hl
	jr z, .blank
	ld a, d
	or c
	ld d, a
.blank
	srl c
	dec b
	jr nz, .line
	pop hl
	inc hl
	pop bc
	dec c
	jr nz, .tile
	pop af
	ldh [$ff4f], a
	ret
