; サファリゾーン（ポケットモンスターピカチュウ フルカラーパッチ と 同じ）を 金に足す（金 日本版）
;
; ・セキチクシティの 北の とじていた入口から 入れる。入口・ちゅうおう・ひがし・きた・にし・きゅうけいハウス 4つ・
;   ひみつの家 の 10マップ。マップの形・絵・色・看板・人・落ちている道具・出るポケモンは ピカチュウ版と同じ。
;   （ひでんマシン・きんのいれば は 入れない）
; ・遊び方も ピカチュウ版と同じ：500円で ボール30こ・502歩。お金が たりないときは へらした ボール。
;   戦いは ボール・エサ・いし・にげる（手もちの ポケモンは 出さない）。つかまえる計算・にげる計算・
;   エサ（たべてる）・いし（おこってる）は ピカチュウ版と同じ。歩数か ボールが なくなると アナウンスで 入口へ。
;   つりざおで つれる ポケモン（ボロ・いい・すごい）も ピカチュウ版と同じで、つった ポケモンとも サファリの 戦い。
;   スタートメニューの 左上に 歩数と ボール。ひがし・きた・にしの 段差（森の タイルの 組み合わせ）も 同じ。
; ・マップ・タイルセット・文章の データは tools/safari_gen.py で ピカチュウ版から作る（src/safari/safari_gen.asm）。
; ・マップの番号は 金で使われていない マップ（〜BETA）を 使う。タイルセットは 新しく 3つ（$1d〜$1f）足す。

INCLUDE "includes.asm"
INCLUDE "src/jp_all_silver.inc"

DEF SAFARI_SCRIPT_BANK EQU $44       ; マップ・スクリプト・文章（銀：$43 は 再戦・とけい・ボールの絵）
DEF SAFARI_DATA_BANK   EQU $45       ; タイルセット・ブロック
DEF SAFARI_PALMAP_ADDR EQU $7c60     ; バンク$02 の空き（picpal の あと）
DEF SAFARI_TEXT_ADDR   EQU $6000     ; バンク SAFARI_SCRIPT_BANK の 文章（$4000〜 は マップ・スクリプト）
DEF SAFARI_WILD_ADDR   EQU $7000     ; 〃 野生のポケモン
DEF SAFARI_CODE_ADDR   EQU $7100     ; 〃 処理
; サファリゲームの WRAM（金の 使われていない 名残。虫とり大会の パークボールと 同じ所）
; wSafariBallsRemaining（$d989）は jp_all.inc にある
DEF wSafariTimeRemaining EQU $d98a  ; 2バイト（上・下の順で使う）
; サファリの 戦い
DEF BATTLETYPE_SAFARI   EQU BATTLETYPE_FORCEITEM + 1   ; 新しい 戦いの種類（11）
DEF wSafariEscapeFactor EQU $cbc1  ; 金の 使われていない wSafariMonAngerCount（戦いの RAM。始めに 0 になる）
DEF wSafariBaitFactor   EQU $cbc2  ; 〃 wSafariMonEating（wSafariEscapeFactor + 1 で なければならない）
DEF wSafariShakes       EQU $cbc3  ; 〃 その次の 空き：ボールが ゆれる回数（0〜3）
DEF J_PrintNum          EQU $31f9  ; 日本版は お金の 印の 処理が ない
DEF J_wTimeOfDayPal EQU $d55b
DEF SAFARI_BATTLE_ADDR  EQU $7400  ; バンク SAFARI_SCRIPT_BANK の 戦いの処理
DEF J_BattleAnimations  EQU $4f9a  ; バンク$32
DEF SAFARI_ANIM_PTRS    EQU $7d50  ; バンク$32 の空き（えさ・いしの アニメ）
DEF SAFARI_ANIM_OBJ     EQU $7fc0  ; バンク$33 の空き（アニメの 部品の表を ふやす。銀は $7e40〜 に 投げるボールの絵の処理）
DEF SAFARI_WOBBLE       EQU $7fe0  ; バンク$03 の空き（ボールの ゆれ）
DEF SAFARI_DOBATTLE     EQU $7f96  ; バンク$0f の空き
DEF MUSIC_SAFARI_ZONE_PK EQU NUM_MUSIC_SONGS  ; 新しい 曲の番号（$5d。MUSIC_MAHOGANY_MART（100）より 小さく）
DEF SFX_SAFARI_ZONE_PA  EQU NUM_SFX          ; 新しい 効果音の番号（$bc）
DEF SAFARI_BALL_ITEM    EQU $b3    ; 使われていない ITEM_B3：投げる ボールの 絵を サファリボールにする 印（銀は ballgfx.asm）
DEF SAFARI_OBJ_BAIT     EQU $f0    ; 新しい アニメの部品
DEF SAFARI_OBJ_ROCK     EQU $f1
DEF SAFARI_ANIM_BAIT    EQU (SAFARI_ANIM_PTRS - J_BattleAnimations) / 2
DEF SAFARI_ANIM_ROCK    EQU SAFARI_ANIM_BAIT + 1

MACRO jfarcall ; 日本版の 名前（J_ / JB_）で farcall
	ld a, JB_\1
	ld hl, J_\1
	rst $08
ENDM

; special の番号（日本版も 英語版と 同じ並び）
DEF SpecialsPointers EQU 0
DEF PlaceMoneyTopRightSpecial EQU 80 * 3
DEF WarpToSpawnPointSpecial EQU 0 * 3

INCLUDE "src/safari/safari_gen.asm"

;---------------------------------------------------------------------
; マップの番号（金で使われていない マップを使う）
MACRO safari_map ; 名前, 元のマップ
	DEF GROUP_\1 EQU GROUP_\2
	DEF MAP_\1 EQU MAP_\2
ENDM
	safari_map SAFARI_GATE,        SAFARI_ZONE_FUCHSIA_GATE_BETA
	safari_map SAFARI_CENTER,      SAFARI_ZONE_BETA
	safari_map SAFARI_EAST,        CINNABAR_POKECENTER_2F_BETA
	safari_map SAFARI_NORTH,       CERULEAN_POKECENTER_2F_BETA
	safari_map SAFARI_WEST,        ROUTE_10_POKECENTER_2F_BETA
	safari_map SAFARI_CENTER_REST, VERMILION_POKECENTER_2F_BETA
	safari_map SAFARI_EAST_REST,   PEWTER_POKECENTER_2F_BETA
	safari_map SAFARI_NORTH_REST,  FUCHSIA_POKECENTER_2F_BETA
	safari_map SAFARI_WEST_REST,   LAVENDER_POKECENTER_2F_BETA
	safari_map SAFARI_SECRET,      CELADON_POKECENTER_2F_BETA

; イベントフラグ（金で使われていない $7f0〜）
	const_def $7f0
	const EVENT_SAFARI_EAST_FULL_RESTORE
	const EVENT_SAFARI_EAST_MAX_POTION
	const EVENT_SAFARI_EAST_CARBOS
	const EVENT_SAFARI_EAST_TM37
	const EVENT_SAFARI_NORTH_PROTEIN
	const EVENT_SAFARI_NORTH_TM40
	const EVENT_SAFARI_WEST_MAX_POTION
	const EVENT_SAFARI_WEST_TM32
	const EVENT_SAFARI_WEST_MAX_REVIVE
	const EVENT_SAFARI_CENTER_NUGGET
	const EVENT_SAFARI_WEST_HIDDEN_REVIVE
	const EVENT_IN_SAFARI_ZONE
	const EVENT_SAFARI_GAME_OVER

;---------------------------------------------------------------------
; マップの見出し（バンク$25 の マップの表。9バイト）
MACRO safari_header ; 場所, 名前, タイルセット, 環境, 音楽
SECTION "safari header \2", ROMX[\1], BANK[$25]
	db BANK(\2_MapAttributes), \3, \4
	dw \2_MapAttributes
	db LANDMARK_FUCHSIA_CITY, \5
	dn TRUE, \6                   ; 電話は かからない。外の 4つは 時間で 色が かわる（PALETTE_AUTO）
	db FISHGROUP_SHORE
ENDM
	safari_header $44a5, SafariGate,       TILESET_SAFARIGATE, INDOOR, MUSIC_CELADON_CITY, PALETTE_DAY
	safari_header $44ae, SafariCenter,     TILESET_SAFARIOUT,  CAVE,   MUSIC_SAFARI_ZONE_PK, PALETTE_AUTO
	safari_header $4574, SafariEast,       TILESET_SAFARIOUT,  CAVE,   MUSIC_SAFARI_ZONE_PK, PALETTE_AUTO
	safari_header $45d7, SafariNorth,      TILESET_SAFARIOUT,  CAVE,   MUSIC_SAFARI_ZONE_PK, PALETTE_AUTO
	safari_header $45fb, SafariWest,       TILESET_SAFARIOUT,  CAVE,   MUSIC_SAFARI_ZONE_PK, PALETTE_AUTO
	safari_header $484d, SafariCenterRest, TILESET_SAFARIGATE, INDOOR, MUSIC_SAFARI_ZONE_PK, PALETTE_DAY
	safari_header $4901, SafariEastRest,   TILESET_SAFARIGATE, INDOOR, MUSIC_SAFARI_ZONE_PK, PALETTE_DAY
	safari_header $4a21, SafariNorthRest,  TILESET_SAFARIGATE, INDOOR, MUSIC_SAFARI_ZONE_PK, PALETTE_DAY
	safari_header $4a69, SafariWestRest,   TILESET_SAFARIGATE, INDOOR, MUSIC_SAFARI_ZONE_PK, PALETTE_DAY
	safari_header $4b9b, SafariSecret,     TILESET_SAFARILAB,  INDOOR, MUSIC_SAFARI_ZONE_PK, PALETTE_DAY

; タイルセットの表を 新しい表（3つ足したもの）にする（LoadMapTileset の ld hl, Tilesets / ld a, BANK(Tilesets)）
SECTION "safari tileset ptr", ROM0[$2db9]
	dw SafariTilesetTable
SECTION "safari tileset bank", ROM0[$2dcb]
	db BANK(SafariTilesetTable)

; セキチクシティの 北の入口（warp 7）→ サファリの入口の 下（warp 1）
SECTION "safari fuchsia warp", ROMX[$71fa + 2], BANK[$36]
	db 1

; セキチクシティの マップの 北の 入口の かべ（ブロック$7d、x9・y1）を ドアの ブロック$80 にする
; （銀の FuchsiaCity_Blocks = $2a:$65f1。20×18 ブロック。safari_gen.py で カントーの ブロックに $80 を 足してある）
SECTION "safari fuchsia door", ROMX[J_FuchsiaCity_Blocks + 1 * 20 + 9], BANK[JB_FuchsiaCity_Blocks]
	db $80

