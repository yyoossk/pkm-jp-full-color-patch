; ピカチュウに 話しかけた とき：ピカチュウフルカラーと 同じ 表情の 絵（follow_talk.inc から INCLUDE）
;   ・表情の えらび方は ピカチュウ版と 同じ：ねむり → ねむる、ほかの 状態異常 → なく、それ以外は なつき度と 気分で 決める
;     （クリスタルには ピカチュウ版の「気分」が ないので、気分は ふつう（列3）と 少し 高い（列4）を ランダムに）。
;   ・ピカチュウの 上に 気持ちの アイコン（ピカチュウ版の 吹き出しに 近い もの。どくろは かなしい）→ 絵の わく（6, 5 から 7×7）に
;     表情の 絵を コマ送りで 出す（鳴き声つき）→ 自動で とじる。文章は 出ない（ピカチュウ版と 同じ）。
;   ・絵の データは ピカチュウフルカラーの ROM で 表情を うごかして 1フレームずつ とった もの（tools/follow_pika_gen.py →
;     follow_pika_data.inc、バンク$7a・$7b）。タイルは 字の 所（vTiles1 $8800〜）に 読み、色は 画面で 使って いない パレット（なければ 7）を
;     しろ・オレンジ・ちゃいろ・くろ に する（wBGPals2 だけ。wBGPals1 は そのまま）。とじる ときは ClosePokepic（$09:$4539）と
;     同じ 手順で 字と 画面を もどすが、GetMemSGBLayout（マップの 色の 読みなおし）は せず、かりた パレット 1つだけを
;     wBGPals1 から もどす（ほかの 色・連れ歩きや 人の 色と きょうごう しない ように）。

DEF FW_PIKACHU         EQU 25
DEF FW_CopyMenuHeader  EQU $1d07
DEF FW_MenuBox         EQU $1c86
DEF FW_UpdateSprites   EQU $1a9d
DEF FW_ApplyTilemap    EQU $31e8
DEF FW_Get2bpp         EQU $0f6c
DEF FW_WaitBGMap       EQU $31c2
DEF FW_DelayFrames     EQU $0468
DEF FW_PlayMonCry2     EQU $37a5
DEF FW_ClearMenuBoxInterior EQU $1cac
DEF FW_LoadOverworldTilemapAndAttrmapPals EQU $2136
DEF FW_LoadStandardFont EQU $0e3b
DEF FW_hBGMapMode      EQU $ffd4
DEF FW_ClearWindowData EQU $1f82
DEF FW_ReanchorBGMap   EQU $659c     ; バンク1 ReanchorBGMap_NoOAMUpdate
DEF FW_HDMATransferTilemapAndAttrmap_Menu EQU $2df2
DEF FW_LoadFonts_NoOAMUpdate EQU $6607 ; バンク1
DEF FW_wTilemap        EQU $c4a0
DEF FW_wBGPals1        EQU $d000      ; WRAM バンク5（もとの 色）
DEF FW_wBGPals2        EQU $d080      ; WRAM バンク5（画面に 出す 色）
DEF FW_wAttrmap        EQU $cdcd
DEF FW_hCGBPalUpdate   EQU $ffe5
DEF wPartyMon1Happiness EQU wPartyMon1 + $1b
DEF wFwP_Anim          EQU wFwT + 7
DEF wFwP_Bank          EQU wFwT + 8
DEF wFwP_Seq           EQU wFwT + 9    ; 2バイト
DEF wFwP_Frames        EQU wFwT + 11   ; 2バイト
DEF wFwP_Pal           EQU wFwT + 13

FwPikaEmoteScripts:
	dw FwPikaEmote0, FwPikaEmote1, FwPikaEmote2, FwPikaEmote3
	dw FwPikaEmote4, FwPikaEmote5, FwPikaEmote6, FwPikaEmote7
FOR N, 8
FwPikaEmote{d:N}:
	fws_showemote N, 15
	fws_sjump FwPikaShow
ENDR
FwPikaShow:
	fws_callasm Fw_PikaOpen           ; opentext と 同じ（文の わくは 出さない）
	fws_callasm Fw_PikaPic
	fws_closetext
	fws_end

; 表情（ピカチュウ版の 番号）と アイコン（$ff = なし）
; ピカチュウ版の PikaPicAnimationScriptPointerLookupTable の 列3・列4
FwPikaMoodTable:
	; なつき度の 上限, 列3, 列4
	db  50, $06, $0d
	db 100, $05, $0c
	db 130, $01, $08
	db 160, $04, $0f
	db 200, $07, $02
	db 250, $10, $0a
	db 255, $13, $14
; 表情ごとの アイコン（ピカチュウ版の 吹き出し → クリスタルの アイコン）
FwPikaEmoteOf:
	db $ff, $ff, 2, $ff, $ff, $ff, 3, $ff   ; 00〜07
	db $ff, 3, 4, 6, $ff, $ff, 5, $ff       ; 08〜0f
	db $ff, $ff, $ff, 4, 4, 7, $ff, $ff     ; 10〜17
	db 0, 5, 6, $ff, $ff                    ; 18〜1c

