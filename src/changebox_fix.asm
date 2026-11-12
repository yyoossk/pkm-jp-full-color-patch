; STARTボタンのメニューの「パソコン」でボックスをかえたあと、人に話しかけると止まるのを直す
; （赤のキット「パソコンでボックスをかえたあとのフリーズ」から）
;
; 原因：ボックスをかえる処理（ChangeBox）の最後（1C:73AC〜）は
;     wCurMapTextPtr（$D2EB）を $CD3D にとっておく → RestoreMapTextPointer（$FFEC を wCurMapTextPtr にもどす）
;     → レポートを書く（1C:7322）→ SetMapTextPointer（hl = $CD3D）→ 画面をなおす所（03:7FB3 など）へ jp
;   元のゲームではパソコンはかならず PrintPredefTextID の中から開くので、wCurMapTextPtr は一時的な表
;   （TextPredefs）、$FFEC はマップの会話の表で、最後に PrintPredefTextID が $FFEC から元にもどす。
;   STARTボタンの「パソコン」は PrintPredefTextID を通らないので、$FFEC の古い値が入り、もどす人もいなくて
;   wCurMapTextPtr が $CD3D のままになり、話しかけるとこわれた表を読んで止まる（からの窓が出る）。
; 直し方：wCurMapTextPtr が TextPredefs のとき（パソコンの机から）だけ元のとおりにする。
;   ちがうとき（STARTボタンから）は、会話の表はもうマップのものなので、レポートを書くだけにする。
;   どちらも最後は、元のとおり画面をなおす所へ行く。

IF HAS_CHANGEBOX_FIX

DEF wCurMapTextPtr EQU $D2EB
DEF wChangeBoxSavedMapTextPointer EQU $CD3D
DEF ChangeBoxTail EQU $73AC      ; どの版も同じ（31バイト）
DEF ChangeBoxSave EQU $7322      ; バンク $1C：レポートを書く

SECTION "ボックスをかえる 最後", ROMX[ChangeBoxTail], BANK[$1C]
	ld b, BANK(ChangeBoxTailFix)
	ld hl, ChangeBoxTailFix
	jp Bankswitch
	ds 31 - 8, 0
	assert @ == ChangeBoxTail + 31

FreeBankA
ChangeBoxTailFix:
	ld hl, wCurMapTextPtr
	ld a, [hli]
	cp LOW(TextPredefs)
	jr nz, .direct
	ld a, [hld]
	cp HIGH(TextPredefs)
	jr nz, .direct
	; パソコンの机から（元のとおり）
	ld de, wChangeBoxSavedMapTextPointer
	ld a, [hli]
	ld [de], a
	inc de
	ld a, [hl]
	ld [de], a
	call RestoreMapTextPointer
	call .save
	ld hl, wChangeBoxSavedMapTextPointer
	call SetMapTextPointer
	jr .redraw
.direct ; STARTボタンのメニューから：会話の表はそのまま
	call .save
.redraw
	ld b, ChangeBoxRedrawBank
	ld hl, ChangeBoxRedraw
	jp Bankswitch
.save
	ld b, $1C
	ld hl, ChangeBoxSave
	jp Bankswitch

ENDC
