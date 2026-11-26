; ポケモンセンターの 回復：銀 日本版（後期版）の値（src/pcheal.asm より前に読みこむ）
; ジョーイさんの スクリプト（$36:$408a）・special の 番号・wOptions2・wScriptVar は 金と 同じ。置き場所だけ ちがう
DEF PH_SCRIPT_BANK     EQU $36
DEF PH_HEAL            EQU $40bc      ; 8a 14 75 fe 02（pause 20 / turnobject LAST_TALKED, LEFT）
DEF PH_HEAL_RET        EQU $40d8      ; checkphonecall（9c）
DEF PH_END             EQU $40f8      ; 8a 0a 53 49 90（pause 10 / waitbutton / closetext / end）
DEF PH_END_PKRS        EQU $4100      ; 53 49 36（waitbutton / closetext / setflag）
DEF PH_SP_HEALPARTY    EQU $1b
DEF PH_SP_HEALANIM     EQU $3d
DEF PH_SP_RESTARTMUSIC EQU $3c
DEF PH_wOptions2       EQU $d1b0
DEF PH_wScriptVar      EQU $d165
DEF PH_BANK            EQU $5e        ; わざマシンの 店と 同じ 空きの バンク（金は $4b）
DEF PH_ADDR            EQU $4400
INCLUDE "src/pcheal.asm"
