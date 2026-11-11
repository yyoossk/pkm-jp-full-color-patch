; タマゴが みつかった ときの そだてやの おじいさん（金 日本版）
;
; ・タマゴが みつかると、おじいさんは 外に 出て まって いる（元は 庭の 中 ＝ 15, 16。そだてやの 中を
;   通らないと 話せなかった）。外の 道（10, 15。そだてやの 左の 入り口の となり）に 立つ ように した。
; ・タマゴを わたすと、となりの 入り口（11, 15）から 中に もどる。プレイヤーが 入り口（11, 15）に
;   立って いる ときは、上（10, 14）を 回って 入り口（11, 14）から もどる。
;
; しくみ（ROUTE_34 の データを 書きかえる だけ）
;   ・人の 表：おじいさん（SPRITE_GRAMPS。EVENT_DAY_CARE_MAN_ON_ROUTE_34）の y・x を 15・10 に（+4 した 値）。
;   ・DayCareManScript_Outside の「readvar VAR_FACING / ifequal RIGHT, .walk_around_player」の RIGHT を LEFT に
;     （プレイヤーが 左を むいて いる ＝ 入り口に 立って いる とき 回りこむ）。
;   ・もどる 動き：Route34MovementData_DayCareManWalksBackInside（slow_step LEFT ×2・UP）→ slow_step RIGHT、
;     ..._WalkAroundPlayer（slow_step DOWN・LEFT ×2・UP ×2）→ slow_step UP・RIGHT。
;
; 銀・クリスタルに 入れるとき：下の DEF を その ROM の 値に する（ROUTE_34 の 作りは 金銀クリスタル 同じ）
;   DO_OBJECT          おじいさんの object_event の y の 場所（元の 値 $14・x $13 ＝ 16・15）
;   DO_FACING          DayCareManScript_Outside の ifequal RIGHT の 値（03）の 場所
;   DO_MOVE1・DO_MOVE2  2つの 動きの 場所（元：0a 0a 09 47 ／ 08 0a 0a 09 09 47）
;   どれも ROUTE_34 の スクリプトの バンク（DO_BANK）

IF !DEF(DO_NO_INCLUDES)          ; クリスタルは src/daycareout_crystal.asm で 先に 読みこむ
INCLUDE "includes.asm"
ENDC

IF !DEF(DO_BANK)
DEF DO_BANK     EQU $2f
DEF DO_OBJECT   EQU $5949      ; object_event の y（元 $14）、つぎが x（元 $13）
DEF DO_FACING   EQU $52c0      ; ifequal RIGHT（元 03）
DEF DO_MOVE1    EQU $54e4
DEF DO_MOVE2    EQU $54e8
ENDC

SECTION "daycareout object", ROMX[DO_OBJECT], BANK[DO_BANK]
	db 15 + 4, 10 + 4

SECTION "daycareout facing", ROMX[DO_FACING], BANK[DO_BANK]
	db LEFT

SECTION "daycareout move1", ROMX[DO_MOVE1], BANK[DO_BANK]
	slow_step RIGHT
	step_end
	step_end
	step_end

SECTION "daycareout move2", ROMX[DO_MOVE2], BANK[DO_BANK]
	slow_step UP
	slow_step RIGHT
	step_end
	step_end
	step_end
	step_end
