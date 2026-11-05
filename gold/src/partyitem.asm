; 手持ちの 画面で、カーソルの ポケモンが 持って いる 道具の 名前を 出す（金 日本版）
;
; ・手持ちを えらぶ 画面で、カーソルを あわせた ポケモンの 道具を 下の 文の わくの 上に
;     もちもの／きせきのタネ      （持って いない ときは「もちもの／なし」）
;   と 出す。「やめる」に あわせた ときは 出さない。タマゴは 出さない。
;   （元は 小さな 印が 出る だけ で、何を 持って いるかは つよさの 画面で しか 見られなかった）
;
; しくみ
;   ・手持ちの 画面の アイコンの うごき（AnimSeq_PartyMon。アイコン ごとに まいフレーム）の
;     さいしょの「ld a, [wMenuCursorY]」を バンク$23 の 空きの PartyItem_Stub の call に。
;     PartyItem_Stub は 新しい バンクの PartyItem を farcall して から 元の ld a を する。
;   ・PartyItem は、手持ちの 画面の メニュー（2DMenu の CursorInitY 1・CursorInitX 0・NumCols 1）の ときだけ、
;     カーソル（wMenuCursorY）が かわった か、文字が まだ ない（画面を かきなおした）ときに hlcoord 6, 13 に かく
;     （濁点は 12行め）。6ぴき いる ときの「やめる」（hlcoord 1, 13）とも かさならない。
;     この 画面の メニューは hBGMapMode が 0 の ままなので、かいた 2行は すぐ VRAM の BG マップ（$9800〜）にも 写す
;     （STAT を 見て 1バイトずつ）。
;     わざの 画面などの メニューを ひらいて いる 間は（CursorInit が ちがうので）何も しない。
;   ・メニュー（わざ・どうぐ・いれかえ など）を ひらく 前に 道具の 名前を けす（LoadMenuHeader の call CopyMenuHeader を
;     ROM0 の 空き（$2dd2。どこからも 呼ばれない DummyEndPredef）の PartyItem_MenuStub に。手持ちの 画面の メニューの とき だけ）。けさないと、メニューの わくの
;     左に「もちもの／な」の ように はみ出して 見えて いた。とじると 画面が もどり、アイコンの うごきの 所で かきなおす。
;   ・前の カーソルは セーブの 使われていない 所（$d7a2）。
;
; 銀・クリスタルに 入れるとき：下の DEF を その ROM の 値に する
;   （クリスタルは 手持ちの 画面の 下の わくの 場所が 同じか 確かめる）

INCLUDE "src/charmap_jp.inc"

IF !DEF(PI_HOOK)
DEF PI_HOOK            EQU $52ed      ; バンク$23 AnimSeq_PartyMon の ld a, [wMenuCursorY]
DEF PI_HOOK_BANK       EQU $23
DEF PI_STUB            EQU $7f80      ; バンク$23 の 空き
DEF PI_GetItemName     EQU $360a
DEF PI_PlaceString     EQU $0f46
DEF PI_w2DMenuCursorInitY EQU $cf0c
DEF PI_w2DMenuCursorInitX EQU $cf0d
DEF PI_w2DMenuNumCols  EQU $cf0f
DEF PI_wMenuCursorY    EQU $cf14
DEF PI_wPartyCount     EQU $d9e8
DEF PI_wPartySpecies   EQU $d9e9
DEF PI_wPartyMon1Item  EQU $d9f1
DEF PI_MONLEN          EQU $30
DEF PI_EGG             EQU $fd
DEF PI_wNamedObjectIndex EQU $d143
DEF PI_wStringBuffer1  EQU $cf87
DEF PI_COORD           EQU $c3a0 + 13 * 20 + 6   ; hlcoord 6, 13
DEF wPILast            EQU $d7a2
DEF PI_MENU_HOOK       EQU $1b59      ; ROM0 LoadMenuHeader の call CopyMenuHeader
DEF PI_CopyMenuHeader  EQU $1b60
DEF PI_ROM0_FREE       EQU $2dd2      ; ROM0 の 空き（DummyEndPredef。どこからも 呼ばれない nop 16こ）
DEF PI_BANK            EQU $45
DEF PI_ADDR            EQU $7500
DEF PI_TEXT_HOOK       EQU $4436      ; バンク$14 PlacePartyMenuText の おわりの pop af / ld [wOptions], a / ret
DEF PI_TEXT_BANK       EQU $14
DEF PI_TEXT_STUB       EQU $3f95      ; 金：バンク$14 に 空きが ないので ROM0 の 空き（$3f95〜$3f9f の 11バイト。60fps版でも 空き）
DEF PI_TEXT_STUB_ROM0  EQU 1
DEF PI_wOptions        EQU $d1ab
ENDC

