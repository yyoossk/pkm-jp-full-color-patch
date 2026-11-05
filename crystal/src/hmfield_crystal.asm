; ひでんわざ（話しかけて使うもの）を、覚えていなくても使えるようにする … クリスタル（日本版）用の値
; （tools/hmfield_find.py で調べた値。本体は hmfield.asm）
DEF HMFIELD_CheckPartyMove      EQU $471a
DEF HMFIELD_CheckPartyMove_BANK EQU $03
DEF HMFIELD_wCurPartyMon        EQU $d0c9
DEF HMFIELD_wPartySpecies       EQU $dc9e
DEF HMFIELD_wPartyMon1Moves     EQU $dca7
DEF HMFIELD_AddNTimes           EQU $30ca
DEF HMFIELD_BANK                EQU $70     ; なまえ・わすれる（$4000〜）と 60fps（$4800〜）の間
DEF HMFIELD_ADDR                EQU $4400

DEF HMFIELD_TM_EVENTS          EQU 1
DEF HMFIELD_wEventFlags        EQU $da65   ; クリスタル日本版
DEF HMFIELD_EVENT_TM02         EQU $5f     ; EVENT_GOT_TM02_HEADBUTT（ウバメのもり）
DEF HMFIELD_EVENT_TM08         EQU $4b     ; EVENT_GOT_TM08_ROCK_SMASH（36ばんどうろ）

INCLUDE "src/hmfield.asm"
