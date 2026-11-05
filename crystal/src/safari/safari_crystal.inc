; サファリゾーン（src/safari/safari.asm）の クリスタル日本版の フックの場所・空き
; （英語版 pokecrystal の ラベルの 中の 命令の並びを 日本版で さがして 確かめた）

; マップの見出し（MapGroupPointers $25:$4000 の 先。9バイト）
DEF SF_MAPHEADER_BANK EQU $25
DEF SF_HDR_SAFARI_ZONE_FUCHSIA_GATE_BETA EQU $4409
DEF SF_HDR_SAFARI_ZONE_BETA              EQU $4412
DEF SF_HDR_CINNABAR_POKECENTER_2F_BETA   EQU $44d8
DEF SF_HDR_CERULEAN_POKECENTER_2F_BETA   EQU $453b
DEF SF_HDR_ROUTE_10_POKECENTER_2F_BETA   EQU $455f
DEF SF_HDR_VERMILION_POKECENTER_2F_BETA  EQU $47c3
DEF SF_HDR_PEWTER_POKECENTER_2F_BETA     EQU $4877
DEF SF_HDR_FUCHSIA_POKECENTER_2F_BETA    EQU $4997
DEF SF_HDR_LAVENDER_POKECENTER_2F_BETA   EQU $49df
DEF SF_HDR_CELADON_POKECENTER_2F_BETA    EQU $4b23

; タイルセットの表（LoadTilesetHeader の ld hl, Tilesets の オペランド・ld a, BANK(Tilesets) の バイト）
DEF SF_TILESETS_PTR      EQU $2cfc
DEF SF_TILESETS_BANKBYTE EQU $2d0e
; タイルごとの 色の表（PalMap）は タイルセットの表と 同じ バンク$13 に置く（map_palettes.asm が バンク$13）
DEF SAFARI_PALMAP_BANK   EQU $13
DEF SAFARI_PALMAP_ADDR   EQU $7800   ; $7760〜 は つよさをみるの並べかえ

; セキチクシティ（イベントは バンク$28、ブロックは バンク$2a）
DEF SF_FUCHSIA_EVENTS_BANK EQU $28
DEF SF_FUCHSIA_WARP7       EQU $6286  ; warp_event 18, 3, SAFARI_ZONE_FUCHSIA_GATE_BETA, 3
DEF SF_FUCHSIA_SIGN5       EQU $62b5  ; bg_event 17, 5（SafariZoneClosedSign）
DEF SF_FUCHSIA_SIGN_FREE   EQU $72e0  ; バンク$28 の空き
DEF SF_FUCHSIA_BLOCKS_BANK EQU $2a
DEF SF_FUCHSIA_DOOR_BLOCK  EQU $660e  ; ブロック（9, 1）＝ $7d

; 水の アニメ（タイルセットの アニメの バンク$3f の空き）
DEF SF_TILEANIM_FREE     EQU $7600

; 1歩ごと・野生の ポケモン（バンク$25。$7fa0〜$7fa9 は 60fps）
DEF SF_STEPHOOK_FREE     EQU $7fb0

; 背景の色（LoadMapPals の ld a, [wEnvironment] / cp TOWN）
DEF SF_MAPPALS_HOOK      EQU $7206
DEF SF_MAPPALS_FREE      EQU $7900   ; バンク$02 の空き（$7800〜 は ずかん・パソコンの絵の色）

; 戦い
DEF SF_DOBATTLE_HOOK     EQU $405d   ; DoBattle の cp BATTLETYPE_DEBUG / jp z, .tutorial_debug
DEF SF_DOBATTLE_FREE     EQU $7fb0   ; バンク$0f の空き（$7f40〜$7fab は バグ修正）
DEF SF_WOBBLE_HOOK       EQU $7e8d   ; GetPokeBallWobble の ld a, [wWildMon] / and a / ld c, 0 / jr nz, .done
DEF SF_WOBBLE_FREE       EQU $7fa0   ; バンク$03 の空き（$7f30〜$7f93 は バグ修正）
DEF SAFARI_ANIM_PTRS     EQU $7dc1   ; バンク$32 の空き（BattleAnimations $4fff からの 差が 偶数になる所）
DEF SF_ANIMOBJ_HOOK      EQU $49b8   ; InitBattleAnimation の ld e, a / ld d, 0 / ld hl, BattleAnimObjects
DEF SAFARI_ANIM_OBJ      EQU $7ff0   ; バンク$33 の空き（16バイト。$7ee0〜 は 投げるボールの絵）
DEF SF_ANIMOBJ_TABLE     EQU $3fea   ; ROM0 の空き（12バイト）

