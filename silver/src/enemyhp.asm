; 戦闘で、相手の HP を 数字でも 出す（金 日本版）
;
; ・相手の HP バーの 下の 線の 所に「 35／ 48」のように 出す（自分の HP と 同じ 3けた）。
;   HP が へる・ふえる ときは、自分の HP と 同じ ように 数字も うごく。野生・トレーナー どちらでも 出る。
;
; しくみ
;   ・DrawEnemyHUD の「farcall DrawEnemyHUDBorder」（6バイト）を 新しい バンクの EnemyHP_Border への farcall に。
;     EnemyHP_Border は DrawEnemyHUDBorder を 呼んで から、hlcoord 3, 3 に 今の HP・／・さいだいの HP を かく。
;   ・HP バーの アニメの HPBarAnim_UpdateHPRemaining は 相手（wWhichHPBar ＝ 0）の とき 何も しないので、
;     「and a / ret z / cp 1 / jr z, .load_15」（6バイト）を「cp 2 / jr nz, .load_15 / nop / nop」に かえて、
;     相手の ときも 自分と 同じ（HP バーの 場所 ＋ 21 ＝ 1行 下・1ます 右）に 今の HP を かくように する。
;
; 銀・クリスタルに 入れるとき：下の DEF を その ROM の 値に する
;   （クリスタルは HPBarAnim_UpdateHPRemaining の バイトが 同じか 確かめる。英語版の 金銀クリスタルは
;     wWhichHPBar 2（手持ちの 画面）の ずれが 22）

IF !DEF(EH_HUD_HOOK)
DEF EH_HUD_HOOK        EQU $5eb1      ; バンク$0f DrawEnemyHUD の farcall DrawEnemyHUDBorder
DEF EH_HUD_BANK        EQU $0f
DEF EH_Border_BANK     EQU $0b
DEF EH_Border          EQU $51a9
DEF EH_ANIM_HOOK       EQU $5a57      ; バンク$03 HPBarAnim_UpdateHPRemaining の and a / ret z / cp 1 / jr z, .load_15
DEF EH_ANIM_BANK       EQU $03
DEF EH_PrintNum        EQU $31f9
DEF EH_wEnemyMonHP     EQU $d0f1
DEF EH_wEnemyMonMaxHP  EQU $d0f3
DEF EH_COORD           EQU $c3a0 + 3 * 20 + 3   ; hlcoord 3, 3
DEF EH_BANK            EQU $45
DEF EH_ADDR            EQU $7400
ENDC

SECTION "enemyhp hud hook", ROMX[EH_HUD_HOOK], BANK[EH_HUD_BANK]
	ld a, BANK(EnemyHP_Border)
	ld hl, EnemyHP_Border
	rst $08

SECTION "enemyhp anim hook", ROMX[EH_ANIM_HOOK], BANK[EH_ANIM_BANK]
	cp 2                              ; 手持ちの 画面（2）だけ ずれ が ちがう
	jr nz, @ + 2 + 7                  ; .load_15（自分・相手）
	nop
	nop

SECTION "enemyhp", ROMX[EH_ADDR], BANK[EH_BANK]
EnemyHP_Border:
	ld a, EH_Border_BANK
	ld hl, EH_Border
	rst $08
	ld hl, EH_COORD
	ld a, $7f
	ld [hli], a
	ld [hli], a
	ld [hli], a
	ld [hl], $f3                      ; ／
	inc hl
	ld [hli], a
	ld [hli], a
	ld [hl], a
	ld hl, EH_COORD
	ld de, EH_wEnemyMonHP
	ld bc, $0203                      ; 2バイト・3けた
	call EH_PrintNum
	ld hl, EH_COORD + 4
	ld de, EH_wEnemyMonMaxHP
	ld bc, $0203
	jp EH_PrintNum
