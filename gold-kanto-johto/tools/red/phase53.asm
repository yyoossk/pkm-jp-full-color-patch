; Phase 53: Red's opening (from the Red full-color hack): copyright, GAME FREAK shooting star,
; Gengar vs Nidorino, and Red's title screen (no "Red Version", no 赤 emblem, logo centered).
; Colors work as in the full-color hack: each CGB palette has 4 base colors and Red's DMG palette
; registers (BGP / OBP0 / OBP1, kept in RAM here) pick which base color each color index shows.
INCLUDE "jp.inc"

DEF DelayFrame       EQU $045A
DEF GetJoypad        EQU $0984
DEF PlaySFX          EQU $3BB0
DEF DisableLCD       EQU $0568
DEF EnableLCD        EQU $058A
DEF Random           EQU $2F5E
DEF FarDecompress    EQU $0B2A
DEF Get2bpp          EQU $0F6C
DEF ClearSprites     EQU $2FD7
DEF CopyBytes        EQU $2FF2

DEF hJoyPressed      EQU $FFA7
DEF hJoyDown         EQU $FFA8
DEF hSCX             EQU $FFCF
DEF hSCY             EQU $FFD0
DEF hWX              EQU $FFD1
DEF hWY              EQU $FFD2
DEF hBGMapMode       EQU $FFD4
DEF hLCDCPointer     EQU $FFC6
DEF hLYOverrideStart EQU $FFC7
DEF hLYOverrideEnd   EQU $FFC8
DEF hCGBPalUpdate    EQU $FFE5
DEF wCurSFX          EQU $C2BF
DEF wShadowOAM       EQU $C400
DEF wBGPals2         EQU $D080    ; WRAM 5 (selected while the opening runs)
DEF wOBPals2         EQU $D0C0
DEF wLYOverrides     EQU $D100
DEF wTitleScreenSelectedOption EQU $CF58
DEF wMonBuffer       EQU $C800    ; decompressed title Pokémon (7x7 tiles)

DEF rLCDC EQU $FF40
DEF rSTAT EQU $FF41
DEF rVBK  EQU $FF4F

