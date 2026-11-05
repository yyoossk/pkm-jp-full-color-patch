; ずかんの「ぶんぷ」を 時間帯で 切りかえる … クリスタル（日本版）用（金銀の src/nesttime.asm と 同じ ことを する）
; クリスタルの すみかの 画面（Pokedex_GetArea）・FindNest は 金と 同じ 形。ちがう 所：
;   ・wNestTime・wNestKanto：WRAM バンク1 に 空きが ないので WRAM バンク2 の $dfc7・$dfc8（読み書きの ときだけ 切りかえる）
;   ・バンク$24 の 入口は 使われていない EntireFlyMap（$24:$6439〜$6529）の 場所に 置く
INCLUDE "src/charmap_jp.inc"

DEF NT_GRASS_HOOK      EQU $604b   ; FindNest .FindGrass（$0a:$6042）の inc hl ×3 / ld a, $15
DEF NT_FINDNEST_BANK   EQU $0a
DEF NT_FINDNEST_FREE   EQU $7e00   ; バンク$0a の 空き
DEF NT_AREA_BANK       EQU $24
DEF NT_AREA            EQU $5e2b   ; Pokedex_GetArea
DEF NT_LOOP_HOOK       EQU $5e88   ; .loop の call JoyTextDelay
DEF NT_TITLE_HOOK      EQU $5f3c   ; .PlaceString_MonsNest の さいごの call PlaceString
DEF NT_RIGHT           EQU $5ed1   ; .right（カントーを 見せる）
DEF NT_AREA_FREE       EQU $6439   ; 使われていない EntireFlyMap の 場所
DEF NT_JoyTextDelay    EQU $0a4d
DEF NT_PlaceString     EQU $1057
DEF NT_ClearSprites    EQU $2fd7
DEF NT_wTownMapPlayerIconLandmark EQU $d002
DEF NT_wTownMapCursorLandmark     EQU $d003
DEF NT_hJoyPressed     EQU $ffa7
DEF NT_hWY             EQU $ffd2
DEF NT_TITLE_COORD     EQU $c4a0   ; hlcoord 0, 0
DEF NT_VARS_WRAMBANK   EQU 2
DEF wNestTime          EQU $dfc7   ; WRAM バンク2（$dfc5・$dfc6 は むしよけ）
DEF wNestKanto         EQU $dfc8
DEF NT_BANK            EQU $76
DEF NT_ADDR            EQU $5800

; a を \1 に しまう／\1 を a に 読む（WRAM バンク2。hl を こわす）
MACRO nt_store
	ld l, a
	ldh a, [$ff70]
	ld h, a
	ld a, NT_VARS_WRAMBANK
	ldh [$ff70], a
	ld a, l
	ld [\1], a
	ld a, h
	ldh [$ff70], a
	ld a, l
ENDM
MACRO nt_load
	ldh a, [$ff70]
	ld h, a
	ld a, NT_VARS_WRAMBANK
	ldh [$ff70], a
	ld a, [\1]
	ld l, a
	ld a, h
	ldh [$ff70], a
	ld a, l
ENDM

; ---- 草むらの 表
SECTION "nesttime grass hook", ROMX[NT_GRASS_HOOK], BANK[NT_FINDNEST_BANK]
	call NestTime_Grass
	nop
	nop

SECTION "nesttime grass", ROMX[NT_FINDNEST_FREE], BANK[NT_FINDNEST_BANK]
; hl = 表の マップの 番号の 次 → hl = 見はじめる 所の 1つ前、a = 見る 数
NestTime_Grass:
	push hl
	nt_load wNestTime
	pop hl
	inc hl
	inc hl
	inc hl
	and a
	jr nz, .time
	ld a, 7 * 3                       ; ぜんぶ
	ret
.time
	push bc
	ld bc, 7 * 2
.offset
	dec a                             ; 1 あさ・2 ひる・3 よる
	jr z, .done
	add hl, bc
	jr .offset
.done
	pop bc
	ld a, 7
	ret

; ---- すみかの 画面
SECTION "nesttime loop hook", ROMX[NT_LOOP_HOOK], BANK[NT_AREA_BANK]
	call NestTime_Loop
SECTION "nesttime title hook", ROMX[NT_TITLE_HOOK], BANK[NT_AREA_BANK]
	call NestTime_Title

SECTION "nesttime area", ROMX[NT_AREA_FREE], BANK[NT_AREA_BANK]
NestTime_Loop:
	call NT_JoyTextDelay
	ld a, BANK(NestTime_Input)
	ld hl, NestTime_Input
	rst $08
	ret nc
	; 作りなおす：.loop から もどらず、Pokedex_GetArea の 始めと 同じ 形に して もう一度
	pop hl
	ld a, [NT_wTownMapPlayerIconLandmark]
	ld e, a
	pop af
	ld [NT_wTownMapCursorLandmark], a
	pop af
	ld [NT_wTownMapPlayerIconLandmark], a
	jp NT_AREA

NestTime_Title:
	call NT_PlaceString
	ld a, BANK(NestTime_DrawTitle)
	ld hl, NestTime_DrawTitle
	rst $08
	ret

SECTION "nesttime", ROMX[NT_ADDR], BANK[NT_BANK]
; キャリー：作りなおす
NestTime_Input:
	nt_load wNestKanto
	and a
	jr z, .input
	xor a
	nt_store wNestKanto
	ld a, NT_AREA_BANK                ; 前に カントーを 見て いた
	ld hl, NT_RIGHT
	rst $08
.input
	ldh a, [NT_hJoyPressed]
	and 1 << 3                        ; START
	ret z                             ; キャリーなし
	nt_load wNestTime
	inc a
	and 3
	nt_store wNestTime
	ldh a, [NT_hWY]
	and a
	jr nz, .johto
	ld a, 1
	nt_store wNestKanto
.johto
	call NT_ClearSprites
	scf
	ret

; わくを 右に のばして 時間帯を かく（ぜんぶ の ときは なにも しない）
NestTime_DrawTitle:
	nt_load wNestTime
	and a
	ret z
	push af
	ld hl, NT_TITLE_COORD + 11
	ld a, $7f
	ld [hli], a
	ld [hli], a
	ld [hli], a
	ld [hl], $06
	ld hl, NT_TITLE_COORD + 20 + 11
	ld a, $7f
	ld [hli], a
	ld [hli], a
	ld [hli], a
	ld [hl], $16
	ld hl, NT_TITLE_COORD + 40 + 11
	ld a, $07
	ld [hli], a
	ld [hli], a
	ld [hli], a
	ld [hl], $27
	pop af
	dec a
	add a
	add a                             ; × 4
	ld e, a
	ld d, 0
	ld hl, .names
	add hl, de
	ld d, h
	ld e, l
	ld hl, NT_TITLE_COORD + 20 + 12
	jp NT_PlaceString
.names
	db "あさ@", 0
	db "ひる@", 0
	db "よる@", 0
