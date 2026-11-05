; ダウジングマシンで 道具の 方向が わかる（金 日本版）
;
; ・ダウジングマシンが はんのう した とき、元の 文の あとに
;     「どうぐは　みぎうえの　ほうに／あるみたいだ！」
;   のように 方向を 出す（うえ・した・ひだり・みぎ・ひだりうえ・みぎうえ・ひだりした・みぎした・あしもと）。
;   近くに いくつか ある ときは いちばん 近い もの（たて＋よこ の 歩数）。
;
; しくみ
;   ・ItemFinder の「farcall CheckForHiddenItems」を 新しい バンクの ItemFinder_Check に：
;     CheckForHiddenItems と 同じ 所（画面の 中の まだ 拾って いない かくれた 道具）を しらべ、
;     いちばん 近い ものとの ずれ（よこ・たて）を おぼえて、あれば キャリー（元と 同じ）。
;   ・はんのう した ときの スクリプト（.Script_FoundSomething）の「writetext / closetext / end」を
;     新しい バンクの ItemFinder_Found への farsjump に：元の 文（写し）の あと 方向の 文を 出す。
;   ・方向の 文は wStringBuffer1 に「どうぐは　○○の　ほうに」を 作って 出す（日本版は TX_RAM を 文の はじめに）。
;   ・ずれ・いちばん 近い 歩数は 使われていない WRAM（$def6〜$def8）。
;
; 銀・クリスタルに 入れるとき：下の DEF を その ROM の 値に する
;   （CheckForHiddenItems・ItemFinder の 作りは 銀・クリスタルも 同じ。.Script_FoundSomething の バイトを 確かめる）

INCLUDE "includes.asm"
INCLUDE "src/charmap_jp.inc"

IF !DEF(IF_HOOK)
DEF IF_HOOK            EQU $67e0      ; バンク$04 ItemFinder の farcall CheckForHiddenItems（6バイト）
DEF IF_HOOK_BANK       EQU $04
DEF IF_SCRIPT_HOOK     EQU $6815      ; .Script_FoundSomething の writetext（4c 23 68 49 90）
DEF IF_TEXT            EQU $6823      ; 元の「おッ！ ダウジングマシンが…」（$58 まで）
DEF IF_TEXT_LEN        EQU 38
DEF IF_GetMapScriptsBank EQU $2cec
DEF IF_GetFarByte      EQU $30e4
DEF IF_GetFarWord      EQU $30f8
DEF IF_EventFlagAction EQU $2eeb
DEF IF_wCurMapScriptBank EQU $d0c5
DEF IF_wCurMapBGEventsPointer EQU $d912
DEF IF_wCurMapBGEventCount EQU $d911
DEF IF_wXCoord         EQU $d9c9
DEF IF_wYCoord         EQU $d9c8
DEF IF_wStringBuffer1  EQU $cf87
DEF wIFBest            EQU $def6      ; いちばん 近い 歩数（$ff ＝ なし）
DEF wIFDX              EQU $def7      ; よこ（＋ みぎ）
DEF wIFDY              EQU $def8      ; たて（＋ した）
DEF wIFCount           EQU $def9
DEF IF_BANK            EQU $45
DEF IF_ADDR            EQU $6800
ENDC

SECTION "itemfinder hook", ROMX[IF_HOOK], BANK[IF_HOOK_BANK]
	ld a, BANK(ItemFinder_Check)
	ld hl, ItemFinder_Check
	rst $08
SECTION "itemfinder script hook", ROMX[IF_SCRIPT_HOOK], BANK[IF_HOOK_BANK]
	farsjump ItemFinder_Found

SECTION "itemfinder", ROMX[IF_ADDR], BANK[IF_BANK]
ItemFinder_Check:
	call IF_GetMapScriptsBank
	ld [IF_wCurMapScriptBank], a
	ld a, $ff
	ld [wIFBest], a
	ld hl, IF_wCurMapBGEventsPointer
	ld a, [hli]
	ld h, [hl]
	ld l, a
	ld a, [IF_wCurMapBGEventCount]
	and a
	jr z, .done
