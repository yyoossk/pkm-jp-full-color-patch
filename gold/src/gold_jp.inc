; ポケットモンスター 金（日本版・後期版 Rev 1）のアドレス一覧
; 英語版の逆アセンブル pret/pokegold と照らし合わせて調べたもの

; --- HRAM
DEF hVBlankCounter        EQU $ff9d
DEF hJoyDown              EQU $ffaa
DEF hBGMapMode            EQU $ffd6
DEF hSCX                  EQU $ffd1
DEF hSCY                  EQU $ffd2
DEF hCGB                  EQU $ffe8

; --- WRAM
DEF wShadowOAM            EQU $c300
DEF wLinkMode             EQU $d03c
DEF wMonType              EQU $ce53
DEF wCurSpecies           EQU $ce54
DEF wMenuBorderTopCoord   EQU $ceed
DEF wMenuBorderBottomCoord EQU $ceef
DEF w2DMenuCursorInitY    EQU $cf0c
DEF w2DMenuNumRows        EQU $cf0e
DEF w2DMenuNumCols        EQU $cf0f
DEF w2DMenuCursorOffsets  EQU $cf12
DEF wMenuCursorY          EQU $cf14
DEF wMenuCursorX          EQU $cf15
DEF wOverworldDelay       EQU $cf1c
DEF wVBlankOccurred       EQU $cf1e
DEF wStringBuffer1        EQU $cf87
DEF wStringBuffer2        EQU $cf92
DEF wCurPartySpecies      EQU $cffe
DEF wCurPartyMon          EQU $cfff
DEF wMonSubmenuCount      EQU $d0c5
DEF wMonSubmenuItems      EQU $d0c6
DEF wNamedObjectIndex     EQU $d143
DEF wStatusFlags2         EQU $d565
DEF wPartyMon1Moves       EQU $d9f2
DEF wPartyMon1PP          EQU $da07
DEF wPartyMonNicknames    EQU $db34
DEF PARTYMON_STRUCT_LENGTH EQU $30
DEF MON_NAME_LENGTH       EQU 6
DEF NUM_MOVES             EQU 4

; --- ホーム（バンク0）
DEF DelayFrame            EQU $032e
DEF PlaceString           EQU $0f46
DEF PrintText             EQU $0f30
DEF StaticMenuJoypad      EQU $1a13
DEF ExitMenu              EQU $1a51
DEF InitVerticalMenuCursor EQU $1a5a
DEF CloseWindow           EQU $1a61
DEF MenuBox               EQU $1afb
DEF MenuBoxCoord2Tile     EQU $1b3d
DEF LoadMenuHeader        EQU $1b59
DEF MenuTextbox           EQU $1b6e
DEF MenuTextboxBackup     EQU $1b86
DEF LoadStandardMenuHeader EQU $1b8d
DEF Call_ExitMenu         EQU $1b9c
DEF YesNoBox              EQU $1bee
DEF CopyBytes             EQU $30d6
DEF CopyName1             EQU $3137
DEF AddNTimes             EQU $315f
DEF FarQueueScript        EQU $3387
DEF ClearBGPalettes       EQU $33ab
DEF WaitBGMap             EQU $33ae
DEF SetDefaultBGPAndOBP   EQU $34a8
DEF GetMoveName           EQU $36a1
DEF GetBaseData           EQU $39dd
DEF GetCurNickname        EQU $3a23
DEF WaitPlaySFX           EQU $3d70

; --- バンクつき
DEF BANK_STARTMENU        EQU $04
DEF StartMenu_Items       EQU $696e   ; 9項目 × 6バイト
DEF StartMenu_MenuDataItemsPtr EQU $696c
DEF StartMenu_AppendMenuList EQU $6b28
DEF StartMenu_ExitAppend  EQU $6b0b   ; ld a, STARTMENUITEM_EXIT / call .AppendMenuList
DEF PCScript_Bank         EQU $36
DEF PCScript              EQU $4145   ; opentext / special PokemonCenterPC / closetext / end