; 水の アニメ（水のタイル $14 だけ。花のタイル $03 は 動かさない）
SECTION "safari water anim", ROMX[$7f40], BANK[$3f]
SafariWaterAnim:
	dw $9140, J_AnimateWaterTile
	dw 0, J_WaitTileAnimation
	dw 0, J_WaitTileAnimation
	dw 0, J_WaitTileAnimation
	dw 0, J_WaitTileAnimation
	dw 0, J_WaitTileAnimation
	dw 0, J_WaitTileAnimation
	dw 0, J_WaitTileAnimation
	dw 0, J_WaitTileAnimation
	dw 0, J_WaitTileAnimation
	dw 0, J_StandingTileFrame8
	dw 0, J_DoneTileAnimation

;---------------------------------------------------------------------
SECTION "safari maps", ROMX[$4000], BANK[SAFARI_SCRIPT_BANK]

MACRO safari_attributes ; 名前, 大文字の名前
\1_MapAttributes::
	db \2_BORDER, \2_HEIGHT, \2_WIDTH
	db BANK(\1_Blocks)
	dw \1_Blocks
	db BANK(\1_MapScripts)
	dw \1_MapScripts
	dw \1_MapEvents
	db 0 ; つながり なし
ENDM

; ---- 入口
	safari_attributes SafariGate, SAFARIGATE
SafariGate_MapScripts:
	def_scene_scripts
	def_callbacks
	callback MAPCALLBACK_NEWMAP, SafariGateCallback
SafariGate_MapEvents:
	db 0, 0
	def_warp_events
	warp_event  3,  5, FUCHSIA_CITY, 7
	warp_event  4,  5, FUCHSIA_CITY, 7
	warp_event  3,  0, SAFARI_CENTER, 1
	warp_event  4,  0, SAFARI_CENTER, 2
	def_coord_events
	coord_event  3,  2, -1, SafariGateEnterScript
	coord_event  4,  2, -1, SafariGateEnterScript
	def_bg_events
	def_object_events
	object_event  6,  2, SPRITE_OFFICER, SPRITEMOVEDATA_STANDING_LEFT, 0, 0, -1, -1, 0, OBJECTTYPE_SCRIPT, 0, SafariGateWorker1Script, -1
	object_event  1,  4, SPRITE_OFFICER, SPRITEMOVEDATA_STANDING_RIGHT, 0, 0, -1, -1, 0, OBJECTTYPE_SCRIPT, 0, SafariGateWorker2Script, -1

; ---- ちゅうおう
	safari_attributes SafariCenter, SAFARICENTER
SafariCenter_MapScripts:
	def_scene_scripts
	def_callbacks
SafariCenter_MapEvents:
	db 0, 0
	def_warp_events
	warp_event 14, 25, SAFARI_GATE, 3
	warp_event 15, 25, SAFARI_GATE, 4
	warp_event  0, 10, SAFARI_WEST, 5
	warp_event  0, 11, SAFARI_WEST, 6
	warp_event 14,  0, SAFARI_NORTH, 5
	warp_event 15,  0, SAFARI_NORTH, 6
	warp_event 29, 10, SAFARI_EAST, 3
	warp_event 29, 11, SAFARI_EAST, 4
	warp_event 17, 19, SAFARI_CENTER_REST, 1
	def_coord_events
	def_bg_events
	bg_event 18, 20, BGEVENT_READ, SafariCenterRestSign
	bg_event 14, 22, BGEVENT_READ, SafariCenterTipsSign
	def_object_events
	object_event 14, 10, SPRITE_POKE_BALL, SPRITEMOVEDATA_STILL, 0, 0, -1, -1, 0, OBJECTTYPE_ITEMBALL, 0, SafariCenterNugget, EVENT_SAFARI_CENTER_NUGGET
SafariCenterRestSign:  jumptext SafariCenter_RestHouseSignText
SafariCenterTipsSign:  jumptext SafariCenter_TipsSignText
SafariCenterNugget:    itemball NUGGET

; ---- ひがし
	safari_attributes SafariEast, SAFARIEAST
SafariEast_MapScripts:
	def_scene_scripts
	def_callbacks
SafariEast_MapEvents:
	db 0, 0
	def_warp_events
	warp_event  0,  4, SAFARI_NORTH, 7
	warp_event  0,  5, SAFARI_NORTH, 8
	warp_event  0, 22, SAFARI_CENTER, 7
	warp_event  0, 23, SAFARI_CENTER, 7
	warp_event 25,  9, SAFARI_EAST_REST, 1
	def_coord_events
	def_bg_events
	bg_event 26, 10, BGEVENT_READ, SafariEastSign5
	bg_event  6,  4, BGEVENT_READ, SafariEastSign6
	bg_event  5, 23, BGEVENT_READ, SafariEastSign7
	def_object_events
	object_event 21, 10, SPRITE_POKE_BALL, SPRITEMOVEDATA_STILL, 0, 0, -1, -1, 0, OBJECTTYPE_ITEMBALL, 0, SafariEastFullRestore, EVENT_SAFARI_EAST_FULL_RESTORE
	object_event  3,  7, SPRITE_POKE_BALL, SPRITEMOVEDATA_STILL, 0, 0, -1, -1, 0, OBJECTTYPE_ITEMBALL, 0, SafariEastMaxPotion, EVENT_SAFARI_EAST_MAX_POTION
	object_event 20, 13, SPRITE_POKE_BALL, SPRITEMOVEDATA_STILL, 0, 0, -1, -1, 0, OBJECTTYPE_ITEMBALL, 0, SafariEastCarbos, EVENT_SAFARI_EAST_CARBOS
	object_event 15, 12, SPRITE_POKE_BALL, SPRITEMOVEDATA_STILL, 0, 0, -1, -1, 0, OBJECTTYPE_ITEMBALL, 0, SafariEastTM37, EVENT_SAFARI_EAST_TM37
SafariEastSign5:       jumptext SafariEast_Sign5Text
SafariEastSign6:       jumptext SafariEast_Sign6Text
SafariEastSign7:       jumptext SafariEast_Sign7Text
SafariEastFullRestore: itemball FULL_RESTORE
SafariEastMaxPotion:   itemball MAX_POTION
SafariEastCarbos:      itemball CARBOS
SafariEastTM37:        itemball TM_SANDSTORM       ; ピカチュウ版は わざマシン37（タマゴばくだん）。金の わざマシン37

; ---- きた
	safari_attributes SafariNorth, SAFARINORTH
SafariNorth_MapScripts:
	def_scene_scripts
	def_callbacks
SafariNorth_MapEvents:
	db 0, 0
	def_warp_events
	warp_event  2, 35, SAFARI_WEST, 1
	warp_event  3, 35, SAFARI_WEST, 2
	warp_event  8, 35, SAFARI_WEST, 3
	warp_event  9, 35, SAFARI_WEST, 4
	warp_event 20, 35, SAFARI_CENTER, 5
	warp_event 21, 35, SAFARI_CENTER, 6
	warp_event 39, 30, SAFARI_EAST, 1
	warp_event 39, 31, SAFARI_EAST, 2
	warp_event 35,  3, SAFARI_NORTH_REST, 1
	def_coord_events
	def_bg_events
	bg_event 36,  4, BGEVENT_READ, SafariNorthSign3
	bg_event  4, 25, BGEVENT_READ, SafariNorthSign4
	bg_event 13, 31, BGEVENT_READ, SafariNorthSign5
	bg_event 19, 33, BGEVENT_READ, SafariNorthSign6
	bg_event 26, 28, BGEVENT_READ, SafariNorthSign7
	def_object_events
	object_event 25,  1, SPRITE_POKE_BALL, SPRITEMOVEDATA_STILL, 0, 0, -1, -1, 0, OBJECTTYPE_ITEMBALL, 0, SafariNorthProtein, EVENT_SAFARI_NORTH_PROTEIN
	object_event 19,  7, SPRITE_POKE_BALL, SPRITEMOVEDATA_STILL, 0, 0, -1, -1, 0, OBJECTTYPE_ITEMBALL, 0, SafariNorthTM40, EVENT_SAFARI_NORTH_TM40
SafariNorthSign3:      jumptext SafariNorth_Sign3Text
SafariNorthSign4:      jumptext SafariNorth_Sign4Text
SafariNorthSign5:      jumptext SafariNorth_Sign5Text
SafariNorthSign6:      jumptext SafariNorth_Sign6Text
SafariNorthSign7:      jumptext SafariNorth_Sign7Text
SafariNorthProtein:    itemball PROTEIN
SafariNorthTM40:       itemball TM_DEFENSE_CURL    ; ピカチュウ版は わざマシン40（ロケットずつき）。金の わざマシン40

; ---- にし
	safari_attributes SafariWest, SAFARIWEST
SafariWest_MapScripts:
	def_scene_scripts
	def_callbacks
SafariWest_MapEvents:
	db 0, 0
	def_warp_events
	warp_event 20,  0, SAFARI_NORTH, 1
	warp_event 21,  0, SAFARI_NORTH, 2
	warp_event 26,  0, SAFARI_NORTH, 3
	warp_event 27,  0, SAFARI_NORTH, 4
	warp_event 29, 22, SAFARI_CENTER, 3
	warp_event 29, 23, SAFARI_CENTER, 4
	warp_event  3,  3, SAFARI_SECRET, 1
	warp_event 11, 11, SAFARI_WEST_REST, 1
	def_coord_events
	def_bg_events
	bg_event 12, 12, BGEVENT_READ, SafariWestSign5
	bg_event 17,  3, BGEVENT_READ, SafariWestSign6
	bg_event 26,  4, BGEVENT_READ, SafariWestSign7
	bg_event 24, 22, BGEVENT_READ, SafariWestSign8
	bg_event  6,  5, BGEVENT_ITEM, SafariWestHiddenRevive
	def_object_events
	object_event  8, 20, SPRITE_POKE_BALL, SPRITEMOVEDATA_STILL, 0, 0, -1, -1, 0, OBJECTTYPE_ITEMBALL, 0, SafariWestMaxPotion, EVENT_SAFARI_WEST_MAX_POTION
	object_event  9,  7, SPRITE_POKE_BALL, SPRITEMOVEDATA_STILL, 0, 0, -1, -1, 0, OBJECTTYPE_ITEMBALL, 0, SafariWestTM32, EVENT_SAFARI_WEST_TM32
	object_event 18, 18, SPRITE_POKE_BALL, SPRITEMOVEDATA_STILL, 0, 0, -1, -1, 0, OBJECTTYPE_ITEMBALL, 0, SafariWestMaxRevive, EVENT_SAFARI_WEST_MAX_REVIVE
