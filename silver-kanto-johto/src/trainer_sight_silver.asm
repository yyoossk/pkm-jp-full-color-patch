; 第127弾 5：トレーナーと 主人公の あいだに かべ（$07）か 段差（$A0〜$A7）が あれば 見つけない
;（9番道路：がけの 上の トレーナーが がけの 下の 主人公を 見つけて 段差の 上に のった）。
; FacingPlayerDistance_bc（$00:$384D、_CheckTrainerBattle だけが 使う）から farcall する。もとと 同じく
; carry ＝ 向いて いる、b ＝ きょり、c ＝ 向き を かえす（クリスタル版の キット asm/trainer_sight.asm を 銀の アドレスで）。

DEF FacingPlayerDistance EQU $3855
DEF GetCoordTile         EQU $2ADD     ; d, e（マップの 座標）→ a ＝ 当たりの 種類
DEF OBJECT_MAP_X         EQU $10

SECTION "trainer sight", ROMX[$4660], BANK[$49]

TSight::
	push de
	push bc
	call FacingPlayerDistance         ; carry ; d = きょり、e = 向き（下 0・上 4・左 8・右 12）
	pop bc
	jr nc, .no
	ld a, d
	cp 2
	jr c, .ok                         ; となり：あいだは ない
	push de
	ld hl, OBJECT_MAP_X
	add hl, bc
	ld a, [hli]
	ld h, [hl]
	ld l, a                           ; l = x、h = y
	pop bc                            ; b = きょり、c = 向き
	push bc
	dec b                             ; あいだの ます
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
	pop bc
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