; スタートメニュー
DEF SF_STARTMENU_HOOK1   EQU $67c0   ; StartMenu .DrawBugContestStatusBox の ld hl, wStatusFlags2 / bit 2, [hl]
DEF SF_STARTMENU_HOOK2   EQU $67cd   ; StartMenu .DrawBugContestStatus の 〃
DEF SF_STARTMENU_FREE    EQU $7f30   ; バンク$09 の空き（$7de0〜$7f1b は 手持ちメニュー）

; つり
DEF SF_FISH_HOOK         EQU $51f3   ; FishFunction の farcall Fish（ld a, BANK(Fish) / ld hl, Fish）
DEF SF_GOTABITE_HOOK     EQU $526c   ; Script_GotABite の writetext RodBiteText（4c c0 52）。そのあと PutTheRodAway・closetext・randomwildmon…
DEF SF_NIBBLE_HOOK       EQU $523f   ; Script_NotEvenANibble の writetext RodNothingText / sjump FallThrough（4c cf 52 03 4b 52）
DEF SF_NIBBLE2_HOOK      EQU $5248   ; Script_NotEvenANibble2 の writetext RodNothingText（4c cf 52）
DEF J_RodNothingText     EQU $52cf   ; バンク$03
DEF J_RodBiteText        EQU $52c0
DEF J_PutTheRodAway      EQU $52b1

; 段差（DoPlayerMovement は バンク$20）
DEF SF_PAIR_HOOK_LAND    EQU $439e
DEF SF_PAIR_HOOK_SURF    EQU $43b4
DEF SF_PAIR_FREE         EQU $5f60   ; バンク$20 の空き（$5f40〜$5f4e は Bダッシュ）

; special の番号（日本版クリスタルも 英語版と 同じ 81）
DEF SF_SPECIAL_PLACEMONEY EQU 81

; ---- 改良（アナウンスの音・曲・手持ちのボール・すべって消える・あなぬけ・ポケギア）
DEF SF_PLAYMUSIC_HOOK    EQU $4b39   ; _PlayMusic の ld hl, Music（バンク$3a。英語版と 同じ）
DEF SF_PLAYSFX_HOOK      EQU $4c78   ; _PlaySFX の ld hl, SFX
DEF SF_AUDIO_FREE        EQU $7fc2   ; バンク$3a の空き（$20バイト）
DEF SF_SLIDE_FREE        EQU $7fe0   ; バンク$0f の空き（$7fb0〜 は サファリの戦い）
DEF SF_HUDS_FREE         EQU $7e60   ; バンク$0b の空き（$7f00〜 は ボールの印）
DEF SF_DIG_HOOK          EQU $4d02   ; DigFunction の スクリプトの farscall Script_AbortBugContest（バンク$03）
DEF SF_LANDMARK_HOOK     EQU $505a   ; ポケギアの地図の 地名の farcall GetLandmarkName（ld a, $24 / ld hl, GetLandmarkName。バンク$24）
DEF SF_SIGN_HOOK         EQU $40e5  ; PlaceMapNameCenterAlign（$2e:$40e1）の farcall GetLandmarkName（3e 24 21 39 65 cf）
DEF SF_SIGN_HOOK_BANK    EQU $2e
DEF SF_LOADMETATILES_FIX EQU $2177  ; LoadMetatiles の add a / ld l, a / ld h, 0 / add hl, hl ×3（87 6f 26 00 29 29 29。ROM0）
DEF SF_GRANDDAUGHTER_HOOK      EQU $5e86  ; えんちょうの まごの スクリプト（faceplayer / opentext / checkevent $00d9 …）
DEF SF_GRANDDAUGHTER_HOOK_BANK EQU $1e
DEF SF_GRANDDAUGHTER_FREE      EQU $7ae0  ; バンク SAFARI_SCRIPT_BANK（$74）の 空き
DEF SF_LANDMARKCOORDS_HOOK     EQU $652a  ; GetLandmarkCoords（push hl / ld l, e / ld h, 0）。Landmarks は $24:$6557
DEF SF_LANDMARKCOORDS_BANK     EQU $24
DEF SF_LANDMARKCOORDS_FREE     EQU $7feb  ; バンク$24 の さいごの 空き（21バイト）
DEF SF_PG_INIT_HOOK            EQU $4d07  ; TownMap_InitCursorAndPlayerIconPositions.LoadLandmark の ld [wPokegearMapPlayerIconLandmark], a
DEF SF_PG_UP_HOOK              EQU $4fc3  ; PokegearMap_ContinueMap .up の ld hl, wPokegearMapCursorLandmark / ld a, [hl]
DEF SF_PG_DOWN_HOOK            EQU $4fd0  ; 〃 .down
DEF SF_PG_FREE                 EQU $6d84  ; 使われていない DebugPrintSlotBias・AnimateSlotReelIcons（$6d84〜$6db6）
DEF SF_OFFICE_ATTRIBUTES       EQU $6200  ; SafariZoneMainOffice_MapAttributes（バンク$25）
