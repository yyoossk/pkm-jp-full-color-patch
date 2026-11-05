; ガンテツのボールをまとめて作る：銀 日本版（後期版）の値（アドレス・wKurtCount は 金と 同じ。置き場所だけ ちがう）
DEF KB_SELECT        EQU $45d1        ; バンク$03 SelectApricornForKurt（28バイト）
DEF KB_SELECT_BANK   EQU $03
DEF KB_GIVEITEM      EQU $763f + 16   ; バンク$25 Script_giveitem の ld [wItemQuantityChange], a
DEF KB_GIVE_BANK     EQU $25
DEF KB_GIVE_FREE     EQU $7fc0        ; バンク$25 の 空き
DEF KB_MAP_GROUP     EQU 8            ; KURTS_HOUSE
DEF KB_MAP_NUMBER    EQU 4
DEF KB_Kurt_SelectApricorn EQU $4ba1
DEF KB_Kurt_SelectApricorn_BANK EQU $09
DEF KB_TossItem      EQU $3025
DEF KB_wScriptVar    EQU $d165
DEF KB_wCurItem      EQU $cffc
DEF KB_wItemQuantityChange EQU $d003
DEF KB_wNumItems     EQU $d5aa
DEF KB_wMapGroup     EQU $d9c6
DEF KB_wMapNumber    EQU $d9c7
DEF wKurtCount       EQU $d7a0        ; wEventFlags（$d7aa）の 前の 空き（レポートに 書かれる）
DEF KB_BANK          EQU $48
DEF KB_ADDR          EQU $5400
INCLUDE "src/kurtbulk.asm"
