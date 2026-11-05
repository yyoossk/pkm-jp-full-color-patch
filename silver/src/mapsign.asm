; 町や 道路に 入った とき、場所の 名前を 出す（クリスタルの 場所の 札。金 日本版）
;
; ・ほかの 場所（ずかんの 地図の 場所 ＝ ランドマーク）に 入ったとき、画面の 下に わくと 名前を 少しの あいだ 出す
;   （2びょう。クリスタルと 同じ くらい）。同じ 場所の 中で 建物に 出入り した ときは 出ない。
; ・ゲートの 中・ラジオとう・ちかつうろ・はつでんしょ・セキエイこうげん などは 出さない（クリスタルと 同じ）。
; ・話しかける・メニューを ひらく・戦闘 など（イベントが はじまる とき）は すぐ けす。
;
; しくみ
;   ・名前は ウィンドウ（$9c00。LCDC で もともと オン）の 上から 4行に かいて、WY を $70 に して 画面の 下 4行に 出す。
;   ・町を あるいて いる とき、文字の タイル（$80〜$ff）は 人の 絵に 使われて いるので、名前の 文字の 絵は
;     VRAM の バンク1 の 同じ 番号の 所に フォント（$3e:$42f2。1bpp）から 写して、その ますの 色の 表の ビット3 を たてる。
;     わくの タイル（$79〜$7e）は バンク0 の もの。色は 文字の わくと 同じ パレット7。
;   ・マップに 入る ときの セットアップの コマンド LoadWildMonData（どの 入り方でも さいごの ほうに ある）の 表の 行を
;     MapSign_Init に かえる（LoadWildMonData を 呼んで から、ランドマークが かわって いれば 札を 出す）。
;   ・HandleMapObjects（あるいて いる 間 まいかい）を MapSign_Frame に（元の 3つを 呼んで から タイマーを へらす）。
;     HandleMapBackground は 60fps 版が かえて いるので 使わない。タイマーは hVBlankCounter で フレームを かぞえる。
;   ・CheckPlayerState の「call DoPlayerEvent」の 前に MapSign_Event（となりの マップへの つながり・その場で むきを かえる
;     いがいの イベントなら 札を けす）。
;   ・前の ランドマーク・タイマー・前の フレーム番号 は 使われていない WRAM（$defc〜$defe）。名前を ならべる ための 40バイトは
;     セーブの 使われていない 所（$d6e5〜）を 一時的に 使う。
;
; 銀・クリスタルに 入れるとき：銀は 下の DEF を 銀の 値に する（作りは 金と 同じ）。クリスタルには もともと ある。

INCLUDE "src/charmap_jp.inc"

IF !DEF(MS_SETUP_ENTRY)
DEF MS_SETUP_ENTRY     EQU $5501      ; バンク$05 MapSetupCommands の LoadWildMonData の 行（db バンク / dw アドレス）
DEF MS_SETUP_BANK      EQU $05
DEF MS_LoadWildMonData_BANK EQU $0a
DEF MS_LoadWildMonData EQU $65ef
DEF MS_OW_BANK         EQU $25
DEF MS_HandleMapObjects EQU $6716    ; farcall HandleNPCStep / farcall _HandlePlayerStep / call _CheckObjectEnteringVisibleRange / ret（16バイト）
DEF MS_EVENT_CALL      EQU $6792      ; CheckPlayerState の call DoPlayerEvent
DEF MS_DoPlayerEvent   EQU $6b1e
DEF MS_STUB            EQU $7fd8      ; バンク$25 の 空き（9バイト）
DEF MS_HandleNPCStep_BANK EQU $01
DEF MS_HandleNPCStep   EQU $56fd
DEF MS_HandlePlayerStep_BANK EQU $03
DEF MS_HandlePlayerStep EQU $576e
DEF MS_CheckObjectEnteringVisibleRange EQU $6751   ; バンク MS_OW_BANK
DEF MS_GetWorldMapLocation EQU $2d44
DEF MS_GetLandmarkName_BANK EQU $24
DEF MS_GetLandmarkName EQU $6498
DEF MS_PlaceString     EQU $0f46
DEF MS_FONT_BANK       EQU $3e
DEF MS_FONT            EQU $42f2      ; 文字 $80〜$ff（1bpp）
DEF MS_GetFarByte      EQU $30e4
DEF MS_wMapGroup       EQU $d9c6
DEF MS_wMapNumber      EQU $d9c7
DEF MS_wEnvironment    EQU $d075
DEF MS_wScriptRunning  EQU $d151
DEF MS_wStringBuffer1  EQU $cf87
DEF MS_hWX             EQU $ffd3
DEF MS_hMapEntryMethod EQU $ffa1
DEF MS_hWY             EQU $ffd4
DEF MS_GATE            EQU 6
DEF wMSPrev            EQU $defc      ; 前の ランドマーク
DEF wMSTimer           EQU $defd      ; のこりの フレーム
DEF wMSLast            EQU $defe      ; 前に 見た hVBlankCounter
DEF MS_hVBlankCounter  EQU $ff9d
DEF MS_BUF             EQU $d6e5      ; 2行 × 20（濁点の 行・名前の 行）
DEF MS_TIME            EQU 120        ; 2びょう（クリスタルと 同じ くらい）
DEF MS_BANK            EQU $45
DEF MS_ADDR            EQU $6f00
ENDC
DEF MS_ATTR            EQU $87        ; パレット7（文字の わく）・前に 出す
DEF rVBK_              EQU $ff4f
DEF rSTAT_             EQU $ff41
DEF rWY_               EQU $ff4a

