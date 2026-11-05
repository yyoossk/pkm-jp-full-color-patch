; 技を思い出させる人：銀 日本版（後期版）。src/moverelearn.asm（金）から 作った もの（tools なしで 手で 置きかえ：jp_all_silver・LearnMove・置き場所）
; わざを おもいださせて くれる 人（金 日本版）
;
; ・フスベシティの「わざわすれの いえ」（わざを わすれさせて くれる 人の 家）に もう ひとり 置く
;   （ハートゴールド・ソウルシルバーと 同じく、わすれさせる 人と おもいださせる 人が 同じ 家に いる）。
; ・ポケモンを えらぶと、いまの レベルまでに レベルで おぼえる わざの うち、いま おぼえて いない わざを 出す。
;   えらんだ わざを おぼえさせる（4つ あれば わすれる わざを えらぶ。元の LearnMove と 同じ）。お金は いらない。
; ・タマゴは えらべない。おもいだせる わざが なければ そう 言う。
;
; しくみ
;   ・MoveDeletersHouse_MapAttributes の スクリプト・イベントを この バンクの 新しい 表に かえる。
;     元の わざわすれの 人（special MoveDeletion）と 本だなの スクリプトも この バンクに 写した（同じ 中身）。
;   ・手もちを えらぶ：SelectMonFromParty（farcall）。わざの 表：EvosAttacksPointers（進化の あとの レベルと わざ）。
;   ・わざの えらび方：ScrollingMenu（SCROLLINGMENU_ITEMS_NORMAL。表は wBufferMon の 場所を 使う）。
;   ・おぼえる：LearnMove（predef LearnMove と 同じ 所を farcall）。
;
; 銀・クリスタルに 入れるとき：下の DEF を その ROM の 値に する

INCLUDE "includes.asm"
INCLUDE "src/jp_all_silver.inc"
INCLUDE "src/charmap_jp.inc"

IF !DEF(MR_ATTR)
DEF MR_ATTR             EQU $5d29   ; MoveDeletersHouse_MapAttributes（バンク$25）
DEF MR_ATTR_BANK        EQU $25
DEF MR_SPECIAL_MOVEDELETION EQU $21 ; 日本版 金の special の 番号（元の スクリプトの「0f 21 00」）
DEF MR_STD_BOOKSHELF    EQU $0001   ; 本だなの jumpstd の 番号（元の「0c 01 00」）
DEF MR_EVOSATTACKS      EQU $695f   ; EvosAttacksPointers
DEF MR_EVOSATTACKS_BANK EQU $10
DEF MR_LEARNMOVE        EQU $67ae   ; LearnMove（銀。金は $67e9）
DEF MR_LEARNMOVE_BANK   EQU $01
DEF MR_SELECTMON        EQU $4000   ; SelectMonFromParty
DEF MR_SELECTMON_BANK   EQU $14
DEF MR_InitScrollingMenu EQU $36d8
DEF MR_ScrollingMenu    EQU $36b5
DEF MR_LIST             EQU wBufferMon   ; わざの 表（数・わざ…・$ff）
DEF MR_BANK             EQU $47   ; 新しい バンク（銀の 2MB の 空き）
DEF MR_ADDR             EQU $4800
ENDC

SECTION "moverelearn attributes", ROMX[MR_ATTR + 6], BANK[MR_ATTR_BANK]
	db BANK(MoveRelearnHouse_MapScripts)
	dw MoveRelearnHouse_MapScripts
	dw MoveRelearnHouse_MapEvents

SECTION "moverelearn", ROMX[MR_ADDR], BANK[MR_BANK]
MoveRelearnHouse_MapScripts:
	def_scene_scripts
	def_callbacks

MoveRelearnHouse_Deleter:            ; 元の わざわすれの 人（同じ 中身）
	faceplayer
	opentext
	db special_command
	dw MR_SPECIAL_MOVEDELETION
	waitbutton
	closetext
	end

MoveRelearnHouse_Bookshelf:          ; 元の 本だな（同じ 中身）
	db jumpstd_command
	dw MR_STD_BOOKSHELF

MoveRelearnHouse_MapEvents:
	db 0, 0
	def_warp_events
	warp_event  2,  7, BLACKTHORN_CITY, 6
	warp_event  3,  7, BLACKTHORN_CITY, 6
	def_coord_events
	def_bg_events
	bg_event  0,  1, BGEVENT_READ, MoveRelearnHouse_Bookshelf
	bg_event  1,  1, BGEVENT_READ, MoveRelearnHouse_Bookshelf
	def_object_events
	object_event  2,  3, SPRITE_SUPER_NERD, SPRITEMOVEDATA_STANDING_DOWN, 0, 0, -1, -1, 0, OBJECTTYPE_SCRIPT, 0, MoveRelearnHouse_Deleter, -1
	object_event  5,  4, SPRITE_GRANNY, SPRITEMOVEDATA_STANDING_DOWN, 0, 0, -1, -1, 0, OBJECTTYPE_SCRIPT, 0, MoveRelearnerScript, -1

