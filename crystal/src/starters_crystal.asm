; カントー御三家 … クリスタル（日本版）用の 値（本体は src/starters.asm）
; マップは MapGroupPointers（$25:$4000）→ ヘッダ → MapAttributes を たどって 調べた
INCLUDE "src/safari/crystal_includes.asm"   ; pokecrystal の 定数・マクロ（スクリプトの 命令の 番号は 英語版 金銀）
DEF ST_NO_INCLUDES EQU 1

DEF ST_BANK            EQU $77        ; ハナダの 家・24ばんどうろの 写しと 本体（セレビィと 伝説の 鳥と 同じ バンク）
DEF ST_BANK_VER        EQU $78        ; クチバシティの 写し（$77 の イワヤマトンネルの 写しと 場所が かさなる）
DEF ST_ADDR            EQU $6200
DEF ST_JENNY_ADDR      EQU $6800
DEF ST_CH_NEWEV        EQU $7400
DEF ST_R24_NEWEV       EQU $7500
DEF ST_VC_NEWEV        EQU $7400
DEF ST_ATTR_BANK       EQU $25
DEF wStarterFlags      EQU $d836      ; legends と 同じ バイト（ビット 0〜3 は セレビィ・鳥）
DEF ST_wKantoBadges    EQU $d84b      ; EngineFlags（$20:$4462）の ENGINE_BOULDERBADGE（$23）の 場所
DEF ST_wScriptVar      EQU $c2dd
; ハナダの こうかんの 話の 家（7-3）
DEF ST_CH_ATTR         EQU $5db0
DEF ST_CH_SRC_BANK     EQU $1c
DEF ST_CH_START        EQU $5bf6
DEF ST_CH_EVENTS       EQU $5c68
DEF ST_CH_OBJCOUNT     EQU $5c77      ; 人の 数（4）
DEF ST_CH_END          EQU $5cac
DEF STARTER_CH_COUNT   EQU 4
DEF ST_CH_X            EQU 6
DEF ST_CH_Y            EQU 3
; 24ばんどうろ（7-15）
DEF ST_R24_ATTR        EQU $56c0
DEF ST_R24_SRC_BANK    EQU $28
DEF ST_R24_START       EQU $6bab
DEF ST_R24_EVENTS      EQU $6df4
DEF ST_R24_OBJCOUNT    EQU $6df9      ; 人の 数（1）
DEF ST_R24_END         EQU $6e07
DEF STARTER_R24_COUNT  EQU 1
DEF ST_R24_X           EQU 9
DEF ST_R24_Y           EQU 1
; クチバシティ（12-3）
DEF ST_VC_ATTR         EQU $55b8
DEF ST_VC_SRC_BANK     EQU $27
DEF ST_VC_START        EQU $6e7f      ; MapScripts（callback 1）
DEF ST_VC_EVENTS       EQU $7192
DEF ST_VC_OBJCOUNT     EQU $71f1      ; 人の 数（6）
DEF ST_VC_END          EQU $7240
DEF STARTER_VC_COUNT   EQU 6
DEF ST_VC_X            EQU 19
DEF ST_VC_Y            EQU 15
; ジュンサーの 絵
DEF ST_SPRITE_JENNY    EQU $58        ; SPRITE_OLD_LINK_RECEPTIONIST（クリスタルでも マップでは 使われて いない）
DEF ST_JENNY_SPRITETYPE EQU 2       ; STANDING_SPRITE（元の $58 と 同じ）。クリスタルは $58 が どの 町の 外の 絵の 表（OutdoorSprites）にも
                                    ; 入って いて、WALKING_SPRITE に すると VRAM の わりあてが ずれ、町で 歩く 人（おじいさん など）の
                                    ; 歩く 絵が こわれて いた。ジュンサーは 歩かないので 向きの 絵（12タイル）だけで よい
DEF ST_OWSPRITES       EQU $4727      ; OverworldSprites（バンク$05。6バイトずつ）
DEF ST_OWSPRITES_BANK  EQU $05
; クチバの 外の 絵の 表（VermilionGroupSprites $05:$457e）には もとから $58 が ある ので かえない（ST_VERMILION_SPRITES は きめない）

INCLUDE "src/starters.asm"
