; わざを おもいださせて くれる 人 … クリスタル（日本版）用の 値（本体は src/moverelearn.asm）
; 値は 英語版 pokecrystal と 命令の 並びで 照らし合わせて 調べた
INCLUDE "src/safari/crystal_includes.asm"   ; pokecrystal の 定数・マクロ（スクリプトの 命令は pokegold の もの）
DEF MR_NO_INCLUDES EQU 1

MACRO jsym ; 名前, バンク, アドレス
DEF J_\1 EQU \3
DEF JB_\1 EQU \2
ENDM
	jsym GetPartyParamLocation, 0, $38c6
	jsym GetFarByte,            0, $3019
	jsym LoadMenuHeader,        0, $1d00
	jsym DelayFrame,            0, $045a
	jsym GetJoypad,             0, $0984
	jsym PlaySFX,               0, $3bb0
	jsym ExitMenu,              0, $1bd2
	jsym MenuBox,               0, $1c86
	jsym UpdateSprites,         0, $1a9d
	jsym GetMoveName,           0, $34c8
	jsym PlaceString,           0, $1057
	jsym ApplyTilemap,          0, $31e8
	jsym CopyName1,             0, $30a2
	jsym FadeToMenu,            0, $2afb
	jsym ClearBGPalettes,       0, $31bf
	jsym ClearScreen,           0, $0fc5
	jsym GetSGBLayout,          0, $330c
	jsym CloseSubmenu,          0, $2b0e
DEF hJoyPressed         EQU $ffa7
DEF hBGMapMode          EQU $ffd4
DEF wScriptVar          EQU $c2dd
DEF wCurPartySpecies    EQU $d0c8
DEF wCurPartyLevel      EQU $d103
DEF wPutativeTMHMMove   EQU $d293
DEF wNamedObjectIndex   EQU $d296
DEF wBufferMon          EQU $d00e
DEF wTilemap            EQU $c4a0

DEF MR_ATTR             EQU $5d5c   ; MoveDeletersHouse_MapAttributes（バンク$25。スクリプト $1e:$57d8・イベント $1e:$57e5）
DEF MR_ATTR_BANK        EQU $25
DEF MR_SPECIAL_MOVEDELETION EQU $21 ; 元の スクリプトの「0f 21 00」（金と 同じ）
DEF MR_STD_BOOKSHELF    EQU $0001   ; 元の「0c 01 00」（金と 同じ）
DEF MR_EVOSATTACKS      EQU $6753   ; EvosAttacksPointers（LearnLevelMoves の ld hl）
DEF MR_EVOSATTACKS_BANK EQU $10
DEF MR_LEARNMOVE        EQU $6650   ; LearnMove
DEF MR_LEARNMOVE_BANK   EQU $01
DEF MR_SELECTMON        EQU $4000   ; SelectMonFromParty
DEF MR_SELECTMON_BANK   EQU $14
DEF MR_InitScrollingMenu EQU 0      ; 使わない
DEF MR_ScrollingMenu    EQU 0
DEF MR_LIST             EQU wBufferMon
DEF MR_BANK             EQU $76
DEF MR_ADDR             EQU $5000

INCLUDE "src/moverelearn.asm"
