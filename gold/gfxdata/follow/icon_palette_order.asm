; How each species' two colors are arranged into its icon palette.
;
; A mon pic is shaded white / color 1 / color 2 / black, and icons reuse those same two colors.
; Icon art is not always shaded the same way round though, so some species read better with the
; pair swapped, or with the light slot pushed to white instead of the mon's own lighter color.
;
; One byte per species, indexed the same way menu_icon_pals.asm is -- by species index, with four
; padding rows ahead of the label so the negative indexes eggs use land on something valid.
; This started as a sparse list of exceptions, but once about half the dex wanted an entry the
; dense form became both smaller and quicker: 251 bytes and a direct index, against 348 bytes and
; a linear scan.
;
; ICON_PAL_OFFWHITE always replaces whichever color ends up in the *light* slot, so which of the
; two it discards depends on whether ICON_PAL_SWAP is set as well:
;
;	ICON_PAL_SWAP                       ; color 2 light, color 1 dark
;	ICON_PAL_OFFWHITE                   ; color 1 discarded, color 2 dark
;	ICON_PAL_SWAP | ICON_PAL_OFFWHITE   ; color 2 discarded, color 1 dark
;
; So if OFFWHITE is eating the color you wanted to keep, add ICON_PAL_SWAP.
;
; A species entry covers every one of its forms. A form that wants something different goes in
; IconPaletteOrderForms below, which is checked first.

	db ICON_PAL_NORMAL ; EGG is -3
	db ICON_PAL_NORMAL ; unused
	db ICON_PAL_NORMAL ; unused
	db ICON_PAL_NORMAL ; unused
