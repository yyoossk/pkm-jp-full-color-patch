; ずかんとパソコンの絵をカラフルに：銀 日本版（後期版）の値
; tools/picpal_find.py で調べた値（金と同じ）＋ 銀で決めた空き。src/picpal_silver.asm から src/picpal.asm より前に読みこむ
DEF PP_DEX_BANK                            EQU $10
DEF PP_DEX_HOOK                            EQU $5170
DEF PP_Pokedex_GetSelectedMon              EQU $4a7d
DEF PP_Pokedex_CheckSeen                   EQU $4a9c
DEF PP_PC_BANK                             EQU $38
DEF PP_PC_HOOK                             EQU $7305
DEF PP_wBillsPC_MonHasMail                 EQU $ca32
DEF PP_CGB_BANK                            EQU $02
DEF PP_DEX_FF                              EQU $54f2
DEF PP_PC_FF                               EQU $5536
DEF PP_PokedexQuestionMarkPalette          EQU $551c
DEF PP_BillsPCOrangePalette                EQU $5563
DEF PP_LoadHLPaletteIntoDE                 EQU $5a68
DEF PP_LoadPalette_White_Col1_Col2_Black   EQU $5a71
DEF PP_GetMonPalettePointer                EQU $5b7a
DEF PP_GetPlayerOrMonPalettePointer        EQU $5b61
DEF PP_wTempSpecies                        EQU $d143
DEF PP_wCurPartySpecies                    EQU $cffe
DEF PP_wTempMonDVs                         EQU $d01a
DEF PP_wBGPals1                            EQU $c200
DEF PP_wBGPals2                            EQU $c280
DEF PP_hCGBPalUpdate                       EQU $ffe7   ; 金銀（クリスタルは $ffe5）
DEF PP_CGB_FREE                            EQU $7e40   ; バンク$02 の空き（$7bc0〜$7fff。$7c60〜$7e37 は サファリの 色。大きく なったので $7c00 から うつした）
DEF PP_HOME_DEX                            EQU $3fe0   ; ホームの空き（$3fdf〜$3fff。再戦のセリフのバンクは $3f8a へうつした）
DEF PP_HOME_PC                             EQU $3f94   ; ホームの空き（$3f8a〜$3f93 は 再戦、$3fa0〜 は 60fps）
DEF PP_wDexPicSpecies                      EQU $de37   ; 使われていない WRAM（相手の手持ちのニックネームのうしろ。$de38〜$de3a はバグ修正）
DEF PP_wPCPicSpecies                       EQU $de3f   ; 使われていない WRAM（$de3b〜$de3e は つよさをみる・手持ちの見た目、$de40〜 は 60fps）
