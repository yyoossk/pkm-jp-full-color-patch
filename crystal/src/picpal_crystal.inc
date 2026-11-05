; ずかんとパソコンの絵をカラフルに（src/picpal.asm）の クリスタル日本版の値
; tools/picpal_find.py で出した値 ＋ 空きの場所
DEF PP_DEX_BANK                            EQU $10
DEF PP_DEX_HOOK                            EQU $516d
DEF PP_Pokedex_GetSelectedMon              EQU $4a7d
DEF PP_Pokedex_CheckSeen                   EQU $4a9c
DEF PP_PC_BANK                             EQU $38
DEF PP_PC_HOOK                             EQU $730d
DEF PP_wBillsPC_MonHasMail                 EQU $cb32
DEF PP_CGB_BANK                            EQU $02
DEF PP_DEX_FF                              EQU $4f82
DEF PP_PC_FF                               EQU $4fc6
DEF PP_PokedexQuestionMarkPalette          EQU $4fac
DEF PP_BillsPCOrangePalette                EQU $4ff3
DEF PP_LoadHLPaletteIntoDE                 EQU $55ed
DEF PP_LoadPalette_White_Col1_Col2_Black   EQU $5600
DEF PP_GetMonPalettePointer                EQU $5732
DEF PP_GetPlayerOrMonPalettePointer        EQU $5708
DEF PP_wTempSpecies                        EQU $d296
DEF PP_wCurPartySpecies                    EQU $d0c8
DEF PP_wTempMonDVs                         EQU $d0e3
DEF PP_wBGPals1                            EQU $d000
DEF PP_wBGPals2                            EQU $d080
DEF PP_PALS_WRAMBANK                       EQU 5
DEF PP_hCGBPalUpdate                       EQU $ffe5
; 空き
DEF PP_CGB_FREE                            EQU $7800    ; バンク$02 の空き
DEF PP_HOME_DEX                            EQU $00c0    ; ホームの空き（$00c0〜$00ff。$0070〜 は 投げるボールの色）
DEF PP_HOME_PC                             EQU $00f0
DEF PP_VARS_WRAMBANK                       EQU 2        ; WRAM バンク2（$df00〜$dfb0 は 60fps・手持ちの見た目が使う）
DEF PP_wDexPicSpecies                      EQU $dfc0
DEF PP_wPCPicSpecies                       EQU $dfc1