SafariWestSign5:       jumptext SafariWest_Sign5Text
SafariWestSign6:       jumptext SafariWest_Sign6Text
SafariWestSign7:       jumptext SafariWest_Sign7Text
SafariWestSign8:       jumptext SafariWest_Sign8Text
SafariWestHiddenRevive: hiddenitem REVIVE, EVENT_SAFARI_WEST_HIDDEN_REVIVE
SafariWestMaxPotion:   itemball MAX_POTION
SafariWestTM32:        itemball TM_DOUBLE_TEAM
SafariWestMaxRevive:   itemball MAX_REVIVE

; ---- きゅうけいハウス・トレジャーハウス
MACRO safari_house ; 名前, 大文字, 出口のマップ, 出口の番号
	safari_attributes \1, \2
\1_MapScripts:
	def_scene_scripts
	def_callbacks
\1_MapEvents:
	db 0, 0
	def_warp_events
	warp_event  2,  7, \3, \4
	warp_event  3,  7, \3, \4
	def_coord_events
	def_bg_events
	def_object_events
ENDM
	safari_house SafariCenterRest, SAFARICENTERREST, SAFARI_CENTER, 9
	object_event  3,  2, SPRITE_LASS, SPRITEMOVEDATA_STANDING_DOWN, 0, 0, -1, -1, 0, OBJECTTYPE_SCRIPT, 0, SafariCenterRestGirl, -1
	object_event  1,  4, SPRITE_SCIENTIST, SPRITEMOVEDATA_WALK_UP_DOWN, 0, 1, -1, -1, 0, OBJECTTYPE_SCRIPT, 0, SafariCenterRestScientist, -1
SafariCenterRestGirl:      jumptextfaceplayer SafariCenterRest_GirlText
SafariCenterRestScientist: jumptextfaceplayer SafariCenterRest_ScientistText

	safari_house SafariWestRest, SAFARIWESTREST, SAFARI_WEST, 8
	object_event  4,  4, SPRITE_SCIENTIST, SPRITEMOVEDATA_WANDER, 1, 1, -1, -1, 0, OBJECTTYPE_SCRIPT, 0, SafariWestRestScientist, -1
	object_event  0,  2, SPRITE_COOLTRAINER_M, SPRITEMOVEDATA_STANDING_RIGHT, 0, 0, -1, -1, 0, OBJECTTYPE_SCRIPT, 0, SafariWestRestCooltrainer, -1
	object_event  6,  2, SPRITE_TEACHER, SPRITEMOVEDATA_STANDING_DOWN, 0, 0, -1, -1, 0, OBJECTTYPE_SCRIPT, 0, SafariWestRestSilph, -1
SafariWestRestScientist:   jumptextfaceplayer SafariWestRest_ScientistText
SafariWestRestCooltrainer: jumptextfaceplayer SafariWestRest_CooltrainerText
SafariWestRestSilph:       jumptextfaceplayer SafariWestRest_SilphText

	safari_house SafariEastRest, SAFARIEASTREST, SAFARI_EAST, 5
	object_event  1,  3, SPRITE_SCIENTIST, SPRITEMOVEDATA_WALK_UP_DOWN, 0, 1, -1, -1, 0, OBJECTTYPE_SCRIPT, 0, SafariEastRestScientist, -1
	object_event  4,  2, SPRITE_ROCKER, SPRITEMOVEDATA_SPINRANDOM_SLOW, 0, 0, -1, -1, 0, OBJECTTYPE_SCRIPT, 0, SafariEastRestRocker, -1
	object_event  5,  2, SPRITE_CLERK, SPRITEMOVEDATA_SPINRANDOM_SLOW, 0, 0, -1, -1, 0, OBJECTTYPE_SCRIPT, 0, SafariEastRestSilph, -1
SafariEastRestScientist:   jumptextfaceplayer SafariEastRest_ScientistText
SafariEastRestRocker:      jumptextfaceplayer SafariEastRest_RockerText
SafariEastRestSilph:       jumptextfaceplayer SafariEastRest_SilphText

	safari_house SafariNorthRest, SAFARINORTHREST, SAFARI_NORTH, 9
	object_event  6,  3, SPRITE_SCIENTIST, SPRITEMOVEDATA_WALK_LEFT_RIGHT, 1, 0, -1, -1, 0, OBJECTTYPE_SCRIPT, 0, SafariNorthRestScientist, -1
	object_event  3,  4, SPRITE_OFFICER, SPRITEMOVEDATA_SPINRANDOM_SLOW, 0, 0, -1, -1, 0, OBJECTTYPE_SCRIPT, 0, SafariNorthRestWorker, -1
	object_event  1,  5, SPRITE_GENTLEMAN, SPRITEMOVEDATA_WALK_UP_DOWN, 0, 1, -1, -1, 0, OBJECTTYPE_SCRIPT, 0, SafariNorthRestGentleman, -1
SafariNorthRestScientist:  jumptextfaceplayer SafariNorthRest_ScientistText
SafariNorthRestWorker:     jumptextfaceplayer SafariNorthRest_WorkerText
SafariNorthRestGentleman:  jumptextfaceplayer SafariNorthRest_GentlemanText

	safari_house SafariSecret, SAFARISECRET, SAFARI_WEST, 7
	object_event  3,  3, SPRITE_FISHING_GURU, SPRITEMOVEDATA_STANDING_DOWN, 0, 0, -1, -1, 0, OBJECTTYPE_SCRIPT, 0, SafariSecretGuru, -1
SafariSecretGuru:          jumptextfaceplayer SafariSecret_GuruText


;---------------------------------------------------------------------
; 入口（ピカチュウ版の SafariZoneGate と同じ流れ）
; サファリゲームの最中かどうかは ENGINE_SAFARI_ZONE（金の名残の フラグ。そらをとぶ・テレポート・あなをほる・
; あなぬけのヒモ・めのまえが まっくらに なったとき に 金が 自分で 消す）。
SafariGateEnterScript:
	checkflag ENGINE_SAFARI_ZONE
	iftrue .end
	opentext
	writetext SafariText_Welcome
	waitbutton
	closetext
	turnobject PLAYER, RIGHT
	readvar VAR_XCOORD
	ifnotequal 3, .ask
	applymovement PLAYER, SafariMove_Right1
.ask
	opentext
	writetext SafariText_Join
	special PlaceMoneyTopRight
	yesorno
	iffalse .no
	checkmoney YOUR_MONEY, 1
	ifequal HAVE_LESS, .nomoney
	checkmoney YOUR_MONEY, 500
	ifequal HAVE_LESS, .notenough
	takemoney YOUR_MONEY, 500
	playsound SFX_TRANSACTION
	waitsfx
	special PlaceMoneyTopRight
	writetext SafariText_Pay
	waitbutton
	loadmem wSafariBallsRemaining, 30
	sjump .enter

.notenough
; お金が 500円 ない：あるだけ もらって ボールを へらす（お金 ÷ 23 + 1こ）
	writetext SafariText_NotEnough
	waitbutton
	callasm SafariLowCostAdmission
	writetext SafariText_LowCost1
	special PlaceMoneyTopRight
	writetext SafariText_LowCost2
	waitbutton
	sjump .enter

.nomoney
; お金が 0円：ことわられる（4回目だけ ボール 1こで 入れてくれる）
	readmem wSafariTimeRemaining
	addval 1
	writemem wSafariTimeRemaining
	ifequal 1, .nomoney1
	ifequal 2, .nomoney2
	ifequal 3, .nomoney3
	writetext SafariText_LowCost8
	ifnotequal 4, .walkdown
	writetext SafariText_OneBall
	waitbutton
	loadmem wSafariBallsRemaining, 1
	sjump .enter
.nomoney1
	writetext SafariText_LowCost5
	sjump .walkdown
.nomoney2
	writetext SafariText_LowCost6
	sjump .walkdown
.nomoney3
	writetext SafariText_LowCost7
	sjump .walkdown

.no
	writetext SafariText_ComeAgain
.walkdown
	waitbutton
	closetext
	applymovement PLAYER, SafariMove_Down1
.end
	end

.enter
	closetext
	loadmem wSafariTimeRemaining, HIGH(502)
	loadmem wSafariTimeRemaining + 1, LOW(502)
	setflag ENGINE_SAFARI_ZONE
	clearevent EVENT_SAFARI_GAME_OVER
	applymovement PLAYER, SafariMove_Up2
	sjump SafariGateToCenter

SafariGateToCenter:
	readvar VAR_XCOORD
	ifequal 4, .right
	warp SAFARI_CENTER, 14, 25
	end
.right
	warp SAFARI_CENTER, 15, 25
	end

; 入口に もどってきたとき（ちゅうおう から・アナウンスで おわったとき）
SafariGateCallback:
	checkflag ENGINE_SAFARI_ZONE
	iffalse .done
	callasm SafariQueueLeaveScript
.done
	endcallback

SafariGateLeaveScript:
	readvar VAR_YCOORD
	ifnotequal 0, .end
	checkevent EVENT_SAFARI_GAME_OVER
	iftrue .over
	opentext
	writetext SafariText_LeavingEarly
	yesorno
	iffalse .stay
	writetext SafariText_ReturnBalls
	waitbutton
	closetext
	clearflag ENGINE_SAFARI_ZONE
	sjump .out
.stay
	writetext SafariText_GoodLuck
	waitbutton
	closetext
	turnobject PLAYER, UP
	sjump SafariGateToCenter
.over
	clearevent EVENT_SAFARI_GAME_OVER
	clearflag ENGINE_SAFARI_ZONE
	opentext
	writetext SafariText_GoodHaul
	waitbutton
	closetext
.out
	loadmem wSafariBallsRemaining, 0
	loadmem wSafariTimeRemaining, 0
	loadmem wSafariTimeRemaining + 1, 0
	turnobject PLAYER, DOWN
	applymovement PLAYER, SafariMove_Down3
.end
	end

; 時間・ボールが なくなったとき（アナウンス → 入口へ）
SafariGameOverScript:
	playmusic MUSIC_NONE             ; ピカチュウ版と同じく 曲を とめて アナウンスの 音
	playsound SFX_SAFARI_ZONE_PA
	opentext
	readmem wSafariBallsRemaining
	iffalse .noballs
	writetext SafariText_TimesUp
.noballs
	writetext SafariText_GameOver
	waitbutton
	closetext
	setevent EVENT_SAFARI_GAME_OVER
	warp SAFARI_GATE, 3, 0
	end

; 野生の ポケモン（サファリの 戦い。ボールが なくなったら ゲームおわり）
SafariBattleScript:
	loadmem wBattleType, BATTLETYPE_SAFARI
	randomwildmon
	startbattle
	reloadmapafterbattle
	readmem wSafariBallsRemaining
	iffalse SafariGameOverScript
	end

