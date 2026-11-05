; 倒した伝説がもどる：銀 日本版（後期版）の値（HallOfFame の farcall SaveGameData $21:$65f1（バグ修正の あとも 同じ バイト）・
; イベント $317・$318・$7b（銀の スクリプトの checkevent / setevent で 確かめた）・wRoamMon1 $dc90・InitRoamMons の 値は 金と 同じ。置き場所だけ ちがう）
DEF LR_HOOK            EQU $65f1      ; バンク$21 HallOfFame の farcall SaveGameData
DEF LR_HOOK_BANK       EQU $21
DEF LR_Save_BANK       EQU $05
DEF LR_Save            EQU $4bf5      ; SaveGameData
DEF LR_wEventFlags     EQU $d7aa
DEF LR_wPokedexCaught  EQU $db78
DEF LR_wRoamMon1       EQU $dc90      ; 7バイト ずつ（しゅるい・レベル・グループ・マップ・HP・個体値 2）
DEF EVENT_FOUGHT_HO_OH_J EQU $317
DEF EVENT_FOUGHT_LUGIA_J EQU $318
DEF EVENT_RELEASED_THE_BEASTS_J EQU $7b
DEF LR_BANK            EQU $48
DEF LR_ADDR            EQU $7100
INCLUDE "src/legendrevive.asm"
