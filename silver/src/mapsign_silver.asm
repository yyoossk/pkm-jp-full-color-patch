; 場所の名前の札：銀 日本版（後期版）の値（アドレスは 金と 同じ。WRAM・置き場所だけ ちがう）
DEF MS_SETUP_ENTRY     EQU $5501      ; バンク$05 MapSetupCommands の LoadWildMonData の 行（db バンク / dw アドレス）
DEF MS_SETUP_BANK      EQU $05
DEF MS_LoadWildMonData_BANK EQU $0a
DEF MS_LoadWildMonData EQU $65ef
DEF MS_OW_BANK         EQU $25
DEF MS_HandleMapObjects EQU $6716    ; farcall HandleNPCStep / farcall _HandlePlayerStep / call _CheckObjectEnteringVisibleRange / ret（16バイト）
DEF MS_EVENT_CALL      EQU $6792      ; CheckPlayerState の call DoPlayerEvent
DEF MS_DoPlayerEvent   EQU $6b1e
DEF MS_STUB            EQU $7fd8      ; バンク$25 の 空き（9バイト）
DEF MS_HandleNPCStep_BANK EQU $01
DEF MS_HandleNPCStep   EQU $56fd
DEF MS_HandlePlayerStep_BANK EQU $03
DEF MS_HandlePlayerStep EQU $576e
DEF MS_CheckObjectEnteringVisibleRange EQU $6751   ; バンク MS_OW_BANK
DEF MS_GetWorldMapLocation EQU $2d44
DEF MS_GetLandmarkName_BANK EQU $24
DEF MS_GetLandmarkName EQU $6498
DEF MS_PlaceString     EQU $0f46
DEF MS_FONT_BANK       EQU $3e
DEF MS_FONT            EQU $42f2      ; 文字 $80〜$ff（1bpp）
DEF MS_GetFarByte      EQU $30e4
DEF MS_wMapGroup       EQU $d9c6
DEF MS_wMapNumber      EQU $d9c7
DEF MS_wEnvironment    EQU $d075
DEF MS_wScriptRunning  EQU $d151
DEF MS_wStringBuffer1  EQU $cf87
DEF MS_hWX             EQU $ffd3
DEF MS_hMapEntryMethod EQU $ffa1
DEF MS_hWY             EQU $ffd4
DEF MS_GATE            EQU 6
DEF wMSPrev            EQU $defb      ; 前の ランドマーク
DEF wMSTimer           EQU $defc      ; のこりの フレーム
DEF wMSLast            EQU $defd      ; 前に 見た hVBlankCounter
DEF MS_hVBlankCounter  EQU $ff9d
DEF MS_BUF             EQU $d6e5      ; 2行 × 20（濁点の 行・名前の 行）
DEF MS_TIME            EQU 118        ; クリスタルと 同じ（59回 × 2フレーム）
DEF wMSState           EQU $def2      ; 0 なし・1 まち・2 つぎで 出す・3 出て いる（使われていない WRAM）
DEF MS_hCGB            EQU $ffe8
DEF MS_wBGPals2_7      EQU $c2b8      ; wBGPals2（$c280）の パレット7
DEF MS_BANK            EQU $48
DEF MS_ADDR            EQU $4600      ; 大きく なったので $6800 から うつした
INCLUDE "src/mapsign.asm"
