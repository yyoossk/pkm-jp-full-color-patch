; 251ひき そろう版：ずかんの 進化の ページの「つうしん」を「レべル37」に
; （251版で のこる つうしん しんかは ヤドン → ヤドキング（おうじゃのしるしを もたせて Lv37）だけ。2行めは「もたせる　おうじゃのしるし」）
INCLUDE "src/charmap_jp.inc"
SECTION "dexinfo trade text", ROMX[$7fe0], BANK[$76]
DI_TradeText::
	db "レべル", $f6 + 3, $f6 + 7, "@"
