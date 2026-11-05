; ポケットモンスター クリスタル（日本版）のアドレス一覧
; 英語版の逆アセンブル pret/pokecrystal と照らし合わせて調べたもの

; --- HRAM
DEF hJoyDown              EQU $ffa8
DEF hBGMapMode            EQU $ffd4
DEF hSCX                  EQU $ffcf
DEF hSCY                  EQU $ffd0

; --- WRAM
DEF wShadowOAM            EQU $c400
DEF wLinkMode             EQU $c2dc
DEF wMonType              EQU $cf53
DEF wCurSpecies           EQU $cf54
DEF wMenuBorderTopCoord   EQU $cf76
DEF wMenuBorderLeftCoord  EQU $cf77
DEF wMenuBorderBottomCoord EQU $cf78
DEF w2DMenuCursorInitY    EQU $cf95
DEF w2DMenuCursorOffsets  EQU $cf9b
DEF w2DMenuNumRows        EQU $cf97
DEF w2DMenuNumCols        EQU $cf98
DEF wMenuCursorY          EQU $cf9d
DEF wMenuCursorX          EQU $cf9e
DEF wOverworldDelay       EQU $cfa5
DEF wOptions              EQU $cfc0
DEF wStringBuffer1        EQU $d05b
DEF wStringBuffer2        EQU $d066
DEF wCurPartySpecies      EQU $d0c8
DEF wCurPartyMon          EQU $d0c9
DEF wMonSubmenuCount      EQU $d21b
DEF wMonSubmenuItems      EQU $d21c
DEF wNamedObjectIndex     EQU $d296
DEF wStatusFlags2         EQU $d840
DEF wPartyMon1Moves       EQU $dca7
DEF wPartyMon1PP          EQU $dcbc
DEF wPartyMonNicknames    EQU $dde9
DEF PARTYMON_STRUCT_LENGTH EQU $30
DEF MON_NAME_LENGTH       EQU 6
DEF NUM_MOVES             EQU 4

; --- ホーム（バンク0）
DEF DelayFrame            EQU $045a
DEF PlaceString           EQU $1057
DEF PrintText             EQU $1041
DEF StaticMenuJoypad      EQU $1b94
DEF ExitMenu              EQU $1bd2
DEF InitVerticalMenuCursor EQU $1bdb
DEF CloseWindow           EQU $1be2
DEF MenuBox               EQU $1c86
DEF MenuBoxCoord2Tile     EQU $1cc8
DEF LoadMenuHeader        EQU $1d00
DEF MenuTextbox           EQU $1d1a
DEF MenuTextboxBackup     EQU $1d32
DEF LoadStandardMenuHeader EQU $1d39
DEF Call_ExitMenu         EQU $1d48
DEF YesNoBox              EQU $1d9a
DEF CopyBytes             EQU $2ff2
DEF AddNTimes             EQU $30ca
DEF CopyName1             EQU $30a2
DEF FarQueueScript        EQU $319b
DEF ClearBGPalettes       EQU $31bf
DEF WaitBGMap             EQU $31c2
DEF SetDefaultBGPAndOBP   EQU $32c5
DEF GetMoveName           EQU $34c8
DEF GetBaseData           EQU $3826
DEF GetCurNickname        EQU $386c
DEF WaitPlaySFX           EQU $3bdb

; --- バンクつき
DEF BANK_STARTMENU        EQU $04
DEF StartMenu_Items       EQU $65c1   ; 9項目 × 6バイト
DEF StartMenu_MenuDataItemsPtr EQU $65bf
DEF StartMenu_AppendMenuList EQU $677b
DEF StartMenu_ExitAppend  EQU $675e   ; ld a, STARTMENUITEM_EXIT / call .AppendMenuList
DEF PCScript_Bank         EQU $2f
DEF PCScript              EQU $4192   ; opentext / special PokemonCenterPC / closetext / end

DEF BANK_MONMENU          EQU $04
DEF PokemonActionSubmenu_ActionsPtr EQU $69ff  ; ld hl, .Actions の hl
DEF PokemonActionSubmenu_Actions EQU $6a11     ; 20項目 × 3バイト
DEF ChooseMoveToDelete    EQU $6fe1
DEF NamingScreen          EQU $565b

DEF BANK_MONSUBMENU       EQU $09
DEF MonMenuOptionStrings  EQU $4cc4
DEF MonMenuOptions        EQU $4cea
DEF MonSubmenu_LoadHeader EQU $4d36   ; ld hl, .MenuHeader / call LoadMenuHeader
DEF MonSubmenu_Header     EQU $4d50
DEF MonMenuLoop_Joypad    EQU $4d78   ; set 6,[w2DMenuFlags1] / call StaticMenuJoypad ...
DEF MonMenuLoop_Select    EQU $4d95
DEF MonSubmenu_GetTopCoordCall EQU $4d3c
DEF MonSubmenu_GetTopCoord EQU $4d58
DEF MonSubmenu_PopulateCall EQU $4d3f
DEF PopulateMonMenu       EQU $4da2
DEF MonMenuLoop_InitCursorCall EQU $4d75
DEF GetMonMenuString      EQU $4dc1
DEF GetMonMenuString_Ptr  EQU $4dc2   ; ld hl, MonMenuOptions + 1
DEF GetMonMenuString_StrPtr EQU $4ddd ; ld hl, MonMenuOptionStrings
DEF IsFieldMove_Ptr       EQU $4e65   ; ld hl, MonMenuOptions
DEF GetMonSubmenuItems_Cancel EQU $4e40
DEF GetMonSubmenuItems_Term EQU $4e4c
DEF AddMonMenuItem        EQU $4e94

DEF BANK_PARTYMENU        EQU $14
DEF LoadPartyMenuGFX      EQU $404f
DEF WritePartyMenuTilemap EQU $405f
DEF InitPartyMenuGFX      EQU $43d4
DEF InitPartyMenuWithCancel EQU $43f9
DEF PlacePartyMenuText    EQU $448e

DEF BANK_PLAYERMOVE       EQU $20
DEF DoPlayerMovement_DoStep EQU $425f
DEF DoPlayerMovement_walk EQU $41ae
DEF DoPlayerMovement_surf EQU $41db

DEF BANK_OVERWORLD        EQU $25
DEF HandleMap_Tail        EQU $678b   ; call NextOverworldFrame / call HandleMapBackground
DEF NextOverworldFrame    EQU $67b7
DEF HandleMapBackground   EQU $67e1

DEF BaseData              EQU $514ba  ; ROM内の位置（バンク$14:$54ba）

; --- 定数
DEF STEP_WALK             EQU 1
DEF STEP_BIKE             EQU 2
DEF B_BUTTON              EQU %00000010
DEF STARTMENUITEM_EXIT    EQU 6
DEF STARTMENUITEM_PC      EQU 9
DEF MONMENU_MENUOPTION    EQU 1
DEF MONMENUITEM_CANCEL    EQU $12
DEF MONMENUITEM_NAME      EQU $16
DEF MONMENUITEM_FORGET    EQU $17
DEF NAME_MON              EQU 0
DEF SFX_MOVE_DELETED      EQU $97
DEF STATUSFLAGS2_BUG_CONTEST_TIMER_F EQU 2

; 追加コードを置くバンク（日本版では空き）
DEF BANK_NEW              EQU $70

MACRO farcall_jp
	ld a, BANK(\1)
	ld hl, \1
	rst $08
ENDM
