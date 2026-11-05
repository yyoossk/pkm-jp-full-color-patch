; むしよけを もう一度 つかう … クリスタル（日本版）用の 値（本体は src/repelask.asm）
INCLUDE "src/safari/crystal_includes.asm"   ; pokecrystal の 定数・マクロ（スクリプトの 命令は pokegold の もの）
DEF RA_NO_INCLUDES EQU 1

DEF RA_HOOK            EQU $6be1   ; DoRepelStep（$25:$6bd7）の ld a, BANK(RepelWoreOffScript) / ld hl, RepelWoreOffScript
DEF RA_HOOK_BANK       EQU $25
DEF RA_WOREOFF_TEXT    EQU $76d2   ; RepelWoreOffScript（$04:$76cb）の 文
DEF RA_WOREOFF_BANK    EQU $04
DEF RA_USEREPEL        EQU $77c4   ; UseRepel（金と 同じ 17バイト）
DEF RA_USEREPEL_BANK   EQU $03
DEF RA_STILL_TEXT      EQU $77d5   ; RepelUsedEarlierIsStillInEffectText
DEF RA_USEITEMTEXT     EQU $7bb7   ; UseItemText（バンク$03）
DEF RA_PrintText       EQU $1041
DEF RA_CheckItem       EQU $2f4b
DEF RA_TossItem        EQU $2f25
DEF RA_wRepelEffect    EQU $dc67
DEF RA_wCurItem        EQU $d0c6
DEF RA_wNumItems       EQU $d885
DEF RA_wItemQuantityChange EQU $d0cc
DEF RA_wScriptVar      EQU $c2dd
DEF RA_wStringBuffer3  EQU $d071   ; ScriptCommand の 文字の バッファの 表（$09:$4000）の 1つめ
DEF RA_VARS_WRAMBANK   EQU 2       ; WRAM バンク2（$dfc0〜$dfc4 は ずかんの絵の色・とけい・ボックスの 自動切りかえ）
DEF wRepelAskLast      EQU $dfc5
DEF wRepelAskItem      EQU $dfc6
DEF RA_BANK            EQU $76     ; ボックスの 自動切りかえ・マスターボールの あと
DEF RA_ADDR            EQU $4300

INCLUDE "src/repelask.asm"
