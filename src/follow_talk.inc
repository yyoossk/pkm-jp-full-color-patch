; 会話の表（scripts/mkfollowtalk.py で作る。会話文案.md の 1・3・4 章。初代にない行は入れていない）
; 気持ちのアイコン: 0 びっくり・1 はてな・2 うれしい・3 かなしい・4 ハート・5 いなずま・6 ねむり
FwTalkRules: ; 種類なら 0・タイプなら 1、あてはまるもの（$FF まで）、マップ（$FF まで）、文の数、はじめの文の番号
	db 0, $99, $FF, $0C, $FF, 2, 5
	db 0, $B0, $FF, $0D, $FF, 1, 7
	db 0, $54, $55, $FF, $0D, $53, $FF, 2, 8
	db 0, $B1, $FF, $0E, $FF, 1, 10
	db 0, $04, $8E, $FF, $3B, $3C, $3D, $FF, 2, 11
	db 0, $22, $FF, $52, $E8, $FF, 1, 13
	db 1, $05, $FF, $52, $E8, $FF, 4, 14
	db 0, $3B, $76, $FF, $C5, $FF, 1, 18
	db 1, $18, $FF, $B7, $FF, 1, 19
	db 0, $AA, $FF, $06, $FF, 1, 20
	db 0, $4C, $FF, $1A, $FF, 1, 21
	db 1, $02, $FF, $1D, $FF, 1, 22
	db 1, $08, $FF, $04, $FF, 1, 23
	db $FF
DEF FWT_SLEEP EQU 0
DEF FWT_POISON EQU 1
DEF FWT_BURN EQU 2
DEF FWT_FREEZE EQU 3
DEF FWT_PARALYZE EQU 4
DEF FWT_NORMAL EQU 24
DEF FWT_FOUND EQU 25
DEF FWT_GOT EQU 26
FwTalkEmotes:
	db 6, 3, 0, 0, 5, 2, 2, 2, 4, 4, 3, 2, 4, 2, 2, 2, 2, 2, 2, 1, 1, 1, 2, 2, 2, 0, 2
FwTalkTexts: ; テキスト番号 $81 + n（DisplayTextID の表）
	dw FwText_Sleep
	dw FwText_Poison
	dw FwText_Burn
	dw FwText_Freeze
	dw FwText_Paralyze
	dw FwText_Kanto0_0
	dw FwText_Kanto0_1
	dw FwText_Kanto1_0
	dw FwText_Kanto2_0
	dw FwText_Kanto2_1
	dw FwText_Kanto3_0
	dw FwText_Kanto4_0
	dw FwText_Kanto4_1
	dw FwText_Kanto5_0
	dw FwText_Kanto6_0
	dw FwText_Kanto6_1
	dw FwText_Kanto6_2
	dw FwText_Kanto6_3
	dw FwText_Kanto7_0
	dw FwText_Kanto8_0
	dw FwText_Kanto9_0
	dw FwText_Kanto10_0
	dw FwText_Kanto11_0
	dw FwText_Kanto12_0
	dw FwText_Normal
	dw FwText_Found
	dw FwText_Got
FwText_Sleep:
	db $01, LOW(wNameBuffer), HIGH(wNameBuffer), $00, "は", $4F, "すこし　ねむそうだ", $57
FwText_Poison:
	db $01, LOW(wNameBuffer), HIGH(wNameBuffer), $00, "は", $4F, "ぐあいが　わるそうだ", $57
FwText_Burn:
	db $01, LOW(wNameBuffer), HIGH(wNameBuffer), $00, "は", $4F, "すこし　いたそうだ", $57
FwText_Freeze:
	db $01, LOW(wNameBuffer), HIGH(wNameBuffer), $00, "は", $4F, "こおりづけに　なっている！", $57
FwText_Paralyze:
	db $01, LOW(wNameBuffer), HIGH(wNameBuffer), $00, "は", $4F, "うごきが　にぶく　なっている", $57