; work RAM (Crystal's wTilemap, unused here)
DEF wBaseBG   EQU $C4A0           ; 8 palettes x 4 base colors
DEF wBaseOB   EQU $C4E0
DEF wBGP      EQU $C520
DEF wOBP0     EQU $C521
DEF wOBP1     EQU $C522
DEF wBaseX    EQU $C523
DEF wBaseY    EQU $C524
DEF wNidoTile EQU $C525
DEF wStarCnt  EQU $C526
DEF wTitleMon EQU $C527
DEF wScroll   EQU $C528
DEF wFixStars EQU $C529

SECTION "Phase53", ROMX[CODE_ADDR], BANK[CODE_BANK]

RedOpening::
	ldh a, [$FF9E]                    ; hVBlank: Crystal's normal mode while the opening runs
	push af
	xor a
	ldh [$FF9E], a
	ldh [hBGMapMode], a
	ldh [hLCDCPointer], a
	ldh [hLYOverrideStart], a
	ldh [hLYOverrideEnd], a
	ldh [hSCX], a
	ldh [hSCY], a
	ld a, 7
	ldh [hWX], a
	ld a, $90
	ldh [hWY], a
	xor a
	ld [wFixStars], a
	ld hl, wBaseBG
	ld bc, $80
	ld a, $FF                         ; all white
	call ByteFill
	xor a
	ld [wBGP], a
	ld [wOBP0], a
	ld [wOBP1], a
	call UpdatePals
	call ClearSprites
	call LYOverridesZero
	call PlayIntro
	call TitleScreen
	ld [wTitleScreenSelectedOption], a
; leave the screen as Crystal expects it
	call DisableLCD
	ld a, 1
	ldh [rVBK], a
	ld hl, $9800
	ld bc, $800
	xor a
	call ByteFill
	xor a
	ldh [rVBK], a
	ld hl, $9C00
	ld bc, $400
	ld a, $7F
	call ByteFill
	xor a
	ldh [hLCDCPointer], a
	ldh [hSCX], a
	ld a, $E3
	ldh [rLCDC], a
	pop af
	ldh [$FF9E], a
	ret

; ---------------------------------------------------------------- palettes
UpdatePals:
	push hl
	push de
	push bc
	ld hl, wBaseBG
	ld de, wBGPals2
	ld a, [wBGP]
	ld c, a
	ld b, 8
.bg
	call .one
	dec b
	jr nz, .bg
	ld b, 8
.ob
	ld a, b
	cp 5
	ld a, [wOBP0]
	jr nc, .p0
	ld a, [wOBP1]
.p0
	ld c, a
	call .one
	dec b
	jr nz, .ob
	ld a, 1
	ldh [hCGBPalUpdate], a
	pop bc
	pop de
	pop hl
	ret

.one ; hl = 4 base colors, de = output; c = DMG palette
	push bc
	ld b, 4
	ld a, c
.col
	push af
	and 3
	push hl
	add a
	add l
	ld l, a
	jr nc, .nc
	inc h
.nc
	ld a, [hli]
	ld [de], a
	inc de
	ld a, [hl]
	ld [de], a
	inc de
	pop hl
	pop af
	rrca
	rrca
	dec b
	jr nz, .col
	ld bc, 8
	add hl, bc
	pop bc
	ret

; a = palette slot (0-7 BG, 8-15 OB), hl = 4 colors (ROM, this bank)
SetBasePal:
	push de
	add a
	add a
	add a
	ld e, a
	ld d, 0
	push hl
	ld hl, wBaseBG
	add hl, de
	ld d, h
	ld e, l
	pop hl
	ld bc, 8
	call CopyBytes
	pop de
	ret

; ---------------------------------------------------------------- frames, input, sound
Frame:
	ld a, [wFixStars]
	and a
	call nz, FixStarPals
	call UpdatePals
	jp DelayFrame

DelayN: ; c frames
	call Frame
	dec c
	jr nz, DelayN
	ret

; carry if Up+Select+B is held or A / Start pressed, within c frames (Red's CheckForUserInterruption)
CheckInt:
	call Frame
	push bc
	call GetJoypad
	pop bc
	ldh a, [hJoyDown]
	and $46
	cp $46
	jr z, .yes
	ldh a, [hJoyPressed]
	and $09
	jr nz, .yes
	dec c
	jr nz, CheckInt
	and a
	ret
.yes
	scf
	ret

Sfx: ; a = sound effect (always plays, like Red's PlaySound)
	push de
	ld e, a
	ld d, 0
	ld a, $FF
	ld [wCurSFX], a
	call PlaySFX
	pop de
	ret

Music: ; a = song
	push de
	ld e, a
	ld d, 0
	call PlayMusic
	pop de
	ret

; ---------------------------------------------------------------- VRAM helpers
; write a to [hl+] while the LCD is on
VPoke:
	push af
	di
.w
	ldh a, [rSTAT]
	and 2
	jr nz, .w
	pop af
	ld [hli], a
	ei
	ret

; copy b rows of c tiles from de to the BG map at hl (32 wide)
VRect:
.row
	push bc
	push hl
.col
	ld a, [de]
	inc de
	call VPoke
	dec c
	jr nz, .col
	pop hl
	ld a, l
	add 32
	ld l, a
	jr nc, .nc
	inc h
.nc
	pop bc
	dec b
	jr nz, .row
	ret

; fill bc bytes at hl with a while the LCD is on
VFill:
	push de
	ld d, a
.l
	ld a, d
	call VPoke
	dec bc
	ld a, b
	or c
	jr nz, .l
	pop de
	ret

LYOverridesZero:
	ld hl, wLYOverrides
	ld bc, $90
	xor a
	jp ByteFill

; lines [b, c) of the LY overrides = a
LYOverridesSet:
	ld h, HIGH(wLYOverrides)
	ld l, b
.l
	ld [hli], a
	inc b
	ld e, a
	ld a, b
	cp c
	ld a, e
	jr nz, .l
	ret

; ---------------------------------------------------------------- intro
PlayIntro:
	call PlayShootingStar
	call PlayIntroScene
; GBFadeOutToWhite
	ld hl, FadeToWhite
	ld b, 3
.fade
	ld a, [hli]
	ld [wBGP], a
	ld a, [hli]
	ld [wOBP0], a
	ld a, [hli]
	ld [wOBP1], a
	ld c, 8
	call DelayN
	dec b
	jr nz, .fade
	xor a
	ldh [hSCX], a
	call ClearSprites
	jp Frame

FadeToWhite:
	db %10010000, %10000000, %10010000
	db %01000000, %01000000, %01000000
	db %00000000, %00000000, %00000000

PlayShootingStar:
; palettes: copyright / GAME FREAK
	xor a
	ld hl, PalGrey
	call SetBasePal
	ld a, 8
	ld hl, PalGF
	call SetBasePal
	ld a, 12
	ld hl, PalStar4
	call SetBasePal
	ld a, 13
	ld hl, PalStar5
	call SetBasePal
	ld a, 14
	ld hl, PalGF
	call SetBasePal
	ld a, 15
	ld hl, PalStar7
	call SetBasePal
; copyright
	call DisableLCD
	call ClearVRAMAttrs
	ld hl, GfxCopyright
	ld de, $9600
	call Decomp
	ld hl, $97F0
	ld bc, 16
	xor a
	call ByteFill
	ld hl, $9800
	ld bc, $400
	ld a, $7F
	call ByteFill
	ld hl, CopyrightLayout
.cl
	ld a, [hli]
	and a
	jr z, .cl_done
	ld e, a
	ld a, [hli]
	ld d, a
.cc
	ld a, [hli]
	and a
	jr z, .cl
	ld [de], a
	inc de
	jr .cc
.cl_done
	ld a, $C3
	ldh [rLCDC], a
	ld a, %11100100
	ld [wBGP], a
	ld c, 180
	call DelayN
; black bars and the intro graphics
	call DisableLCD
	ld hl, GfxGengar
	ld de, $9000
	call Decomp
	ld hl, GfxGFIntro
	ld de, $9600
	call Decomp
	ld hl, GfxGFIntro
	ld de, $8800
	call Decomp
	ld hl, GfxNidorino
	ld de, $8000
	call Decomp
	ld hl, GfxStars
	ld de, $8A00
	ld bc, 3 * 16
	call CopyBytes
	ld hl, $9C00
	ld bc, $400
	xor a
	call ByteFill
	ld hl, $9C00
	ld bc, 4 * 32
	ld a, 1
	call ByteFill
	ld hl, $9C00 + 14 * 32
	ld bc, 4 * 32
	ld a, 1
	call ByteFill
	ld a, $CB                          ; BG map $9C00, window off
	ldh [rLCDC], a
	ld c, 64
	call DelayN
	call AnimateShootingStar
	push af
; "PRESENTS"
	ld hl, $9C00 + 11 * 32 + 7
	ld a, $67
	ld b, 6
.pr
	call VPoke
	inc a
	dec b
	jr nz, .pr
	pop af
	jr c, .next
	ld c, 40
	call DelayN
.next
	ld a, MUS_INTRO
	call Music
; IntroClearMiddleOfScreen
	ld hl, $9C00 + 4 * 32
	ld bc, 10 * 32
	xor a
	call VFill
	call ClearSprites
	ld c, 3
	jp DelayN

AnimateShootingStar:
	ld a, %11111001
	ld [wOBP0], a
	ld a, %10100100
	ld [wOBP1], a
	ld hl, GFLogoOAM
	ld de, wShadowOAM + 24 * 4
	ld bc, 16 * 4
	call CopyBytes
	ld hl, BigStarOAM
	ld de, wShadowOAM
	ld bc, 4 * 4
	call CopyBytes
	ld a, 1
	ld [wFixStars], a
	ld a, SFX_SHOOTING_STAR
	call Sfx
; move the big star down and left across the screen
	ld hl, wShadowOAM
	ld bc, $A004
.big
	push hl
	push bc
.big_in
	ld a, [hl]
	add 4
	ld [hli], a
	ld a, [hl]
	add -4
	ld [hli], a
	inc hl
	inc hl
	dec c
	jr nz, .big_in
	ld c, 1
	call CheckInt
	pop bc
	pop hl
	jp c, .end
	ld a, [hl]
	cp b
	jr nz, .big
; clear the big star
	ld hl, wShadowOAM
	ld c, 4
	ld de, 4
.clr
	ld [hl], 160
	add hl, de
	dec c
	jr nz, .clr
; make the GAME FREAK logo flash
	ld b, 3
.flash
	ld a, [wOBP0]
	rrca
	rrca
	ld [wOBP0], a
	ld c, 10
	call CheckInt
	jp c, .end
	dec b
	jr nz, .flash
; 24 small stars (off-screen)
	ld de, wShadowOAM
	ld a, 24
.init
	push af
	ld hl, SmallStarOAM
	ld bc, 4
	call CopyBytes
	pop af
	dec a
	jr nz, .init
; the small stars fall from the logo in waves
	xor a
	ld [wStarCnt], a
	ld hl, SmallStarWaves
	ld c, 6
.waves
	ld a, [hli]
	ld e, a
	ld a, [hli]
	ld d, a
	push bc
	push hl
	ld hl, wShadowOAM + 20 * 4
	ld c, 4
.wave_in
	ld a, [de]
	cp -1
	jr z, .wave_done
	ld [hli], a
	inc de
	ld a, [de]
	ld [hli], a
	inc de
	inc hl
	inc hl
	dec c
	jr nz, .wave_in
	ld a, [wStarCnt]
	cp 24
	jr z, .wave_done
	add 6
	ld [wStarCnt], a
.wave_done
	call MoveDownSmallStars
	push af
	ld hl, wShadowOAM + 4 * 4
	ld de, wShadowOAM
	ld bc, 20 * 4
	call CopyBytes
	pop af
	pop hl
	pop bc
	jr c, .end
	dec c
	jr nz, .waves
	and a
.end
	push af
	xor a
	ld [wFixStars], a
	pop af
	ret

MoveDownSmallStars:
	ld b, 8
.l
	ld hl, wShadowOAM + 23 * 4
	ld a, [wStarCnt]
	ld de, -4
	ld c, a
	and a
	jr z, .none
.in
	inc [hl]
	add hl, de
	dec c
	jr nz, .in
.none
	ld a, [wOBP1]
	xor %10100000
	ld [wOBP1], a
	ld c, 3
	call CheckInt
	ret c
	dec b
	jr nz, .l
	ret

; the full-color hack's star colors: big star palette 6, small stars 4, 7, 6, 5 by OAM slot
FixStarPals:
	push hl
	push bc
	ld hl, wShadowOAM + 2
	ld b, 0
.l
	ld a, [hli]
	cp $A0
	jr z, .big
	cp $A1
	jr z, .big
	cp $A2
	jr nz, .next
	ld a, b
	and 3
	push hl
	ld hl, .small
	add l
	ld l, a
	jr nc, .nc
	inc h
.nc
	ld c, [hl]
	pop hl
	jr .set
.big
	ld c, 6
.set
	ld a, [hl]
	and $F8
	or c
	ld [hl], a
.next
	inc hl
	inc hl
	inc hl
	inc b
	ld a, b
	cp 40
	jr nz, .l
	pop bc
	pop hl
	ret
.small
	db 4, 7, 6, 5

PlayIntroScene:
	xor a
	ld hl, PalGengar
	call SetBasePal
	ld a, 8
	ld hl, PalNidorino
	call SetBasePal
	ld a, %11100100
	ld [wBGP], a
	ld [wOBP0], a
	ld [wOBP1], a
	xor a
	ldh [hSCX], a
	ld [wNidoTile], a                  ; この MOD（phase68）：赤と 同じく 0 から（前は 前の 画面の のこりで 絵が ずれた）
	call Frame                         ; この MOD（phase68）：色と SCX を 先に 出してから ゲンガーを 描く（前は 1コマ 灰色で 出た）
	ld de, GengarTilemap1
	call GengarTiles
	ld a, 8
	ld [wBaseX], a
	ld a, $50
	ld [wBaseY], a
	call InitNidorinoOAM
	ld de, 40 << 8 | $FF
	call IntroMoveMon
	ret c
; hip
	ld a, SFX_INTRO_HIP
	call Sfx
	xor a
	ld [wNidoTile], a
	ld de, NidoAnim1
	call AnimateNidorino
; hop
	ld a, SFX_INTRO_HOP
	call Sfx
	ld de, NidoAnim2
	call AnimateNidorino
	ld c, 10
	call CheckInt
	ret c
; hip
	ld a, SFX_INTRO_HIP
	call Sfx
	ld de, NidoAnim1
	call AnimateNidorino
; hop
	ld a, SFX_INTRO_HOP
	call Sfx
	ld de, NidoAnim2
	call AnimateNidorino
	ld c, 30
	call CheckInt
	ret c
; raise
	ld de, GengarTilemap2
	call GengarTiles
	ld a, SFX_INTRO_RAISE
	call Sfx
	ld de, 4 << 8 | 1
	call IntroMoveMon
	ld c, 30
	call CheckInt
	ret c
; slash
	ld de, GengarTilemap3
	call GengarTiles
	ld a, SFX_INTRO_CRASH
	call Sfx
	ld de, 8 << 8 | 0
	call IntroMoveMon
; hip
	ld a, SFX_INTRO_HIP
	call Sfx
	ld a, $24
	ld [wNidoTile], a
	ld de, NidoAnim3
	call AnimateNidorino
	ld c, 30
	call CheckInt
	ret c
	ld de, 4 << 8 | 1
	call IntroMoveMon
	ld de, GengarTilemap1
	call GengarTiles
	ld c, 60
	call CheckInt
	ret c
; hip
	ld a, SFX_INTRO_HIP
	call Sfx
	xor a
	ld [wNidoTile], a
	ld de, NidoAnim4
	call AnimateNidorino
; hip
	ld a, SFX_INTRO_HIP
	call Sfx
	ld de, NidoAnim5
	call AnimateNidorino
	ld c, 20
	call CheckInt
	ret c
	ld a, $24
	ld [wNidoTile], a
	ld de, NidoAnim6
	call AnimateNidorino
	ld c, 30
	call CheckInt
	ret c
; lunge
	ld a, SFX_INTRO_LUNGE
	call Sfx
	ld a, $48
	ld [wNidoTile], a
	ld de, NidoAnim7
	call AnimateNidorino
	ld c, 80
	jp CheckInt

GengarTiles: ; de = 7x7 tile IDs -> BG (13, 7)
	ld hl, $9C00 + 7 * 32 + 13
	ld bc, 7 << 8 | 7
	jp VRect

AnimateNidorino:
	ld a, [de]
	cp $50
	ret z
	ld [wBaseY], a
	inc de
	ld a, [de]
	ld [wBaseX], a
	push de
	ld c, 36
	call UpdateNidorinoOAM
	ld c, 5
	call DelayN
	pop de
	inc de
	jr AnimateNidorino

UpdateNidorinoOAM:
	ld hl, wShadowOAM
	ld a, [wNidoTile]
	ld d, a
.l
	ld a, [wBaseY]
	add [hl]
	ld [hli], a
	ld a, [wBaseX]
	add [hl]
	ld [hli], a
	ld a, d
	ld [hli], a
	inc hl
	inc d
	dec c
	jr nz, .l
	ret

InitNidorinoOAM:
	ld hl, wShadowOAM
	ld d, 0
	ld b, 6
.col
	ld a, [wBaseY]
	ld e, a
	ld c, 6
.row
	ld a, e
	add 8
	ld e, a
	ld [hli], a
	ld a, [wBaseX]
	ld [hli], a
	ld a, d
	ld [hli], a
	ld a, $80
	ld [hli], a
	inc d
	dec c
	jr nz, .row
	ld a, [wBaseX]
	add 8
	ld [wBaseX], a
	dec b
	jr nz, .col
	ret

IntroMoveMon: ; d = steps (2 pixels), e = $FF Nidorino right, 1 Gengar left, 0 Gengar right
	ld a, e
	cp $FF
	jr z, .nido
	cp 1
	jr z, .left
	ldh a, [hSCX]
	dec a
	dec a
	jr .set
.nido
	push de
	ld a, 2
	ld [wBaseX], a
	xor a
	ld [wBaseY], a
	ld c, 36
	call UpdateNidorinoOAM
	pop de
.left
	ldh a, [hSCX]
	inc a
	inc a
.set
	ldh [hSCX], a
	push de
	ld c, 2
	call CheckInt
	pop de
	ret c
	dec d
	jr nz, IntroMoveMon
	ret

; ---------------------------------------------------------------- title screen
TitleScreen:
	xor a
	ld [wBGP], a
	ld [wOBP0], a
	ld [wOBP1], a
	call Frame
	call DisableLCD
	call ClearSprites
	call ClearVRAMAttrs
	ld hl, GfxCopyright
	ld de, $9410
	call Decomp
	ld hl, GfxLogo
	ld de, $8800
	call Decomp
	ld hl, GfxPlayer
	ld de, $8000
	call Decomp
	ld hl, $97F0
	ld bc, 16
	xor a
	call ByteFill
	ld hl, $9800
	ld bc, $400
	ld a, $7F
	call ByteFill
; the logo
	ld de, TitleLogoMap
	ld hl, $9800 + LOGO_ROW * 32 + LOGO_COL
	ld b, LOGO_H
.lr
	push hl
	ld c, LOGO_W
.lc
	ld a, [de]
	inc de
	ld [hli], a
	dec c
	jr nz, .lc
	pop hl
	ld a, l
	add 32
	ld l, a
	jr nc, .lnc
	inc h
.lnc
	dec b
	jr nz, .lr
; "©1995 GAME FREAK inc."
	ld hl, $9800 + 17 * 32 + 3
	ld a, $41
	ld b, 13
.cr
	ld [hli], a
	inc a
	dec b
	jr nz, .cr
; the Pokémon (7x7, column by column, at (9, 10))
	ld hl, $9800 + 10 * 32 + 9
	ld de, 0
	ld b, 7
.mr
	push hl
	ld a, e
	ld c, 7
.mc
	ld [hli], a
	add 7
	dec c
	jr nz, .mc
	pop hl
	ld a, l
	add 32
	ld l, a
	jr nc, .mnc
	inc h
.mnc
	inc e
	dec b
	jr nz, .mr
; attributes: logo palette 1, copyright palette 3 (the Pokémon: 0)
	ld a, 1
	ldh [rVBK], a
	ld hl, $9800
	ld bc, 10 * 32
	ld a, 1
	call ByteFill
	ld hl, $9800 + 17 * 32
	ld bc, 32
	ld a, 3
	call ByteFill
	xor a
	ldh [rVBK], a
; the player (5x7 sprites)
	ld hl, wShadowOAM
	ld de, $6030
	ld b, 7
	xor a
	ld [wScroll], a
.pr
	push de
	ld c, 5
.pc
	ld a, d
	ld [hli], a
	ld a, e
	ld [hli], a
	add 8
	ld e, a
	ld a, [wScroll]
	ld [hli], a
	inc a
	ld [wScroll], a
	xor a
	ld [hli], a
	dec c
	jr nz, .pc
	pop de
	ld a, 8
	add d
	ld d, a
	dec b
	jr nz, .pr
; first Pokémon: Charmander
	xor a
	ld [wTitleMon], a
	call LoadTitleMon
	ld hl, wMonBuffer
	ld de, $9000
	ld bc, 49 * 16
	call CopyBytes
; palettes
	ld a, 1
	ld hl, PalLogo
	call SetBasePal
	ld a, 4
	ld hl, PalLogo
	call SetBasePal
	ld a, 3
	ld hl, PalCopyright
	call SetBasePal
	ld a, 8
	ld hl, PalPlayer
	call SetBasePal
; the logo comes in from the right
	ld a, $90
	ld [wScroll], a
	ldh [hSCX], a
	ld b, 0
	ld c, 63
	call LYOverridesSet
	ld a, $43
	ldh [hLCDCPointer], a
	ld a, $C3
	ldh [rLCDC], a
	ld a, %11100100
	ld [wBGP], a
	ld [wOBP0], a
	ld a, SFX_INTRO_WHOOSH
	call Sfx
.slide
	call Frame
	ld a, [wScroll]
	add 4
	ld [wScroll], a
	ldh [hSCX], a                      ; line 0 (and any line the LCD interrupt misses)
	ld b, 0
	ld c, 63
	call LYOverridesSet
	ld a, [wScroll]
	and a
	jr nz, .slide
	ld c, 20 + 3
	call DelayN
	ld a, MUS_TITLE
	call Music
.loop
	ld c, 255
	call CheckInt
	jr c, .done
	ld de, 0 << 8 | 20                 ; scroll the Pokémon out to the left
	call ScrollMon
	call PickNewMon
	ld de, $A0 << 8 | 12               ; and the new one in from the right
	call ScrollMon
	call LYOverridesZero
	jr .loop
.done
	call LYOverridesZero
	ld a, [wTitleMon]
	ld c, a
	ld b, 0
	ld hl, TitleMons
	add hl, bc
	ld a, [hl]
	call PlayMonCry
	call WaitSFX
	xor a
	ld [wBGP], a
	ld [wOBP0], a
	ld [wOBP1], a
	ld c, 3
	call DelayN
	call ClearSprites
	ldh a, [hJoyDown]
	and $46
	cp $46
	ld a, 1                            ; delete the save file
	ret z
	xor a
	ret

ScrollMon: ; d = first SCX, e = frames; SCX += 8 each frame, on the Pokémon's lines
.l
	push de
	ld a, d
	ld b, $47                          ; the value at index LY is used from line LY + 1
	ld c, $87
	call LYOverridesSet
	call Frame
	pop de
	ld a, d
	add 8
	ld d, a
	dec e
	jr nz, .l
	ret

PickNewMon:
.r
	call Random
	and 15
	ld hl, wTitleMon
	cp [hl]
	jr z, .r
	ld [hl], a
	call LoadTitleMon
	ld de, wMonBuffer
	ld hl, $9000
	ldh a, [$FF9D]
	ld b, a
	ld c, 49
	jp Get2bpp

LoadTitleMon: ; wTitleMon -> wMonBuffer, its palette in BG 0
	ld a, [wTitleMon]
	ld l, a
	ld h, 0
	add hl, hl
	add hl, hl
	add hl, hl
	ld de, TitleMonPals
	add hl, de
	xor a
	call SetBasePal
	ld a, [wTitleMon]
	ld l, a
	ld h, 0
	add hl, hl
	ld de, TitleMonPics
	add hl, de
	ld a, [hli]
	ld h, [hl]
	ld l, a
	ld de, wMonBuffer
	ld a, MON_BANK
	jp FarDecompress

; ---------------------------------------------------------------- misc
Decomp: ; hl -> de (this bank)
	ld a, CODE_BANK
	jp FarDecompress

ClearVRAMAttrs:
	ld a, 1
	ldh [rVBK], a
	ld hl, $9800
	ld bc, $800
	xor a
	call ByteFill
	xor a
	ldh [rVBK], a
	ret

INCLUDE "phase53_data.inc"