MoveRelearnerScript:
	faceplayer
	opentext
	writetext MoveRelearner_IntroText
	yesorno
	iffalse .no
	writetext MoveRelearner_WhichMonText
	promptbutton
	callasm MoveRelearner_SelectMon
	iffalse .no
	ifequal 2, .egg
	callasm MoveRelearner_MakeList
	iffalse .none
	writetext MoveRelearner_WhichMoveText
	callasm MoveRelearner_Menu
	iffalse .no
	callasm MoveRelearner_Teach
	iffalse .no
	writetext MoveRelearner_DoneText
	waitbutton
	closetext
	end
.egg
	writetext MoveRelearner_EggText
	waitbutton
	closetext
	end
.none
	writetext MoveRelearner_NoneText
	waitbutton
	closetext
	end
.no
	writetext MoveRelearner_ComeAgainText
	waitbutton
	closetext
	end

; wScriptVar：0 = やめた、1 = えらんだ、2 = タマゴ
MoveRelearner_SelectMon:
	ld a, MR_SELECTMON_BANK
	ld hl, MR_SELECTMON
	rst $08
	ld a, 0
	jr c, .set
	ld a, [wCurPartySpecies]
	cp EGG
	ld a, 2
	jr z, .set
	ld a, 1
.set
	ld [wScriptVar], a
	ret

; MR_LIST に おもいだせる わざを 入れる。wScriptVar = その 数
MoveRelearner_MakeList:
	ld hl, MR_LIST
	xor a
	ld [hli], a
	ld [hl], -1
	; レベル
	ld a, MON_LEVEL
	call J_GetPartyParamLocation
	ld a, [hl]
	ld [wCurPartyLevel], a
	; わざの 表
	ld a, [wCurPartySpecies]
	dec a
	ld c, a
	ld b, 0
	ld hl, MR_EVOSATTACKS
	add hl, bc
	add hl, bc
	ld a, MR_EVOSATTACKS_BANK
	call J_GetFarByte
	ld e, a
	inc hl
	ld a, MR_EVOSATTACKS_BANK
	call J_GetFarByte
	ld d, a
	ld h, d
	ld l, e
.skip_evos
	ld a, MR_EVOSATTACKS_BANK
	call J_GetFarByte
	inc hl
	and a
	jr nz, .skip_evos
.loop
	ld a, MR_EVOSATTACKS_BANK
	call J_GetFarByte                ; レベル
	inc hl
	and a
	jr z, .done
	ld b, a
	ld a, MR_EVOSATTACKS_BANK
	call J_GetFarByte                ; わざ
	inc hl
	ld c, a
	ld a, [wCurPartyLevel]
	cp b
	jr c, .loop                      ; まだ おぼえない レベル
	push hl
	call .add
	pop hl
	jr .loop
.done
	ld a, [MR_LIST]
	ld [wScriptVar], a
	ret

; c = わざ：おぼえて いなくて、表に まだ なければ 足す
.add
	push bc
	ld a, MON_MOVES
	call J_GetPartyParamLocation
	pop bc
	ld b, NUM_MOVES
.known
	ld a, [hli]
	cp c
	ret z
	dec b
	jr nz, .known
	ld hl, MR_LIST
	ld a, [hli]
	ld b, a
	and a
	jr z, .append
.inlist
	ld a, [hli]
	cp c
	ret z
	dec b
	jr nz, .inlist
.append
	ld [hl], c
	inc hl
	ld [hl], -1
	ld hl, MR_LIST
	inc [hl]
	ret

; わざを えらぶ。wScriptVar = 1（wPutativeTMHMMove に わざ）/ 0（やめた）
; 自分で かく 一覧（5つ ずつ 見える。上下で えらぶ・はしで スクロール。A で きめる・B で やめる）
DEF MR_ROWS EQU 5
DEF wMRCursor EQU wBufferMon + 30    ; 一覧の 中の いまの 番号（0〜）
DEF wMRScroll EQU wBufferMon + 31    ; 上に 見えて いる 番号
MoveRelearner_Menu:
	ld hl, .MenuHeader
	call J_LoadMenuHeader            ; 画面を とっておく（ExitMenu で もどす）
	xor a
	ld [wMRCursor], a
	ld [wMRScroll], a
	; 一覧の さいごに「やめる」（$ff）を 足す：数を 1 ふやす
	ld hl, MR_LIST
	inc [hl]
.redraw
	call .Draw
.loop
	call J_DelayFrame
	call J_GetJoypad
	ldh a, [hJoyPressed]
	bit B_PAD_A, a
	jr nz, .a
	bit B_PAD_B, a
	jr nz, .cancel
	bit B_PAD_UP, a
	jr nz, .up
	bit B_PAD_DOWN, a
	jr nz, .down
	jr .loop
.up
	ld a, [wMRCursor]
	and a
	jr z, .loop
	dec a
	ld [wMRCursor], a
	ld b, a
	ld a, [wMRScroll]
	cp b
	jr c, .redraw
	jr z, .redraw
	ld a, b
	ld [wMRScroll], a
	jr .redraw