SECTION "mapsign setup", ROMX[MS_SETUP_ENTRY], BANK[MS_SETUP_BANK]
	db BANK(MapSign_Init)
	dw MapSign_Init

SECTION "mapsign frame hook", ROMX[MS_HandleMapObjects], BANK[MS_OW_BANK]
	ld a, BANK(MapSign_Frame)
	ld hl, MapSign_Frame
	rst $08
	ret

SECTION "mapsign event hook", ROMX[MS_EVENT_CALL], BANK[MS_OW_BANK]
	call MapSign_EventStub
SECTION "mapsign event stub", ROMX[MS_STUB], BANK[MS_OW_BANK]
MapSign_EventStub:
	ld a, BANK(MapSign_Event)
	ld hl, MapSign_Event
	rst $08
	jp MS_DoPlayerEvent

SECTION "mapsign", ROMX[MS_ADDR], BANK[MS_BANK]
MapSign_Frame:
	ld a, MS_HandleNPCStep_BANK
	ld hl, MS_HandleNPCStep
	rst $08
	ld a, MS_HandlePlayerStep_BANK
	ld hl, MS_HandlePlayerStep
	rst $08
	ld a, MS_OW_BANK
	ld hl, MS_CheckObjectEnteringVisibleRange
	rst $08
	; タイマー（フレーム）を すぎた フレームの 数 だけ へらす（60fps 版でも 同じ 長さに なる）
	ld a, [wMSTimer]
	and a
	ret z
	ld b, a
	ldh a, [MS_hVBlankCounter]
	ld c, a
	ld a, [wMSLast]
	ld d, a
	ld a, c
	ld [wMSLast], a
	sub d                             ; すぎた フレーム
	ld c, a
	ld a, b
	sub c
	jr z, MapSign_Hide
	jr c, MapSign_Hide
	ld [wMSTimer], a
	ret
MapSign_Hide:
	xor a
	ld [wMSTimer], a
	ld a, $90
	ldh [MS_hWY], a
	ldh [rWY_], a
	ret

MapSign_Event:
	ld a, [wMSTimer]
	and a
	ret z
	ld a, [MS_wScriptRunning]
	inc a                             ; PLAYEREVENT_MAPSCRIPT（$ff。マップに 入った とき の シーン など）
	ret z
	dec a
	cp 4                              ; PLAYEREVENT_CONNECTION
	ret z
	cp 9                              ; PLAYEREVENT_JOYCHANGEFACING
	ret z
	jr MapSign_Hide

MapSign_Init:
	ld a, MS_LoadWildMonData_BANK
	ld hl, MS_LoadWildMonData
	rst $08
	ld a, [MS_wMapGroup]
	ld b, a
	ld a, [MS_wMapNumber]
	ld c, a
	call MS_GetWorldMapLocation
	ld c, a
	ld a, [MS_wEnvironment]
	cp MS_GATE
	jr nz, .not_gate
	ld c, $ff
.not_gate
	ld a, [wMSPrev]
	cp c
	ret z                             ; 同じ 場所
	ld a, c
	ld [wMSPrev], a
	ldh a, [MS_hMapEntryMethod]
	cp $f2                            ; MAPSETUP_CONTINUE（つづきから はじめる ときは 出さない。クリスタルと 同じ）
	jp z, MapSign_Hide
	ld hl, .Skip
.skip
	ld a, [hli]
	cp $fe
	jr z, .show
	cp c
	jr nz, .skip
	jr MapSign_Hide

