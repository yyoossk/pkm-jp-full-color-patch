; 場所の名前の看板（ウインドウ）の上に、人などのスプライトが重なる不具合を直す
;
; PrepareOAMData（バンク 1）の最後の「使わない OAM を消す」所を、
; 空いているバンクの処理に飛ばす。そこで、看板が出ているときだけ
; 看板の行にかかるスプライトを画面の外にかくしてから、元の処理をする。
; 看板：hWY = $70（画面の Y 112〜143）。8x8 のスプライトは OAM の Y が
; 112 + 16 - 8 + 1 = 121 以上なら看板に重なる。

IF HAS_PLACE_SIGN

SECTION "看板とスプライト 呼び出し", ROMX[$49C4], BANK[$01]
	ld hl, PrepareOAM_HideUnderSign
	ld b, BANK(PrepareOAM_HideUnderSign)
	jp Bankswitch

FreeBankA
PrepareOAM_HideUnderSign:
	ldh a, [hWY]
	cp PLACE_SIGN_WY
	jr nz, .clearUnused
	ldh a, [rSVBK]
	ld c, a
	ld a, 1
	ldh [rSVBK], a
	ld a, [wPlaceSignTimer]
	ld b, a
	ld a, c
	ldh [rSVBK], a
	ld a, b
	and a
	jr z, .clearUnused
	ldh a, [hOAMBufferOffset]
	and a
	jr z, .clearUnused
	ld b, a
	ld hl, wShadowOAM
.hideLoop
	ld a, [hl]
	cp PLACE_SIGN_WY + 16 - 8 + 1
	jr c, .next
	ld [hl], $A0
.next
	ld a, l
	add 4
	ld l, a
	cp b
	jr c, .hideLoop

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
