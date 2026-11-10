; ずかんの 説明の ページで SELECT を おすと、タイプ・種族値・進化の しかたの ページに 切りかわる（銀 日本版。クリスタル追加機能キットの 57。src/dexinfo_crystal.asm を 銀に した もの）
; （ピカチュウ版フルカラーの「A で タイプ」に 種族値・進化を 足した もの。つかまえた ポケモンだけ）
;
; ・説明の 右下（18, 15）に「▼」。SELECT で つぎの ページ、さいごの ページの つぎは 説明に もどる。
;     1ページめ（もとの 説明）
;     2ページめ：タイプ（タイプ1／タイプ2）・たいりょく・こうげき・ぼうぎょ・すばやさ
;     3ページめ：とくこう・とくぼう・進化 2行（進化しない ポケモンは「しんかしない」）
;     4ページめ から：進化の のこり（3行ずつ。イーブイなど）
;   進化の 行：「なまえ　じょうけん」。じょうけんは レべル nn・どうぐの 名前・つうしん・なつく（ひる・よる）。
;   どうぐを もたせて つうしん（ヤドキング など）・こうげきと ぼうぎょで きまる（カポエラー など）は 2行めに
;   「もたせる　どうぐ」・「こうげきが　たかい」など。
;   文字は 説明の わく（1〜18, 10〜15。3行。濁点は 1行 上）の 中だけに かく。
; しくみ（銀。ずかんの 説明の 画面の 作りと 場所は クリスタルと 同じ）
;   ・Pokedex_UpdateDexEntryScreen の「ld hl, hJoyPressed / B を 見る / A を 見る」（$10:$41d9〜$41e5、13バイト）を
;     DexInfo_Joy への farcall に：B なら キャリー、A なら nz で もどり（farcall は フラグを のこす）、SELECT なら ページを かえる。
;     （バンク$10 に 空きが ないので）
;   ・説明の 画面を かく 3か所の farcall DisplayDexEntry（$10:$41b2・$4222・$42d2）を DexInfo_Entry に：説明を かいて ▼、ページを 0 に。
;   ・ページと ポケモンは 使われていない WRAM の $deeb・$deec（金銀は WRAM の バンクを 切りかえない）。
;   ・種族値・タイプは BaseData（$14:$5aa9。32バイトずつ）、進化は EvosAttacksPointers（$10:$695f）から GetFarByte で 読む。

INCLUDE "src/charmap_jp.inc"

DEF DI_BANK              EQU $43
DEF DI_ADDR              EQU $5b80
DEF DI_wTilemap          EQU $c3a0
DEF DI_wPrevDexEntry     EQU $c1d5
DEF DI_wPokedexCaught    EQU $db78
DEF DI_wNamedObjectIndex EQU $d143
DEF DI_wStringBuffer1    EQU $cf87
DEF DI_TMP               EQU $cf9e     ; wStringBuffer2（$cf92）＋ 12〜（ページを かく 間 だけ）
DEF DI_PAGE              EQU $deeb     ; 使われていない WRAM
DEF DI_SPECIES           EQU $deec
DEF DI_DisplayDexEntry_BANK EQU $11
DEF DI_DisplayDexEntry   EQU $4267
DEF DI_WaitBGMap         EQU $33ae
DEF DI_PlaceString       EQU $0f46
DEF DI_PrintNum          EQU $31f9
DEF DI_GetFarByte        EQU $30e4
DEF DI_GetPokemonName    EQU $35e0
DEF DI_GetItemName       EQU $360a
DEF DI_Predef            EQU $2e05
DEF DI_PREDEF_PRINTTYPE  EQU $2b
DEF DI_BASEDATA_BANK     EQU $14
DEF DI_BaseData          EQU $5aa9
DEF DI_EVOS_BANK         EQU $10
DEF DI_EvosAttacksPointers EQU $695f
DEF DI_ARROW             EQU $ee       ; ▼

MACRO dicoord ; x, y
	ld hl, DI_wTilemap + (\2) * 20 + (\1)
ENDM

; Pokedex_UpdateDexEntryScreen の ld hl, hJoyPressed 〜 A を 見る 所（$10:$41d9〜$41e5）
SECTION "dexinfo joypad hook", ROMX[$41d9], BANK[$10]
	ld a, BANK(DexInfo_Joy)
	ld hl, DexInfo_Joy
	rst $08
	jr c, @ + $41f8 - $41df          ; B → .return_to_prev_screen（$41f8）
	jr nz, @ + $41ee - $41e1         ; A → .do_menu_action（$41ee）
	nop
	nop
	nop
MACRO di_entry_hook ; 場所
SECTION "dexinfo entry hook \1", ROMX[\1], BANK[$10]
	ld a, BANK(DexInfo_Entry)
	ld hl, DexInfo_Entry
	rst $08
