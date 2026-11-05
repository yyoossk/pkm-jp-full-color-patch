; レベルアップ・わざマシンで わざを覚えるとき、A ボタンの連打で わざを上書きしないようにする（クリスタル日本版）
;
; 「〜を わすれさせて ○○を おぼえますか？」と「○○を おぼえるのを あきらめますか？」の
; 「はい／いいえ」の カーソルを はじめから「いいえ」にする。
; A を連打すると 2つの質問を くり返す（ループ）だけで、わざを わすれたり あきらめたりしない。
; 覚えさせるとき・あきらめるときは「はい」に合わせて A を押す。

DEF YesNoBox_Coords   EQU $0e07     ; YesNoBox と同じ場所
DEF YesNoMenuHeader   EQU $1de0
DEF CopyMenuHeader    EQU $1d07
DEF _YesNoBox_Place   EQU $1dac     ; _YesNoBox のメニューの見出しを写したあと
DEF wMenuCursorPosition EQU $cf7c   ; メニューの見出しの「はじめのカーソル」

SECTION "learn ask forget", ROMX[$6722], BANK[$01]   ; ForgetMove
	call YesNoBox_DefaultNo
SECTION "learn ask stop", ROMX[$6703], BANK[$01]     ; LearnMove.cancel
	call YesNoBox_DefaultNo

SECTION "learn yesno no", ROMX[$7ea0], BANK[$01]
YesNoBox_DefaultNo:
	ld bc, YesNoBox_Coords
	push bc
	ld hl, YesNoMenuHeader
	call CopyMenuHeader
	ld a, 2                      ; いいえ
	ld [wMenuCursorPosition], a
	pop bc
	jp _YesNoBox_Place
