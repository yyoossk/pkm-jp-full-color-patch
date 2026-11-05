; ボールの印を赤白に（src/redballs.asm）の クリスタル日本版の値
; tools/redballs_find.py で出した値 ＋ 空きの場所 ＋ ホームの処理（クリスタル日本版）
DEF RB_BALLGFX_BANK        EQU $0b
DEF RB_BALLGFX             EQU $529c
DEF RB_HUD_ATTR            EQU $527c
DEF RB_HUD_FREE            EQU $7f00    ; バンク$0b の空き（10バイト）
DEF RB_CAUGHT_BANK         EQU $3e
DEF RB_CAUGHT_GFX          EQU $4b90
DEF RB_BATTLEPAL_BANK      EQU $02
DEF RB_BATTLEPAL_HOOK      EQU $4e73
DEF RB_BattleObjectPals    EQU $5759
DEF RB_ApplyAttrmap        EQU $5670
DEF RB_DEX_BANK            EQU $10
DEF RB_DEX_LOAD1           EQU $44f9
DEF RB_DEX_LOAD2           EQU $5214
DEF RB_PokedexLZ           EQU $5242
DEF RB_DEX_TILES           EQU 49
DEF RB_wOBPals1            EQU $d040
DEF RB_wBGPals1            EQU $d000
DEF RB_wAttrmap            EQU $cdcd
DEF RB_PALS_WRAMBANK       EQU 5
DEF RB_BATTLEPAL_LEN       EQU 18
DEF RB_BANK                EQU $70      ; 新しいバンクの空き
DEF RB_ADDR                EQU $5e00
; ホーム（クリスタル日本版）
DEF RB_FarCopyBytes        EQU $0e77
DEF RB_CopyBytes           EQU $2ff2
DEF RB_FarDecompress       EQU $0b2a
DEF RB_DecompressRequest2bpp EQU $0e5d
DEF RB_Request2bpp         EQU $0ea4
