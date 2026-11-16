; Phase 54: the Kanto Hall of Fame and the staff roll as in Red (the Red full-color hack's layout and colors).
; Crystal's Hall of Fame (saving, the Hall of Fame record) runs first; then, in Kanto mode, Red's animation
; and Red's credits instead of Crystal's.  The Johto Hall of Fame stays Crystal's.
INCLUDE "jp.inc"

DEF DelayFrame       EQU $045A
DEF PlaceString      EQU $1057
DEF TextboxBorder    EQU $0FDB
DEF PrintNum         EQU $3164
DEF ClearScreen      EQU $0FC5
DEF WaitBGMap2       EQU $31CC
DEF LoadStandardFont EQU $0E3B
DEF CountSetBits     EQU $332B
DEF Get2bpp          EQU $0F6C
DEF DisableLCD       EQU $0568
DEF EnableLCD        EQU $058A
DEF FarDecompress    EQU $0B2A

DEF hSCX             EQU $FFCF
DEF hSCY             EQU $FFD0
DEF hWY              EQU $FFD2
DEF hBGMapMode       EQU $FFD4
DEF hLCDCPointer     EQU $FFC6
DEF hLYOverrideStart EQU $FFC7
DEF hLYOverrideEnd   EQU $FFC8
DEF hCGBPalUpdate    EQU $FFE5
DEF hROMBank         EQU $FF9D
DEF rSVBK            EQU $FF70
DEF rVBK             EQU $FF4F
DEF rLCDC            EQU $FF40

DEF wTilemap         EQU $C4A0
DEF wPartySpecies    EQU $DC9E
DEF wPartyMon1Level  EQU $DCA5 + $1F
DEF wPartyMonNicks   EQU $DDE9
DEF wPlayerName      EQU $D48E
DEF wGameTimeHours   EQU $D4B7
DEF wGameTimeMinutes EQU $D4B9
DEF wMoney           EQU $D841
DEF wPokedexCaught   EQU $DE2D
DEF wPokedexSeen     EQU $DE4D
DEF wBaseType1       EQU $D26E
DEF wBaseType2       EQU $D26F
DEF wMusicFadeID     EQU $C2A9
DEF wMusicFade       EQU $C2A7
DEF wBGPals2         EQU $D080            ; WRAM 5
DEF wLYOverrides     EQU $D100            ; WRAM 5
DEF wEventFlags      EQU $DA65

; work RAM (the overworld's; the game resets after the credits)
DEF wHoFMon     EQU $CB00
DEF wHoFLevel   EQU $CB01
DEF wHoFIndex   EQU $CB02
DEF wDexSeen    EQU $CB03
DEF wDexOwned   EQU $CB04
DEF wCredPage   EQU $CB05
DEF wCredMon    EQU $CB06
DEF wCredPtr    EQU $CB07                 ; 2 bytes
DEF wPalPtr     EQU $CB09                 ; 2 bytes
DEF wBGP        EQU $CB0B
DEF wSavedB     EQU $CB0C

MACRO lb ; reg, hi, lo
	ld \1, ((\2) << 8) | ((\3) & $FF)
ENDM

MACRO coord ; x, y
	ld hl, wTilemap + (\2) * 20 + (\1)
ENDM

SECTION "Phase54", ROMX[CODE_ADDR], BANK[CODE_BANK]

; replaces "call AnimateHallOfFame / farcall Credits" in Crystal's HallOfFame (b = status flags)
HallOfFameAnimAndCredits::
	ld a, b
	ld [wSavedB], a
	ld a, [wEventFlags + ($44 >> 3)]      ; EVENT_BEAT_ELITE_FOUR: set by Johto's Hall of Fame (Crystal)
	bit $44 & 7, a
	jr z, .kanto
	farcall_ $21, $6695                  ; Crystal: AnimateHallOfFame
	ld a, [wSavedB]
	ld b, a
	farcall_ $42, $58BF                  ; Crystal: Credits
	ret
.kanto
	call RedHallOfFame
	jp RedCredits

; Continue: TryLoadSaveFile; a save from before phase 52 gets the rival's name シゲル (Crystal's default was グリーン)
ContinueLoad::
	farcall_ $05, $4E87
	ret c
	ld hl, RIVAL_NAMED_BYTE
	bit RIVAL_NAMED_BIT, [hl]
	ret nz
	set RIVAL_NAMED_BIT, [hl]
	ld hl, DefaultRival
	ld de, $D4A6
	ld bc, 6
	call CopyBytes
	and a
	ret


; ---------------------------------------------------------------- palettes
; all BG palettes = 4 colors at [wPalPtr] (this bank) through the DMG palette wBGP
ApplyPal:
	push hl
	push de
	push bc
	ldh a, [rSVBK]
	push af
	ld a, 5
	ldh [rSVBK], a
	ld de, wBGPals2
	ld b, 8
.pal
	ld a, [wBGP]
	ld c, 4
.col
	push af
	and 3
	add a
	ld hl, wPalPtr
	push de
	ld e, [hl]
	inc hl
	ld d, [hl]
	add e
	ld l, a
	ld a, d
	adc 0
	ld h, a
	pop de
	ld a, [hli]
	ld [de], a
	inc de
	ld a, [hl]
	ld [de], a
	inc de
	pop af
	rrca
	rrca
	dec c
	jr nz, .col
	dec b
	jr nz, .pal
	pop af
	ldh [rSVBK], a
	ld a, 1
	ldh [hCGBPalUpdate], a
	pop bc
	pop de
	pop hl
	ret

SetPal: ; hl = 4 colors, a = DMG palette
	ld [wBGP], a
	ld a, l
	ld [wPalPtr], a
	ld a, h
	ld [wPalPtr + 1], a
	jr ApplyPal

SetBGP:
	ld [wBGP], a
	jr ApplyPal

FadeOutToWhite: ; Red's GBFadeOutToWhite (BG)
	ld a, %10010000
	call SetBGP
	ld c, 8
	call DelayFrames
	ld a, %01000000
	call SetBGP
	ld c, 8
	call DelayFrames
	xor a
	call SetBGP
	ld c, 8
	jp DelayFrames

FadeOutMusic:
	xor a
	ld [wMusicFadeID], a
	ld [wMusicFadeID + 1], a
	ld a, 10
	ld [wMusicFade], a
	ret

; hl = species' palette (FC table; dex 0-151, others: grey)
MonPal:
	ld a, [wHoFMon]
	cp 152
	jr c, .ok
	xor a
.ok
	ld l, a
	ld h, 0
	add hl, hl
	add hl, hl
	add hl, hl
	ld de, MonPals
	add hl, de
	ret

; place a 7-wide column-major picture: hl = coord, a = first tile, b = height, c = width
PlacePic:
.col
	push bc
	push hl
.row
	ld [hl], a
	inc a
	ld de, 20
	add hl, de
	dec b
	jr nz, .row
	pop hl
	inc hl
	pop bc
	dec c
	jr nz, .col
	ret

; ---------------------------------------------------------------- Hall of Fame (Red's AnimateHallOfFame)
RedHallOfFame:
	call ClearScreen
	call WaitBGMap2
	call LoadStandardFont
	call LoadFontsExtra
	ld a, $90
	ldh [hWY], a
	xor a
	ld [wHoFIndex], a
	ld a, MUS_HALL_OF_FAME
	ld e, a
	ld d, 0
	call PlayMusic
.mon
	ld a, [wHoFIndex]
	ld e, a
	ld d, 0
	ld hl, wPartySpecies
	add hl, de
	ld a, [hl]
	cp $FF
	jr z, .player
	cp $FD                               ; an egg: skipped
	jr z, .next
	ld [wHoFMon], a
	ld hl, wPartyMon1Level
	ld bc, $30
	ld a, [wHoFIndex]
	call AddNTimes
	ld a, [hl]
	ld [wHoFLevel], a
	xor a
	call ShowMonOrPlayer
	call DisplayMonInfo
	ld c, 80
	call DelayFrames
	coord 2, 13
	ld b, 3
	ld c, 14
	call TextboxBorder
	coord 3, 15
	ld de, HoFText
	call PlaceString
	call WaitBGMap
	ld c, 180
	call DelayFrames
	call FadeOutToWhite
.next
	ld hl, wHoFIndex
	inc [hl]
	jr .mon
.player
	xor a
	ld [wHoFMon], a
	inc a
	call ShowMonOrPlayer
	call DisplayPlayerStats
	call FadeOutMusic
	call FadeOutToWhite
	xor a
	ldh [hSCX], a
	ldh [hSCY], a
	ret

DEF AddNTimes EQU $30CA
DEF CopyBytes EQU $2FF2

; a = 0: the Pokémon wHoFMon, 1: the player
ShowMonOrPlayer:
	push af
	call ClearScreen
	call WaitBGMap2
	ld a, $D0
	ldh [hSCY], a
	ld a, $C0
	ldh [hSCX], a
	pop af
	and a
	jr nz, .player
	ld a, [wHoFMon]
	ld [wCurPartySpecies], a
	ld [wCurSpecies], a
	call GetBaseData
	ld de, $9000
	farcall_ $14, $510D                  ; GetMonFrontpic -> tiles $00
	ld de, $9310
	farcall_ $14, $5202                  ; GetMonBackpic -> tiles $31
	call MonPal
	jr .pics
.player
	ld de, $48B2                         ; the player's picture (raw 7x7)
	ld hl, $9000
	lb bc, $22, 49
	call Get2bpp
	farcall_ $22, $482E                  ; GetPlayerBackpic -> tiles $31
	ld hl, PalPlayer
.pics
	ld a, %11100100
	call SetPal
; the back picture scrolls in and away to the left
	coord 12, 6
	ld a, $31
	lb bc, 6, 6
	call PlacePic
	call WaitBGMap
	ld d, $A0
	ld e, 4
	call .scroll
	xor a
	ldh [hSCY], a
; the front picture slides in from the left
	call ClearTilemapNoPal
	coord 12, 5
	xor a
	lb bc, 7, 7
	call PlacePic
	call WaitBGMap
	ld d, 0
	ld e, -4
.scroll
	call DelayFrame
	ldh a, [hSCX]
	add e
	ldh [hSCX], a
	cp d
	jr nz, .scroll
	ret

ClearTilemapNoPal:
	ld hl, wTilemap
	ld bc, 20 * 18
	ld a, $7F
	jp ByteFill

DisplayMonInfo:
	coord 0, 3
	ld b, 8
	ld c, 9
	call TextboxBorder
	coord 1, 7
	ld de, HoFMonInfoText
	call PlaceString
	ld a, [wHoFIndex]
	ld hl, wPartyMonNicks
	ld bc, 6
	call AddNTimes
	ld d, h
	ld e, l
	coord 2, 5
	call PlaceString
	coord 7, 7
	ld de, wHoFLevel
	lb bc, 1, 3
	call PrintNum
	ld a, [wBaseType1]
	coord 6, 9
	call PrintTypeName
	ld a, [wBaseType1]
	ld b, a
	ld a, [wBaseType2]
	cp b
	jr z, .one
	coord 6, 11
	call PrintTypeName
.one
	call WaitBGMap
	ld a, [wHoFMon]
	call PlayMonCry
	jp WaitSFX

PrintTypeName: ; type a at hl (Crystal's type names)
	push hl
	ld l, a
	ld h, 0
	add hl, hl
	ld de, TypeNames
	add hl, de
	ld a, [hli]
	ld d, [hl]
	ld e, a
	pop hl
	jp PlaceString

DisplayPlayerStats:
; Red's Pokédex rating: Pokémon seen / caught (the first 151)
	ld hl, wPokedexSeen
	ld b, 19
	call CountSetBits
	ld [wDexSeen], a
	ld hl, wPokedexCaught
	ld b, 19
	call CountSetBits
	ld [wDexOwned], a
	coord 0, 4
	ld b, 6
	ld c, 10
	call TextboxBorder
	coord 5, 0
	ld b, 2
	ld c, 8
	call TextboxBorder
	coord 7, 2
	ld de, wPlayerName
	call PlaceString
	coord 1, 6
	ld de, HoFPlayTimeText
	call PlaceString
	coord 5, 7
	ld de, wGameTimeHours
	lb bc, 2, 3
	call PrintNum
	ld [hl], $6D
	inc hl
	ld de, wGameTimeMinutes
	lb bc, $81, 2
	call PrintNum
	coord 1, 9
	ld de, HoFMoneyText
	call PlaceString
	coord 4, 10
	ld de, wMoney
	lb bc, 3, 6
	call PrintNum
	ld [hl], $F0                         ; 円
	call WaitBGMap
	ld hl, DexSeenOwnedText
	call PrintAndDelay
	ld hl, DexRatingText
	call PrintAndDelay
	ld hl, DexRatings
.find
	ld a, [wDexOwned]
	cp [hl]
	inc hl
	jr c, .found
	inc hl
	inc hl
	jr .find
.found
	ld a, [hli]
	ld h, [hl]
	ld l, a
PrintAndDelay:
	call PrintText
	ld c, 120
	jp DelayFrames

; ---------------------------------------------------------------- credits (Red's)
RedCredits:
	call ClearScreen
	call WaitBGMap2
	ld c, 100
	call DelayFrames
	call DisableLCD
; text fades in: the font's black (color 3) becomes color 2
	ld hl, $8800
	ld bc, $80 * 16 / 2
.shift
	ld [hl], 0
	inc hl
	inc hl
	dec bc
	ld a, b
	or c
	jr nz, .shift
	ld hl, $97E0                          ; tile $7E: solid black
	ld bc, 16
	ld a, $FF
	call ByteFill
	ld a, 1
	ldh [rVBK], a
	ld hl, $9800
	ld bc, $400
	xor a
	call ByteFill
	xor a
	ldh [rVBK], a
	ld hl, wTilemap
	ld bc, 20 * 4
	ld a, $7E
	call ByteFill
	ld hl, wTilemap + 14 * 20
	ld bc, 20 * 4
	ld a, $7E
	call ByteFill
	call FillMiddleWhite
	ld hl, $9800
	ld bc, $400
	ld a, $7F
	call ByteFill
	ld hl, PalPlayer
	ld a, %11000000
	call SetPal
	call EnableLCD
	call WaitBGMap
	ld de, 0                              ; music off, then Red's staff roll music
	call PlayMusic
	call DelayFrame
	ld de, MUS_CREDITS
	call PlayMusic
	ld c, 128
	call DelayFrames
	xor a
	ld [wCredPage], a
	ld [wCredMon], a
.page
	ld a, [wCredPage]
	cp NUM_CRED_PAGES
	jr z, .end
	ld l, a
	ld h, 0
	add hl, hl
	ld de, CreditsPages
	add hl, de
	ld a, [hli]
	ld h, [hl]
	ld l, a
	ld a, l
	ld [wCredPtr], a
	ld a, h
	ld [wCredPtr + 1], a
	ld hl, wCredPage
	inc [hl]
	call CreditsPage
	jr .page
.end
; THE END stays until a button is pressed
.wait
	call DelayFrame
	call GetJoypad
	ldh a, [$FFA7]
	and $0F
	jr z, .wait
	call FadeOutMusic
	jp FadeOutToWhite

DEF GetJoypad EQU $0984

FillMiddleWhite:
	ld hl, wTilemap + 4 * 20
	ld bc, 20 * 10
	ld a, $7F
	jp ByteFill

CreditsPage:
	call FillMiddleWhite
	coord 9, 6
	push hl
.cmd
	ld hl, wCredPtr
	ld a, [hli]
	ld h, [hl]
	ld l, a
	ld a, [hli]
	ld b, a
	ld a, l
	ld [wCredPtr], a
	ld a, h
	ld [wCredPtr + 1], a
	ld a, b
	cp $FF
	jr z, .fade_mon
	cp $FE
	jr z, .mon
	cp $FD
	jr z, .fade
	cp $FC
	jr z, .text
	cp $FB
	jr z, .copyright
	cp $FA
	jr z, .the_end
; a credits line: centered around column 9
	ld l, a
	ld h, 0
	ld de, CreditsXOffsets
	add hl, de
	ld c, [hl]
	ld b, $FF
	ld l, a
	ld h, 0
	add hl, hl
	ld de, CreditsTexts
	add hl, de
	ld a, [hli]
	ld d, [hl]
	ld e, a
	pop hl
	push hl
	add hl, bc
	call PlaceString
	pop hl
	ld bc, 40
	add hl, bc
	push hl
	jr .cmd
.fade_mon
	pop hl
	call WaitBGMap
	call FadeInCredits
	ld c, 168
	call DelayFrames
	jp CreditsMon
.mon
	pop hl
	call WaitBGMap
	ld c, 168
	call DelayFrames
	jp CreditsMon
.fade
	pop hl
	call WaitBGMap
	call FadeInCredits
	ld c, 168
	jp DelayFrames
.text
	pop hl
	call WaitBGMap
	ld c, 168
	jp DelayFrames
.copyright
	push bc
	ld hl, GfxCopyright
	ld de, $9600
	lb bc, CODE_BANK, 25
	call FarDecompressToVRAM
	ld hl, CopyrightLines
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
	pop bc
	jp .cmd
.the_end
	pop hl
	ld c, 16
	call DelayFrames
	call FillMiddleWhite
	ld de, GfxTheEnd
	ld hl, $9600
	ldh a, [hROMBank]
	ld b, a
	ld c, 10
	call Get2bpp
	coord 4, 8
	ld de, TheEnd1
	call PlaceString
	coord 4, 9
	ld de, TheEnd2
	call PlaceString
	call WaitBGMap
	jp FadeInCredits

; decompress (from bank b) into WRAM, then copy c tiles to VRAM at de
FarDecompressToVRAM:
	push de
	push bc
	ld a, b
	ld de, $C800
	call FarDecompress
	pop bc
	pop hl
	ld de, $C800
	ldh a, [hROMBank]
	ld b, a
	jp Get2bpp

FadeInCredits:
	ld hl, .bgps
	ld b, 4
.l
	ld a, [hli]
	push hl
	push bc
	call SetBGP
	ld c, 5
	call DelayFrames
	pop bc
	pop hl
	dec b
	jr nz, .l
	ret
.bgps
	db %11000000, %11010000, %11100000, %11110000

; a black Pokémon passes across the middle of the screen from the right
CreditsMon:
	call FillMiddleWhite
	call WaitBGMap
	ld a, [wCredMon]
	ld e, a
	ld d, 0
	inc a
	ld [wCredMon], a
	ld hl, CreditsMons
	add hl, de
	ld a, [hl]
	ld [wCurPartySpecies], a
	ld [wCurSpecies], a
	call GetBaseData
	ld de, $9000
	farcall_ $14, $510D                  ; GetMonFrontpic
; the picture in BG columns 20-26 (off the screen), rows 6-12
	ld hl, $9800 + 6 * 32 + 20
	xor a
	ld c, 7
.col
	push hl
	ld b, 7
.row
	call VPoke
	inc a
	ld de, 32 - 1
	add hl, de
	dec b
	jr nz, .row
	pop hl
	inc hl
	dec c
	jr nz, .col
	ld a, %11111100                     ; a silhouette
	call SetBGP
	ldh a, [rSVBK]
	push af
	ld a, 5
	ldh [rSVBK], a
	ld hl, wLYOverrides
	ld bc, $90
	xor a
	call ByteFill
	ld a, $43
	ldh [hLCDCPointer], a
	ld d, 0
	ld e, 27
.scroll
	ld a, d
	ld hl, wLYOverrides + 31
	ld b, 80
.ov
	ld [hli], a
	dec b
	jr nz, .ov
	call DelayFrame
	ld a, d
	add 8
	ld d, a
	dec e
	jr nz, .scroll
	xor a
	ldh [hLCDCPointer], a
	pop af
	ldh [rSVBK], a
; clear the picture
	ld hl, $9800 + 6 * 32 + 20
	ld b, 7
.cr
	push bc
	push hl
	ld b, 7
	ld a, $7F
.cc
	call VPoke
	dec b
	jr nz, .cc
	pop hl
	ld de, 32
	add hl, de
	pop bc
	dec b
	jr nz, .cr
	ld a, %11000000
	jp SetBGP

VPoke: ; [hl+] = a while the LCD is on
	push af
	di
.w
	ldh a, [$FF41]
	and 2
	jr nz, .w
	pop af
	ld [hli], a
	ei
	ret

INCLUDE "phase54_data.inc"
