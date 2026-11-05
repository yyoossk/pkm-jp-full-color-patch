; レベルアップ（わざマシン）で わざを覚えるとき、A ボタンの連打で わざを上書きしないようにする（金 日本版）
;
; 元のゲーム：わざが4つのときに
;   1.「〜の かわりに ほかの わざを わすれさせますか？」 はい／いいえ（カーソルは はい）
;      → はい：わざを選ぶ画面（カーソルは1つ目）→ A で 1つ目のわざを忘れてしまう
;   2. いいえ：「〜を おぼえるのを あきらめますか？」 はい／いいえ（カーソルは はい）→ はい：覚えずに終わる、いいえ：1 にもどる
; 変えたあと：1・2 の はい／いいえ を カーソルが「いいえ」から始まるようにする。
;   A を連打すると 1（いいえ）→ 2（いいえ）→ 1 … と くり返すだけで、わざは上書きされず、あきらめもしない。
;   わざを覚えるときは 上を押して「はい」、あきらめるときは 2 で 上を押して「はい」。
; ほかの はい／いいえ（ポケモンセンターなど）は 元のまま（この2か所の call YesNoBox だけを置きかえる）。

DEF YesNoMenuHeader     EQU $1c34
DEF CopyMenuHeader      EQU $1b60
DEF _YesNoBox_AfterCopy EQU $1c00    ; _YesNoBox の push bc / ld hl, YesNoMenuHeader / call CopyMenuHeader / pop bc（$1bff）のつぎ
DEF wMenuCursorPosition EQU $cef3    ; メニューの見出しの「はじめのカーソル」
DEF LM_BANK             EQU $01      ; LearnMove・ForgetMove のバンク
DEF LM_FORGET_YESNO     EQU $68bb    ; ForgetMove の call YesNoBox（わすれさせますか？）
DEF LM_CANCEL_YESNO     EQU $689c    ; LearnMove.cancel の call YesNoBox（あきらめますか？）
DEF LM_FREE             EQU $7fb0    ; バンク$01 の空き（$7fa0〜$7fa5 はバグ修正）

SECTION "learnmove forget yesno", ROMX[LM_FORGET_YESNO], BANK[LM_BANK]
	call NoYesBox_LearnMove
SECTION "learnmove cancel yesno", ROMX[LM_CANCEL_YESNO], BANK[LM_BANK]
	call NoYesBox_LearnMove

SECTION "learnmove noyes", ROMX[LM_FREE], BANK[LM_BANK]
; YesNoBox と同じ（同じ場所・同じ答え：はい = キャリーなし）。カーソルだけ「いいえ」から
NoYesBox_LearnMove:
	ld bc, (14 << 8) | 7         ; YesNoBox と同じ場所（lb bc, SCREEN_WIDTH - 6, 7）
	push bc
	ld hl, YesNoMenuHeader
	call CopyMenuHeader
	pop bc
	ld a, 2                      ; いいえ
	ld [wMenuCursorPosition], a
	jp _YesNoBox_AfterCopy
