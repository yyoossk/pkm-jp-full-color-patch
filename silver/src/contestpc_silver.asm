; むしとり大会の ポケモンを パソコンへ：銀 日本版（後期版）の 値（銀の ROM で さがした）
DEF CP_HOOK            EQU $6a62      ; BugContest_SetCaughtContestMon（$03:$6a4d）の lb bc, 14, 12 / call PlaceYesNoBox / ret c（01 0c 0e cd f1 1b d8）
DEF CP_HOOK_BANK       EQU $03
DEF CP_GENSTATS        EQU $6a7c      ; BugContest_SetCaughtContestMon.generatestats
DEF CP_InsertPokemonIntoBox EQU $59a7
DEF CP_InsertPokemonIntoBox_BANK EQU $14
DEF CP_CopyBytes       EQU $30d6
DEF CP_PlaceYesNoBox   EQU $1bf1
DEF CP_PrintText       EQU $0f30
DEF CP_GetPokemonName  EQU $35e0
DEF CP_GetBaseData     EQU $39dd
DEF CP_OpenSRAM        EQU $309d
DEF CP_CloseSRAM       EQU $30ad
DEF CP_sBoxCount       EQU $ad10
DEF CP_sBoxMonNicknames EQU $b1a4
DEF CP_wContestMon     EQU $dc5d
DEF CP_wBufferMon      EQU $cf2d
DEF CP_wBufferMonOT    EQU $cf27
DEF CP_wCurPartyMon    EQU $cfff
DEF CP_wPlayerName     EQU $d1b5
DEF CP_wTempEnemyMonSpecies EQU $d0df
DEF CP_wNamedObjectIndex EQU $d143
DEF CP_wCurPartySpecies EQU $cffe
DEF CP_wCurSpecies     EQU $ce54
DEF CP_wStringBuffer1  EQU $cf87
DEF CP_SAVE            EQU $d740      ; 使われていない WRAM（wEventFlags の 前の すき間。$d6e5〜$d70c は 場所の 名前の 札、$d7a0〜 は ほかの 機能）
DEF CP_BANK            EQU $48
DEF CP_ADDR            EQU $7700
INCLUDE "src/contestpc.asm"
