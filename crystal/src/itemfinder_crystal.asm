; ダウジングマシンの方向 … クリスタル（日本版）用の 値（本体は src/itemfinder.asm）
; ItemFinder（$04:$6433）・CheckForHiddenItems（$2e:$4152）は 金と 同じ 作り
INCLUDE "src/safari/crystal_includes.asm"   ; pokecrystal の 定数・マクロ（スクリプトの 命令の 番号は 英語版 金銀）
DEF IF_NO_INCLUDES EQU 1

DEF IF_HOOK            EQU $6433      ; バンク$04 ItemFinder の farcall CheckForHiddenItems（ld a, $2e / ld hl, $4152 / rst $08）
DEF IF_HOOK_BANK       EQU $04
DEF IF_SCRIPT_HOOK     EQU $6468      ; .Script_FoundSomething（$6460：refreshmap / special / callasm）の writetext（4c 76 64 49 90）
DEF IF_TEXT            EQU $6476      ; 元の「おッ！ ダウジングマシンが…」（$58 まで）
DEF IF_TEXT_LEN        EQU 38
DEF IF_GetMapScriptsBank EQU $2c29
DEF IF_GetFarByte      EQU $3019
DEF IF_GetFarWord      EQU $3029
DEF IF_EventFlagAction EQU $2e41
DEF IF_wCurMapScriptBank EQU $d21b    ; CheckForHiddenItems が 使う 所
DEF IF_wCurMapBGEventsPointer EQU $dbc8
DEF IF_wCurMapBGEventCount EQU $dbc7
DEF IF_wXCoord         EQU $dc7e
DEF IF_wYCoord         EQU $dc7d
DEF IF_wStringBuffer1  EQU $d05b
DEF wIFBest            EQU $d066      ; wStringBuffer2（しらべる あいだ だけ）
DEF wIFCount           EQU $d067
DEF wIFDX              EQU $d838      ; wTimeOfDayPal の あとの 使われていない バイト（スクリプトまで のこす）
DEF wIFDY              EQU $d83c      ; wCurTimeOfDay の あとの 使われていない バイト
DEF IF_BANK            EQU $76
DEF IF_ADDR            EQU $6400

INCLUDE "src/itemfinder.asm"