; Fw_Pick から（ピカチュウの とき）：表情を えらんで とぶ 先を hl に
Fw_PikaChoose:
	call Fw_Status
	and %111
	ld a, $0b                         ; ねむる
	jr nz, .got
	call Fw_Status
	and a
	ld a, $1c                         ; なく
	jr nz, .got
	call Fw_Happy
	ld b, a
	ld hl, FwPikaMoodTable
.row
	ld a, [hl]
	cp b
	jr nc, .found
	inc hl
	inc hl
	inc hl
	jr .row
.found
	inc hl
	call FW_Random
	and 1
	jr z, .col3
	inc hl
.col3
	ld a, [hl]
.got
	ld [wFwP_Anim], a
	ld e, a
	ld d, 0
	ld hl, FwPikaEmoteOf
	add hl, de
	ld a, [hl]
	cp $ff
	ld hl, FwPikaShow
	ret z
	add a
	ld e, a
	ld hl, FwPikaEmoteScripts
	add hl, de
	ld a, [hli]
	ld h, [hl]
	ld l, a
	ret

; opentext（OpenText $2dda）から 文の わく（SpeechTextbox）を ぬいた もの。
; BG マップを 画面の 左上に あわせなおすので、wTilemap の 位置と 画面が そろう（しないと わくが ずれたり、前の 画面の 行が 出た）
Fw_PikaOpen:
	call FW_ClearWindowData
	fw_farcall 1, FW_ReanchorBGMap
	call FW_HDMATransferTilemapAndAttrmap_Menu
	fw_farcall 1, FW_LoadFonts_NoOAMUpdate
	ret

FwPikaMenuHeader:
	db $40                            ; MENU_BACKUP_TILES
	db 5, 6                           ; 上・左
	db 11, 12                         ; 下・右
	dw 0
	db 1

; 表情の 絵を 出す（callasm）
Fw_PikaPic:
	; 表から バンクと 見出し
	ld a, [wFwP_Anim]
	ld l, a
	ld h, 0
	ld e, l
	ld d, h
	add hl, hl
	add hl, de
	ld de, PikaPicTable
	add hl, de
	ld a, [hli]
	ld [wFwP_Bank], a
	ld a, [hli]
	ld h, [hl]
	ld l, a                           ; hl = 見出し（そのバンク）
	push hl
	; 見出し：タイルの 数、タイル、コマ、順番
	ld a, [wFwP_Bank]
	call FW_GetFarByte
	ld c, a                           ; タイルの 数
	pop hl
	inc hl
	push bc
	call .farword                     ; de = タイル
	push de
	call .farword
	ld a, e
	ld [wFwP_Frames], a
	ld a, d
	ld [wFwP_Frames + 1], a
	call .farword
	ld a, e
	ld [wFwP_Seq], a
	ld a, d
	ld [wFwP_Seq + 1], a
	; わく
	ld hl, FwPikaMenuHeader
	call FW_CopyMenuHeader
	call FW_MenuBox
	call Fw_PikaPickPal               ; 画面で 使って いない 色の 番号を さがして わくの 中に
	call FW_UpdateSprites
	call FW_ApplyTilemap
	; 色（えらんだ 番号の パレットを ピカチュウの 絵の 色に）。
	; ApplyTilemap（割りこみを 止めて 画面を うつす）の あとに する。前に すると、人の 多い マップ（コガネ）で
	; VBlank の 色の 書きこみが おくれて 画面に 入らず、絵が みどりの まま だった
	ld a, [wFwP_Pal]                  ; （バンク5に する 前に 読む。wFwT は $d0xx）
	add a
	add a
	add a
	add LOW(FW_wBGPals2)
	ld l, a
	ld h, HIGH(FW_wBGPals2)
	ldh a, [$ff70]
	push af
	ld a, 5
	ldh [$ff70], a
	ld de, FwPikaPal
	ld c, 8
.pal
	ld a, [de]
	inc de
	ld [hli], a
	dec c
	jr nz, .pal
	pop af
	ldh [$ff70], a
	ld a, 1
	ldh [FW_hCGBPalUpdate], a
	ld c, 1
	call FW_DelayFrames
	; 絵の タイル（字の 所）
	pop de
	pop bc
	ld a, [wFwP_Bank]
	ld b, a
	ld hl, $8800
	call FW_Get2bpp
	ld a, 1
	ld [wFwP_Anim], a                 ; 1 = まだ 鳴いて いない
.loop
	; 次の（コマ, フレーム数）
	ld a, [wFwP_Seq]
	ld l, a
	ld a, [wFwP_Seq + 1]
	ld h, a
	ld a, [wFwP_Bank]
	call FW_GetFarByte
	cp $ff
	jr z, .done
	ld b, a                           ; コマ
	inc hl
	push bc
	ld a, [wFwP_Bank]
	call FW_GetFarByte
	pop bc
	ld c, a                           ; フレーム数
	inc hl
	ld a, l
	ld [wFwP_Seq], a
	ld a, h
	ld [wFwP_Seq + 1], a
	push bc
	; コマ b の 25バイトを わくの 中（7, 6）へ
	call .frameaddr                   ; hl = コマの はじめ
	ld de, FW_wTilemap + 6 * 20 + 7
	ld b, 5