SafariMove_Right1:
	step RIGHT
	step_end
SafariMove_Down1:
	step DOWN
	step_end
SafariMove_Down3:
	step DOWN
	step DOWN
	step DOWN
	step_end
SafariMove_Up2:
	step UP
	step UP
	step_end

; 入口の人
SafariGateWorker1Script:
	jumptextfaceplayer SafariText_Welcome
SafariGateWorker2Script:
	faceplayer
	opentext
	writetext SafariText_FirstTime
	yesorno
	iffalse .regular
	writetext SafariText_Explain
	waitbutton
	closetext
	end
.regular
	writetext SafariText_Regular
	waitbutton
	closetext
	end

;---------------------------------------------------------------------
SECTION "safari code", ROMX[SAFARI_CODE_ADDR], BANK[SAFARI_SCRIPT_BANK]

; 入口に もどったときの 話を 予約する（マップを読んだあとに 動く）
SafariQueueLeaveScript:
	ld hl, wMapReentryScriptQueueFlag
	ld a, [hl]
	and a
	ret nz
	ld [hl], 1
	inc hl
	ld [hl], BANK(SafariGateLeaveScript)
	inc hl
	ld [hl], LOW(SafariGateLeaveScript)
	inc hl
	ld [hl], HIGH(SafariGateLeaveScript)
	ret

; お金が 500円 ないとき：ボール = お金 ÷ 23 + 1（29まで）、お金は 0 に
SafariLowCostAdmission:
	ld a, [wMoney + 1]
	ld h, a
	ld a, [wMoney + 2]
	ld l, a                      ; 500円より少ないので 下の 2バイトで足りる
	ld b, 0
.div
	ld a, l
	sub 23
	ld e, a
	ld a, h
	sbc 0
	jr c, .done
	ld h, a
	ld l, e
	inc b
	jr .div
.done
	ld a, b
	inc a
	cp 29
	jr c, .ok
	ld a, 29
.ok
	ld [wSafariBallsRemaining], a
	xor a
	ld [wMoney], a
	ld [wMoney + 1], a
	ld [wMoney + 2], a
	ret

; サファリの中か（入口は ちがう）：キャリー = 中
SafariInZone:
	ld a, [wMapTileset]
	cp TILESET_SAFARIOUT
	jr z, .yes
	cp TILESET_SAFARILAB
	jr z, .yes
	cp TILESET_SAFARIGATE
	jr nz, .no
	ld a, [wMapGroup]
	cp GROUP_SAFARI_GATE
	jr nz, .yes
	ld a, [wMapNumber]
	cp MAP_SAFARI_GATE
	jr nz, .yes
.no
	and a
	ret
.yes
	scf
	ret

; 1歩ごと（CountStep の頭から）：キャリー = アナウンスの スクリプトを 始めた
SafariStep:
	ld a, [wStatusFlags2]
	bit STATUSFLAGS2_SAFARI_GAME_F, a
	ret z                        ; キャリーなし
	call SafariInZone
	ret nc
	ld hl, wSafariTimeRemaining
	ld a, [hli]
	or [hl]
	jr z, SafariGameOver
	ld a, [hl]
	sub 1
	ld [hld], a
	ld a, [hl]
	sbc 0
	ld [hl], a
	and a                        ; キャリーなし
	ret

SafariGameOver:
	ld a, BANK(SafariGameOverScript)
	ld hl, SafariGameOverScript
	call J_CallScript
	scf
	ret

; 野生の ポケモン（ピカチュウ版の TryDoWildEncounter と同じ）：キャリー = 出る
SafariTryEncounter:
	ld a, [wStatusFlags2]
	bit STATUSFLAGS2_SAFARI_GAME_F, a
	jr z, .no                    ; ゲームの外（ふつうは 入れない）
	ld hl, wTilemap + 9 * SCREEN_WIDTH + 8
	ld a, [hl]
	cp $20                       ; くさむらの タイル
	jr nz, .no
	call .table                  ; hl = このマップの表
	jr nc, .no
	call J_Random
	ld b, [hl]                   ; 出る確率
	inc hl
	ldh a, [hRandomAdd]
	cp b
	jr nc, .no
	ldh a, [hRandomSub]
	ld b, a
	ld de, SafariSlotChances
	ld c, 0
.slot
	ld a, [de]
	inc de
	cp b
	jr nc, .got
	inc c
	jr .slot
.got
	ld b, 0
	add hl, bc
	add hl, bc
	ld a, [hli]
	ld [wCurPartyLevel], a
	ld b, a
	ld a, [hl]
	ld [wTempWildMonSpecies], a
	ld a, [wRepelEffect]
	and a
	jr z, .yes
	ld a, [wPartyMon1Level]
	ld c, a
	ld a, b
	cp c
	jr c, .no                    ; むしよけ：先頭の ポケモンより レベルが ひくい
.yes
	scf
	ret
.no
	and a
	ret

.table
	ld a, [wMapGroup]
	ld b, a
	ld a, [wMapNumber]
	ld c, a
	ld hl, .maps
.find
	ld a, [hli]
	and a
	ret z                        ; キャリーなし
	cp b
	jr nz, .next
	ld a, [hl]
	cp c
	jr nz, .next
	inc hl
	ld a, [hli]
	ld h, [hl]
	ld l, a
	scf
	ret
.next
	inc hl
	inc hl
	inc hl
	jr .find
.maps
	db GROUP_SAFARI_CENTER, MAP_SAFARI_CENTER
	dw SafariCenter_WildMons
	db GROUP_SAFARI_EAST, MAP_SAFARI_EAST
	dw SafariEast_WildMons
	db GROUP_SAFARI_NORTH, MAP_SAFARI_NORTH
	dw SafariNorth_WildMons
	db GROUP_SAFARI_WEST, MAP_SAFARI_WEST
	dw SafariWest_WildMons
	db 0

; ピカチュウ版の WildMonEncounterSlotChances（10こ、合わせて 256）
SafariSlotChances:
	db 50, 101, 140, 165, 190, 215, 228, 241, 252, 255

;---------------------------------------------------------------------
; ホーム：1歩ごと（CountStep の頭の ld a, [wLinkMode] の代わり）
SECTION "safari step hooks", ROMX[$7f4c], BANK[$25]   ; バンク$25 の空き（ホームは 60fps版で いっぱい）
SafariCountStepHook:
	ld a, BANK(SafariStep)
	ld hl, SafariStep
	rst $08
	jr c, .script
	ld a, [wLinkMode]
	ret
.script
	pop hl                       ; CountStep から もどる（スクリプトを 始めた）
	ld a, -1
	scf
	ret

; 野生の ポケモン（RandomEncounter の頭の call CheckWildEncounterCooldown の代わり）
SafariEncounterHook:
	ld a, [wMapTileset]
	cp TILESET_SAFARIOUT
	jp nz, J_CheckWildEncounterCooldown
	ld a, BANK(SafariTryEncounter)
	ld hl, SafariTryEncounter
	rst $08
	pop hl                       ; RandomEncounter から もどる
	jr c, .yes
	ld a, 1
	and a
	ret
.yes
	ld a, BANK(SafariBattleScript)
	ld hl, SafariBattleScript
	call J_CallScript
	scf
	ret

SECTION "safari countstep hook", ROMX[J_CountStep], BANK[JB_CountStep]
	call SafariCountStepHook
SECTION "safari encounter hook", ROMX[J_RandomEncounter], BANK[JB_RandomEncounter]
	call SafariEncounterHook

;---------------------------------------------------------------------
; 背景の色：サファリの マップは ピカチュウ版と同じ 7つの色にする（8つめの 文字の色は 金のまま）。
; 外の 4つは 金と 同じく 時間で かわる：昼 ＝ ピカチュウ版の 色、朝 ＝ 明るい色だけ 金の 朝の色（28,31,16）、
; 夜 ＝ 金の 昼→夜の 色の かわり方（bg_tiles.pal から 求めた 式）で 作った 色
; LoadMapPals の おわり（OBJ の色を写したあと）の ld a, [wEnvironment] / cp TOWN（5バイト）
SECTION "safari pals hook", ROMX[$7626], BANK[2]
	call SafariMapPals
	nop
	nop

SECTION "safari pals", ROMX[SAFARI_PALMAP_ADDR + 3 * 64], BANK[2]
SafariMapPals:
	ld a, [$d074]                ; wMapTileset
	cp TILESET_SAFARIOUT
	jr c, .no
	cp TILESET_SAFARILAB + 1
	jr nc, .no
	ld hl, .indoor
	cp TILESET_SAFARIOUT
	jr nz, .copy
	ld hl, .outdoor
	ld a, [J_wTimeOfDayPal]
	and %11
	cp 1                         ; DAY_F
	jr z, .copy
	ld hl, .morn
	and a                        ; MORN_F
	jr z, .copy
	ld hl, .nite                 ; NITE_F・DARKNESS_F
.copy
	ld de, $c200                 ; wBGPals1
	ld bc, 7 * 8
	call $30d6                   ; CopyBytes
	pop hl                       ; LoadMapPals から もどる（屋根の色は 使わない）
	ret
.no
	ld a, [$d075]                ; wEnvironment（元の処理）
	cp TOWN
	ret
.outdoor
	dw $6ffb, $56b5, $35ad, $1ce7
	dw $2bf6, $1e58, $0df4, $1ce7
	dw $2bf6, $072c, $01c5, $1ce7
	dw $7ef7, $7e72, $7d8d, $1ce7
	dw $6ffb, $1fff, $061f, $1ce7
	dw $6ffb, $1e58, $0df4, $1ce7
	dw $2bf6, $3bf4, $16eb, $1ce7
.morn
	dw $43fc, $56b5, $35ad, $1ce7
	dw $2bf6, $1e58, $0df4, $1ce7
	dw $2bf6, $072c, $01c5, $1ce7
	dw $7ef7, $7e72, $7d8d, $1ce7
	dw $43fc, $1fff, $061f, $1ce7
	dw $43fc, $1e58, $0df4, $1ce7
	dw $2bf6, $3bf4, $16eb, $1ce7
.nite
	dw $61d0, $492b, $30c7, $0000
	dw $59ed, $34eb, $2ce9, $0000
	dw $59ed, $49a8, $3104, $0000
	dw $514d, $490b, $3ca8, $0000
	dw $61d0, $51cf, $28ac, $0000
	dw $61d0, $34eb, $2ce9, $0000
	dw $59ed, $5dec, $4987, $0000
