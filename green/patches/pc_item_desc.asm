; パソコンの「どうぐを ひきだす」（と「どうぐを すてる」）の リストでも、カーソルの ある 道具の 説明を
; 下の わくに 出す（フレンドリィショップで 買う ときの 説明と 同じ 文・同じ 出し方。「やめる」では 何も 出さない）。
;
; 緑の ショップの 説明は、リストを 出す たびに よばれる 37:55C4 の 後ろ半分（37:55F3〜）に ある：
;   wListMenuID が 2（かう）なら、見る キーに 上下を 足し（上下でも HandleMenuInput から もどる）、
;   MartPrintDescription（33:4471）で 説明を 出し、カーソルの 位置を wMenuItemToSwap（$CC35）に 入れて 覚える。
;   上下で もどると リストは ページの 中で 動いても スクロール して しまうので、つぎの 回の はじめ（37:55C4）に
;   $CC35 から スクロールを もどして いる。
; パソコンで これを 使うと、$CC35 が SELECT の 入れかえの しるしと ぶつかる。そこで パソコンでは、
;   リストを 出した あと（入力の 前）に カーソルの 位置を wPCDescCursor に 覚えて おき、リストの 上下の
;   処理（$1752 → $0023）で「カーソルが ページの 中で 動いた（wCurrentMenuItem ≠ 覚えた 位置）」ときは
;   スクロールせずに リストを かきなおすだけに する（ページの はしで 動けなかった ときだけ スクロール）。
;   （wLastMenuItem は HandleMenuInput が もどる 前に 新しい 位置に なるので 使えない）
;   wPCDescCursor は どこからも 使われて いない $D688（連れ歩きの $D689 の となり）。入力の 前に 毎回 書く。

DEF wCurrentMenuItem_PD EQU $cc26
DEF wMenuWatchedKeys_PD EQU $cc29
DEF wPCDescCursor       EQU $d688
DEF wListScrollOffset_PD EQU $cc36
DEF wListPointer_PD     EQU $cf72
DEF wListMenuID_PD      EQU $cf7b
DEF wNumBoxItems_PD     EQU $d4b9
DEF wBoxItems_PD        EQU $d4ba
DEF BagPrintItemDesc_PD EQU $44ba  ; バンク $33：a = 道具の 説明を 出す（ショップ・リュックと 同じ）
DEF ClearScreenArea_PD  EQU $0374

; ---------------------------------------------------------------- リストの 左右・上下（$1752 から jp $0023）
; もとは 左右（$30）なら 3F:490A（ページ送り）を 呼んで $166D へ、ちがえば bit 7, b / jp $1755（上下の スクロール）
SECTION "リスト 左右 上下", ROM0[$0023]
	ld e, a                ; おされた キー（Bankswitch は de を こわさない）
	ld b, BANK(KitListKeys)
	ld hl, KitListKeys
	call $3500             ; Bankswitch（フラグは そのまま かえる）
	ld b, e
	jp nz, $166d           ; ここで すんだ → リストを かきなおす
	bit 7, b               ; 下
	jp $1755
	assert @ <= $0040

; ---------------------------------------------------------------- 本体（バンク $37）
SECTION "パソコンの 道具の 説明", ROMX[$7e00], BANK[$37]
; e = おされた キー。nz で もどると $166D へ、z なら 元の 上下の スクロールへ
KitListKeys:
	ld a, e
	and $30                ; 左・右
	jr z, .upDown
	ld a, e
	ld [$df27], a
	ld b, $3f
	ld hl, $490a
	call $3500             ; ページ送り（元の 処理）
	ld a, 1
	and a                  ; nz
	ret
.upDown
	call KitIsPCBoxList
	jr nz, .scroll
	ld a, [wCurrentMenuItem_PD]
	ld hl, wPCDescCursor
	cp [hl]
	jr z, .scroll          ; ページの はしで 動けなかった → スクロール
	ld a, 1
	and a                  ; ページの 中で 動いた → かきなおすだけ
	ret
.scroll
	xor a
	ret

; z = パソコンに あずけた 道具の リスト（wListMenuID = 3 で wListPointer = wNumBoxItems）
KitIsPCBoxList:
	ld a, [wListMenuID_PD]
	cp 3
	ret nz
	ld a, [wListPointer_PD]
	cp LOW(wNumBoxItems_PD)
	ret nz
	ld a, [wListPointer_PD + 1]
	cp HIGH(wNumBoxItems_PD)
	ret

; 37:55F3（リストを 出した あと）から：ショップは 元の とおり、パソコンの 道具なら 説明を 出す
KitListEnd:
	ld a, [wListMenuID_PD]
	cp 2
	jp z, $55f9            ; ショップ（元の とおり）
	call KitIsPCBoxList
	ret nz
	ld a, [wMenuWatchedKeys_PD]
	or $c0                 ; 上下でも もどる
	ld [wMenuWatchedKeys_PD], a
	ld a, [wCurrentMenuItem_PD]
	ld [wPCDescCursor], a  ; 入力の 前の 位置
	ld hl, $c3a0 + 13 * 20 + 1 ; hlcoord 1, 13
	ld bc, $0412           ; 4 行 18 字
	call ClearScreenArea_PD
	ld a, [wListScrollOffset_PD]
	ld b, a
	ld a, [wCurrentMenuItem_PD]
	add b
	ld b, a
	ld a, [wNumBoxItems_PD]
	cp b
	ret z                  ; やめる
	ret c
	ld a, b
	add a
	ld e, a
	ld d, 0
	ld hl, wBoxItems_PD
	add hl, de
	ld e, [hl]             ; 道具（Bankswitch は de を こわさない）
	ld b, $33
	ld hl, KitPCDescStub
	jp $3500
	assert @ <= $7f00

SECTION "パソコンの 道具の 説明 つなぎ", ROMX[$55f3], BANK[$37]
	jp KitListEnd

SECTION "パソコンの 道具の 説明 入り口", ROMX[$7ff0], BANK[$33]
KitPCDescStub:
	ld a, e
	jp BagPrintItemDesc_PD
