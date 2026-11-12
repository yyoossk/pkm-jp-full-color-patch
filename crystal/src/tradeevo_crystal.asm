; 通信交換で 進化する ポケモンを 交換 しなくても 進化させる … クリスタル（日本版）用（251匹そろう版 src/edition251_crystal.asm の その 部分だけ）
;  ・交換で 進化する 10ぴきは Lv37 で 進化する：ユンゲラー → フーディン、ゴーリキー → カイリキー、ゴローン → ゴローニャ、ゴースト → ゲンガー、
;    ニョロゾ → ニョロトノ、イワーク → ハガネール、シードラ → キングドラ、ストライク → ハッサム、ポリゴン → ポリゴン2（どうぐは いらない）
;  ・ヤドンは Lv37 で ヤドラン。おうじゃのしるしを もたせて Lv37 いじょうで レベルが あがると ヤドキング（しるしは なくなる）
;  ・9ひきは 交換では もう 進化しない（表を レベルに かえた ため）。ヤドキングは しるしを もたせて 交換しても 進化する
;  ・251匹そろう版と いっしょには 組まない（同じ 物が edition251 に 入って いる）


DEF ED_wLinkMode       EQU $c2dc
DEF ED_wForceEvolution EQU $d21a
DEF ED_wTempMonLevel   EQU $d0ed
DEF ED_TRADE_LEVEL     EQU 37

; ---- しんか ----------------------------------------------------------------
; EVOLVE_TRADE（03, どうぐ, しゅるい） → EVOLVE_LEVEL（01, 37, しゅるい）
MACRO ed_evo_level
SECTION "tradeevo evo \1", ROMX[\1], BANK[$10]
	db $01, ED_TRADE_LEVEL
ENDM
	ed_evo_level $6e2f   ; ニョロゾ → ニョロトノ
	ed_evo_level $6e5d   ; ユンゲラー → フーディン
	ed_evo_level $6ea5   ; ゴーリキー → カイリキー
	ed_evo_level $6f5e   ; ゴローン → ゴローニャ
	ed_evo_level $70f6   ; ゴースト → ゲンガー
	ed_evo_level $7125   ; イワーク → ハガネール
	ed_evo_level $7317   ; シードラ → キングドラ
	ed_evo_level $739a   ; ストライク → ハッサム
	ed_evo_level $74bd   ; ポリゴン → ポリゴン2

; ヤドン： こうかん（おうじゃのしるし）→ ヤドキング を 先に、Lv37 → ヤドラン を あとに
SECTION "tradeevo evo slowpoke", ROMX[$6fc6], BANK[$10]
	db $03, $52, $c7     ; おうじゃのしるし → ヤドキング
	db $01, ED_TRADE_LEVEL, $50   ; Lv37 → ヤドラン

; EvolveAfterBattle の .trade（$10:$641c）の「つうしん していなければ しんかしない」を
; 「つうしん中、または（どうぐで しんか では なく）Lv37 いじょう なら すすむ」に かえる
SECTION "tradeevo trade hook", ROMX[$641c], BANK[$10]
	call ED_TradeCheck   ; z = しんかしない
	jp z, $6567
	nop

SECTION "tradeevo trade check", ROMX[$7fa0], BANK[$10]
ED_TradeCheck:
	ld a, [ED_wLinkMode]
	and a
	ret nz
	ld a, [ED_wForceEvolution]
	and a
	jr nz, .no
	ld a, [ED_wTempMonLevel]
	cp ED_TRADE_LEVEL
	jr c, .no
	or 1
	ret
.no
	xor a
	ret