.indoor
	dw $6b9e, $4e73, $35ad, $1ce7
	dw $6b9e, $627f, $195e, $1ce7
	dw $6b9e, $068f, $01a9, $1ce7
	dw $6b9e, $7e0f, $7d29, $1ce7
	dw $6b9e, $1fff, $061f, $1ce7
	dw $6b9e, $1e35, $0db0, $1ce7
	dw $6b9e, $7e71, $7e0e, $1ce7

;---------------------------------------------------------------------
; サファリの 戦い（ピカチュウ版と 同じ：ボール・エサ・いし・にげる。手もちの ポケモンは 出さない）
; DoBattle の cp BATTLETYPE_DEBUG / jp z, .tutorial_debug（デバッグ用の 戦いは 使われていない）を かえる
SECTION "safari dobattle hook", ROMX[$405d], BANK[$0f]
	call SafariDoBattle
	nop
	nop

SECTION "safari dobattle", ROMX[SAFARI_DOBATTLE], BANK[$0f]
; a = wBattleType。サファリの 戦いなら ここで 戦って DoBattle から もどる
; つりは 「つりあげた ○○が とびかかってきた！」を 出したあとの ここで サファリの 戦いに かえる
SafariDoBattle:
	cp BATTLETYPE_FISH
	jr nz, .notfish
	ld a, [wStatusFlags2]
	bit STATUSFLAGS2_SAFARI_GAME_F, a
	jr z, .fish
	ld a, [wMapTileset]
	cp TILESET_SAFARIOUT
	jr nz, .fish
	ld a, BATTLETYPE_SAFARI
	ld [wBattleType], a
	jr .safari
.fish
	ld a, BATTLETYPE_FISH
	ret
.notfish
	cp BATTLETYPE_SAFARI
	ret nz
.safari
	pop hl                           ; DoBattle から もどる
	ld a, BANK(SafariBattle)
	ld hl, SafariBattle
	rst $08
	ret

SECTION "safari battle", ROMX[SAFARI_BATTLE_ADDR], BANK[SAFARI_SCRIPT_BANK]
SafariBattle:
	xor a
	ld [wSafariEscapeFactor], a
	ld [wSafariBaitFactor], a
.menu
	jfarcall EmptyBattleTextbox
	call J_LoadTilemapToTempTilemap
	ld hl, SafariBattleMenuHeader
	call J_LoadMenuHeader
	ld a, [wBattleMenuCursorPosition]
	ld [wMenuCursorPosition], a
	call J__2DMenu
	ld a, [wMenuCursorPosition]
	ld [wBattleMenuCursorPosition], a
	call J_ExitMenu
	ld a, 1
	ldh [hBGMapMode], a
	ld a, [wBattleMenuCursorPosition]
	cp 2
	jp z, .bait
	cp 3
	jp z, .rock
	cp 4
	jp z, .run

; ボール
	ld a, [wPartyCount]
	cp PARTY_LENGTH
	jr nz, .room
	ld a, 1                          ; BANK(sBoxCount)
	call J_OpenSRAM
	ld a, [sBoxCount]
	cp 30                            ; 日本版の ボックスは 30匹（MONS_PER_BOX は 英語版の 20）
	call J_CloseSRAM
	jr nz, .room
	ld hl, SafariText_BoxFull        ; ピカチュウ版の 文
	call J_PrintText
	jp .menu
.room
	ld hl, wSafariBallsRemaining
	dec [hl]
	ld hl, SafariText_UseBall
	call J_PrintText
	call SafariCatchCalc
	ld c, 20
	call J_DelayFrames
	ld a, POKE_BALL
	ld [wBattleAnimParam], a
	ld a, SAFARI_BALL_ITEM           ; 投げる ボールの 絵・色を サファリボールに（src/pikaballs.asm）
	ld [wCurItem], a
	ld de, ANIM_THROW_POKE_BALL
	ld a, e
	ld [wFXAnimID], a
	ld a, d
	ld [wFXAnimID + 1], a
	xor a
	ldh [hBattleTurn], a
	ld [wThrownBallWobbleCount], a
	ld [wBattleAfterAnim], a
	jfarcall PlayBattleAnim
	ld a, [wWildMon]
	and a
	jr nz, .caught
	ld a, [wThrownBallWobbleCount]   ; 1〜4（ゆれた回数 + 1）
	dec a
	and 3
	add a
	ld e, a
	ld d, 0
	ld hl, .balltexts
	add hl, de
	ld a, [hli]
	ld h, [hl]
	ld l, a
	call J_PrintText
	call J_ClearSprites
	jp .after

.balltexts
	dw SafariText_BallMissed, SafariText_BallBroke, SafariText_BallAww, SafariText_BallClose

.caught
	ld a, PARK_BALL                  ; 道具は へらない（バッグに ないので）
	ld [wCurItem], a
	jfarcall PokeBallEffect__caught   ; やったー！… 図鑑・名前・ボックス（金と同じ）
	xor a
	ld [wWildMon], a
	ld a, [wBattleResult]
	and BATTLERESULT_BITMASK
	ld [wBattleResult], a            ; WIN
	call J_ClearWindowData
	call J_SetDefaultBGPAndOBP
	ret

; えさ・いし
.bait
	ld hl, SafariText_ThrewBait
	call J_PrintText
	ld hl, wEnemyMonCatchRate
	srl [hl]                         ; つかまえやすさ ÷2
	ld de, SAFARI_ANIM_BAIT
	ld hl, wSafariBaitFactor
	ld bc, wSafariEscapeFactor
	jr .baitrock
.rock
	ld hl, SafariText_ThrewRock
	call J_PrintText
	ld hl, wEnemyMonCatchRate
	ld a, [hl]
	add a                            ; つかまえやすさ ×2（255まで）
	jr nc, .nocarry
	ld a, $ff
.nocarry
	ld [hl], a
	ld de, SAFARI_ANIM_ROCK
	ld hl, wSafariEscapeFactor
	ld bc, wSafariBaitFactor
.baitrock
	xor a
	ld [bc], a
.random
	call J_Random
	and 7
	cp 5
	jr nc, .random
	inc a                            ; 1〜5
	add [hl]
	jr nc, .nocarry2
	ld a, $ff
.nocarry2
	ld [hl], a
	ld a, e
	ld [wFXAnimID], a
	ld a, d
	ld [wFXAnimID + 1], a
	xor a
	ldh [hBattleTurn], a
	ld [wBattleAnimParam], a
	ld [wBattleAfterAnim], a
	jfarcall PlayBattleAnim
	ld c, 70
	call J_DelayFrames

; 行動のあと：ボールが なくなった → おわり。でなければ たべてる・おこってる、にげるか
.after
	ld a, [wSafariBallsRemaining]
	and a
	jr nz, .notout
	ld hl, SafariText_OutOfBalls
	call J_PrintText
	jr .draw
.notout
	call SafariEatingAngry
	ld a, [wEnemyMonSpeed + 1]
	add a
	ld b, a                          ; すばやさ（下の 1バイト）×2
	jr c, .fled                      ; 128 以上なら かならず にげる
	ld a, [wSafariBaitFactor]
	and a
	jr z, .escape
	srl b
	srl b                            ; たべている：÷4
.escape
	ld a, [wSafariEscapeFactor]
	and a
	jr z, .compare
	sla b                            ; おこっている：×2（255まで）
	jr nc, .compare
	ld b, $ff
.compare
	call J_Random
	cp b
	jp nc, .menu
.fled
	ld hl, SafariText_Fled
	call J_PrintText
	ld de, SFX_RUN
	call J_PlaySFX
	call J_WaitSFX
	ld a, BANK(SafariSlideEnemyOff)  ; 相手の ポケモンが 右へ すべって 消える（ピカチュウ版と同じ）
	ld hl, SafariSlideEnemyOff
	rst $08
	jr .draw

.run
	ld de, SFX_RUN
	call J_PlaySFX
	call J_WaitSFX
	ld hl, SafariText_GotAway
	call J_PrintText
.draw
	ld a, [wBattleResult]
	and BATTLERESULT_BITMASK
	add DRAW
	ld [wBattleResult], a
	ret

SafariBattleMenuHeader:
	db MENU_BACKUP_TILES
	menu_coords 0, 12, SCREEN_WIDTH - 1, SCREEN_HEIGHT - 1
	dw .MenuData
	db 1
.MenuData
	db STATICMENU_CURSOR | STATICMENU_DISABLE_B
	dn 2, 2
	db 11
	dba SafariMenuItems
	dba .Balls
.Balls
	hlcoord 10, 14
	ld de, wSafariBallsRemaining
	lb bc, 1, 2
	jp J_PrintNum

; たべてる・おこってる（ピカチュウ版の PrintSafariZoneBattleText）
SafariEatingAngry:
	ld hl, wSafariBaitFactor
	ld a, [hl]
	and a
	jr z, .nobait
	dec [hl]
	ld hl, SafariText_Eating
	jp J_PrintText
.nobait
	dec hl                           ; wSafariEscapeFactor
	ld a, [hl]
	and a
	ret z
	dec [hl]
	ld hl, SafariText_Angry
	jr nz, .print
	push hl                          ; おこるのが おわった：つかまえやすさを 元に もどす
	ld a, [wEnemyMonSpecies]
	ld [wCurSpecies], a
	call J_GetBaseData
	ld a, [wBaseCatchRate]
	ld [wEnemyMonCatchRate], a
	pop hl
.print
	jp J_PrintText

; つかまえられるか（ピカチュウ版の サファリボールと 同じ計算）
; wWildMon = つかまえた ポケモン（だめなら 0）、wSafariShakes = ゆれる回数
SafariCatchCalc:
	xor a
	ld [wWildMon], a
.loop
	call J_Random
	cp 151
	jr nc, .loop                     ; 0〜150
	ld b, a
	ld a, [wEnemyMonStatus]
	and a
	jr z, .nostatus
	and 1 << FRZ | SLP_MASK
	ld c, 12
	jr z, .notfrzslp
	ld c, 25
.notfrzslp
	ld a, b
	sub c
	jp c, .captured
	ld b, a
.nostatus
	push bc
	xor a
	ldh [hMultiplicand], a
	ld hl, wEnemyMonMaxHP
	ld a, [hli]
	ldh [hMultiplicand + 1], a
	ld a, [hl]
	ldh [hMultiplicand + 2], a
	ld a, 255
	ldh [hMultiplier], a
	call J_Multiply
	ld a, 12
	ldh [hDivisor], a
	ld b, 4
	call J_Divide
	ld hl, wEnemyMonHP
	ld a, [hli]
	ld b, a
	ld a, [hl]
	srl b
	rr a
	srl b
	rr a
	and a
	jr nz, .hpok
	inc a