.loop
	ld [wIFCount], a
	push hl
	call .GetFarByte                  ; y
	ld e, a
	call .GetFarByte                  ; x
	ld d, a
	call .GetFarByte                  ; 形
	cp BGEVENT_ITEM
	jr nz, .next
	; 画面の 中か（元と 同じ：たて −4〜＋4、よこ −4〜＋5）
	ld a, [IF_wYCoord]
	ld b, a
	ld a, e
	sub b
	ld e, a                           ; e = たての ずれ
	add 4
	cp 9
	jr nc, .next
	ld a, [IF_wXCoord]
	ld b, a
	ld a, d
	sub b
	ld d, a                           ; d = よこの ずれ
	add 4
	cp 10
	jr nc, .next
	; まだ 拾って いないか
	push de
	ld a, [IF_wCurMapScriptBank]
	call IF_GetFarWord
	ld a, [IF_wCurMapScriptBank]
	call IF_GetFarWord
	ld d, h
	ld e, l
	ld b, 2                           ; CHECK_FLAG
	call IF_EventFlagAction
	ld a, c
	pop de
	and a
	jr nz, .next
	; 歩数 ＝ |よこ| ＋ |たて|
	ld a, d
	call .Abs
	ld b, a
	ld a, e
	call .Abs
	add b
	ld b, a
	ld a, [wIFBest]
	cp b
	jr c, .next
	jr z, .next
	ld a, b
	ld [wIFBest], a
	ld a, d
	ld [wIFDX], a
	ld a, e
	ld [wIFDY], a
.next
	pop hl
	ld bc, 5                          ; BG_EVENT_SIZE
	add hl, bc
	ld a, [wIFCount]
	dec a
	jr nz, .loop
.done
	ld a, [wIFBest]
	cp $ff
	ret z                             ; なし（キャリーなし）
	scf
	ret

.GetFarByte
	ld a, [IF_wCurMapScriptBank]
	call IF_GetFarByte
	inc hl
	ret

.Abs
	bit 7, a
	ret z
	cpl
	inc a
	ret

ItemFinder_Found:
	callasm ItemFinder_MakeDir
	writetext ItemFinder_OrigText
	writetext ItemFinder_DirText
	closetext
	end

; wStringBuffer1 に「どうぐは　○○の　ほうに」（あしもと なら「どうぐは　あしもとに」）
ItemFinder_MakeDir:
	ld hl, IF_wStringBuffer1
	ld de, .Head
	call .Copy
	ld a, [wIFDX]
	ld c, a
	ld a, [wIFDY]
	ld b, a
	or c
	jr nz, .dir
	ld de, .Feet
	jr .Copy
.dir
	ld a, c                           ; よこ
	and a
	jr z, .vert
	ld de, .Left
	bit 7, a
	jr nz, .h
	ld de, .Right
.h
	call .Copy
.vert
	ld a, b                           ; たて
	and a
	jr z, .tail
	ld de, .Up
	bit 7, a
	jr nz, .v
	ld de, .Down
.v
	call .Copy
.tail
	ld de, .Tail
.Copy                                 ; de の 文字を hl へ（@ まで。@ も 書く。hl は @ の 所）
	ld a, [de]
	ld [hl], a
	cp $50                            ; @
	ret z
	inc de
	inc hl
	jr .Copy

.Head  db "どうぐは　@"
.Feet  db "あしもとに@"
.Left  db "ひだり@"
.Right db "みぎ@"
.Up    db "うえ@"
.Down  db "した@"
.Tail  db "の　ほうに@"

ItemFinder_OrigText:
	INCBIN "base.gbc", IF_HOOK_BANK * $4000 + IF_TEXT - $4000, IF_TEXT_LEN
ItemFinder_DirText:
	db $01
	dw IF_wStringBuffer1
	db $00, $4f, "あるみたいだ！", $58
