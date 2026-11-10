; ポケットモンスター 金・銀（日本版）60fps（フィールドの移動だけ）
; （クリスタル追加機能キットの fps60.asm を移植）
;
; 元のゲームのフィールドは 2フレームに1回 2ドットずつ動く（30fps）。
; ゲームの進み方（速さ・タイミング・処理の順番）は変えずに、
;   1フレーム目 … 「前の位置と今の位置のまん中」を表示
;   2フレーム目 … 今の位置を表示（VBlank の中でもとにもどす）
; として、1ドットずつ動いて見えるようにする。
; 背景のスクロール（hSCX/hSCY）とスプライト（wShadowOAM の Y・X）が対象。
;
; ・作業用のメモリ：クリスタルは WRAM バンク2 を使ったが、金銀はスタックが WRAM バンク1（$dfff から下）に
;   あるので、バンクを切りかえるとスタックがずれてしまう。そこで、日本版 金銀のゲームデータの後ろ
;   （$de37〜。どこからも使われていない。スタックは英語版でも $fc バイトしか取っていないので $df00 より下には来ない）
;   の $de40〜$dee7 を使う。バンクを切りかえないので、初代ゲームボーイでもそのまま動く。
; ・金銀の HandleMapBackground には PlaceMapNameSign が無い（クリスタルだけ）。

INCLUDE "src/version.inc"

; 使われていない WRAM（$de40〜$dee7）
DEF wFps60Flag        EQU FPS60_WRAM + 0 ; 1 = まん中を表示中（次の VBlank でもどす）
DEF wFps60Count       EQU FPS60_WRAM + 1 ; 対象の OAM の数
DEF wFps60Valid       EQU FPS60_WRAM + 3 ; 1 = 前の位置が入っている
DEF wFps60Buf         EQU FPS60_WRAM + 4 ; (まん中, 今) × (SCX, SCY, OAM 40個の Y・X) = 164バイト
DEF FPS60_MAXDIFF     EQU 4          ; これより大きく動いた物は補間しない（ワープ・出現など）
DEF OAM_HIDDEN_Y      EQU $a0
DEF rLY_FPS           EQU $ff44
DEF FPS60_LY_LIMIT    EQU 110        ; この行より後なら、そのフレームは補間しない（計算が1フレームに収まらないので。120 で遅れなし、余裕を見て 110）

;---------------------------------------------------------------------
SECTION "60fps HandleMap tail", ROMX[HandleMap_Tail], BANK[BANK_OVERWORLD]
	call Fps60_NextOverworldFrame
	call Fps60_HandleMapBackground

SECTION "60fps tramp", ROMX[BANK25_FREE], BANK[BANK_OVERWORLD]
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

SECTION "60fps vblank", ROM0[HOME_FREE_FPS]
Fps60_VBlank:
	xor a
	ld [wVBlankOccurred], a
.restore
	ld hl, wFps60Flag
	ld a, [hl]
	and a
	ret z
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
	jp Fps60_RestoreOAM.next

; a = 表示中の値、[hl] = (まん中, 今) → まん中のままなら今の値を返す
.one_h
	cp [hl]
	inc hl
	jr nz, .keep
	ld a, [hl]
.keep
	inc hl
	ret

; a = 今の値、[hl] = (まん中, 前の値)：[de] と [hl] に まん中、[hl+1] に 今の値、hl += 2（c を つかう）
MACRO fps60_coord
	ld c, a
	inc hl
	ld a, [hl]                   ; 前
	ld [hl], c                   ; 今
	dec hl
	sub c                        ; 前 - 今
	jr z, .same\@
	add FPS60_MAXDIFF
	cp FPS60_MAXDIFF * 2 + 1
	jr nc, .same\@               ; 大きく 動いた（ワープ・出現 など）
	sub FPS60_MAXDIFF
	sra a
	add c                        ; 今 + (前 - 今) / 2
	jr .put\@
.same\@
	ld a, c
.put\@
	ld [hli], a
	inc hl
	ld [de], a
ENDM

; OAM を もどす ループ（速くするため .one_h を 中に 書く。ホームの 空きが たりないので 分けた：
; 使われていない PlaceBCDNumberSprite $3e9e〜$3edc の うしろ。前は 連れ歩き follow.asm）
SECTION "60fps vblank oam", ROM0[$3ec2]
Fps60_RestoreOAM:
.loop
	ld a, [de]
	cp [hl]
	inc hl
	jr nz, .k1
	ld a, [hl]
	ld [de], a
.k1
	inc hl
	inc e
	ld a, [de]
	cp [hl]
	inc hl
	jr nz, .k2
	ld a, [hl]
	ld [de], a
.k2
	inc hl
	inc e
	inc e
	inc e
.next
	dec c
	jr nz, .loop
	ret

;---------------------------------------------------------------------
SECTION "60fps main", ROMX[NEW_ADDR_FPS], BANK[BANK_NEW]

; HandleMapBackground と同じことをして、すぐにまん中の位置を出す
Fps60_Background:
	ldh a, [hVBlankCounter]      ; スプライトを 並べる 前に 見る（並べて いる 間に VBlank を こえたら、もう おそいので まん中は 出さない）
	push af
	ld a, UpdateSprites_Bank
	ld hl, _UpdateSprites
	rst $08
	ld a, ScrollScreen_Bank
	ld hl, ScrollScreen
	rst $08
	pop bc                       ; b = 位置が決まる前の VBlank の回数

	di
	call Fps60_VBlank.restore    ; 前のぶんが残っていたらもどす
	ei

; マップの新しい列を読みこんだフレームなどで、もう VBlank が近いときは まん中の計算をしない。
; ここで計算すると 1フレームに収まらず、ゲームが1フレーム遅れる（じてんしゃ・Bダッシュで約16フレームごと）。
	ldh a, [rLY_FPS]
	cp 144
	jr nc, .in_time              ; もう VBlank 中 → 下の hVBlankCounter のくらべで「記録だけ」になる
	cp FPS60_LY_LIMIT
	jr c, .in_time
	xor a
	ld [wFps60Valid], a          ; 次の回は「記録だけ」
	ret
.in_time
	ld a, [wFps60Valid]
	and a
	jp z, .record_only
	ldh a, [hVBlankCounter]
	cp b
	jp nz, .record_only          ; 今の位置がもう表示された → この回は補間しない

; 背景
	ld hl, wFps60Buf
	ldh a, [hSCX]
	call .coord
	ld d, a
	ldh a, [hSCY]
	call .coord
	ld e, a
; OAM（前から、隠れている物が出てくるまで。速くするため .coord を 中に 書く）
	push de
	push bc
	ld de, wShadowOAM
.loop
	ld a, [de]
	cp OAM_HIDDEN_Y
	jr z, .oam_done
	fps60_coord
	inc e
	ld a, [de]
	fps60_coord
	inc e
	inc e
	inc e
	ld a, e
	cp 40 * 4
	jr c, .loop
.oam_done
	ld a, e
	srl a
	srl a
	ld [wFps60Count], a
	pop bc
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