.hpok
	ldh [hDivisor], a
	ld b, 4
	call J_Divide
	ldh a, [hQuotient + 2]
	and a
	jr z, .xok
	ld a, 255
	ldh [hQuotient + 3], a
.xok
	pop bc
	ld a, [wEnemyMonCatchRate]
	cp b
	jr c, .failed
	ldh a, [hQuotient + 2]
	and a
	jr nz, .captured
	call J_Random
	ld b, a
	ldh a, [hQuotient + 3]
	cp b
	jr c, .failed
.captured
	ld a, [wEnemyMonSpecies]
	ld [wWildMon], a
	ld a, 3
	ld [wSafariShakes], a
	ret

.failed
	ldh a, [hQuotient + 3]
	ld [wSafariShakes], a            ; X を とっておく
	xor a
	ldh [hMultiplicand], a
	ldh [hMultiplicand + 1], a
	ld a, [wEnemyMonCatchRate]
	ldh [hMultiplicand + 2], a
	ld a, 100
	ldh [hMultiplier], a
	call J_Multiply
	ld a, 150
	ldh [hDivisor], a
	ld b, 4
	call J_Divide
	ldh a, [hQuotient + 2]
	and a
	ld b, 3
	jr nz, .set
	ld a, [wSafariShakes]
	ldh [hMultiplier], a
	call J_Multiply
	ld a, 255
	ldh [hDivisor], a
	ld b, 4
	call J_Divide
	ld a, [wEnemyMonStatus]
	and a
	jr z, .nostatus2
	and 1 << FRZ | SLP_MASK
	ld b, 5
	jr z, .addstatus
	ld b, 10
.addstatus
	ldh a, [hQuotient + 3]
	add b
	ldh [hQuotient + 3], a
.nostatus2
	ldh a, [hQuotient + 3]
	ld b, 0
	cp 10
	jr c, .set
	inc b
	cp 30
	jr c, .set
	inc b
	cp 70
	jr c, .set
	inc b
.set
	ld a, b
	ld [wSafariShakes], a
	ret

;---------------------------------------------------------------------
; ボールの ゆれ（GetPokeBallWobble の ld a, [wWildMon] / and a / ld c, 0 / ret nz を かえる）
SECTION "safari wobble hook", ROMX[$7f16], BANK[$03]
	call SafariWobble
	ret nz
	nop
	nop
	nop

SECTION "safari wobble", ROMX[SAFARI_WOBBLE], BANK[$03]
; a = ゆれた回数 + 1（1〜3）。nz で もどると c（0 = つづける、2 = でてしまう）で おわり
SafariWobble:
	ld c, a
	ld a, [wBattleType]
	cp BATTLETYPE_SAFARI
	jr nz, .normal
	ld a, [wSafariShakes]
	cp c
	ld c, 0
	jr nc, .ret
	ld c, 2
.ret
	or 1
	ret
.normal
	ld a, [wWildMon]
	and a
	ld c, 0
	ret

;---------------------------------------------------------------------
; えさ・いしの アニメ（ピカチュウ版：ポケモンに むかって 投げる）
SECTION "safari anims", ROMX[SAFARI_ANIM_PTRS], BANK[$32]
	dw SafariBaitAnim
	dw SafariRockAnim
SafariBaitAnim:
	anim_1gfx BATTLE_ANIM_GFX_EGG
	anim_sound 6, 2, SFX_THROW_BALL
	anim_obj SAFARI_OBJ_BAIT, 64, 92, $10
	anim_wait 36
	anim_ret
SafariRockAnim:
	anim_2gfx BATTLE_ANIM_GFX_ROCKS, BATTLE_ANIM_GFX_HIT
	anim_sound 6, 2, SFX_THROW_BALL
	anim_obj SAFARI_OBJ_ROCK, 64, 92, $10
	anim_wait 36
	anim_sound 0, 1, SFX_POUND
	anim_obj BATTLE_ANIM_OBJ_HIT_YFIX, 136, 48, $0
	anim_wait 16
	anim_ret

; InitBattleAnimation の ld e, a / ld d, 0 / ld hl, BattleAnimObjects を かえる（$f0〜 は 新しい 部品）
SECTION "safari animobj hook", ROMX[$4906], BANK[$33]
	call SafariAnimObj
	nop
	nop
	nop

SECTION "safari animobj", ROMX[SAFARI_ANIM_OBJ], BANK[$33]
SafariAnimObj:
	ld e, a
	ld d, 0
	ld hl, $4a79                     ; BattleAnimObjects
	cp SAFARI_OBJ_BAIT
	ret c
	sub SAFARI_OBJ_BAIT
	ld e, a
	ld hl, .objects
	ret
.objects
	; えさ（まるい 小さな もの）
	db 1, $90, BATTLE_ANIM_FRAMESET_BARRAGE_BALL, BATTLE_ANIM_FUNC_THROW_TO_TARGET_DISAPPEAR, PAL_BATTLE_OB_BROWN, BATTLE_ANIM_GFX_EGG
	; いし
	db 1, $90, BATTLE_ANIM_FRAMESET_SMALL_ROCK, BATTLE_ANIM_FUNC_THROW_TO_TARGET_DISAPPEAR, PAL_BATTLE_OB_BROWN, BATTLE_ANIM_GFX_ROCKS

;---------------------------------------------------------------------
; スタートメニューの 左上に のこりの 歩数と ボール（ピカチュウ版と同じ「nnn/500」「ボール nnこ」）
; StartMenu の .DrawBugContestStatusBox・.DrawBugContestStatus の ld hl, wStatusFlags2 / bit 2, [hl] を
; ld a, [wStatusFlags2] / and %110（サファリゲーム か 虫とり大会）にして、
; 虫とり大会の 表示（バンク$09）の 頭で サファリなら こちらを 出す
SECTION "safari startmenu hook 1", ROMX[$6b6d], BANK[4]
	ld a, [wStatusFlags2]
	and 1 << STATUSFLAGS2_SAFARI_GAME_F | 1 << STATUSFLAGS2_BUG_CONTEST_TIMER_F
SECTION "safari startmenu hook 2", ROMX[$6b7a], BANK[4]
	ld a, [wStatusFlags2]
	and 1 << STATUSFLAGS2_SAFARI_GAME_F | 1 << STATUSFLAGS2_BUG_CONTEST_TIMER_F

; StartMenu_DrawBugContestStatusBox の hlcoord 0, 0・StartMenu_PrintBugContestStatus の ld hl, wOptions を かえる
SECTION "safari startmenu hook 3", ROMX[$4b1e], BANK[$09]
	call SafariStartMenuBox9
SECTION "safari startmenu hook 4", ROMX[$4b29], BANK[$09]
	call SafariStartMenuPrint9

SECTION "safari startmenu", ROMX[$7fb1], BANK[$09]
SafariStartMenuBox9:
	ld a, [wStatusFlags2]
	bit STATUSFLAGS2_SAFARI_GAME_F, a
	jr nz, SafariStartMenu9
	hlcoord 0, 0
	ret
SafariStartMenuPrint9:
	ld a, [wStatusFlags2]
	bit STATUSFLAGS2_SAFARI_GAME_F, a
	jr nz, SafariStartMenu9
	ld hl, wOptions
	ret
SafariStartMenu9:
	pop hl                           ; 虫とり大会の 表示は しない
	ld a, BANK(SafariStartMenuBox)
	ld hl, SafariStartMenuBox
	rst $08
	ret

SECTION "safari startmenu box", ROMX[SAFARI_BATTLE_ADDR + $400], BANK[SAFARI_SCRIPT_BANK]
SafariStartMenuBox:
	call SafariInZone
	ret nc
	hlcoord 0, 0
	lb bc, 3, 7
	call J_Textbox
	hlcoord 1, 1
	ld de, wSafariTimeRemaining
	lb bc, 2, 3
	call J_PrintNum
	hlcoord 4, 1
	ld de, .Steps
	call J_PlaceString
	hlcoord 1, 3
	ld de, .Balls
	call J_PlaceString
	hlcoord 5, 3
	ld de, wSafariBallsRemaining
	lb bc, 1, 2
	jp J_PrintNum
.Steps ; 「/500」（ピカチュウ版の 文字）
	db $f3, $fb, $f6, $f6, $50
.Balls ; 「ボール   こ」
	db $1c, $e3, $a6, $7f, $7f, $7f, $ba, $50

;---------------------------------------------------------------------
; つり（ピカチュウ版と同じ：ボロ＝コイキング5、いい＝トサキント・ニョロモ10（半分 つれない）、
;       すごい＝マップごと（半分 つれない））。つれた ポケモンとも サファリの 戦いを する
; FishFunction .goodtofish の farcall Fish の 行き先を かえる
SECTION "safari fish hook", ROMX[$524d], BANK[$03]
	ld a, BANK(SafariFish)
	ld hl, SafariFish

; つれないとき：Script_NotEvenANibble の writetext RodNothingText / sjump（6バイト）を 下の 文の スクリプトへ。
;   Script_NotEvenANibble2 の writetext（3バイト）は そこへの sjump に する
SECTION "safari fish nibble hook", ROMX[$5299], BANK[$03]
	farsjump SafariFishNibbleScript
	db $00, $00
SECTION "safari fish nibble hook 2", ROMX[$52a2], BANK[$03]
	sjump $5299
; つれたとき：Script_GotABite の writetext RodBiteText から あと（randomwildmon ほか）を かえる
SECTION "safari fish battle hook", ROMX[$52c6], BANK[$03]
	farsjump SafariFishBiteScript

SECTION "safari fish", ROMX[SAFARI_BATTLE_ADDR + $480], BANK[SAFARI_SCRIPT_BANK]
; e = つりざお（0 ボロ・1 いい・2 すごい）→ d = ポケモン（0 = つれない）、e = レベル
SafariFish:
	ld a, [wMapTileset]
	cp TILESET_SAFARIOUT
	jr z, .safari
	jfarcall Fish
	ret
.safari
	ld a, e
	and a
	jr z, .old
	dec a
	jr z, .good
; すごいつりざお
	ld hl, .super_center
	ld a, [wMapGroup]
	cp GROUP_SAFARI_CENTER
	jr nz, .other
	ld a, [wMapNumber]
	cp MAP_SAFARI_CENTER
	jr z, .gotmap
.other
	ld hl, .super_other
.gotmap
	call J_Random
	cp 40 * 255 / 100
	jr c, .slot
	inc hl
	inc hl
	cp 70 * 255 / 100
	jr c, .slot
	inc hl
	inc hl
	cp 90 * 255 / 100
	jr c, .slot
	inc hl
	inc hl
.slot
	ld d, [hl]
	inc hl
	ld e, [hl]
	call J_Random
	and 1
	ret nz
	jr .nobite