.down
	ld a, [MR_LIST]
	ld b, a
	ld a, [wMRCursor]
	inc a
	cp b
	jr nc, .loop
	ld [wMRCursor], a
	ld b, a
	ld a, [wMRScroll]
	add MR_ROWS - 1
	cp b
	jr nc, .redraw
	ld a, b
	sub MR_ROWS - 1
	ld [wMRScroll], a
	jr .redraw
.a
	ld a, [wMRCursor]
	call .Item
	cp -1
	jr z, .cancel
	ld [wPutativeTMHMMove], a
	ld de, SFX_READ_TEXT_2
	call J_PlaySFX
	ld a, 1
	jr .done
.cancel
	xor a
.done
	ld [wScriptVar], a
	ld hl, MR_LIST
	dec [hl]
	call J_ExitMenu
	ret

; a = 一覧の 番号 → a = わざ（$ff = やめる）
.Item:
	ld hl, MR_LIST
	ld c, a
	ld a, [hl]
	dec a
	cp c
	ld a, -1
	ret z                            ; さいごは やめる
	ld b, 0
	inc hl
	add hl, bc
	ld a, [hl]
	ret

.Draw:
	xor a
	ldh [hBGMapMode], a
	call J_MenuBox                   ; .MenuHeader の わく（VerticalMenu と 同じ かき方）
	call J_UpdateSprites             ; わくの 下の 人を かくす
	ld a, [wMRScroll]
	ld b, a                          ; b = 番号
	hlcoord 2, 2
	ld c, MR_ROWS
.drawloop
	ld a, [MR_LIST]
	dec b
	inc b
	cp b
	jr z, .drawn
	jr c, .drawn
	push bc
	push hl
	ld a, b
	call .Item
	cp -1
	jr z, .drawcancel
	ld [wNamedObjectIndex], a
	call J_GetMoveName
	jr .place
.drawcancel
	ld de, .CancelString
.place
	pop hl
	push hl
	call J_PlaceString
	pop hl
	ld bc, 2 * SCREEN_WIDTH
	add hl, bc
	pop bc
	inc b
	dec c
	jr nz, .drawloop
.drawn
	; カーソル
	ld a, [wMRCursor]
	ld b, a
	ld a, [wMRScroll]
	ld c, a
	ld a, b
	sub c
	add a                            ; ×2 行
	ld bc, SCREEN_WIDTH
	hlcoord 1, 2
.cur
	and a
	jr z, .curok
	add hl, bc
	dec a
	jr .cur
.curok
	ld [hl], $ed                     ; ▶
	; 下に まだ あれば ▼
	ld a, [wMRScroll]
	add MR_ROWS
	ld b, a
	ld a, [MR_LIST]
	cp b
	jr c, .noarrow
	jr z, .noarrow
	hlcoord 18, 11
	ld [hl], $ee                     ; ▼
.noarrow
	jp J_ApplyTilemap                ; 色（ウインドウの 色・人の 前）も いっしょに

.MenuHeader:
	db MENU_BACKUP_TILES
	menu_coords 0, 0, SCREEN_WIDTH - 1, 11
	dw 0
	db 1

.CancelString:
	db "やめる@"

; えらんだ わざを おぼえさせる。wScriptVar = 1（おぼえた）/ 0
MoveRelearner_Teach:
	ld a, [wPutativeTMHMMove]
	ld [wNamedObjectIndex], a
	call J_GetMoveName
	call J_CopyName1                 ; わざの 名前 → wStringBuffer2
	; クリスタルの MoveTutor と 同じく、メニューの 画面で おぼえさせて マップに もどる
	; （フィールドの まま LearnMove の わすれる わざの 画面を 出すと マップの 絵が くずれるため）
	call J_FadeToMenu
	call J_ClearBGPalettes
	call J_ClearScreen
	call J_DelayFrame
	ld b, SCGB_MOVE_LIST
	call J_GetSGBLayout
	ld a, MR_LEARNMOVE_BANK
	ld hl, MR_LEARNMOVE
	rst $08
	push bc
	call J_CloseSubmenu
	pop bc
	ld a, b
	and a
	jr z, .set
	ld a, 1
.set
	ld [wScriptVar], a
	ret

MoveRelearner_IntroText:
	db $00, "わたしは　わすれた　わざを", $4f
	db "おもいださせて　あげられるのよ", $51
	db "おもいださせて　ほしい", $4f
	db "わざが　あるかい？", $57
MoveRelearner_WhichMonText:
	db $00, "どの　ポケモンに", $4f
	db "おもいださせるんだい？", $57
MoveRelearner_WhichMoveText:
	db $00, "どの　わざを", $4f
	db "おもいださせるんだい？", $57
MoveRelearner_EggText:
	db $00, "タマゴは　まだ　わざを", $4f
	db "おもいだせないよ", $57
MoveRelearner_NoneText:
	db $00, "その　ポケモンが", $4f
	db "おもいだせる　わざは", $55
	db "ないみたいだねえ", $57
MoveRelearner_DoneText:
	db $00, "また　いつでも", $4f
	db "おいでなさいね", $57
MoveRelearner_ComeAgainText:
	db $00, "そうかい", $4f
	db "また　いつでも　おいで", $57