FwText_Kanto0_0:
	db $01, LOW(wNameBuffer), HIGH(wNameBuffer), $00, "は", $4F, "つるを　くねくね　させた！", $57
FwText_Kanto0_1:
	db $01, LOW(wNameBuffer), HIGH(wNameBuffer), $00, "は", $4F, "つるを　ぴしっと　ならした！", $57
FwText_Kanto1_0:
	db $01, LOW(wNameBuffer), HIGH(wNameBuffer), $00, "は", $4F, "しっぽの　ほのおを　もやした！", $57
FwText_Kanto2_0:
	db $01, LOW(wNameBuffer), HIGH(wNameBuffer), $00, "は", $4F, "たのしく　おどった！", $57
FwText_Kanto2_1:
	db $01, LOW(wNameBuffer), HIGH(wNameBuffer), $00, "は　うれしくて", $4F, "おどりだした！", $57
FwText_Kanto3_0:
	db $01, LOW(wNameBuffer), HIGH(wNameBuffer), $00, "は　ころんで", $4F, "ちょっと　くやしそうだ！", $57
FwText_Kanto4_0:
	db $01, LOW(wNameBuffer), HIGH(wNameBuffer), $00, "は", $4F, "そらを　みあげている！", $57
FwText_Kanto4_1:
	db $01, LOW(wNameBuffer), HIGH(wNameBuffer), $00, "は", $4F, "とつぜん　おどりだした！", $57
FwText_Kanto5_0:
	db $01, LOW(wNameBuffer), HIGH(wNameBuffer), $00, "は　たのしそうに", $4F, "じめんに　もぐっている！", $57
FwText_Kanto6_0:
	db $01, LOW(wNameBuffer), HIGH(wNameBuffer), $00, "は　たのしそうに", $4F, "ころがっている！", $57
FwText_Kanto6_1:
	db $01, LOW(wNameBuffer), HIGH(wNameBuffer), $00, "は", $4F, "いわを　けずりはじめた！", $57
FwText_Kanto6_2:
	db $01, LOW(wNameBuffer), HIGH(wNameBuffer), $00, "は　たのしそうに", $4F, "いわを　ぶつけている！", $57
FwText_Kanto6_3:
	db $01, LOW(wNameBuffer), HIGH(wNameBuffer), $00, "は　じめんを", $4F, "たたいて　ならしはじめた！", $57
FwText_Kanto7_0:
	db $01, LOW(wNameBuffer), HIGH(wNameBuffer), $00, "は　からだを", $4F, "のばして　くつろいでいる！", $57
FwText_Kanto8_0:
	db $00, "……　……　……　……", $51, $01, LOW(wNameBuffer), HIGH(wNameBuffer), $00, "は", $4F, "だまって　うなずいた！", $57
FwText_Kanto9_0:
	db $01, LOW(wNameBuffer), HIGH(wNameBuffer), $00, "は", $4F, "なにか　つぶやいた……", $57
FwText_Kanto10_0:
	db $00, "……おや？　", $01, LOW(wNameBuffer), HIGH(wNameBuffer), $00, "の", $4F, "すがたは……", $51, "かわらなかった！", $57
FwText_Kanto11_0:
	db $01, LOW(wNameBuffer), HIGH(wNameBuffer), $00, "は", $4F, "ゆうがに　そらを　とんでいる！", $57
FwText_Kanto12_0:
	db $01, LOW(wNameBuffer), HIGH(wNameBuffer), $00, "は　たのしそうに", $4F, "ゆらゆら　ゆれている", $57
FwText_Normal:
	db $01, LOW(wNameBuffer), HIGH(wNameBuffer), $00, "は", $4F, "あなたと　いっしょで　うれしそうだ！", $57
FwText_Found:
	db $08
	jp FwFoundAsm
FwText_FoundMsg:
	db $01, LOW(wNameBuffer), HIGH(wNameBuffer), $00, "は", $4F, "なにか　みつけた　ようだ", $51, "ひろいますか？", $50, $50
FwText_Got:
	db $00, $52, "は　きんのたまを", $4F, "てにいれた！", $50, $0B, $50
