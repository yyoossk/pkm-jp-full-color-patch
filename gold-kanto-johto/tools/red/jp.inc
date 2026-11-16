; JP Crystal addresses used by the MOD's assembly sources
DEF PrintText        EQU $1041
DEF ClearTilemap     EQU $0FB2
DEF PlayMusic        EQU $3B24
DEF RotateFourPalettesLeft  EQU $04DD
DEF RotateFourPalettesRight EQU $04A3
DEF RotateThreePalettesRight EQU $04B6
DEF RotateThreePalettesLeft  EQU $04F0
DEF GetSGBLayout     EQU $330C
DEF GetBaseData      EQU $3826
DEF PrepMonFrontpic  EQU $3756
DEF PlayMonCry       EQU $379E
DEF WaitSFX          EQU $3BE2
DEF LoadMenuHeader   EQU $1D00
DEF VerticalMenu     EQU $1D4C
DEF CopyNameFromMenu EQU $1D83
DEF CloseWindow      EQU $1BE2
DEF ByteFill         EQU $300D
DEF CopyName2        EQU $30A5
DEF LoadFontsExtra   EQU $0E49
DEF WaitBGMap        EQU $31C2
DEF InitName         EQU $2ECB
DEF DelayFrames      EQU $0468

DEF wCurSpecies      EQU $CF54
DEF wCurPartySpecies EQU $D0C8
DEF wTrainerClass    EQU $D264
DEF wTempMonDVs      EQU $D0E3
DEF wMenuCursorY     EQU $CF9D
DEF wStringBuffer2   EQU $D066
DEF wGreensName      EQU $D4A6
DEF wPlayerGender    EQU $D463

DEF SCGB_TRAINER_OR_MON_FRONTPIC_PALS EQU $1C
DEF POKEMON_PROF     EQU $0A
DEF BLUE_CLASS       EQU $40
DEF NIDORINO         EQU $21

MACRO farcall_ ; bank, address
	ld a, \1
	ld hl, \2
	rst $08
ENDM

; extended event flag 0x9F6 (phase 52): the rival was named (Oak's speech) -> DA01 + $1F6 / 8, bit 6
DEF RIVAL_NAMED_BYTE EQU $DA3F
DEF RIVAL_NAMED_BIT  EQU 6
