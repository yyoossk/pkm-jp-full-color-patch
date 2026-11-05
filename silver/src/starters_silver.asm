; カントー御三家：銀 日本版（後期版）の値（3つの マップの 場所・人の 数・OverworldSprites・VermilionGroupSprites の SPRITE_BIKER は 銀の バイトで 確かめて 金と 同じ。置き場所だけ ちがう）
DEF ST_BANK_VER        EQU $47        ; クチバシティの 写し（$6df6〜・$7c00。$4000〜$4b1d は ほかの 機能）
DEF ST_BANK            EQU $4a        ; ハナダの 家・24ばんどうろの 写しと 本体（銀は $48 を 技教えの人などが 使う）
DEF ST_ADDR            EQU $4000
DEF ST_ATTR_BANK       EQU $25
DEF wStarterFlags      EQU $d7a1      ; legends.asm と 同じ バイト（ビット 0〜3 は セレビィ・鳥）
DEF ST_wKantoBadges    EQU $d570
DEF ST_wScriptVar      EQU $d165
; ハナダの こうかんの 話の 家（CERULEAN_TRADE_SPEECH_HOUSE）
DEF ST_CH_ATTR         EQU $5d7d
DEF ST_CH_SRC_BANK     EQU $28
DEF ST_CH_START        EQU $6efe
DEF ST_CH_EVENTS       EQU $6f70
DEF ST_CH_OBJCOUNT     EQU $6f7f      ; 人の 数（4）
DEF ST_CH_END          EQU $6fb4
DEF ST_CH_X            EQU 6
DEF ST_CH_Y            EQU 3
; 24ばんどうろ（ROUTE_24）
DEF ST_R24_ATTR        EQU $56f9
DEF ST_R24_SRC_BANK    EQU $35
DEF ST_R24_START       EQU $779c
DEF ST_R24_EVENTS      EQU $79e5
DEF ST_R24_OBJCOUNT    EQU $79ea      ; 人の 数（1）
DEF ST_R24_END         EQU $79f8
DEF ST_R24_X           EQU 9
DEF ST_R24_Y           EQU 1
; クチバシティ（VERMILION_CITY）
DEF ST_VC_ATTR         EQU $55f1
DEF ST_VC_SRC_BANK     EQU $35
DEF ST_VC_START        EQU $6df6
DEF ST_VC_EVENTS       EQU $7109
DEF ST_VC_OBJCOUNT     EQU $7168      ; 人の 数（6）
DEF ST_VC_END          EQU $71b7
DEF ST_VC_X            EQU 19
DEF ST_VC_Y            EQU 15
; ジュンサーの 絵
DEF ST_SPRITE_JENNY    EQU $58        ; SPRITE_OLD_LINK_RECEPTIONIST（金では 使われて いない）
DEF ST_OWSPRITES       EQU $47b0      ; OverworldSprites（バンク$05。6バイトずつ）
DEF ST_VERMILION_SPRITES EQU $46df    ; VermilionGroupSprites（バンク$05。9番めが SPRITE_BIKER）
INCLUDE "src/starters.asm"
