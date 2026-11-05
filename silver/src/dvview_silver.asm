; 個体値・きそポイント：銀 日本版（後期版）の値（アドレスは 金と 同じ。wTempMon の きそポイント $d010 も 同じ。WRAM・置き場所だけ ちがう）
DEF DV_JOY_HOOK        EQU $4ce2      ; バンク$14 StatsScreen_LoadPage .joypad_loop の call GetJoypad
DEF DV_HOOK_BANK       EQU $14
DEF DV_STUB            EQU $7fd1      ; バンク$14 の 空き（7バイト）
DEF DV_BLUE_HOOK       EQU $50d8      ; LoadBluePage の farcall LoadStatsScreenPals
DEF DV_LoadBluePage    EQU $50ae
DEF DV_Pals_BANK       EQU $02
DEF DV_Pals            EQU $5241
DEF DV_GetJoypad       EQU $0934
DEF DV_PlaceString     EQU $0f46
DEF DV_PrintNum        EQU $31f9
DEF DV_hJoyPressed     EQU $ffa9
DEF DV_wTempMonDVs     EQU $d01a
DEF DV_wTempMonStatExp EQU $d010      ; HP・こうげき・ぼうぎょ・すばやさ・とくしゅ（2バイトずつ）
DEF DV_wBuffer         EQU $cf87      ; wStringBuffer1（1バイト）
DEF DV_COORD           EQU $c3a0      ; hlcoord 0, 0
DEF wDVShow            EQU $defe
DEF DV_BANK            EQU $48
DEF DV_ADDR            EQU $6c00
DEF DV_ADDR2           EQU $6f00      ; きそポイント（あとから 足した ぶん）
INCLUDE "src/dvview.asm"