IconPaletteOrders:
	table_width 1
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; BULBASAUR
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; IVYSAUR
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; VENUSAUR
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; CHARMANDER
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; CHARMELEON
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; CHARIZARD
	db ICON_PAL_NORMAL                   ; SQUIRTLE
	db ICON_PAL_OFFWHITE                 ; WARTORTLE
	db ICON_PAL_NORMAL                   ; BLASTOISE
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; CATERPIE
	db ICON_PAL_NORMAL                   ; METAPOD
	db ICON_PAL_NORMAL                   ; BUTTERFREE
	db ICON_PAL_NORMAL                   ; WEEDLE
	db ICON_PAL_NORMAL                   ; KAKUNA
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; BEEDRILL
	db ICON_PAL_NORMAL                   ; PIDGEY
	db ICON_PAL_OFFWHITE                 ; PIDGEOTTO
	db ICON_PAL_OFFWHITE                 ; PIDGEOT
	db ICON_PAL_OFFWHITE                 ; RATTATA
	db ICON_PAL_NORMAL                   ; RATICATE
	db ICON_PAL_SWAP                     ; SPEAROW
	db ICON_PAL_NORMAL                   ; FEAROW
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; EKANS
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; ARBOK
	db ICON_PAL_NORMAL                   ; PIKACHU
	db ICON_PAL_NORMAL                   ; RAICHU
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; SANDSHREW
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; SANDSLASH
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; NIDORAN_F
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; NIDORINA
	db ICON_PAL_NORMAL                   ; NIDOQUEEN
	db ICON_PAL_OFFWHITE                 ; NIDORAN_M
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; NIDORINO
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; NIDOKING
	db ICON_PAL_NORMAL                   ; CLEFAIRY
	db ICON_PAL_NORMAL                   ; CLEFABLE
	db ICON_PAL_NORMAL                   ; VULPIX
	db ICON_PAL_NORMAL                   ; NINETALES
	db ICON_PAL_NORMAL                   ; JIGGLYPUFF
	db ICON_PAL_NORMAL                   ; WIGGLYTUFF
	db ICON_PAL_NORMAL                   ; ZUBAT
	db ICON_PAL_NORMAL                   ; GOLBAT
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; ODDISH
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; GLOOM
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; VILEPLUME
	db ICON_PAL_NORMAL                   ; PARAS
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; PARASECT
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; VENONAT
	db ICON_PAL_NORMAL                   ; VENOMOTH
	db ICON_PAL_SWAP                     ; DIGLETT
	db ICON_PAL_SWAP                     ; DUGTRIO
	db ICON_PAL_NORMAL                   ; MEOWTH
	db ICON_PAL_NORMAL                   ; PERSIAN
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; PSYDUCK
	db ICON_PAL_NORMAL                   ; GOLDUCK
	db ICON_PAL_NORMAL                   ; MANKEY
	db ICON_PAL_NORMAL                   ; PRIMEAPE
	db ICON_PAL_NORMAL                   ; GROWLITHE
	db ICON_PAL_NORMAL                   ; ARCANINE
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; POLIWAG
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; POLIWHIRL
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; POLIWRATH
	db ICON_PAL_SWAP                     ; ABRA
	db ICON_PAL_SWAP                     ; KADABRA
	db ICON_PAL_SWAP                     ; ALAKAZAM
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; MACHOP
	db ICON_PAL_SWAP                     ; MACHOKE
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; MACHAMP
	db ICON_PAL_NORMAL                   ; BELLSPROUT
	db ICON_PAL_NORMAL                   ; WEEPINBELL
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; VICTREEBEL
	db ICON_PAL_SWAP                     ; TENTACOOL
	db ICON_PAL_SWAP                     ; TENTACRUEL
	db ICON_PAL_NORMAL                   ; GEODUDE
	db ICON_PAL_NORMAL                   ; GRAVELER
	db ICON_PAL_NORMAL                   ; GOLEM
	db ICON_PAL_NORMAL                   ; PONYTA
	db ICON_PAL_NORMAL                   ; RAPIDASH
	db ICON_PAL_OFFWHITE                 ; SLOWPOKE
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; SLOWBRO
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; MAGNEMITE
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; MAGNETON
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; FARFETCH_D
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; DODUO
	db ICON_PAL_NORMAL                   ; DODRIO
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; SEEL
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; DEWGONG
	db ICON_PAL_NORMAL                   ; GRIMER
	db ICON_PAL_NORMAL                   ; MUK
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; SHELLDER
	db ICON_PAL_NORMAL                   ; CLOYSTER
	db ICON_PAL_OFFWHITE                 ; GASTLY
	db ICON_PAL_SWAP                     ; HAUNTER
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; GENGAR -- swap the purple and white, and make the purple off-white
	db ICON_PAL_NORMAL                   ; ONIX
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; DROWZEE
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; HYPNO
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; KRABBY
	db ICON_PAL_NORMAL                   ; KINGLER
	db ICON_PAL_NORMAL | ICON_PAL_OFFWHITE ; VOLTORB
	db ICON_PAL_NORMAL | ICON_PAL_OFFWHITE ; ELECTRODE
	db ICON_PAL_NORMAL                   ; EXEGGCUTE
	db ICON_PAL_NORMAL                   ; EXEGGUTOR
	db ICON_PAL_NORMAL                   ; CUBONE
	db ICON_PAL_NORMAL                   ; MAROWAK
	db ICON_PAL_SWAP                     ; HITMONLEE
	db ICON_PAL_SWAP                     ; HITMONCHAN
	db ICON_PAL_SWAP                     ; LICKITUNG
	db ICON_PAL_OFFWHITE                 ; KOFFING
	db ICON_PAL_OFFWHITE                 ; WEEZING
	db ICON_PAL_NORMAL                   ; RHYHORN
	db ICON_PAL_NORMAL                   ; RHYDON
	db ICON_PAL_NORMAL                   ; CHANSEY
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; TANGELA
	db ICON_PAL_NORMAL                   ; KANGASKHAN
	db ICON_PAL_NORMAL                   ; HORSEA
	db ICON_PAL_NORMAL                   ; SEADRA
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; GOLDEEN
	db ICON_PAL_OFFWHITE                 ; SEAKING
	db ICON_PAL_NORMAL                   ; STARYU
	db ICON_PAL_NORMAL                   ; STARMIE
	db ICON_PAL_NORMAL                   ; MR__MIME
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; SCYTHER
	db ICON_PAL_SWAP                     ; JYNX
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; ELECTABUZZ
	db ICON_PAL_NORMAL                   ; MAGMAR
	db ICON_PAL_OFFWHITE                 ; PINSIR
	db ICON_PAL_NORMAL		     ; TAUROS
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; MAGIKARP
	db ICON_PAL_NORMAL                   ; GYARADOS
	db ICON_PAL_NORMAL                   ; LAPRAS
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; DITTO
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; EEVEE
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; VAPOREON
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; JOLTEON
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; FLAREON
	db ICON_PAL_NORMAL                   ; PORYGON
	db ICON_PAL_OFFWHITE                 ; OMANYTE
	db ICON_PAL_OFFWHITE                 ; OMASTAR
	db ICON_PAL_NORMAL                   ; KABUTO
	db ICON_PAL_SWAP                     ; KABUTOPS
	db ICON_PAL_NORMAL                   ; AERODACTYL
	db ICON_PAL_NORMAL                   ; SNORLAX
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; ARTICUNO
	db ICON_PAL_NORMAL                   ; ZAPDOS
	db ICON_PAL_NORMAL                   ; MOLTRES
	db ICON_PAL_NORMAL | ICON_PAL_OFFWHITE; DRATINI
	db ICON_PAL_OFFWHITE                 ; DRAGONAIR
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; DRAGONITE
	db ICON_PAL_NORMAL                   ; MEWTWO
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; MEW
	db ICON_PAL_NORMAL                   ; CHIKORITA
	db ICON_PAL_NORMAL                   ; BAYLEEF
	db ICON_PAL_SWAP                     ; MEGANIUM
	db ICON_PAL_NORMAL                   ; CYNDAQUIL
	db ICON_PAL_NORMAL                   ; QUILAVA
	db ICON_PAL_NORMAL                   ; TYPHLOSION
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; TOTODILE
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; CROCONAW
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; FERALIGATR
	db ICON_PAL_NORMAL                   ; SENTRET
	db ICON_PAL_NORMAL                   ; FURRET
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; HOOTHOOT
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; NOCTOWL
	db ICON_PAL_NORMAL                   ; LEDYBA
	db ICON_PAL_NORMAL                   ; LEDIAN
	db ICON_PAL_NORMAL                   ; SPINARAK
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; ARIADOS
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; CROBAT
	db ICON_PAL_NORMAL                   ; CHINCHOU
	db ICON_PAL_NORMAL                   ; LANTURN
	db ICON_PAL_NORMAL                   ; PICHU
	db ICON_PAL_NORMAL                   ; CLEFFA
	db ICON_PAL_NORMAL                   ; IGGLYBUFF
	db ICON_PAL_NORMAL                   ; TOGEPI
	db ICON_PAL_NORMAL                   ; TOGETIC
	db ICON_PAL_SWAP                     ; NATU
	db ICON_PAL_SWAP                     ; XATU
	db ICON_PAL_NORMAL                   ; MAREEP
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; FLAAFFY
	db ICON_PAL_NORMAL                   ; AMPHAROS
	db ICON_PAL_SWAP                     ; BELLOSSOM
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; MARILL
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; AZUMARILL
	db ICON_PAL_NORMAL                   ; SUDOWOODO
	db ICON_PAL_NORMAL                   ; POLITOED
	db ICON_PAL_NORMAL                   ; HOPPIP
	db ICON_PAL_NORMAL                   ; SKIPLOOM
	db ICON_PAL_NORMAL                   ; JUMPLUFF
	db ICON_PAL_NORMAL                   ; AIPOM
	db ICON_PAL_NORMAL                   ; SUNKERN
	db ICON_PAL_NORMAL                   ; SUNFLORA
	db ICON_PAL_NORMAL                   ; YANMA
	db ICON_PAL_SWAP                     ; WOOPER
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; QUAGSIRE
	db ICON_PAL_SWAP                     ; ESPEON
	db ICON_PAL_NORMAL                   ; UMBREON
	db ICON_PAL_NORMAL                   ; MURKROW
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; SLOWKING
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; MISDREAVUS
	db ICON_PAL_OFFWHITE                 ; UNOWN
	db ICON_PAL_NORMAL                   ; WOBBUFFET
	db ICON_PAL_NORMAL                   ; GIRAFARIG
	db ICON_PAL_NORMAL                   ; PINECO
	db ICON_PAL_SWAP                     ; FORRETRESS
	db ICON_PAL_NORMAL                   ; DUNSPARCE
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; GLIGAR
	db ICON_PAL_NORMAL                   ; STEELIX
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; SNUBBULL
	db ICON_PAL_NORMAL                   ; GRANBULL
	db ICON_PAL_NORMAL                   ; QWILFISH
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; SCIZOR
	db ICON_PAL_NORMAL                   ; SHUCKLE
	db ICON_PAL_OFFWHITE                 ; HERACROSS
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; SNEASEL
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; TEDDIURSA
	db ICON_PAL_NORMAL                   ; URSARING
	db ICON_PAL_NORMAL                   ; SLUGMA
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; MAGCARGO
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; SWINUB
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; PILOSWINE
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; CORSOLA
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; REMORAID
	db ICON_PAL_NORMAL                   ; OCTILLERY
	db ICON_PAL_OFFWHITE                 ; DELIBIRD
	db ICON_PAL_NORMAL                   ; MANTINE
	db ICON_PAL_SWAP                     ; SKARMORY
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; HOUNDOUR
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; HOUNDOOM
	db ICON_PAL_NORMAL                   ; KINGDRA
	db ICON_PAL_SWAP                     ; PHANPY
	db ICON_PAL_NORMAL                   ; DONPHAN
	db ICON_PAL_SWAP                     ; PORYGON2
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; STANTLER
	db ICON_PAL_NORMAL                   ; SMEARGLE
	db ICON_PAL_NORMAL                   ; TYROGUE
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; HITMONTOP
	db ICON_PAL_NORMAL                   ; SMOOCHUM
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; ELEKID
	db ICON_PAL_NORMAL                   ; MAGBY
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; MILTANK
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; BLISSEY
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; RAIKOU
	db ICON_PAL_NORMAL                   ; ENTEI
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; SUICUNE
	db ICON_PAL_SWAP                     ; LARVITAR
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; PUPITAR
	db ICON_PAL_SWAP                     ; TYRANITAR
	db ICON_PAL_NORMAL                   ; LUGIA
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; HO_OH
	db ICON_PAL_SWAP | ICON_PAL_OFFWHITE ; CELEBI
	assert_table_length NUM_POKEMON

; Per-form overrides, checked before the species table. Entries are
; (species index, form number, order), so only the forms that differ need listing.
;
;	dwbb SMEARGLE, SMEARGLE_BLUE_FORM, ICON_PAL_SWAP

IconPaletteOrderForms:
	dwbb ARBOK, ARBOK_ROCKET_FORM, 0
	dwbb MACHOKE, MACHOKE_RB_FORM, 0
	dw 0 ; terminator -- add entries above this line
