; 倒した伝説がもどる … クリスタル（日本版）用の 値（本体は src/legendrevive.asm）
; HallOfFame（$21:$65e0）の farcall SaveGameData（$21:$6608：ld a, $05 / ld hl, $4b79 / rst $08）。バグ修正は ここを かえて いない。
; イベントの 番号は 英語版と 同じ（スクリプトの setevent で 確かめた：$1a:$5f5a ホウオウ・$1c:$4acc ルギア・$17:$49ba スイクン・$17:$5599 にげだした）。
; クリスタルは スイクンが あるきまわらない：あるきまわるのは ライコウ・エンテイ の 2ひき（wRoamMon1・2）、スイクンは EVENT_FOUGHT_SUICUNE を けし、
; スズのとう 1かいの scene も 0 に もどす（戦った あと 1 に なって いて、そのままだと 立って いる だけで 戦えない）。
DEF LR_HOOK            EQU $6608
DEF LR_HOOK_BANK       EQU $21
DEF LR_Save_BANK       EQU $05
DEF LR_Save            EQU $4b79      ; SaveGameData
DEF LR_wEventFlags     EQU $da65
DEF LR_wPokedexCaught  EQU $de2d
DEF LR_wRoamMon1       EQU $df45      ; 7バイト ずつ（InitRoamMons $0a:$6290）
DEF EVENT_FOUGHT_HO_OH_J EQU $317
DEF EVENT_FOUGHT_LUGIA_J EQU $318
DEF EVENT_FOUGHT_SUICUNE_J EQU $335
DEF EVENT_RELEASED_THE_BEASTS_J EQU $7b
DEF LR_wTinTower1FSceneID EQU $d999 ; MapScenes（$13:$50e2 の 3-4）。スズのとう 1かいの scene を 0（スイクンと 戦う）に もどす
DEF LR_NUM_ROAMERS     EQU 2
DEF LR_RAIKOU_GROUP    EQU $02        ; 42ばんどうろ（InitRoamMons と 同じ）
DEF LR_RAIKOU_MAP      EQU $05
DEF LR_ENTEI_GROUP     EQU $0a        ; 37ばんどうろ
DEF LR_ENTEI_MAP       EQU $04
DEF LR_SUICUNE_GROUP   EQU 0          ; （使わない）
DEF LR_SUICUNE_MAP     EQU 0
DEF LR_BANK            EQU $76
DEF LR_ADDR            EQU $7300

INCLUDE "src/legendrevive.asm"
