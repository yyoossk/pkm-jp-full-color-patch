; ぶんぷの時間帯：銀 日本版（後期版）の値（アドレスは 金と 同じ。WRAM・置き場所だけ ちがう）
DEF NT_GRASS_HOOK      EQU $6655   ; FindNest .FindGrass の inc hl ×3 / ld a, $15（5バイト）
DEF NT_FINDNEST_BANK   EQU $0a
DEF NT_FINDNEST_FREE   EQU $7fc9   ; バンク$0a の 空き
DEF NT_AREA_BANK       EQU $24
DEF NT_AREA            EQU $5da5   ; Pokedex_GetArea
DEF NT_LOOP_HOOK       EQU $5e02   ; .loop の call JoyTextDelay
DEF NT_TITLE_HOOK      EQU $5eb6   ; .PlaceString_MonsNest の さいごの call PlaceString
DEF NT_RIGHT           EQU $5e4b   ; .right（カントーを 見せる）
DEF NT_AREA_FREE1      EQU $7f1c   ; バンク$24 の 空き
DEF NT_AREA_FREE2      EQU $7fde
DEF NT_JoyTextDelay    EQU $09fd
DEF NT_PlaceString     EQU $0f46
DEF NT_ClearSprites    EQU $30bb
DEF NT_wTownMapPlayerIconLandmark EQU $cf21
DEF NT_wTownMapCursorLandmark     EQU $cf22
DEF NT_hJoyPressed     EQU $ffa9
DEF NT_hWY             EQU $ffd4
DEF NT_TITLE_COORD     EQU $c3a0   ; hlcoord 0, 0
DEF wNestTime          EQU $deed   ; 使われていない WRAM（むしよけの $deeb・$deec の 次）
DEF wNestKanto         EQU $deee
DEF NT_BANK            EQU $47
DEF NT_ADDR            EQU $4600
INCLUDE "src/nesttime.asm"
