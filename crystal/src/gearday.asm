; ポケギアの 時計の 画面に 今日の できごとを 出す（金 日本版）
;
; ・時計の 画面の 下の 文（元は「ボタンを おすと ポケギアを しゅうりょうします」）を、今日の できごとに する：
;     1行め：曜日きょうだいの いる 場所（日 37ばんどうろ・月 40ばんどうろ・火 29ばんどうろ・水 いかりのみずうみ・
;            木 36ばんどうろ・金 32ばんどうろ・土 フスベシティ）
;     2行め：火・木・土 は「しぜんこうえんで むしとりたいかい」、金 は「つながりのどうくつに ラプラス」
;   （ボタンを おすと おわるのは 元と 同じ）
;
; しくみ
;   ・PokegearClock_Init の「ld hl, PokegearPressButtonText / call PrintText」（6バイト）を 新しい バンクの GearDay への
;     farcall に。GearDay は GetWeekday（0 日〜6 土）で 文を えらんで PrintText。
;
; 銀・クリスタルに 入れるとき：下の DEF を その ROM の 値に する
;   （銀の できごとは 金と 同じ。クリスタルは ラプラスが 金曜・むしとりたいかいが 火・木・土 で 同じ。
;     クリスタルの PokegearClock_Init の バイトを 確かめる）

INCLUDE "src/charmap_jp.inc"
FOR GD_N, 10
	charmap STRCAT("{d:GD_N}"), $f6 + GD_N   ; 数字
ENDR
	charmap "／", $f3
	charmap "ベ", $3d

IF !DEF(GD_HOOK)
DEF GD_HOOK            EQU $4e5f      ; バンク$24 PokegearClock_Init の ld hl, PokegearPressButtonText / call PrintText
DEF GD_HOOK_BANK       EQU $24
DEF GD_GetWeekday      EQU $351b
DEF GD_PrintText       EQU $0f30
DEF GD_BANK            EQU $45
DEF GD_ADDR            EQU $6c00
ENDC

SECTION "gearday hook", ROMX[GD_HOOK], BANK[GD_HOOK_BANK]
	ld a, BANK(GearDay)
	ld hl, GearDay
	rst $08

SECTION "gearday", ROMX[GD_ADDR], BANK[GD_BANK]
GearDay:
	call GD_GetWeekday
	ld e, a
	ld d, 0
	ld hl, .Texts
	add hl, de
	add hl, de
	ld a, [hli]
	ld h, [hl]
	ld l, a
	jp GD_PrintText

.Texts
	dw .Sun, .Mon, .Tue, .Wed, .Thu, .Fri, .Sat

.Sun db $00, "ようびきょうだい／37ばんどうろ", $57
.Mon db $00, "ようびきょうだい／40ばんどうろ", $57
.Tue db $00, "ようびきょうだい／29ばんどうろ", $4f
     db "しぜんこうえんで　むしとりたいかい", $57
.Wed db $00, "ようびきょうだい／いかりのみずうみ", $57
.Thu db $00, "ようびきょうだい／36ばんどうろ", $4f
     db "しぜんこうえんで　むしとりたいかい", $57
.Fri db $00, "ようびきょうだい／32ばんどうろ", $4f
     db "つながりのどうくつに　ラプラス", $57
.Sat db $00, "ようびきょうだい／フスベシティ", $4f
     db "しぜんこうえんで　むしとりたいかい", $57
