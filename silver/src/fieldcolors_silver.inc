; フィールドのボール・回復の機械・肌の色：銀 日本版（後期版）の値（tools/fieldcolors_find.py で パッチを入れる前の ROM から調べた値。金と同じ）
; src/fieldcolors_silver.asm から src/fieldcolors.asm より前に読みこむ
DEF FC_OBJ_BANK            EQU $01
DEF FC_INIT_HOOK           EQU $5996
DEF FC_ATTR_HOOK           EQU $5a14    ; （FC_END_HOOK が ある ときは 使わない）
DEF FC_END_HOOK            EQU $5a20    ; InitSprite の さいごの ld a, c / ldh [hUsedSpriteIndex], a（79 e0 bf）
DEF FC_hUsedSpriteIndex    EQU $ffbf
DEF FC_wShadowOAM          EQU $c300
DEF FC_hCurSpriteOAMFlags  EQU $ffc4
DEF FC_BALLGFX_BANK        EQU $31
DEF FC_BALLGFX             EQU $7380
DEF FC_SPRITES_BANK        EQU $05
DEF FC_SPRITES             EQU $47b0
DEF FC_LABOBJ_BANK         EQU $13
DEF FC_LABOBJ              EQU $74bc
DEF FC_NPCPALS_BANK        EQU $02
DEF FC_NPCPALS             EQU $7834
DEF FC_HEALPAL_BANK        EQU $04
DEF FC_HEALPAL             EQU $6698
DEF FC_FREE                EQU $7fc3   ; バンク$01 の空き（$7fc3〜$7fff。$7fb0〜$7fc2 は わざの上書き防止）
DEF FC_LABGFX_BANK         EQU $3f     ; 研究所のボールの絵（64バイト）
DEF FC_LABGFX              EQU $7f00   ; バンク$3f の空き（$7e74〜$7fff。$7e00〜$7e73 は ひでんわざ）
