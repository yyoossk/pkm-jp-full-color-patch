; タマゴの つよさの 画面に、うまれるまでの 歩数を 出す（金 日本版）
;
; ・タマゴの つよさの 画面（「なにが うまれて くるのかな？」など）の 下に「あと　１２３４ほ」と 出す。
;   手持ちで あるいた とき、あと 何歩で うまれるか（タマゴが いくつか あって 同じ 歩で うまれる ときは、
;   さきに うまれる タマゴの つぎの 回に なるので すこし ずれる）。
; ・タマゴの のこりの 回数（なつき度の ばしょ。wTempMonHappiness）は 128歩 ごとに 1 へる
;   （src/eggfast.asm。wStepCount が $00 か $80 に なった 歩。0 に なった 歩で うまれる）。なので
;     歩数 ＝ つぎに へる までの 歩数（$80 − (wStepCount and $7f)）＋（のこりの 回数 − 1）× 128
;   （元の 256歩 ごとの ときは $80 − wStepCount〔0 なら 256〕＋（のこり − 1）× 256 だった）
;
; しくみ
;   ・EggStatsScreen の「call WaitBGMap / ld a, 1 / ldh [hBGMapMode], a」（7バイト）を 新しい バンクの EggSteps への
;     farcall に。EggSteps は 歩数を かいて から 元と 同じ ことを する。
;
; 銀・クリスタルに 入れるとき：下の DEF を その ROM の 値に する
;   （クリスタルの EggStatsScreen は 文の 場所が ちがうか 確かめる。歩数の 計算は 金銀クリスタル 同じ）

INCLUDE "src/charmap_jp.inc"

IF !DEF(ES_HOOK)
DEF ES_HOOK            EQU $51bf      ; バンク$14 EggStatsScreen .picked の あと の call WaitBGMap / ld a, 1 / ldh [hBGMapMode], a
DEF ES_HOOK_BANK       EQU $14
DEF ES_WaitBGMap       EQU $33ae
DEF ES_PlaceString     EQU $0f46
DEF ES_PrintNum        EQU $31f9
DEF ES_wTempMonHappiness EQU $d020
DEF ES_wStepCount      EQU $d983
DEF ES_wBuffer         EQU $cf87      ; wStringBuffer1（2バイト）
DEF ES_hBGMapMode      EQU $ffd6
DEF ES_COORD           EQU $c3a0 + 15 * 20 + 9   ; hlcoord 9, 15
DEF ES_BANK            EQU $45
DEF ES_ADDR            EQU $6d00
ENDC

SECTION "eggsteps hook", ROMX[ES_HOOK], BANK[ES_HOOK_BANK]
	ld a, BANK(EggSteps)
	ld hl, EggSteps
	rst $08
	nop

SECTION "eggsteps", ROMX[ES_ADDR], BANK[ES_BANK]
EggSteps:
	ld a, [ES_wTempMonHappiness]
	and a
	jr z, .done
	dec a
	ld e, 0                           ; de = （のこり − 1）× 128（src/eggfast.asm で 128歩 ごとに へる）
	srl a
	rr e
	ld d, a
	ld a, [ES_wStepCount]
	and $7f
	ld b, a
	ld a, $80
	sub b                             ; つぎに へる までの 歩数（1〜128）
	ld l, a
	ld h, 0
	add hl, de
	ld a, h
	ld [ES_wBuffer], a
	ld a, l
	ld [ES_wBuffer + 1], a
	ld hl, ES_COORD
	ld de, .Head
	call ES_PlaceString
	ld hl, ES_COORD + 3
	ld de, ES_wBuffer
	ld bc, $4205                      ; 2バイト・5けた・左づめ
	call ES_PrintNum
	ld de, .Tail
	call ES_PlaceString
.done
	call ES_WaitBGMap
	ld a, 1
	ldh [ES_hBGMapMode], a
	ret

.Head db "あと　@"
.Tail db "ほ@"