.rows
	push bc
	ld c, 5
.cols
	ld a, [wFwP_Bank]
	push hl
	call FW_GetFarByte
	pop hl
	inc hl
	ld [de], a
	inc de
	dec c
	jr nz, .cols
	ld a, e
	add 20 - 5
	ld e, a
	jr nc, .nc
	inc d
.nc
	pop bc
	dec b
	jr nz, .rows
	call FW_WaitBGMap
	; はじめの コマで 鳴く
	ld a, [wFwP_Anim]
	and a
	jr z, .nocry
	xor a
	ld [wFwP_Anim], a
	ld a, FW_PIKACHU
	call FW_PlayMonCry2
.nocry
	pop bc
	ld a, c
	sub 3                             ; WaitBGMap の ぶん
	jr c, .loop
	jr z, .loop
	ld c, a
	call FW_DelayFrames
	jr .loop
.done
	; とじる：ClosePokepic と 同じ だが、色は マップの 色を 読みなおさず（GetMemSGBLayout を しない）、
	; かりた パレット 1つだけを もとに もどす（ほかの 色・連れ歩きや 人の 色に さわらない）
	ld hl, FwPikaMenuHeader
	call FW_CopyMenuHeader
	call FW_ClearMenuBoxInterior
	call FW_WaitBGMap
	xor a
	ldh [FW_hBGMapMode], a
	call FW_LoadOverworldTilemapAndAttrmapPals
	call FW_ApplyTilemap
	call Fw_PikaRestorePal            ; （ApplyTilemap の あとに。上と 同じ わけ）
	ld c, 1
	call FW_DelayFrames
	call FW_UpdateSprites
	jp FW_LoadStandardFont

; hl から（そのバンクの）2バイトを de に
.farword
	ld a, [wFwP_Bank]
	push hl
	call FW_GetFarByte
	pop hl
	inc hl
	ld e, a
	ld a, [wFwP_Bank]
	push hl
	call FW_GetFarByte
	pop hl
	inc hl
	ld d, a
	ret

; b = コマ → hl = コマの はじめ（コマの 表 ＋ b × 25）
.frameaddr
	ld a, [wFwP_Frames]
	ld l, a
	ld a, [wFwP_Frames + 1]
	ld h, a
	ld de, 25
	ld a, b
	and a
	ret z
.fa
	add hl, de
	dec b
	jr nz, .fa
	ret

; かりた パレットを もとの 色（wBGPals1 の 同じ 番号）に もどす
Fw_PikaRestorePal:
	ld a, [wFwP_Pal]                  ; （バンク5に する 前に 読む）
	add a
	add a
	add a
	ld c, a
	ld b, 0
	ldh a, [$ff70]
	push af
	ld a, 5
	ldh [$ff70], a
	ld hl, FW_wBGPals1
	add hl, bc
	ld a, LOW(FW_wBGPals2)
	add c
	ld e, a
	ld d, HIGH(FW_wBGPals2)
	ld c, 8
.copy
	ld a, [hli]
	ld [de], a
	inc de
	dec c
	jr nz, .copy
	pop af
	ldh [$ff70], a
	ld a, 1
	ldh [FW_hCGBPalUpdate], a
	ret

; 画面（wAttrmap）で 使って いない 色の 番号（0〜6）を さがして、わくの 中（7, 6 から 5×5）の 色に する。
; ない ときは 7（文の 色。この 色を 使う 地面の 色が かわって 見える）
; （元は 文の 色 7 に して いたが、7 を 使う 木や 段差が オレンジに なって 見えた）
Fw_PikaPickPal:
	ld hl, FW_wAttrmap
	ld bc, 20 * 18
	ld d, 0                           ; 使って いる 色の ビット
.scan
	ld a, [hli]
	and 7
	push bc
	ld b, a
	ld a, 1
	inc b
.shift
	dec b
	jr z, .gotbit
	add a
	jr .shift
.gotbit
	or d
	ld d, a
	pop bc
	dec bc
	ld a, b
	or c
	jr nz, .scan
	ld e, 0
.find
	srl d
	jr nc, .free
	inc e
	ld a, e
	cp 7
	jr c, .find
.free
	ld a, e
	ld [wFwP_Pal], a
	ld hl, FW_wAttrmap + 6 * 20 + 7
	ld b, 5
.rows
	ld c, 5
.cols
	ld [hli], a
	dec c
	jr nz, .cols
	ld de, 20 - 5
	add hl, de
	dec b
	jr nz, .rows
	ret

FwPikaPal:
	dw $7fff, $025f, $04f3, $0c63     ; しろ・オレンジ・ちゃいろ・くろ
