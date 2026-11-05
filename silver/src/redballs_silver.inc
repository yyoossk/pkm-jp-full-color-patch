; ボールの印を赤白に：銀 日本版（後期版）の値（tools/redballs_find.py で調べた値）
; src/redballs.asm より前に読みこむ（src/redballs_silver.asm から INCLUDE）
DEF RB_BALLGFX_BANK      EQU $0b
DEF RB_BALLGFX           EQU $5255
DEF RB_HUD_ATTR          EQU $5236
DEF RB_HUD_FREE          EQU $7c80    ; バンク $0b の空き（10バイト）
DEF RB_CAUGHT_BANK       EQU $3e
DEF RB_CAUGHT_GFX        EQU $4c82
DEF RB_BATTLEPAL_BANK    EQU $02
DEF RB_BATTLEPAL_HOOK    EQU $5429
DEF RB_BattleObjectPals  EQU $5b9f
DEF RB_ApplyAttrmap      EQU $5acb
DEF RB_DEX_BANK          EQU $10
DEF RB_DEX_LOAD1         EQU $44f9
DEF RB_DEX_LOAD2         EQU $5217
DEF RB_PokedexLZ         EQU $5245
DEF RB_DEX_TILES         EQU 49
DEF RB_wOBPals1          EQU $c240
DEF RB_wBGPals1          EQU $c200
DEF RB_wAttrmap          EQU $cccd
DEF RB_BANK              EQU $3f      ; バンク $3f の空き（$6f29-$78ff）。statsmove（$6e00-$6f28）のうしろ
DEF RB_ADDR              EQU $6f40
