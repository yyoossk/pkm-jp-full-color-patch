; サファリゾーンで使う 日本版クリスタルの アドレス（英語版 pokecrystal の ラベルの名前で）
; tools の align.py（命令の並びで 英語版と 照らし合わせる）と、ROM の 中身で 確かめた
; J_名前 = アドレス、JB_名前 = バンク

MACRO jsym ; 名前, バンク, アドレス
DEF J_\1 EQU \3
DEF JB_\1 EQU \2
ENDM
; ---- ホーム
	jsym CallScript,              0, $25e2
	jsym Random,                  0, $2f5e
	jsym ExitMenu,                0, $1bd2
	jsym OpenSRAM,                0, $2f9d
	jsym CloseSRAM,               0, $2fad
	jsym ClearSprites,            0, $2fd7
	jsym ClearWindowData,         0, $1f82
	jsym SetDefaultBGPAndOBP,     0, $32c5
	jsym PlaySFX,                 0, $3bb0
	jsym WaitSFX,                 0, $3be2
	jsym PrintNum,                0, $3164
	jsym GetBaseData,             0, $3826
	jsym Multiply,                0, $30e5
	jsym Divide,                  0, $30f0
	jsym Textbox,                 0, $0fd2
	jsym FarCopyWRAM,             0, $3037
	jsym PrintText,               0, $1041
	jsym DelayFrames,             0, $0468
	jsym PlaceString,             0, $1057
	jsym CopyBytes,               0, $2ff2
	jsym LoadTilemapToTempTilemap, 0, $3069
	jsym LoadMenuHeader,          0, $1d00
	jsym _2DMenu,                 0, $1fed
; ---- バンクの中
	jsym CountStep,               $25, $6b79
	jsym RandomEncounter,         $25, $7c82
	jsym CheckWildEncounterCooldown, $25, $68c7
	jsym MapGroupPointers,        $25, $4000
	jsym LoadMapPals,             $02, $719b
	jsym DoBattle,                $0f, $4000
	jsym EmptyBattleTextbox,      $0f, $6de3
	jsym GetPokeBallWobble,       $03, $7e79
	jsym GetPokeBallWobble__done, $03, $7eba
	jsym PokeBallEffect,          $03, $6b58
	jsym PokeBallEffect__caught,  $03, $6cab
	jsym Ball_BoxIsFullMessage,   $03, $7c0a
	jsym FishFunction,            $03, $51ac
	jsym Script_GotABite,         $03, $5274   ; ここは 中の randomwildmon の所
	jsym Fish,                    $24, $6975
	jsym InitBattleAnimation,     $33, $49b5
	jsym BattleAnimObjects,       $33, $4b2b
	jsym PlayBattleAnim,          $33, $40e5
	jsym BattleAnimations,        $32, $4fff
	jsym StartMenu,               $04, $64b5
	jsym StartMenu_DrawBugContestStatusBox, $09, $4bf6
	jsym StartMenu_PrintBugContestStatus,   $09, $4c01
	jsym DoPlayerMovement,        $20, $4000
	jsym AnimateWaterTile,        $3f, $4402
	jsym StandingTileFrame8,      $3f, $42ff
	jsym WaitTileAnimation,       $3f, $42fe
	jsym DoneTileAnimation,       $3f, $42fb
	jsym TilesetHouseAnim,        $3f, $42e7

; ---- RAM
DEF wTilemap                  EQU $c4a0
DEF wLinkMode                 EQU $c2dc
DEF wScriptVar                EQU $c2dd
DEF wWildMon                  EQU $c644
DEF wEnemyMonNickname         EQU $c616
DEF wBattleAnimParam          EQU $c67d
DEF wSafariMonAngerCount      EQU $c6ef
DEF wSafariMonEating          EQU $c6f0
DEF wCurSpecies               EQU $cf54
DEF wMenuCursorPosition       EQU $cf7c
DEF wFXAnimID                 EQU $cfb6
DEF wBattleAfterAnim          EQU $cfbe
DEF wOptions                  EQU $cfc0
DEF wBGPals1                  EQU $d000   ; WRAM バンク5
DEF wWalkingDirection         EQU $d039
DEF wBattleMenuCursorPosition EQU $d092
DEF wBattleResult             EQU $d0ae
DEF wCurItem                  EQU $d0c6
DEF wCurPartyLevel            EQU $d103
DEF wTilePermissions          EQU $d142
DEF wMapTileset               EQU $d1ca
DEF wEnvironment              EQU $d1cb
DEF wThrownBallWobbleCount    EQU $d21c
DEF wEnemyMonSpecies          EQU $d237
DEF wEnemyMonStatus           EQU $d245
DEF wEnemyMonHP               EQU $d247
DEF wEnemyMonMaxHP            EQU $d249
DEF wEnemyMonSpeed            EQU $d24f
DEF wEnemyMonCatchRate        EQU $d25c
DEF wTempWildMonSpecies       EQU $d25f
DEF wBattleType               EQU $d261
DEF wBaseCatchRate            EQU $d270
DEF wMapReentryScriptQueueFlag EQU $d44d
DEF wStatusFlags2             EQU $d840
DEF wMoney                    EQU $d841
DEF wPlayerState              EQU $d950
DEF wSafariBallsRemaining     EQU $dc3f
DEF wSafariTimeRemaining      EQU $dc40
DEF wRepelEffect              EQU $dc67
DEF wMapGroup                 EQU $dc7b
DEF wMapNumber                EQU $dc7c
DEF wPartyCount               EQU $dc9d
DEF wPartyMon1Level           EQU $dcc4
DEF sBoxCount                 EQU $ad10
DEF JP_MONS_PER_BOX           EQU 30      ; 日本版は 1つの ボックスに 30
DEF hQuotient                 EQU $ffb3
DEF hMultiplicand             EQU $ffb4
DEF hMultiplier               EQU $ffb7
DEF hDivisor                  EQU $ffb7
DEF hBGMapMode                EQU $ffd4
DEF hRandomAdd                EQU $ffe1
DEF hRandomSub                EQU $ffe2
DEF hBattleTurn               EQU $ffe4

; ---- 改良で使うもの
	jsym Music,                   $3a, $506e
	jsym SFX,                     $3a, $527c
	jsym SlideBattlePicOut,       $0f, $5483
	jsym BattleStart_TrainerHuds, $0b, $512a
	jsym DigFunction,             $03, $4b9c   ; （バンクだけ使う）
	jsym Script_AbortBugContest,  $04, $6129
	jsym GetWhiteoutSpawn,        $04, $63da
	jsym GetLandmarkName,         $24, $6539
DEF wStringBuffer1            EQU $d05b
DEF wTimeOfDayPal            EQU $d834   ; GetTimePalette などで 確かめた（英語版 $d841）
