; タマゴが みつかった ときの そだてやの おじいさん … クリスタル（日本版）用の 値（本体は src/daycareout.asm）
; クリスタルの ROUTE_34（11-1）の 作り（おじいさん 15, 16・DayCareManScript_Outside・2つの 動き）は 金銀と 同じ。
INCLUDE "src/safari/crystal_includes.asm"
DEF DO_NO_INCLUDES EQU 1

DEF DO_BANK     EQU $1c        ; ROUTE_34 の スクリプトの バンク
DEF DO_OBJECT   EQU $47ba      ; 7人め（SPRITE_GRAMPS、EVENT_DAY_CARE_MAN_ON_ROUTE_34 $06e6）の y（元 $14）、つぎが x（元 $13）
DEF DO_FACING   EQU $404e      ; DayCareManScript_Outside（$403d）の「readvar VAR_FACING / ifequal RIGHT」の RIGHT（元 03）
DEF DO_MOVE1    EQU $4333      ; ..._WalksBackInside（0a 0a 09 47）
DEF DO_MOVE2    EQU $4337      ; ..._WalkAroundPlayer（08 0a 0a 09 09 47）

INCLUDE "src/daycareout.asm"
