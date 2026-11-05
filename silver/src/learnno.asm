; レベルアップ・わざマシンで わざを覚えるとき、A ボタンの連打で わざを上書きしないようにする（日本版 銀）
; （クリスタル追加機能キットの learnno.asm を移植）
;
; 「〜を わすれさせて ○○を おぼえますか？」と「○○を おぼえるのを あきらめますか？」の
; 「はい／いいえ」の カーソルを はじめから「いいえ」にする。
; A を連打すると 2つの質問を くり返す（ループ）だけで、わざを わすれたり あきらめたりしない。
; 覚えさせるとき・あきらめるときは「はい」に合わせて A を押す。
;
; 日本版 銀のアドレス（金は ForgetMove などの位置がちがうので 調べなおすこと）
;   ForgetMove の call YesNoBox      $01:$6880
;   LearnMove.cancel の call YesNoBox $01:$6861
;   YesNoBox（ld bc, $0e07 / jr _YesNoBox）$1bee、_YesNoBox $1bf8（push bc / ld hl, YesNoMenuHeader / call CopyMenuHeader / pop bc）
;   YesNoMenuHeader $1c34（最後の 1バイトが はじめのカーソル = wMenuCursorPosition $cef3）

DEF YesNoBox_Coords   EQU $0e07     ; YesNoBox と同じ場所
DEF YesNoMenuHeader   EQU $1c34
DEF CopyMenuHeader    EQU $1b60
DEF _YesNoBox_Place   EQU $1c00     ; _YesNoBox のメニューの見出しを写して pop bc したあと
DEF wMenuCursorPosition EQU $cef3   ; メニューの見出しの「はじめのカーソル」

SECTION "learn ask forget", ROMX[$6880], BANK[$01]   ; ForgetMove
	call YesNoBox_DefaultNo
SECTION "learn ask stop", ROMX[$6861], BANK[$01]     ; LearnMove.cancel
	call YesNoBox_DefaultNo

SECTION "learn yesno no", ROMX[$7fb0], BANK[$01]
YesNoBox_DefaultNo:
	ld bc, YesNoBox_Coords
	push bc
	ld hl, YesNoMenuHeader
	call CopyMenuHeader
	ld a, 2                      ; いいえ
	ld [wMenuCursorPosition], a
	pop bc
	jp _YesNoBox_Place
