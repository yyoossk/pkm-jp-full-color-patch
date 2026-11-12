; STARTボタンの メニューの「パソコン」で ボックスを かえた あと、人に 話しかけると 止まるのを 直す。
; 原因：ボックスを かえる 処理（ChangeBox）の 最後（1C:6C8B〜6CA2 の 24バイト）は、
;     wCurMapTextPtr（$D2EB）を $CD3D に とっておく
;     → RestoreMapTextPointer（$3E15：hSavedMapTextPtr〔$FFEC〕を wCurMapTextPtr に もどす）
;     → レポートを 書く（1C:6C0D）→ SetMapTextPointer（$3E1F、hl = $CD3D）
;   と なって いる。もとの ゲームでは パソコンは かならず PrintPredefTextID（$3E05）の 中から 開くので、
;   wCurMapTextPtr は 一時的な 表（TextPredefs $3E32）、$FFEC は マップの 会話の 表で、最後に
;   PrintPredefTextID が $FFEC から もとに もどす。STARTボタンの メニューの「パソコン」は これを 通らないので、
;   $FFEC には 古い 値が 入った まま。もどす 人も いないので wCurMapTextPtr が $CD3D の ままに なり、
;   そのあと 人に 話しかけると こわれた 表を 読んで 止まる。
; 直し方：wCurMapTextPtr が TextPredefs の ときだけ（パソコンの 机から 開いた とき）元の とおりに する。
;   ちがう とき（STARTボタンの メニュー）は、wCurMapTextPtr は もう マップの 会話の 表なので、
;   そのまま レポートを 書くだけに する。（番地は 12の 版 すべて 同じ）

DEF wCurMapTextPtr_CB    EQU $d2eb
DEF wChangeBoxSavedPtr   EQU $cd3d
DEF RestoreMapTextPtr_CB EQU $3e15
DEF SetMapTextPtr_CB     EQU $3e1f
DEF TextPredefs_CB       EQU $3e32
DEF SaveGameData_CB      EQU $6c0d ; バンク $1C

SECTION "ボックスを かえる 最後", ROMX[$6c8b], BANK[$1c]
	ld b, BANK(KitChangeBoxSave)
	ld hl, KitChangeBoxSave
	jp $3500               ; Bankswitch（もどると ChangeBox を 呼んだ 所へ）

SECTION "ボックスを かえる レポート", ROMX[$7f80], BANK[$37]
KitChangeBoxSave:
	ld hl, wCurMapTextPtr_CB
	ld a, [hli]
	cp LOW(TextPredefs_CB)
	jr nz, .direct
	ld a, [hld]
	cp HIGH(TextPredefs_CB)
	jr nz, .direct
	; パソコンの 机から（元の とおり）
	ld de, wChangeBoxSavedPtr
	ld a, [hli]
	ld [de], a
	inc de
	ld a, [hl]
	ld [de], a
	call RestoreMapTextPtr_CB
	call .save
	ld hl, wChangeBoxSavedPtr
	jp SetMapTextPtr_CB
.direct ; STARTボタンの メニューから：会話の 表は そのまま
.save
	ld b, $1c
	ld hl, SaveGameData_CB
	jp $3500
	assert @ <= $8000
