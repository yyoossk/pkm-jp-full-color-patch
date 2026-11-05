; 2列のメニュー：銀 日本版（後期版）の値（2DMenu の call _2DMenuInterpretJoypad $09:$4166・空き $09:$7fd9・wMonSubmenuCount $d0c5 は 金と 同じ。置き場所だけ ちがう）
DEF MF_HOOK            EQU $4166      ; バンク$09 の call _2DMenuInterpretJoypad
DEF MF_BANK9           EQU $09
DEF MF_Interpret       EQU $419c      ; _2DMenuInterpretJoypad
DEF MF_STUB            EQU $7fd9      ; バンク$09 の 空き（12バイト）
DEF MF_w2DMenuNumRows  EQU $cf0e
DEF MF_w2DMenuNumCols  EQU $cf0f
DEF MF_w2DMenuCursorOffsets EQU $cf12
DEF MF_wMenuCursorY    EQU $cf14
DEF MF_wMenuCursorX    EQU $cf15
DEF MF_wMonSubmenuCount EQU $d0c5
DEF MF_BANK            EQU $48
DEF MF_ADDR            EQU $7200
INCLUDE "src/monmenu_fix.asm"