SECTION "partyitem hook", ROMX[PI_HOOK], BANK[PI_HOOK_BANK]
	call PartyItem_Stub
SECTION "partyitem stub", ROMX[PI_STUB], BANK[PI_HOOK_BANK]
PartyItem_Stub:
	push bc
	ld a, BANK(PartyItem)
	ld hl, PartyItem
	rst $08
	pop bc
	ld a, [PI_wMenuCursorY]
	ret

; メニューを ひらく とき（LoadMenuHeader）：手持ちの 画面の 上に わざ・どうぐ などの メニューが ひらく なら、
; 先に 道具の 名前を けして おく（けさないと メニューの わくの 左に「もちもの／な」の ように はみ出して 見える。
; メニューを とじると けした 画面が もどるので、アイコンの うごきの 所で かきなおす）
IF DEF(PI_wMenuHeader)
; クリスタル：戦闘の 手持ちの メニュー（いれかえる・つよさをみる）などは LoadMenuHeader を 通らず CopyMenuHeader を
; じかに 呼ぶので、CopyMenuHeader の 頭（ld de, wMenuHeader の 3バイト）を つなぐ（PI_wMenuHeader を 決めた とき）。
; CopyMenuHeader は bc・de を こわすので、hl だけ とって おけば よい
SECTION "partyitem menu hook", ROM0[PI_CopyMenuHeader]
	jp PartyItem_MenuStub
SECTION "partyitem menu stub", ROM0[PI_ROM0_FREE]
PartyItem_MenuStub:
	push hl
	ld a, BANK(PartyItem_BeforeMenu)
	ld hl, PartyItem_BeforeMenu
	rst $08
	pop hl
	ld de, PI_wMenuHeader             ; 元の 命令
	jp PI_CopyMenuHeader + 3
ELSE
SECTION "partyitem menu hook", ROM0[PI_MENU_HOOK]
	call PartyItem_MenuStub
SECTION "partyitem menu stub", ROM0[PI_ROM0_FREE]
PartyItem_MenuStub:
	push bc
	push de
	push hl
	ld a, BANK(PartyItem_BeforeMenu)
	ld hl, PartyItem_BeforeMenu
	rst $08
	pop hl
	pop de
	pop bc
	jp PI_CopyMenuHeader
ENDC

; 手持ちの 画面を ひらく とき：PlacePartyMenuText（下の 文の わく）の おわりで 道具の 名前も かく（PI_TEXT_HOOK を 決めた とき）。
; アイコンの うごきの 所 だけ だと、画面が 出て から 4フレーム ほど おくれて「もちもの／…」が 出て いた。
; PlacePartyMenuText の おわりの「pop af / ld [wOptions], a / ret」（5バイト）を つなぐ
IF DEF(PI_TEXT_HOOK)
SECTION "partyitem text hook", ROMX[PI_TEXT_HOOK], BANK[PI_TEXT_BANK]
	jp PartyItem_TextStub
	nop
	nop
IF DEF(PI_TEXT_STUB_ROM0)
SECTION "partyitem text stub", ROM0[PI_TEXT_STUB]
ELSE
SECTION "partyitem text stub", ROMX[PI_TEXT_STUB], BANK[PI_TEXT_BANK]
ENDC
PartyItem_TextStub:
	pop af
	ld [PI_wOptions], a
	ld a, BANK(PartyItem)
	ld hl, PartyItem
	rst $08
	ret
ENDC

SECTION "partyitem", ROMX[PI_ADDR], BANK[PI_BANK]
PartyItem:
	; 手持ちの 画面の メニュー？
	ld a, [PI_w2DMenuCursorInitY]
	dec a
	jp nz, PartyItem_Hide
	ld a, [PI_w2DMenuCursorInitX]
	and a
	jp nz, PartyItem_Hide
	ld a, [PI_w2DMenuNumCols]
	dec a
	jp nz, PartyItem_Hide
	ld a, [PI_wMenuCursorY]
	ld b, a
	ld a, [wPILast]
	cp b
	jr nz, .draw
	; 同じ カーソル：もう かいて あれば なにも しない（「やめる」・タマゴ は かかない）
	ld a, [PI_COORD]
	cp $d3                            ; も
	ret z
	ld a, [PI_wPartyCount]
	cp b
	ret c
	ld a, b
	dec a
	ld e, a
	ld d, 0
	ld hl, PI_wPartySpecies
	add hl, de
	ld a, [hl]
	cp PI_EGG
	ret z
