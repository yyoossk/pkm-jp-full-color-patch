; フィールドのボール・回復の機械・肌の色（src/fieldcolors.asm）の クリスタル日本版の値
; tools/fieldcolors_find.py（パッチを入れる前の ROM）で出した値 ＋ 空きの場所
DEF FC_OBJ_BANK            EQU $01
DEF FC_INIT_HOOK           EQU $5a38
DEF FC_ATTR_HOOK           EQU $5aaf
DEF FC_hCurSpriteOAMFlags  EQU $ffc2
DEF FC_FREE                EQU $7f00    ; バンク$01 の空き 50バイト（$7ea0〜$7eb2 は わざの上書き防止）
DEF FC_BALLGFX_BANK        EQU $31
DEF FC_BALLGFX             EQU $7380
DEF FC_SPRITES_BANK        EQU $05
DEF FC_SPRITES             EQU $4727
DEF FC_LABOBJ_BANK         EQU $1b
DEF FC_LABOBJ              EQU $7313
DEF FC_LABGFX_BANK         EQU $70      ; 研究所のボールの絵 64バイト（新しいバンクの空き）
DEF FC_LABGFX              EQU $6000
DEF FC_NPCPALS_BANK        EQU $02
DEF FC_NPCPALS             EQU $7426
DEF FC_HEALPAL_BANK        EQU $04
DEF FC_HEALPAL             EQU $62db