ENDM
	di_entry_hook $41b2              ; Pokedex_InitDexEntryScreen
	di_entry_hook $4222              ; Pokedex_ReinitDexEntryScreen
	di_entry_hook $42d2              ; ぶんぷ・なきごえ などから もどる
SECTION "dexinfo", ROMX[DI_ADDR], BANK[DI_BANK]
; ボタン：B ＝ キャリー、A ＝ nz（キャリーなし）、ほか ＝ z（SELECT なら ページを かえる）
DexInfo_Joy:
	ldh a, [$ffa9]                   ; hJoyPressed
	bit 1, a                         ; B
	jr nz, .b
	bit 2, a                         ; SELECT
	jr nz, .select
	and $01                          ; A（nz）・なにも なし（z）。キャリーなし
	ret
.b
	scf
	ret
.select
	call DexInfo_Select
	xor a                            ; z・キャリーなし
	ret

; 説明を かく（もとの farcall の かわり）＋ ▼・ページを 0 に
DexInfo_Entry:
	ld a, DI_DisplayDexEntry_BANK
	ld hl, DI_DisplayDexEntry
	rst $08
	xor a
	call DI_SetPage
	jp DI_Arrow

; SELECT：つぎの ページ
DexInfo_Select:
	call DI_Caught
	ret nc
	call DI_GetPage                  ; a ＝ ページ（ポケモンが かわって いれば 0）
	inc a
	push af
	ld a, $ff
	call DI_Layout                   ; c ＝ ページの 数
	pop af
	cp c
	jr c, .ok
	xor a
.ok
	push af
	call DI_SetPage
	pop af
	and a
	jr nz, .draw
	call DI_Clear
	ld a, [DI_wPrevDexEntry]
	ld [DI_wNamedObjectIndex], a     ; DisplayDexEntry は これを 見る（進化の 名前で かわって いる）
	ld a, DI_DisplayDexEntry_BANK
	ld hl, DI_DisplayDexEntry
	rst $08
	jr .done
.draw
	push af
	call DI_Clear
	pop af
	dec a
	jr z, .page1
	dec a
	jr z, .page2
	; 4ページめ から：進化（3行）
	add 2                            ; a ＝ ページ − 2 → ページ
	call DI_Layout
	jr .done
.page1
	call DI_Page1
	jr .done
.page2
	call DI_Page2
.done
	ld a, [DI_wPrevDexEntry]
	ld [DI_wNamedObjectIndex], a     ; もとに もどす
	call DI_Arrow
	jp DI_WaitBGMap

; キャリー ＝ いまの ポケモンを つかまえて いる
DI_Caught:
	ld a, [DI_wPrevDexEntry]
	dec a
	ld c, a
	srl a
	srl a
	srl a
	ld e, a
	ld d, 0
	ld hl, DI_wPokedexCaught
	add hl, de
	ld a, c
	and 7
	ld b, a
	ld a, [hl]
	inc b
.shift
	dec b
	jr z, .bit
	rrca
	jr .shift
.bit
	rrca                             ; ビット 0 → キャリー
	ret

DI_GetPage:
	ld a, [DI_wPrevDexEntry]
	ld b, a
	ld a, [DI_SPECIES]
	cp b
	ld a, 0
	jr nz, .got
	ld a, [DI_PAGE]
.got
	ret

DI_SetPage:                          ; a ＝ ページ
	ld [DI_PAGE], a
	ld a, [DI_wPrevDexEntry]
	ld [DI_SPECIES], a
	ret

; ▼（つかまえて いて、（18, 15）が あいて いる とき）
DI_Arrow:
	call DI_Caught
	ret nc
	dicoord 18, 15
	ld a, [hl]
	cp $7f
	ret nz
	ld [hl], DI_ARROW
	ret

; 説明の わく（1〜18, 10〜15）を けす
DI_Clear:
	dicoord 1, 10
	ld b, 6
.row
	ld c, 18
	ld a, $7f
.col
	ld [hli], a
	dec c
	jr nz, .col
	ld de, 2
	add hl, de
	dec b
	jr nz, .row
	ret

; BaseData の b バイトめ → a
DI_Base:
	ld a, [DI_wPrevDexEntry]
	dec a
	ld l, a
	ld h, 0
	add hl, hl
	add hl, hl
	add hl, hl
	add hl, hl
	add hl, hl                       ; × 32
	ld c, b
	ld b, 0
	add hl, bc
	ld bc, DI_BaseData
	add hl, bc
	ld a, DI_BASEDATA_BANK
	jp DI_GetFarByte

; hl ＝ 数の 場所、b ＝ BaseData の バイト（3けた）
DI_Stat:
	push hl
	call DI_Base
	ld [DI_TMP], a
	pop hl
	ld de, DI_TMP
	ld bc, $0103
	jp DI_PrintNum

