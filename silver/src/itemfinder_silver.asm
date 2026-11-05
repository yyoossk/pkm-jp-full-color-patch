; ダウジングマシンの方向：銀 日本版（後期版）の値（ItemFinder・スクリプト・元の 文（38バイト）は 金と 同じ。WRAM・置き場所だけ ちがう）
DEF IF_HOOK            EQU $67e0      ; バンク$04 ItemFinder の farcall CheckForHiddenItems（6バイト）
DEF IF_HOOK_BANK       EQU $04
DEF IF_SCRIPT_HOOK     EQU $6815      ; .Script_FoundSomething の writetext（4c 23 68 49 90）
DEF IF_TEXT            EQU $6823      ; 元の「おッ！ ダウジングマシンが…」（$58 まで）
DEF IF_TEXT_LEN        EQU 38
DEF IF_GetMapScriptsBank EQU $2cec
DEF IF_GetFarByte      EQU $30e4
DEF IF_GetFarWord      EQU $30f8
DEF IF_EventFlagAction EQU $2eeb
DEF IF_wCurMapScriptBank EQU $d0c5
DEF IF_wCurMapBGEventsPointer EQU $d912
DEF IF_wCurMapBGEventCount EQU $d911
DEF IF_wXCoord         EQU $d9c9
DEF IF_wYCoord         EQU $d9c8
DEF IF_wStringBuffer1  EQU $cf87
DEF wIFBest            EQU $def5      ; いちばん 近い 歩数（$ff ＝ なし）
DEF wIFDX              EQU $def6      ; よこ（＋ みぎ）
DEF wIFDY              EQU $def7      ; たて（＋ した）
DEF wIFCount           EQU $def8
DEF IF_BANK            EQU $48
DEF IF_ADDR            EQU $5a00
INCLUDE "src/itemfinder.asm"
