; ボックスが いっぱいに なった ときの マサキからの 電話を ならないように する
;
; ・やせいの ポケモンを つかまえて ボックスが いっぱいに なると、戦闘の あとの Script_reloadmapafterbattle が
;   wBattleResult の ビット7（BATTLERESULT_BOX_FULL）を 見て Script_SpecialBillCall（マサキの 電話）を よぶ。
; ・その「bit 7, a / jr z, .done」の jr z を jr に して、いつも .done へ とぶ（1バイト）。
;   ボックスが いっぱいの ときの ほかの 動き（つかまえた ときの ことば・ボックスを かえる 機能）は かわらない。
;   ポケギアから マサキに かける 電話（ボックスの のこり）は そのまま。
;
; ほかの バージョンに 入れるとき：NB_JRZ・NB_BANK を その ROM の「cb 7f 28 xx 06 bb 11」の 28 の 場所に する

IF !DEF(NB_JRZ)
DEF NB_JRZ   EQU $7317          ; バンク$25 Script_reloadmapafterbattle.was_wild の jr z（28 0b）
DEF NB_BANK  EQU $25
ENDC

SECTION "nobillcall", ROMX[NB_JRZ], BANK[NB_BANK]
	db $18                          ; jr z → jr（つぎの 0b は そのまま ＝ .done へ）
