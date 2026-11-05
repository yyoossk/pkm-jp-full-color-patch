; ずかんの「ぶんぷをみる」に釣りの場所を出す … クリスタル（日本版）用の値
; （tools/fishnest_find.py で調べた値。本体は fishnest.asm）
DEF FISHNEST_HOOK              EQU $5f4a
DEF FISHNEST_HOOK_BANK         EQU $24
DEF FISHNEST_DONE_NEST         EQU $5f75
DEF FISHNEST_FindNest          EQU $600f
DEF FISHNEST_FindNest_BANK     EQU $0a
DEF FISHNEST_GetLandmarkCoords EQU $652a
DEF FISHNEST_GetLandmarkCoords_BANK EQU $24
DEF FISHNEST_wTilemap          EQU $c4a0
DEF FISHNEST_wShadowOAM        EQU $c400
DEF FISHNEST_wNamedObjectIndex EQU $d296
DEF FISHNEST_KANTO_LANDMARK    EQU $2f
DEF FISHNEST_wOBPals1          EQU $d040   ; WRAM バンク5
DEF FISHNEST_wOBPals2          EQU $d0c0
DEF FISHNEST_PALS_WRAMBANK     EQU 5
DEF FISHNEST_hCGB              EQU 0       ; カラー専用
DEF FISHNEST_hCGBPalUpdate     EQU $ffe5
DEF FISHNEST_MAPS EQUS "src/fishnest_maps_crystal.inc"
DEF FISHNEST_BANK              EQU $70     ; ひでんわざ（$4400〜）の後ろ、60fps（$4800〜）の前
DEF FISHNEST_ADDR              EQU $4480
DEF FISHNEST_EXTRA_LANDMARK    EQU $60     ; サファリゾーン（クリスタルの 地名は $00〜$5f（$5f は LANDMARK_FAST_SHIP）なので 使われていない $60。座標は safari.asm の SafariLandmarkCoords が 返す）

INCLUDE "src/fishnest.asm"
