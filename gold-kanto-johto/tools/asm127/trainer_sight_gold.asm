; 第127弾（金）：キットの trainer_sight.asm を 金の 住所に。
; Phase 127: a trainer does not see the player through a wall or over a ledge.
; (Route 9: the youngster above the ledge saw the player below it and walked onto the ledge.)
; FacingPlayerDistance_bc（金 00:384D、_CheckTrainerBattle だけが 使う）から farcall TSight:
;   as before (carry: facing the player, b = distance, c = direction), but no carry when a tile between the trainer and
;   the player is a wall ($07) or a ledge ($A0-$A7).

DEF FacingPlayerDistance EQU $3855     ; 金（日本版）
DEF GetCoordTile         EQU $2ADD     ; 金：GetCoordTileCollision（d, e ＝ マップの 座標 → a ＝ 当たり）
DEF OBJECT_MAP_X         EQU $10

SECTION "trainer sight", ROMX[CODE_ADDR], BANK[CODE_BANK]

TSight::
	push de
	push bc
	call FacingPlayerDistance         ; carry ; d = distance, e = direction (OW_DOWN 0, UP 4, LEFT 8, RIGHT 12)
	pop bc
	jr nc, .no
	ld a, d
	cp 2
	jr c, .ok                         ; next to him: nothing between
	push de                           ; distance / direction
	ld hl, OBJECT_MAP_X
	add hl, bc
	ld a, [hli]
	ld h, [hl]
	ld l, a                           ; l = x, h = y
	pop bc                            ; b = distance, c = direction
	push bc
	dec b                             ; the tiles between
.loop
	ld a, c
	and a
	jr nz, .notdown
	inc h
	jr .step
.notdown
	cp 4
	jr nz, .notup
	dec h
	jr .step
.notup
	cp 8
	jr nz, .right
	dec l
	jr .step
.right
	inc l
.step
	push bc
	push hl
	ld d, l
	ld e, h
	call GetCoordTile
	pop hl
	pop bc
	cp $07
	jr z, .blocked
	and $f8
	cp $a0
	jr z, .blocked
	dec b
	jr nz, .loop
	pop bc                            ; b = distance, c = direction
	pop de
	scf
	ret
.ok
	ld b, d
	ld c, e
	pop de
	scf
	ret
.blocked
	pop bc
.no
	pop de
	and a
	ret
