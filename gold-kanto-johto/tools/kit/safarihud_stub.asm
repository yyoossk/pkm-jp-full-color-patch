; カントー＆ジョウト（金）：サファリの 表示は MOD の もの（gold_safari.py が 組んで 新しい バンクの $7900 に 置く）。
; 場所の 名前の 札（mapsign.asm）が 毎フレーム 呼ぶ SafariHUD は ここ。バンクの 番号は 移植の ときに 書く（$7F:$4001）。
SECTION "SafariHUD stub", ROMX[$4000], BANK[$7F]
	db $00
SafariHUD::
	ld a, $00
	ld hl, $7900
	rst $08
	ret
