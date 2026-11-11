; タマゴが うまれるまでの 歩数を 半分に（金 日本版）
;
; ・タマゴの のこりの 回数（なつき度の ばしょ）は、元は 256歩 ごと（wStepCount が $80 の 歩）に 1 へる。
;   128歩 ごと（wStepCount が $00 と $80 の 歩）に へる ように した。うまれるまでの 歩数は 元の 半分。
; ・タマゴの つよさの 画面の「あと　○ほ」（src/eggsteps.asm）も 128歩 ごとで 計算する。
;
; しくみ
;   ・CountStep の「ld a, [wStepCount] / cp $80 / jr nz, .skip_egg」の cp $80 を and $7f に（2バイト）。
;
; 銀・クリスタルに 入れるとき：下の DEF を その ROM の 値に する
;   EF_HOOK・EF_HOOK_BANK  CountStep の「cp $80」（fe 80）の 場所。前が「ld a, [wStepCount]」（fa xx xx）、
;                          後ろが「jr nz」（20 xx）か 確かめる
;   src/eggsteps.asm の 計算も いっしょに かえる（銀・クリスタルの eggsteps も 同じ 計算に）

IF !DEF(EF_HOOK)
DEF EF_HOOK      EQU $6ad2      ; バンク$25 CountStep
DEF EF_HOOK_BANK EQU $25
ENDC

SECTION "eggfast", ROMX[EF_HOOK], BANK[EF_HOOK_BANK]
	and $7f
