; ずかんの「ぶんぷ」を 時間帯で 切りかえる（金 日本版）
;
; ・すみかの 画面で START を おすと：ぜんぶ → あさ → ひる → よる → ぜんぶ … と 切りかわる。
;   あさ・ひる・よる の ときは、その 時間に 草むら・どうくつで 出る 場所だけ マークする（つり・なみのりは 時間で かわらないので そのまま）。
; ・上の「○○の すみか」の わくの 右に「あさ」「ひる」「よる」を 出す（ぜんぶ の ときは 元のまま）。
; ・カントーを 見て いた ときは 切りかえた あとも カントー。
;
; しくみ
;   ・FindNest の 草むらの 表を 見る 所（.FindGrass の「inc hl ×3 / ld a, NUM_GRASSMON * 3」）を NestTime_Grass に：
;     時間帯が えらんで あれば、その 時間の 7つ だけ 見る（表は 朝 7・昼 7・夜 7 の じゅん）。
;   ・すみかの 画面の くりかえし（Pokedex_GetArea .loop の call JoyTextDelay）を NestTime_Loop に：
;     START なら 時間帯を すすめて、すみかの 画面を はじめから 作りなおす（Pokedex_GetArea へ もどる）。
;   ・わくを かく 所（.PlaceString_MonsNest の さいごの call PlaceString）の あとで わくを 右に のばして 時間帯を かく。
;   ・wNestTime（0 ぜんぶ・1 あさ・2 ひる・3 よる）・wNestKanto は 使われていない WRAM。
;
; 銀・クリスタルに 入れるとき：下の DEF を その ROM の 値に する
;   （クリスタルの FindNest は 表の 形が 同じ。すみかの 画面は クリスタルでは 作りが ちがうので 合わせる）

INCLUDE "src/charmap_jp.inc"

IF !DEF(NT_GRASS_HOOK)
DEF NT_GRASS_HOOK      EQU $6655   ; FindNest .FindGrass の inc hl ×3 / ld a, $15（5バイト）
DEF NT_FINDNEST_BANK   EQU $0a
DEF NT_FINDNEST_FREE   EQU $7fc9   ; バンク$0a の 空き
DEF NT_AREA_BANK       EQU $24
DEF NT_AREA            EQU $5da5   ; Pokedex_GetArea
DEF NT_LOOP_HOOK       EQU $5e02   ; .loop の call JoyTextDelay
DEF NT_TITLE_HOOK      EQU $5eb6   ; .PlaceString_MonsNest の さいごの call PlaceString
DEF NT_RIGHT           EQU $5e4b   ; .right（カントーを 見せる）
DEF NT_AREA_FREE1      EQU $7f1c   ; バンク$24 の 空き
DEF NT_AREA_FREE2      EQU $7fde
DEF NT_JoyTextDelay    EQU $09fd
DEF NT_PlaceString     EQU $0f46
DEF NT_ClearSprites    EQU $30bb
DEF NT_wTownMapPlayerIconLandmark EQU $cf21
DEF NT_wTownMapCursorLandmark     EQU $cf22
DEF NT_hJoyPressed     EQU $ffa9
DEF NT_hWY             EQU $ffd4
DEF NT_TITLE_COORD     EQU $c3a0   ; hlcoord 0, 0
DEF wNestTime          EQU $def4   ; 使われていない WRAM（むしよけの $def2・$def3 の 次）
DEF wNestKanto         EQU $def5
DEF NT_BANK            EQU $45
DEF NT_ADDR            EQU $5800
ENDC

; ---- 草むらの 表
SECTION "nesttime grass hook", ROMX[NT_GRASS_HOOK], BANK[NT_FINDNEST_BANK]
	call NestTime_Grass
	nop
	nop

SECTION "nesttime grass", ROMX[NT_FINDNEST_FREE], BANK[NT_FINDNEST_BANK]
; hl = 表の 2バイトめ（マップの 番号の 次）→ hl = 見はじめる 所の 1つ前、a = 見る 数
NestTime_Grass:
	inc hl
	inc hl
	inc hl
	ld a, [wNestTime]
	and a
	ld a, 7 * 3
	ret z
	push bc
	ld bc, 7 * 2
	ld a, [wNestTime]
.offset
	dec a
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

SECTION "nesttime loop", ROMX[NT_AREA_FREE1], BANK[NT_AREA_BANK]
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

SECTION "nesttime title", ROMX[NT_AREA_FREE2], BANK[NT_AREA_BANK]
NestTime_Title:
	call NT_PlaceString
	ld a, BANK(NestTime_DrawTitle)
	ld hl, NestTime_DrawTitle
	rst $08
	ret

SECTION "nesttime", ROMX[NT_ADDR], BANK[NT_BANK]
; キャリー：作りなおす
NestTime_Input:
	ld a, [wNestKanto]
	and a
	jr z, .input
	xor a
	ld [wNestKanto], a
	ld a, NT_AREA_BANK                ; 前に カントーを 見て いた
	ld hl, NT_RIGHT
	rst $08
.input
	ldh a, [NT_hJoyPressed]
	and 1 << 3                        ; START
	ret z                             ; キャリーなし
	ld a, [wNestTime]
	inc a
	and 3
	ld [wNestTime], a
	ldh a, [NT_hWY]
	and a
	jr nz, .johto
	ld a, 1
	ld [wNestKanto], a
.johto
	call NT_ClearSprites
	scf
	ret

; わくを 右に のばして 時間帯を かく（ぜんぶ の ときは なにも しない）
NestTime_DrawTitle:
	ld a, [wNestTime]
	and a
	ret z
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
	ld a, [wNestTime]
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