.draw
	ld a, b
	ld [wPILast], a
	; けす（12・13行め の x 6〜18）
	ld hl, PI_COORD - 20
	ld a, $7f
	ld c, 13
.clear1
	ld [hli], a
	dec c
	jr nz, .clear1
	ld hl, PI_COORD
	ld c, 13
.clear2
	ld [hli], a
	dec c
	jr nz, .clear2
	; やめる？
	ld a, [PI_wPartyCount]
	cp b
	jr c, PartyItem_Show
	ld a, b
	dec a
	ld c, a
	ld e, a
	ld d, 0
	ld hl, PI_wPartySpecies
	add hl, de
	ld a, [hl]
	cp PI_EGG
	jr z, PartyItem_Show
	ld hl, PI_wPartyMon1Item
	ld de, PI_MONLEN
	ld a, c
	and a
	jr z, .got
.mon
	add hl, de
	dec c
	jr nz, .mon
.got
	ld a, [hl]
	push af
	ld hl, PI_COORD
	ld de, .Label
	call PI_PlaceString
	pop af
	ld de, .None
	and a
	jr z, .put
	ld [PI_wNamedObjectIndex], a
	call PI_GetItemName
	ld de, PI_wStringBuffer1
.put
	ld hl, PI_COORD + 5
	call PI_PlaceString
	; fallthrough

; 12・13行めの x 6〜18 を すぐ 画面（BG マップ $9800）に 写す（この 画面の メニューは hBGMapMode が 0 の ままなので）
PartyItem_Show:
	ld hl, PI_COORD - 20
	ld de, $9800 + 12 * 32 + 6
	call .row
	ld hl, PI_COORD
	ld de, $9800 + 13 * 32 + 6
.row
	ld c, 13
.loop
	ld b, [hl]
	inc hl
	di
.wait
	ldh a, [$ff41]
	and 2
	jr nz, .wait
	ld a, b
	ld [de], a
	ei
	inc de
	dec c
	jr nz, .loop
	ret

; LoadMenuHeader から：手持ちの 画面の メニューの まま で、道具の 名前（「もちもの／」）が かいて あれば けす
PartyItem_BeforeMenu:
	ld a, [PI_w2DMenuCursorInitY]
	dec a
	ret nz
	ld a, [PI_w2DMenuCursorInitX]
	and a
	ret nz
	ld a, [PI_w2DMenuNumCols]
	dec a
	ret nz
	ld hl, PI_COORD
	ld de, PartyItem.Label
	ld c, 5
.cmp
	ld a, [de]
	cp [hl]
	ret nz
	inc de
	inc hl
	dec c
	jr nz, .cmp
	ld a, $ff
	ld [wPILast], a
	ld hl, PI_COORD - 20
	ld a, $7f
	ld c, 13
.c1
	ld [hli], a
	dec c
	jr nz, .c1
	ld hl, PI_COORD
	ld c, 13
.c2
	ld [hli], a
	dec c
	jr nz, .c2
	jp PartyItem_Show

; わざ・どうぐ などの メニューが 手持ちの 画面の 上に ひらいた とき（アイコンの うごきが つづいて いる 場合）：その メニューの わくの 左に「もちもの／な」の ように
; 文字が はみ出して 見えるので、わくの 線（$79〜$7e）の 手前まで 空白に する（メニューを とじると 元の 画面が もどり、
; 文字は かきなおす）。メニューが 文字の 頭（x 6）まで かかって いる ときは 何も しない
PartyItem_Hide:
	ld a, [PI_COORD]
	cp $d3                            ; も（まだ 文字が ある）
	ret nz
	ld a, $ff
	ld [wPILast], a                   ; メニューを とじたら かきなおす
	ld hl, PI_COORD - 20
	call .row
	ld hl, PI_COORD
	call .row
	jp PartyItem_Show
.row
	ld c, 13
.loop
	ld a, [hl]
	cp $79
	jr c, .clear
	cp $7f
	ret c                             ; わくの 線
.clear
	ld [hl], $7f
	inc hl
	dec c
	jr nz, .loop
	ret

PartyItem.Label db "もちもの", $f3, "@"   ; ／
PartyItem.None db "なし@"