; de ＝ 文、hl ＝ 場所
DI_Str:
	jp DI_PlaceString

DI_Page1:
	dicoord 1, 11
	ld de, .Type
	call DI_Str
	ld b, 7
	call DI_Base
	ld [DI_TMP + 1], a
	ld b, a
	dicoord 5, 11
	ld a, DI_PREDEF_PRINTTYPE
	call DI_Predef
	ld b, 8
	call DI_Base
	ld b, a
	ld a, [DI_TMP + 1]
	cp b
	jr z, .one
	push bc
	call DI_TypeLen                  ; タイプ1 の 名前の 長さ → c
	ld hl, DI_wTilemap + 11 * 20 + 5
	ld b, 0
	add hl, bc
	ld [hl], $f3                     ; ／（タイプ1 の すぐ うしろ）
	inc hl
	pop bc
	ld a, DI_PREDEF_PRINTTYPE
	call DI_Predef
.one
	dicoord 1, 13
	ld de, .HP
	call DI_Str
	dicoord 6, 13
	ld b, 1
	call DI_Stat
	dicoord 10, 13
	ld de, .Atk
	call DI_Str
	dicoord 15, 13
	ld b, 2
	call DI_Stat
	dicoord 1, 15
	ld de, .Def
	call DI_Str
	dicoord 6, 15
	ld b, 3
	call DI_Stat
	dicoord 10, 15
	ld de, .Spe
	call DI_Str
	dicoord 15, 15
	ld b, 4
	jp DI_Stat
.Type db "タイプ@"
.HP   db "たいりょく@"
.Atk  db "こうげき@"
.Def  db "ぼうぎょ@"
.Spe  db "すばやさ@"

; タイプ1（DI_TMP＋1）の 名前の 長さ（11行めに かいた 文字を 数える）→ c
DI_TypeLen:
	ld hl, DI_wTilemap + 11 * 20 + 5
	ld c, 0
.loop
	ld a, [hli]
	cp $7f
	ret z
	inc c
	jr .loop

DI_Page2:
	dicoord 1, 11
	ld de, .SpA
	call DI_Str
	dicoord 6, 11
	ld b, 5
	call DI_Stat
	dicoord 10, 11
	ld de, .SpD
	call DI_Str
	dicoord 15, 11
	ld b, 6
	call DI_Stat
	call DI_EvoPtr
	call DI_ReadEvo
	and a
	jr nz, .evo
	dicoord 1, 13
	ld de, .None
	jp DI_Str
.evo
	ld a, 2
	jp DI_Layout
.SpA  db "とくこう@"
.SpD  db "とくぼう@"
.None db "しんかしない@"

; 進化の データの 先頭 → hl（バンク DI_EVOS_BANK）
DI_EvoPtr:
	ld a, [DI_wPrevDexEntry]
	dec a
	ld l, a
	ld h, 0
	add hl, hl
	ld bc, DI_EvosAttacksPointers
	add hl, bc
	push hl
	ld a, DI_EVOS_BANK
	call DI_GetFarByte
	ld c, a
	pop hl
	inc hl
	ld a, DI_EVOS_BANK
	call DI_GetFarByte
	ld h, a
	ld l, c
	ret

DI_Byte:                             ; [hl+] → a（バンク DI_EVOS_BANK）
	push bc
	ld a, DI_EVOS_BANK
	call DI_GetFarByte
	inc hl
	pop bc
	ret

; 1つの 進化を 読む：hl → DI_TMP＋2 ＝ 種類、＋3 ＝ 1つめ、＋4 ＝ 2つめ（STAT だけ）、＋5 ＝ ポケモン。
; a ＝ 行の 数（1 か 2。0 ＝ おわり）
DI_ReadEvo:
	call DI_Byte
	ld [DI_TMP + 2], a
	and a
	ret z
	call DI_Byte
	ld [DI_TMP + 3], a
	ld a, [DI_TMP + 2]
	cp 5                             ; EVOLVE_STAT
	jr nz, .no2
	call DI_Byte
	ld [DI_TMP + 4], a
.no2
	call DI_Byte
	ld [DI_TMP + 5], a
	ld a, [DI_TMP + 2]
	cp 5
	ld a, 2
	ret z
	ld a, [DI_TMP + 2]
	cp 3                             ; EVOLVE_TRADE
	jr nz, .one
	ld a, [DI_TMP + 3]
	inc a
	ld a, 2
	ret nz                           ; どうぐを もたせる
.one
	ld a, 1
	ret

; 進化を ページに わける（1つの 進化の 2行は おなじ ページに。3ページめ（2）は 2行、つぎから 3行）
; a ＝ かく ページ（$ff ＝ かかない）→ c ＝ ページの 数（3〜）
DI_Layout:
	ld [DI_TMP + 7], a               ; かく ページ
	ld a, 2
	ld [DI_TMP + 8], a               ; いまの ページ
	xor a
	ld [DI_TMP + 9], a               ; その ページで つかった 行
	call DI_EvoPtr
