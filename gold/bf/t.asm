INCLUDE "bf/pg.inc"
SECTION "t", ROMX[$7f00], BANK[$0f]
	call J_HasPlayerFainted
	hlcoord 1, 2
	ld a, PLAYER_SURF
