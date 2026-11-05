; ポケットモンスター クリスタル（日本版）60fps（フィールドの移動だけ）
;
; 元のゲームのフィールドは 2フレームに1回 2ドットずつ動く（30fps）。
; ゲームの進み方（速さ・タイミング・処理の順番）は変えずに、
;   1フレーム目 … 「前の位置と今の位置のまん中」を表示
;   2フレーム目 … 今の位置を表示（VBlank の中でもとにもどす）
; として、1ドットずつ動いて見えるようにする。
; 背景のスクロール（hSCX/hSCY）とスプライト（wShadowOAM の Y・X）が対象。
;
; ・まん中の計算は、もともと何もしないで待っている時間（NextOverworldFrame の前）に行うので、
;   処理の重い場面でも元のゲームより遅くならない。
; ・今の位置がもう表示されてしまった回（処理が重くて VBlank をまたいだ回）は補間しない。
; ・もどすときは「まん中の値のまま変わっていない所」だけをもどすので、
;   その間にほかの処理が書きかえた値はそのまま残る。

INCLUDE "src/crystal_jp.inc"

DEF hVBlankCounter    EQU $ff9b
DEF rSVBK             EQU $ff70
DEF wVBlankOccurred   EQU $cfa7
DEF VBlank_ClearOccurred EQU $02fc   ; xor a / ld [wVBlankOccurred], a（4バイト）
DEF FPS60_WRAMBANK    EQU 2
; WRAM バンク2 の使われていない所
DEF wFps60Flag        EQU $df00      ; 1 = まん中を表示中（次の VBlank でもどす）
DEF wFps60Count       EQU $df01      ; 対象の OAM の数
DEF wFps60VBlank      EQU $df02      ; 位置が決まったときの hVBlankCounter
DEF wFps60Valid       EQU $df03      ; 1 = 前の位置が入っている
DEF wFps60Buf         EQU $df04      ; (まん中, 今) × (SCX, SCY, OAM 40個の Y・X)
DEF FPS60_MAXDIFF     EQU 4          ; これより大きく動いた物は補間しない（ワープ・出現など）
DEF OAM_HIDDEN_Y      EQU $a0

DEF UpdateSprites_Bank  EQU $01
DEF _UpdateSprites      EQU $5920
DEF ScrollScreen_Bank   EQU $03
DEF ScrollScreen        EQU $574f
DEF PlaceMapNameSign_Bank EQU $2e
DEF PlaceMapNameSign    EQU $4098

;---------------------------------------------------------------------
SECTION "60fps HandleMap tail", ROMX[HandleMap_Tail], BANK[BANK_OVERWORLD]
	call Fps60_NextOverworldFrame
	call Fps60_HandleMapBackground

SECTION "60fps tramp", ROMX[$7fa0], BANK[BANK_OVERWORLD]
Fps60_NextOverworldFrame:
	jp NextOverworldFrame

Fps60_HandleMapBackground:
	ld a, BANK(Fps60_Background)
	ld hl, Fps60_Background
	rst $08
	ret

;---------------------------------------------------------------------
; VBlank：OAM を転送したあとで、まん中の値を今の値にもどす
SECTION "60fps vblank hook", ROM0[VBlank_ClearOccurred]
	call Fps60_VBlank
	nop

SECTION "60fps vblank", ROM0[$3f90]
Fps60_VBlank:
	xor a
	ld [wVBlankOccurred], a
	ldh a, [rSVBK]
	push af
	ld a, FPS60_WRAMBANK
	ldh [rSVBK], a
	call .restore
	pop af
	ldh [rSVBK], a
	ret

; WRAM バンク2 にしてから呼ぶ
.restore
	ld hl, wFps60Flag
	ld a, [hl]
	and a
	jr z, .done
	ld [hl], 0
	inc hl
	ld c, [hl]          ; OAM の数
	ld hl, wFps60Buf
	ldh a, [hSCX]
	call .one_h
	ldh [hSCX], a
	ldh a, [hSCY]
	call .one_h
	ldh [hSCY], a
	ld de, wShadowOAM
	inc c
	jr .next
.loop
	ld a, [de]
	call .one_h
	ld [de], a
	inc de
	ld a, [de]
	call .one_h
	ld [de], a
	inc de
	inc de
	inc de