DEF BANK_MONMENU          EQU $04
DEF PokemonActionSubmenu_ActionsPtr EQU $6dac  ; ld hl, .Actions の hl
DEF PokemonActionSubmenu_Actions EQU $6dbe     ; 20項目 × 3バイト
DEF ChooseMoveToDelete    EQU $7388
DEF NamingScreen          EQU $5a47

DEF BANK_MONSUBMENU       EQU $09
DEF MonMenuOptionStrings  EQU $4c30
DEF MonMenuOptions        EQU $4c56
DEF MonSubmenu_LoadHeader EQU $4ca2   ; ld hl, .MenuHeader / call LoadMenuHeader
DEF MonSubmenu_GetTopCoordCall EQU $4ca8
DEF MonSubmenu_PopulateCall EQU $4cab
DEF MonSubmenu_Header     EQU $4cbc
DEF MonSubmenu_GetTopCoord EQU $4cc4
DEF MonMenuLoop_InitCursorCall EQU $4ce1
DEF MonMenuLoop_Joypad    EQU $4ce4   ; ld hl, w2DMenuFlags1 / set 6, [hl] / call StaticMenuJoypad ...
DEF MonMenuLoop_Select    EQU $4d01
DEF PopulateMonMenu       EQU $4d0e
DEF GetMonMenuString      EQU $4d2d
DEF GetMonMenuString_Ptr  EQU $4d2e   ; ld hl, MonMenuOptions + 1
DEF GetMonMenuString_StrPtr EQU $4d49 ; ld hl, MonMenuOptionStrings
DEF GetMonSubmenuItems_Cancel EQU $4dac
DEF GetMonSubmenuItems_Term EQU $4db8
DEF IsFieldMove_Ptr       EQU $4dd1   ; ld hl, MonMenuOptions
DEF AddMonMenuItem        EQU $4e00

DEF BANK_PARTYMENU        EQU $14
DEF LoadPartyMenuGFX      EQU $404f
DEF WritePartyMenuTilemap EQU $405f
DEF InitPartyMenuGFX      EQU $4349
DEF InitPartyMenuWithCancel EQU $436e
DEF PlacePartyMenuText    EQU $4403

DEF BANK_PLAYERMOVE       EQU $04
DEF DoPlayerMovement_DoStep EQU $425f
DEF DoPlayerMovement_walk EQU $41ae
DEF DoPlayerMovement_surf EQU $41db

DEF BANK_OVERWORLD        EQU $25
DEF HandleMap_Tail        EQU $66d0   ; call NextOverworldFrame / call HandleMapBackground
DEF NextOverworldFrame    EQU $66fc
DEF HandleMapBackground   EQU $6726

DEF UpdateSprites_Bank    EQU $01
DEF _UpdateSprites        EQU $5896
DEF ScrollScreen_Bank     EQU $03
DEF ScrollScreen          EQU $57a9

DEF VBlank_ClearOccurred  EQU $01ca   ; xor a / ld [wVBlankOccurred], a（4バイト）

DEF BaseData              EQU $51aa9  ; ROM内の位置（バンク$14:$5aa9）

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

; 追加コードを置く所（日本版 金では空き）
DEF BANK_NEW              EQU $3f
DEF NEW_ADDR              EQU $6100   ; なまえ・わすれる
DEF NEW_ADDR_FPS          EQU $6800   ; 60fps
DEF HOME_FREE1            EQU $0068   ; $0068-$00ff
DEF HOME_FREE2            EQU $3f10   ; $3f10-$3fff
DEF BANK4_FREE            EQU $7f58   ; $7f54-$7fff
DEF BANK9_FREE            EQU $7f34   ; $7f31-$7fff
DEF BANK25_FREE           EQU $7f00   ; $7e02-$7fff

MACRO farcall_jp
	ld a, BANK(\1)
	ld hl, \1
	rst $08
ENDM
DEF HOME_FREE_FPS EQU $3fa0
DEF FPS60_WRAM EQU $de40