.old
	ld de, MAGIKARP << 8 | 5
	ret
.good
	call J_Random
	srl a
	jr c, .nobite
	and %11
	cp 2
	jr nc, .good
	ld de, GOLDEEN << 8 | 10
	and a
	ret z
	ld de, POLIWAG << 8 | 10
	ret
.nobite
	ld d, 0
	ret
.super_center
	db MAGIKARP, 5, MAGIKARP, 10, DRATINI, 10, DRAGONAIR, 15
.super_other
	db MAGIKARP, 5, MAGIKARP, 10, MAGIKARP, 15, DRATINI, 15

; 釣りの 文：サファリの中は ピカチュウ版の 文、外は 元の 文
DEF J_RodNothingText EQU $5329
DEF J_RodBiteText EQU $531a
DEF J_PutTheRodAway EQU $530b
SafariFishNibbleScript:
	callasm SafariInGame
	iftrue .pk
	db farwritetext_command, $03
	dw J_RodNothingText
	sjump .done
.pk
	farwritetext SafariText_FishNoBite
.done
	db callasm_command, $03
	dw J_PutTheRodAway
	closetext
	end

SafariFishBiteScript:
	callasm SafariInGame
	iftrue .pk
	db farwritetext_command, $03
	dw J_RodBiteText
	sjump .done
.pk
	farwritetext SafariText_FishBite
.done
	db callasm_command, $03
	dw J_PutTheRodAway
	closetext
	sjump SafariFishBattleScript

; つった ポケモンとの 戦い（サファリの中なら SafariDoBattle で サファリの 戦いになる。ボールが なくなったら おわり）
SafariFishBattleScript:
	randomwildmon
	startbattle
	reloadmapafterbattle
	callasm SafariInGame
	iffalse .end
	readmem wSafariBallsRemaining
	iffalse SafariGameOverScript
.end
	end

SafariFuchsiaSignScript:
	jumptext SafariText_FuchsiaSign

; wScriptVar = サファリゲームの 中（サファリの マップに いて、ゲームを している）
SafariInGame:
	xor a
	ld [wScriptVar], a
	ld a, [wStatusFlags2]
	bit STATUSFLAGS2_SAFARI_GAME_F, a
	ret z
	call SafariInZone
	ret nc
	ld a, 1
	ld [wScriptVar], a
	ret

;---------------------------------------------------------------------
; 段差の 組み合わせ（ピカチュウ版の TilePairCollisions：森の タイルセット）
; DoPlayerMovement .CheckLandPerms・.CheckSurfPerms の ld a, [wTilePermissions] を かえる
SECTION "safari pair hook land", ROMX[$439e], BANK[$04]
	call SafariPairHook
SECTION "safari pair hook surf", ROMX[$43b4], BANK[$04]
	call SafariPairHook

SECTION "safari pair hook", ROMX[$7feb], BANK[$04]   ; バンク$04 の空き
; a = wTilePermissions（とおれない 組み合わせなら $ff）
SafariPairHook:
	ld a, [wMapTileset]
	cp TILESET_SAFARIOUT
	jr nz, .normal
	ld a, BANK(SafariPairCheck)
	ld hl, SafariPairCheck
	rst $08
	ld a, $ff
	ret c
.normal
	ld a, [wTilePermissions]
	ret

SECTION "safari pair", ROMX[SAFARI_BATTLE_ADDR + $580], BANK[SAFARI_SCRIPT_BANK]
; キャリー = とおれない（いまの タイルと 進む先の タイルが 組み合わせに ある）
SafariPairCheck:
	ld a, [wWalkingDirection]
	and 3
	add a
	ld e, a
	ld d, 0
	ld hl, .front
	add hl, de
	ld a, [hli]
	ld h, [hl]
	ld l, a
	ld b, [hl]                       ; 進む先
	ld a, [wTilemap + 9 * SCREEN_WIDTH + 8]
	ld c, a                          ; いまの所
	ld hl, .land
	ld a, [wPlayerState]
	cp PLAYER_SURF
	jr z, .water
	cp PLAYER_SURF_PIKA
	jr nz, .got
.water
	ld hl, .watertiles
.got
	ld a, c
	cp $2e
	jr z, .check
	ld a, b
	cp $2e
	jr nz, .ok
	ld b, c
.check
	ld a, [hli]
	cp $ff
	jr z, .ok
	cp b
	jr nz, .check
	scf
	ret
.ok
	and a
	ret
.front ; した・うえ・ひだり・みぎ
	dw wTilemap + 11 * SCREEN_WIDTH + 8
	dw wTilemap + 7 * SCREEN_WIDTH + 8
	dw wTilemap + 9 * SCREEN_WIDTH + 6
	dw wTilemap + 9 * SCREEN_WIDTH + 10
.land
	db $30, $52, $55, $56, $20, $5e, $5f, $ff
.watertiles
	db $14, $48, $ff

;---------------------------------------------------------------------
; セキチクシティの 入口の となりの 看板（「えんちょうは がいこくへ…」→ ピカチュウ版の「めいぶつ！ サファリ ゲーム！」）
SECTION "safari fuchsia sign event", ROMX[$7229 + 3], BANK[$36]
	dw SafariFuchsiaSign
SECTION "safari fuchsia sign", ROMX[$7fd8], BANK[$36]
SafariFuchsiaSign:
	farsjump SafariFuchsiaSignScript

;---------------------------------------------------------------------
; サファリゾーンの 曲（ピカチュウ版の Music_SafariZone を 金の 書き方に した。
; 命令は ほぼ 同じ。toggle_perfect_pitch（音を 1 だけ 高くする）は 金の pitch_offset 1。波形 0 は 金も 同じ）
; _PlayMusic の ld hl, Music を かえて、MUSIC_SAFARI_ZONE_PK だけ ここの 表を 見る
SECTION "safari music hook", ROMX[$4b39], BANK[$3a]
	call SafariMusicTable

SECTION "safari music table", ROMX[$7fb7], BANK[$3a]
SafariMusicTable:
	ld hl, $506e                     ; Music
	ld a, e
	cp MUSIC_SAFARI_ZONE_PK
	ret nz
	ld hl, .entry - MUSIC_SAFARI_ZONE_PK * 3
	ret
.entry
	dba Music_SafariZonePK

SECTION "safari music", ROMX[$7900], BANK[SAFARI_DATA_BANK]
Music_SafariZonePK:
	channel_count 3
	channel 1, Music_SafariZonePK_Ch1
	channel 2, Music_SafariZonePK_Ch2
	channel 3, Music_SafariZonePK_Ch3

Music_SafariZonePK_Ch1:
	tempo 132
	volume 7, 7
	vibrato 6, 3, 4
	pitch_offset 1                   ; ピカチュウ版の toggle_perfect_pitch
	duty_cycle 2
	note_type 12, 9, 2
	octave 3
	pitch_slide 1, 4, A_
	note C_, 1
	pitch_slide 1, 4, A_
	note G_, 1
	pitch_slide 1, 4, A_
	note C_, 1
	pitch_slide 1, 4, A_
	note G_, 1
	rest 4
	duty_cycle 3
.mainloop:
	sound_call .sub1
	note_type 12, 10, 4
	note F#, 4
	sound_call .sub1
	note_type 12, 10, 4
	note F#, 4
	sound_loop 0, .mainloop
.sub1:
	note_type 12, 10, 2
	octave 3
	note C_, 4
	note G_, 4
	note C_, 4
	note G_, 4
	note C_, 4
	note G_, 4
	note C_, 4
	sound_ret

Music_SafariZonePK_Ch2:
	duty_cycle 2
	vibrato 8, 2, 5
	note_type 12, 10, 2
	octave 4
	note G_, 1
	note D_, 1
	note G_, 1
	note D_, 1
	rest 4
	duty_cycle 3
.mainloop:
	sound_call .sub1
	note_type 12, 11, 5
	note A_, 4
	sound_call .sub1
	note_type 12, 11, 5
	note B_, 4
	sound_loop 0, .mainloop
.sub1:
	note_type 12, 11, 2
	octave 3
	note G_, 4
	note D_, 4
	note G_, 4
	note D_, 4
	note G_, 4
	note D_, 4
	note G_, 4
	sound_ret

Music_SafariZonePK_Ch3:
	note_type 12, 1, 0
	rest 8
.mainloop:
	sound_call .sub1
	octave 4
	note A_, 4
	sound_call .sub1
	octave 4
	note B_, 4
	sound_loop 0, .mainloop
.sub1:
	octave 3
	note A_, 2
	rest 2
	octave 4
	note D_, 2
	rest 2
	octave 3
	note A_, 2
	rest 2
	octave 4
	note D_, 2
	rest 2
	octave 3
	note A_, 2
	rest 2
	octave 4
	note D_, 2
	rest 2
	octave 3
	note A_, 2
	rest 2
	sound_ret

;---------------------------------------------------------------------
; アナウンスの 音（ピカチュウ版の SFX_Safari_Zone_PA。命令は 金も 同じ）
; _PlaySFX の ld hl, SFX を かえて、SFX_SAFARI_ZONE_PK だけ ここの 表を 見る
SECTION "safari sfx hook", ROMX[$4c78], BANK[$3a]
	call SafariSFXTable

SECTION "safari sfx table", ROMX[$7fc8], BANK[$3a]
SafariSFXTable:
	ld hl, $525e                     ; SFX
	ld a, e
	cp SFX_SAFARI_ZONE_PA
	ret nz
	ld hl, .entry - SFX_SAFARI_ZONE_PA * 3
	ret
.entry
	dba Sfx_SafariZonePA

SECTION "safari sfx", ROMX[$7a00], BANK[SAFARI_DATA_BANK]
Sfx_SafariZonePA:
	channel_count 1
	channel 5, Sfx_SafariZonePA_Ch5
Sfx_SafariZonePA_Ch5:
	duty_cycle 2
	square_note 15, 15, 3, 1840
	square_note 8, 6, 5, 1840
	square_note 15, 15, 4, 1792
	square_note 15, 7, 4, 1792
	square_note 15, 4, 4, 1792
	square_note 15, 2, 4, 1792
	sound_ret

;---------------------------------------------------------------------
; にげだした ポケモンが 右へ すべって 消える（SlideBattlePicOut：相手が 入れかわるときと 同じ）
SECTION "safari slide", ROMX[$7fc0], BANK[$0f]
SafariSlideEnemyOff:
	hlcoord 18, 0
	ld a, 8
	jp $534a                         ; SlideBattlePicOut