.next
	dec c
	jr nz, .loop
.done
	ret

; a = 表示中の値、[hl] = (まん中, 今) → まん中のままなら今の値を返す
.one_h
	cp [hl]
	inc hl
	jr nz, .keep
	ld a, [hl]
.keep
	inc hl
	ret

;---------------------------------------------------------------------
SECTION "60fps main", ROMX[$4800], BANK[BANK_NEW]

; HandleMapBackground と同じことをして、すぐにまん中の位置を出す
Fps60_Background:
	ld a, UpdateSprites_Bank
	ld hl, _UpdateSprites
	rst $08
	ldh a, [hVBlankCounter]
	push af
	ld a, ScrollScreen_Bank
	ld hl, ScrollScreen
	rst $08
	ld a, PlaceMapNameSign_Bank
	ld hl, PlaceMapNameSign
	rst $08
	pop bc                       ; b = 位置が決まる前の VBlank の回数

	ldh a, [rSVBK]
	push af
	ld a, FPS60_WRAMBANK
	ldh [rSVBK], a

	di
	call Fps60_VBlank.restore    ; 前のぶんが残っていたらもどす
	ei

	ld a, [wFps60Valid]
	and a
	jr z, .record_only
	ldh a, [hVBlankCounter]
	cp b
	jr nz, .record_only          ; 今の位置がもう表示された → この回は補間しない

; 背景
	ld hl, wFps60Buf
	ldh a, [hSCX]
	call .coord
	ld d, a
	ldh a, [hSCY]
	call .coord
	ld e, a
; OAM（前から、隠れている物が出てくるまで）
	push de
	ld de, wShadowOAM
	ld c, 0
.loop
	ld a, [de]
	cp OAM_HIDDEN_Y
	jr z, .oam_done
	call .coord
	ld [de], a
	inc de
	ld a, [de]
	call .coord
	ld [de], a
	inc de
	inc de
	inc de
	inc c
	ld a, c
	cp 40
	jr nz, .loop
.oam_done
	ld a, c
	ld [wFps60Count], a
	pop de
; 背景もまん中にして「もどす」印をつける（その間に VBlank があったらやめる）
	di
	ldh a, [hVBlankCounter]
	cp b
	jr nz, .undo
	ld a, d
	ldh [hSCX], a
	ld a, e
	ldh [hSCY], a
	ld a, 1
	ld [wFps60Flag], a
	ei
.done
	ld a, 1
	ld [wFps60Valid], a
	pop af
	ldh [rSVBK], a
	ret

.undo
	ld a, 1
	ld [wFps60Flag], a
	call Fps60_VBlank.restore    ; OAM をもとにもどす
	ei
	jr .done

.record_only
	ld hl, wFps60Buf + 1
	ldh a, [hSCX]
	ld [hli], a
	inc hl
	ldh a, [hSCY]
	ld [hli], a
	inc hl
	ld de, wShadowOAM
	ld c, 0
.rloop
	ld a, [de]
	cp OAM_HIDDEN_Y
	jr z, .rdone
	ld [hli], a
	inc hl
	inc de
	ld a, [de]
	ld [hli], a
	inc hl
	inc de
	inc de
	inc de
	inc c
	ld a, c
	cp 40
	jr nz, .rloop
.rdone
	ld a, c
	ld [wFps60Count], a
	jr .done

; a = 今の値、[hl] = (まん中, 前の値) → a = まん中、[hl] = (まん中, 今の値)、hl += 2
.coord
	push bc          ; b・c は呼ぶ側で使っている
	ld c, a
	inc hl
	ld b, [hl]       ; 前の値
	ld [hl], c       ; 今の値
	dec hl
	sub b            ; 今 - 前
	jr z, .same
	cp FPS60_MAXDIFF + 1
	jr c, .half
	cp -FPS60_MAXDIFF
	jr c, .same
.half
	cpl
	inc a            ; 前 - 今
	sra a
	add c            ; 今 + (前 - 今) / 2
	ld [hli], a
	inc hl
	pop bc
	ret
.same
	ld a, c
	ld [hli], a
	inc hl
	pop bc
	ret
