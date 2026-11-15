; ボックスの 自動切りかえ … クリスタル（日本版）用の 値（本体は src/autobox.asm）
; 値は 英語版 pokecrystal と 命令の 並びで 照らし合わせて 調べた（CheckTimeEvents・ChangeBoxSaveGame・GetBoxCount・CompareLoadedAndSavedPlayerID）
INCLUDE "src/safari/crystal_includes.asm"   ; pokecrystal の 定数・マクロ（スクリプトの 命令は pokegold の もの）
INCLUDE "src/safari/jp_crystal.inc"         ; CallScript・OpenSRAM・CloseSRAM・wScriptVar・wStringBuffer1
DEF AUTOBOX_NO_INCLUDES EQU 1

	jsym CheckPhoneCall,                $24, $4074
	jsym CompareLoadedAndSavedPlayerID, $05, $4bbf
	jsym PauseGameLogic,                $05, $4b48
	jsym SaveBox,                       $05, $4dee
	jsym LoadBox,                       $05, $4fef
	jsym _SaveGameData,                 $05, $4c04
	jsym ResumeGameLogic,               $05, $4b4e
DEF wCurBox            EQU $db65
DEF wSavedAtLeastOnce  EQU $d4ac

DEF AUTOBOX_HOOK        EQU $695d    ; CheckTimeEvents（$25:$693a）.do_daily の さいごの farcall CheckPhoneCall（3e 24 21 74 40 cf）
DEF AUTOBOX_HOOK_BANK   EQU $25
DEF AUTOBOX_BANK        EQU $76      ; 使われていない バンク
DEF AUTOBOX_ADDR        EQU $4000
DEF AUTOBOX_VARS_WRAMBANK EQU 2      ; WRAM バンク2（$df00〜$dfb0 は 60fps・手持ちの見た目、$dfc0〜$dfc2 は ずかんの絵の色・とけい）
DEF wAutoBoxDone        EQU $dfc3
DEF wAutoBoxNew         EQU $dfc4
DEF AUTOBOX_NUM_BOXES   EQU 9
DEF AUTOBOX_MONS_PER_BOX EQU 30
DEF AUTOBOX_SBOX_BANK   EQU 1        ; GetBoxCount.activebox（$38:$7dd5）
DEF AUTOBOX_SBOXCOUNT   EQU $ad10
; ボックス1〜9 の 場所は 金と 同じ（GetBoxCount.BoxBankAddresses $38:$7de0）

INCLUDE "src/autobox.asm"

; ボックスが いっぱいに なった とき の マサキの 電話を ならさない（自動で 次の ボックスに かわるので）。
; Script_reloadmap の 前（$25:$747a）：ld a, [wBattleResult] / bit BATTLERESULT_BOX_FULL, a / jr z, .done
;   / ld b, BANK(Script_SpecialBillCall) / ld de, Script_SpecialBillCall / farcall LoadMemScript
; の jr z（28 0b）を jr（18 0b）に して、いつも とばす。
SECTION "autobox no bill call", ROMX[$747f], BANK[$25]
	db $18
