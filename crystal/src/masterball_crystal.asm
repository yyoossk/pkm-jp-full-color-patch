; マスターボールを 売る … クリスタル（日本版）用の 値（本体は src/masterball.asm）
; GetMart は 金と 同じ 22バイト（7b fe 22 38 06 06 05 11 2e 66 c9 21 c3 64 19 19 5e 23 56 06 05 c9）
INCLUDE "src/safari/crystal_includes.asm"   ; pokecrystal の 定数・マクロ（道具の 番号は 日本版も 同じ）
DEF MB_NO_INCLUDES EQU 1

DEF MB_GETMART      EQU $5ce1    ; GetMart（バンク$05）
DEF MB_GETMART_BANK EQU $05
DEF MB_MARTS        EQU $64c3    ; Marts
DEF MB_NUM_MARTS    EQU $22      ; 店の 数（GetMart の cp の 値。金と 同じ 34）
DEF MB_MART_INDIGO  EQU $661f    ; MartIndigoPlateau（7こ。金と 同じ 品ぞろえ）
DEF MB_ITEMATTR     EQU $69fa    ; ItemAttributes（バンク$01）
DEF MB_ITEMATTR_BANK EQU $01
DEF MB_EVENT_BYTE   EQU $da65 + $7c / 8   ; EVENT_GOT_MASTER_BALL_FROM_ELM（ProfElmScript $1b:$6203 の checkevent $007c）
DEF MB_EVENT_BIT    EQU $7c % 8           ; wEventFlags は EventFlagAction（ROM0 $2e41）の ld hl, $da65
DEF MB_BANK         EQU $76      ; ボックスの 自動切りかえ（$76:$4000〜）の あと
DEF MB_ADDR         EQU $4200

INCLUDE "src/masterball.asm"