;---------------------------------------------------------------------
; 戦いの 始まりに 手もちの ボール（●●●○○○）を 出さない（ピカチュウ版の サファリと 同じ）
; BattleStart_TrainerHuds の ld a, $e4 / ldh [rOBP0], a を かえる
SECTION "safari huds hook", ROMX[$50e4], BANK[$0b]
	call SafariTrainerHuds
	nop
SECTION "safari huds", ROMX[$7d00], BANK[$0b]
SafariTrainerHuds:
	ld a, [wStatusFlags2]
	bit STATUSFLAGS2_SAFARI_GAME_F, a
	jr z, .normal
	ld a, [wMapTileset]
	cp TILESET_SAFARIOUT
	jr nz, .normal
	pop af                           ; BattleStart_TrainerHuds から もどる（何も 出さない）
	ret
.normal
	ld a, $e4
	ldh [rOBP0], a
	ret

;---------------------------------------------------------------------
; あなぬけのヒモ・あなをほる：サファリゲーム中は 最後に つかった ポケモンセンターへ（ピカチュウ版と同じ）
; 金の しくみでは ゲートの 入口の前（wDigWarp）に 出るので、使ったあとの スクリプトの
; farscall Script_AbortBugContest を こちらに かえて、サファリなら テレポートと 同じ 出かたに する
; （行き先は めのまえが まっくらに なったときと 同じ（GetWhiteoutSpawn：さいごの ポケモンセンター））
SECTION "safari dig hook", ROMX[$4d5c], BANK[$03]
	farscall SafariDigScript

SECTION "safari dig", ROMX[SAFARI_BATTLE_ADDR + $600], BANK[SAFARI_SCRIPT_BANK]
SafariDigScript:
	db farscall_command, $04
	dw $64e8                         ; Script_AbortBugContest（元の 命令）
	callasm SafariInGame
	iffalse .normal
	callasm SafariSetSpawn
	special WarpToSpawnPoint
	loadvar VAR_MOVEMENT, PLAYER_NORMAL
	newloadmap MAPSETUP_TELEPORT
	playsound SFX_WARP_FROM
	applymovement PLAYER, .DigReturn
	endall
.normal
	end
.DigReturn
	show_object
	return_dig 32
	step_end

SafariSetSpawn:
	jfarcall GetWhiteoutSpawn
	ret

;---------------------------------------------------------------------
; ポケギアの 地図：地名 SAFARI_LANDMARK（$5f）は「サファリゾーン」（ピカチュウ版の タウンマップと同じ 名前）
; PokegearMap_UpdateLandmarkName の farcall GetLandmarkName を かえる
SECTION "safari landmark hook", ROMX[$501d], BANK[$24]
	ld a, BANK(SafariLandmarkName)
	ld hl, SafariLandmarkName

SECTION "safari landmark", ROMX[SAFARI_BATTLE_ADDR + $680], BANK[SAFARI_SCRIPT_BANK]
; e = 地名 → wStringBuffer1
SafariLandmarkName:
	ld a, e
	cp SAFARI_LANDMARK
	jr z, .safari
	ld a, $24
	ld hl, $6498                     ; GetLandmarkName
	rst $08
	ret
.safari
	ld hl, .name
	ld de, wStringBuffer1
	ld c, .end - .name
.copy
	ld a, [hli]
	ld [de], a
	inc de
	dec c
	jr nz, .copy
	ld e, SAFARI_LANDMARK
	ret
.name ; 「サファリゾーン」（ピカチュウ版の 文字）
	db $8a, $9b, $e9, $d8, $0e, $e3, $ab, $50
.end

;---------------------------------------------------------------------
; セキチクの「サファリゾーンが しまっている」話を かえる
; ・女の人・事務所の 看板・フレンドリィショップの つりびと：ピカチュウ版の 文を 元の 場所に 書く（safari_gen.py。元より 短い）
; ・えんちょうの まご（文が 長くなる）：話しかけた ときの スクリプト（$2d:$63b3）を farsjump にして こちらで 同じ 流れ
SECTION "safari granddaughter hook", ROMX[$63b3], BANK[$2d]
	farsjump SafariGranddaughterScript

SECTION "safari granddaughter", ROMX[$7aa8], BANK[SAFARI_SCRIPT_BANK]
DEF EVENT_TALKED_TO_WARDENS_GRANDDAUGHTER_JP EQU $00d9
SafariGranddaughterScript:
	faceplayer
	opentext
	checkevent EVENT_TALKED_TO_WARDENS_GRANDDAUGHTER_JP
	iftrue .later
	writetext SafariText_Granddaughter1
	waitbutton
	closetext
	setevent EVENT_TALKED_TO_WARDENS_GRANDDAUGHTER_JP
	end
.later
	writetext SafariText_Granddaughter2
	waitbutton
	closetext
	end

;---------------------------------------------------------------------
; ポケギアの 地図・ずかんの ぶんぷ：サファリゾーンを セキチクシティの 北の 別の 点（SAFARI_LANDMARK）に する
; SAFARI_LANDMARK（$5f）は 金に ない 地名の 番号。マップの 見出しの 地名は セキチクの まま
; （$5f は VICTORY_ROAD より 後ろなので、見出しに 書くと ジョウト あつかいに なる）。
;   ・GetLandmarkCoords（$24:$6489）：$5f なら セキチクの 北（x 100, y 120。セキチクは x 100, y 132）
;   ・地名：SafariLandmarkName（$5f なら「サファリゾーン」）
;   ・ポケギアを ひらいた とき（.LoadLandmark $24:$4cd4）：サファリの中で セキチクなら 自分の 場所・カーソルを $5f に
;   ・カーソルの 上下（.up $24:$4f90・.down $24:$4f9d）：セキチク（$50）と 19ばんすいどう（$51）の あいだに $5f を はさむ
;   ・ずかんの ぶんぷ：fishnest.asm の FISHNEST_EXTRA_LANDMARK = $5f
DEF SAFARI_LANDMARK EQU $5f
DEF SAFARI_LANDMARK_X EQU 100
DEF SAFARI_LANDMARK_Y EQU 120
DEF J_wPokegearMapPlayerIconLandmark EQU $c5d8
DEF J_wPokegearMapCursorLandmark EQU $c5d7
DEF J_PokegearMap_DoneDPad EQU $4fa8
SECTION "safari landmark coords hook", ROMX[$6489], BANK[$24]
	jp SafariLandmarkCoords
	nop
SafariLandmarkCoords_Cont:              ; add hl, hl から（$648d）

SECTION "safari pokegear init hook", ROMX[$4cd4], BANK[$24]
	call SafariPokegearInit                ; ld [wPokegearMapPlayerIconLandmark], a の 代わり

SECTION "safari pokegear up hook", ROMX[$4f90], BANK[$24]
	call SafariCursorUp
	nop                                    ; ld hl, wPokegearMapCursorLandmark / ld a, [hl] の 代わり
SECTION "safari pokegear down hook", ROMX[$4f9d], BANK[$24]
	call SafariCursorDown
	nop

SECTION "safari landmark coords", ROMX[$7f40], BANK[$24]
SafariLandmarkCoords:
	ld a, e
	cp SAFARI_LANDMARK
	jr z, .safari
	push hl                                ; 元の 処理
	ld l, e
	ld h, 0
	jp SafariLandmarkCoords_Cont
.safari
	ld e, SAFARI_LANDMARK_X
	ld d, SAFARI_LANDMARK_Y
	ret

; a = いまの 場所の 地名
SafariPokegearInit:
	cp LANDMARK_FUCHSIA_CITY
	jr nz, .set
	call SafariInZone24
	ld a, LANDMARK_FUCHSIA_CITY
	jr nc, .set
	ld a, SAFARI_LANDMARK
.set
	ld [J_wPokegearMapPlayerIconLandmark], a
	ret

SafariCursorUp:
	ld hl, J_wPokegearMapCursorLandmark
	ld a, [hl]
	cp LANDMARK_FUCHSIA_CITY
	jr z, .to_safari
	cp SAFARI_LANDMARK
	ret nz                                 ; 元の 処理へ
	ld [hl], LANDMARK_FUCHSIA_CITY + 1
	jr SafariCursorDone
.to_safari
	ld [hl], SAFARI_LANDMARK
	jr SafariCursorDone

SafariCursorDown:
	ld hl, J_wPokegearMapCursorLandmark
	ld a, [hl]
	cp LANDMARK_FUCHSIA_CITY + 1
	jr z, .to_safari
	cp SAFARI_LANDMARK
	ret nz
	ld [hl], LANDMARK_FUCHSIA_CITY
	jr SafariCursorDone
.to_safari
	ld [hl], SAFARI_LANDMARK
SafariCursorDone:
	pop hl                                 ; 元の 処理を とばして .done_dpad へ
	jp J_PokegearMap_DoneDPad

; サファリの中か（SafariInZone と 同じ。キャリー = 中）
SafariInZone24:
	ld a, [wMapTileset]
	cp TILESET_SAFARIOUT
	jr z, .yes
	cp TILESET_SAFARILAB
	jr z, .yes
	cp TILESET_SAFARIGATE
	jr nz, .no
	ld a, [wMapGroup]
	cp GROUP_SAFARI_GATE
	jr nz, .yes
	ld a, [wMapNumber]
	cp MAP_SAFARI_GATE
	jr nz, .yes
.no
	and a
	ret
.yes
	scf
	ret

;---------------------------------------------------------------------
; セキチクの サファリゾーン じむきょく（金では 中に だれも いない）に 案内の 人を 置く
; 話す 文は ピカチュウ版の セキチクの 人の「サファリ ゾーンは いりぐち ふきんは どうぶつえんで…」（ほかで 使っていない 文）
; SafariZoneMainOffice_MapAttributes（$25:$61b5）の スクリプト・イベントの バンクと 場所を こちらに かえる
SECTION "safari office attributes", ROMX[$61b5 + 6], BANK[$25]
	db BANK(SafariOffice_MapScripts)
	dw SafariOffice_MapScripts
	dw SafariOffice_MapEvents

SECTION "safari office", ROMX[$7b00], BANK[SAFARI_SCRIPT_BANK]
SafariOffice_MapScripts:
	def_scene_scripts
	def_callbacks
SafariOffice_MapEvents:
	db 0, 0
	def_warp_events
	warp_event  2,  7, FUCHSIA_CITY, 2
	warp_event  3,  7, FUCHSIA_CITY, 2
	def_coord_events
	def_bg_events
	def_object_events
	object_event  5,  3, SPRITE_GRAMPS, SPRITEMOVEDATA_STANDING_DOWN, 0, 0, -1, -1, 0, OBJECTTYPE_SCRIPT, 0, SafariOfficeManScript, -1

SafariOfficeManScript:
	jumptextfaceplayer SafariText_OfficeMan