.loop
	call DI_ReadEvo
	and a
	jr z, .done
	ld b, a                          ; この 進化の 行の 数
	ld a, [DI_TMP + 8]
	cp 2
	ld c, 2
	jr z, .cap
	ld c, 3
.cap
	ld a, [DI_TMP + 9]
	add b
	cp c
	jr z, .fits
	jr c, .fits
	ld a, [DI_TMP + 8]               ; つぎの ページへ
	inc a
	ld [DI_TMP + 8], a
	xor a
	ld [DI_TMP + 9], a
.fits
	ld a, [DI_TMP + 8]
	ld c, a
	ld a, [DI_TMP + 7]
	cp c
	jr nz, .skip
	push hl
	push bc
	call DI_DrawEvo
	pop bc
	pop hl
.skip
	ld a, [DI_TMP + 9]
	add b
	ld [DI_TMP + 9], a
	jr .loop
.done
	ld a, [DI_TMP + 8]
	inc a
	ld c, a
	ret

; DI_TMP の 進化を かく（b ＝ 行の 数。場所 ＝ ページの 行 DI_TMP＋9）
DI_DrawEvo:
	push bc
	call DI_EvoRow
	call DI_EvoFirst
	pop bc
	dec b
	ret z
	ld a, [DI_TMP + 9]
	inc a
	ld [DI_TMP + 9], a
	call DI_EvoRow
	call DI_EvoSecond
	ld a, [DI_TMP + 9]
	dec a
	ld [DI_TMP + 9], a
	ret

; hl ＝ 行の 左（3ページめ は 13行めから、ほかは 11行めから。1行 ＝ 2）
DI_EvoRow:
	ld a, [DI_TMP + 8]
	cp 2
	ld a, [DI_TMP + 9]
	jr nz, .base
	inc a
.base
	ld hl, DI_wTilemap + 11 * 20 + 1
	and a
	ret z
	ld bc, 40
.add
	add hl, bc
	dec a
	jr nz, .add
	ret

; 1行め：なまえ（1）・じょうけん（7）
DI_EvoFirst:
	push hl
	ld a, [DI_TMP + 5]
	ld [DI_wNamedObjectIndex], a
	call DI_GetPokemonName
	pop hl
	push hl
	call DI_PlaceString
	pop hl
	ld bc, 6
	add hl, bc
	ld a, [DI_TMP + 2]
	cp 1
	jr z, .level
	cp 5
	jr z, .level
	cp 2
	jr z, .item
	cp 3
	jr z, .trade
	; なつく
	push hl
	ld de, .Happy
	call DI_PlaceString
	pop hl
	ld bc, 4
	add hl, bc
	ld a, [DI_TMP + 3]
	ld de, .Day
	cp 2
	jr z, .time
	ld de, .Nite
	cp 3
	ret nz
.time
	jp DI_PlaceString
.level
	push hl
	ld de, .Level
	call DI_PlaceString
	pop hl
	inc hl
	inc hl
	inc hl
	ld de, DI_TMP + 3
	ld bc, $4103                     ; 1バイト・ひだりよせ
	jp DI_PrintNum
.item
	push hl
	ld a, [DI_TMP + 3]
	ld [DI_wNamedObjectIndex], a
	call DI_GetItemName
	pop hl
	jp DI_PlaceString
.trade
	ld de, .Trade
	jp DI_PlaceString
.Happy db "なつく@"
.Day   db "ひる@"
.Nite  db "よる@"
.Level db "レべル@"
IF DEF(DI_TRADE251)
.Trade db "レべル", $f6 + 3, $f6 + 7, "@"     ; 251匹そろう版
ELSE
.Trade db "つうしん@"
ENDC

; 2行め（もたせる どうぐ・こうげきと ぼうぎょ）：hl ＝ 行の 左
DI_EvoSecond:
	inc hl
	ld a, [DI_TMP + 2]
	cp 3
	jr nz, .stat
	push hl
	ld de, .Hold
	call DI_PlaceString
	ld a, [DI_TMP + 3]
	ld [DI_wNamedObjectIndex], a
	call DI_GetItemName
	pop hl
	ld bc, 5
	add hl, bc
	jp DI_PlaceString
.stat
	ld a, [DI_TMP + 4]
	ld de, .AtkHi
	cp 1
	jr z, .put
	ld de, .DefHi
	cp 2
	jr z, .put
	ld de, .Same
.put
	jp DI_PlaceString
.Hold  db "もたせる@"
.AtkHi db "こうげきが　たかい@"
.DefHi db "ぼうぎょが　たかい@"
.Same  db "こうげきと　ぼうぎょが　おなじ@"