.show
	; 名前 → wStringBuffer1
	ld e, c
	ld a, MS_GetLandmarkName_BANK
	ld hl, MS_GetLandmarkName
	rst $08
	; 2行を 空白に
	ld hl, MS_BUF
	ld c, 40
	ld a, $7f
.clear
	ld [hli], a
	dec c
	jr nz, .clear
	; 名前の 長さ → まん中に
	ld hl, MS_wStringBuffer1
	ld c, 0
.len
	ld a, [hli]
	cp $50
	jr z, .lend
	inc c
	jr .len
.lend
	ld a, 18
	sub c
	jr nc, .fits
	xor a
.fits
	srl a
	inc a
	ld e, a
	ld d, 0
	ld hl, MS_BUF + 20
	add hl, de
	ld de, MS_wStringBuffer1
	call MS_PlaceString               ; 濁点は 1行 上（MS_BUF の 1行め）

	; 文字の 絵を バンク1 に（空白 $7f も バンク1 は 空白に）
	ld a, 1
	ldh [rVBK_], a
	ld hl, $9000 + $7f * 16
	ld c, 16
	xor a
.blank
	call .VPut
	dec c
	jr nz, .blank
	ld de, MS_BUF
	ld b, 40
.glyphs
	ld a, [de]
	inc de
	cp $80
	jr c, .next_glyph
	push bc
	push de
	; hl = $8800 ＋（文字 − $80）× 16、de = フォント ＋（文字 − $80）× 8
	sub $80
	ld l, a
	ld h, 0
	add hl, hl
	add hl, hl
	add hl, hl
	ld de, MS_FONT
	add hl, de
	ld d, h
	ld e, l
	add hl, hl
	ld bc, $8800 - MS_FONT * 2
	add hl, bc
	ld c, 8
.glyph_row
	push hl
	ld h, d
	ld l, e
	ld a, MS_FONT_BANK
	call MS_GetFarByte
	pop hl
	inc de
	call .VPut
	call .VPut
	dec c
	jr nz, .glyph_row
	pop de
	pop bc
.next_glyph
	dec b
	jr nz, .glyphs

	; 色の 表（バンク1 の $9c00〜 の 4行）
	ld hl, $9c00
	ld c, 20
.attr_top
	ld a, MS_ATTR
	call .VPut
	dec c
	jr nz, .attr_top
	ld hl, $9c00 + 32
	call .AttrRow
	ld hl, $9c00 + 64
	call .AttrRow
	ld hl, $9c00 + 96
	ld c, 20
.attr_bottom
	ld a, MS_ATTR
	call .VPut
	dec c
	jr nz, .attr_bottom

	; タイル（バンク0）
	xor a
	ldh [rVBK_], a
	ld hl, $9c00
	ld a, $79
	call .VPut
	ld c, 18
.top
	ld a, $7a
	call .VPut
	dec c
	jr nz, .top
	ld a, $7b
	call .VPut
	ld hl, $9c00 + 32
	ld de, MS_BUF
	call .TileRow
	ld hl, $9c00 + 64
	ld de, MS_BUF + 20
	call .TileRow
	ld hl, $9c00 + 96
	ld a, $7d
	call .VPut
	ld c, 18
.bottom
	ld a, $7a
	call .VPut
	dec c
	jr nz, .bottom
	ld a, $7e
	call .VPut

	ld a, 7
	ldh [MS_hWX], a
	ld a, $70
	ldh [MS_hWY], a
	ldh a, [MS_hVBlankCounter]
	ld [wMSLast], a
	ld a, MS_TIME
	ld [wMSTimer], a
	ret

; わく ＋ 18ます ＋ わく（de = MS_BUF の 行。はしの 2ますは わく に する）
.TileRow
	ld a, $7c
	call .VPut
	inc de
	ld c, 18
.trow
	ld a, [de]
	inc de
	call .VPut
	dec c
	jr nz, .trow
	ld a, $7c
	jp .VPut

.AttrRow
	ld a, MS_ATTR
	call .VPut
	ld c, 18
.arow
	ld a, MS_ATTR | 8                 ; バンク1 の タイル
	call .VPut
	dec c
	jr nz, .arow
	ld a, MS_ATTR
	jp .VPut

; a を [hl+] へ（VRAM に 書ける とき まで まつ）
.VPut
	push af
	di
.wait
	ldh a, [rSTAT_]
	and 2
	jr nz, .wait
	pop af
	ld [hli], a
	ei
	ret

; 札を 出さない 場所（$ff ＝ ゲート・0 ＝ とくべつ・ラジオとう・ちかつうろ・はつでんしょ・シオンの ラジオとう・セキエイこうげん）
.Skip db $ff, $00, $11, $3a, $43, $45, $59, $fe
