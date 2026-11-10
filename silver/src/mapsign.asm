; 町や 道路に 入った とき、場所の 名前を 出す（クリスタルの 場所の 札と 同じ。金 日本版）
;
; クリスタルと 同じ にした 所（engine/events/map_name_sign.asm）
;   ・わくは クリスタルの 札の 絵（gfx/frames/map_entry_sign.2bpp・14タイル）。色も クリスタルの 文字の パレット
;     （31,31,16／31,31,16／14,9,0／0,0,0。クリーム色の 板に 茶色の ふち）。名前は 2行めの まん中（濁点は 1行め）。
;   ・出る タイミング：マップに 入って 画面が 出た あと、歩く ループの 2回め で 出る（クリスタルは タイマー 60 → 59 で 出す）。
;   ・出て いる 長さ：118フレーム（クリスタルの 59回 × 2フレーム）。すぎたら いっぺんに 消える（すべる 動きは ない。クリスタルも ない）。
;   ・人の 絵より 前に 出す（クリスタルと 同じ OAM_PRIO）。
;   ・白黒の ゲームボーイ（hCGB = 0）では 出さない（クリスタルは カラー専用。VRAM の バンク1 が ないため）。
;
; ・ほかの 場所（ずかんの 地図の 場所 ＝ ランドマーク）に 入ったとき、画面の 下に わくと 名前を 少しの あいだ 出す
;   （2びょう。クリスタルと 同じ くらい）。同じ 場所の 中で 建物に 出入り した ときは 出ない。
; ・ゲートの 中・ラジオとう・ちかつうろ・はつでんしょ・セキエイこうげん などは 出さない（クリスタルと 同じ）。
; ・話しかける・メニューを ひらく・戦闘 など（イベントが はじまる とき）は すぐ けす。
;
; しくみ
;   ・名前は ウィンドウ（$9c00。LCDC で もともと オン）の 上から 4行に かいて、WY を $70 に して 画面の 下 4行に 出す。
;   ・町を あるいて いる とき、文字の タイル（$80〜$ff）は 人の 絵に 使われて いるので、名前の 文字の 絵は
;     VRAM の バンク1 の 同じ 番号の 所に フォント（$3e:$42f2。1bpp）から 写す。わくの 14タイルも バンク1 の $60〜$6d（$9600）に 写す。
;     4行 ぜんぶの 色の 表を MS_ATTR（パレット7・バンク1・人より 前）に する。
;   ・パレット7 は 出して いる 間だけ クリスタルの 色に かえ、けす ときに wBGPals2 の パレット7 に もどす（メニューの わくの 色）。
;   ・名前は いちど 置いて から、ほんとうの 長さ（「ばん　どうろ」の まとめ文字も のばした 長さ）で まん中に ずらす。
;   ・マップに 入る ときの セットアップの コマンド LoadWildMonData（どの 入り方でも さいごの ほうに ある）の 表の 行を
;     MapSign_Init に かえる（LoadWildMonData を 呼んで から、ランドマークが かわって いれば 札を 出す）。
;   ・HandleMapObjects（あるいて いる 間 まいかい）を MapSign_Frame に（元の 3つを 呼んで から タイマーを へらす）。
;     HandleMapBackground は 60fps 版が かえて いるので 使わない。タイマーは hVBlankCounter で フレームを かぞえる。
;   ・CheckPlayerState の「call DoPlayerEvent」の 前に MapSign_Event（となりの マップへの つながり・その場で むきを かえる
;     いがいの イベント（メニュー・話しかける・マップの シーン など）なら 札を けす。クリスタルと 同じ）。
;   ・前の ランドマーク・タイマー・前の フレーム番号（$defc〜$defe）と 札の 状態 wMSState（$deff）は 使われていない WRAM（金で 確かめる）。名前を ならべる ための 40バイトは
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
DEF MS_TIME            EQU 118        ; クリスタルと 同じ（59回 × 2フレーム）
DEF wMSState           EQU $deff      ; 0 なし・1 まち・2 つぎで 出す・3 出て いる（金は 空きの WRAM を その ROM で 確かめる）
DEF MS_hCGB            EQU $ffe8
DEF MS_wBGPals2_7      EQU $c2b8      ; wBGPals2 の パレット7（もとに もどす ため）
DEF MS_BANK            EQU $45
DEF MS_ADDR            EQU $6f00
ENDC
DEF MS_ATTR            EQU $8f        ; パレット7・VRAM バンク1 の タイル・前に 出す（わくも 文字も バンク1）
DEF MS_SIGN            EQU $60        ; わくの タイル（バンク1 の $60〜$6d。クリスタルの MAP_NAME_SIGN_START と 同じ 番号）
DEF rBCPS_             EQU $ff68
DEF rBCPD_             EQU $ff69
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
	ld a, [wMSState]
	and $7f
IF DEF(MS_IDLE)
	; 札が 出て いない とき：ほかの 機能（銀は サファリの 歩数・ボールの 表示）
	jr nz, .active
	ld a, BANK(MS_IDLE)
	ld hl, MS_IDLE
	rst $08
	ret
.active
ELSE
	ret z
ENDC
	dec a
	jr z, .first                      ; 1：ループの 1回め（クリスタルの タイマー 60。まだ 出さない）
	dec a
	jr z, .show                       ; 2：ループの 2回め（クリスタルの タイマー 59。ここで 出す）
	; 3：出て いる。タイマー（フレーム）を すぎた フレームの 数 だけ へらす（60fps 版でも 同じ 長さに なる）
	ld a, [wMSTimer]
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
	; 札を 出した あとで 画面の 色が まとめて 書きなおされる（マップに 入った ときの フェードの さいご など）と
	; パレット7 が もとの 白に もどって 札が 白く なる → パレット7 の 色0 の 上の バイトを 見て、ちがえば 書きなおす
	di
.kp_wait
	ldh a, [rSTAT_]
	and 2
	jr nz, .kp_wait
	ld a, 7 * 8 + 1
	ldh [rBCPS_], a
	ldh a, [rBCPD_]
	ei
	cp HIGH(31 | 31 << 5 | 16 << 10)
	ret z
	ld hl, .CrystalPal
	jp MapSign_SetPal7

.first
	ld a, [wMSState]
	inc a
	ld [wMSState], a
	ret

.show
	ld a, $80 | 3                     ; ビット7 ＝ パレット7 を かえた
	ld [wMSState], a
	call MapSign_PutName              ; 名前を わくの 中に
	ld a, MS_TIME
	ld [wMSTimer], a
	ldh a, [MS_hVBlankCounter]
	ld [wMSLast], a
	; パレット7 を クリスタルの 文字の 色に
	ld hl, .CrystalPal
	call MapSign_SetPal7
	ld a, 7
	ldh [MS_hWX], a
	ld a, $70
	ldh [MS_hWY], a
	ret

.CrystalPal
	dw 31 | 31 << 5 | 16 << 10, 31 | 31 << 5 | 16 << 10, 14 | 9 << 5 | 0 << 10, 0

; hl の 8バイトを パレット7 に
MapSign_SetPal7:
	ld a, $80 | 7 * 8
	ld c, LOW(rBCPS_)
	ld b, 8
	di
.wait0
	ldh a, [rSTAT_]
	and 2
	jr nz, .wait0
	ld a, $80 | 7 * 8
	ldh [rBCPS_], a
	ei
.loop
	di
.wait
	ldh a, [rSTAT_]
	and 2
	jr nz, .wait
	ld a, [hli]
	ldh [rBCPD_], a
	ei
	dec b
	jr nz, .loop
	ret

MapSign_Hide:
	ld a, [wMSState]
	bit 7, a
	jr z, .no_pal
	ld hl, MS_wBGPals2_7              ; パレット7 を もとに
	call MapSign_SetPal7
.no_pal
	xor a
	ld [wMSState], a
	ld [wMSTimer], a
	ld a, $90
	ldh [MS_hWY], a
	ldh [rWY_], a
	ret

MapSign_Event:
	ld a, [wMSState]
	and $7f
	ret z
	ld a, [MS_wScriptRunning]         ; クリスタルの PlayerEvents .ok と 同じ：つながり・その場で むきを かえる いがいは けす
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
	ldh a, [MS_hCGB]
	and a
	jp z, MapSign_Hide                ; 白黒の ゲームボーイ では 出さない
	ld hl, MapSign_Skip
.skip
	ld a, [hli]
	cp $fe
	jr z, .show
	cp c
	jr nz, .skip
	jp MapSign_Hide

.show
	; 前の 札が 出て いる ときは そのまま（クリスタルも つながりを 歩いて 次の 場所に 入ると、札は 出た まま
	; わくが かきなおされて 名前が 消え、2回め で 新しい 名前が 出る）
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
	; 名前を いったん 左はしに ならべて（$35 のような「ばん　どうろ」を まとめた 文字も ひろがる）、
	; ならんだ 長さ で まん中に よせる（クリスタルの PlaceMapNameCenterAlign：(20 − 長さ) ÷ 2）
	ld hl, MS_BUF + 20
	ld de, MS_wStringBuffer1
	call MS_PlaceString               ; 濁点は 1行 上（MS_BUF の 1行め）
	ld hl, MS_BUF + 39
	ld c, 20
.len
	ld a, [hld]
	cp $7f
	jr nz, .lend
	dec c
	jr nz, .len
.lend                                 ; c ＝ 長さ
	ld a, 20
	sub c
	srl a
	jr nz, .off_ok
	inc a                             ; ふちに かからない ように
.off_ok
	ld b, a                           ; b ＝ ずらす 数
	ld hl, MS_BUF
	call .shift
	ld hl, MS_BUF + 20
	call .shift

	ld a, 1
	ldh [rVBK_], a
	; わくの 絵（14タイル）を バンク1 の $60〜 に
	ld hl, $9000 + MS_SIGN * 16
	ld de, MapSign_FrameGFX
	ld b, 14 * 16
.frame_gfx
	ld a, [de]
	inc de
	call .VPut
	dec b
	jr nz, .frame_gfx
	; 文字の 絵を バンク1 に
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

	; 色の 表（バンク1 の $9c00〜 の 4行。ぜんぶ パレット7・バンク1・前）
	ld hl, $9c00
	ld b, 4
.attr_rows
	ld c, 20
.attr
	ld a, MS_ATTR
	call .VPut
	dec c
	jr nz, .attr
	ld de, 32 - 20
	add hl, de
	dec b
	jr nz, .attr_rows

	; タイル（バンク0 の 表に 書く。クリスタルの PlaceMapNameFrame と 同じ ならび）
	xor a
	ldh [rVBK_], a
	ld hl, $9c00
	ld a, MS_SIGN + 1
	call .VPut
	ld a, MS_SIGN + 2
	call .TopBottom
	ld a, MS_SIGN + 4
	call .VPut
	ld hl, $9c00 + 32
	ld b, MS_SIGN + 5
	ld c, MS_SIGN + 11
	call .TileRow
	ld hl, $9c00 + 64
	ld b, MS_SIGN + 6
	ld c, MS_SIGN + 12
	call .TileRow
	ld hl, $9c00 + 96
	ld a, MS_SIGN + 7
	call .VPut
	ld a, MS_SIGN + 8
	call .TopBottom
	ld a, MS_SIGN + 10
	call .VPut

	; 名前を 入れて 出すのは 歩く ループの 2回め（MapSign_Frame）
	ld a, [wMSState]
	and $80
	or 1
	ld [wMSState], a
	ret

; hl の 行（20ます）を 右へ b ます ずらす（左は 空白）
.shift
	push bc
	ld a, 20
	sub b
	ld c, a                           ; 写す 数
	ld e, l
	ld d, h
	ld a, 19
	add e
	ld e, a
	adc d
	sub e
	ld d, a                           ; de ＝ 行の さいご
	ld a, c
	dec a
	add l
	ld l, a
	adc h
	sub l
	ld h, a                           ; hl ＝ 写す もとの さいご
.sh_loop
	ld a, [hld]
	ld [de], a
	dec de
	dec c
	jr nz, .sh_loop
.sh_fill
	ld a, $7f
	ld [de], a
	dec de
	dec b
	jr nz, .sh_fill
	pop bc
	ret

; クリスタルの .FillTopBottom：a+1, a+1, (a, a, a+1, a+1) × 4（18ます）
.TopBottom
	ld c, 5
	jr .tb_enter
.tb_loop
	call .VPut
	call .VPut
.tb_enter
	inc a
	call .VPut
	call .VPut
	dec a
	dec c
	jr nz, .tb_loop
	ret

; b ＝ 左はし・c ＝ 右はし・あいだ 18ます は クリスタルの 中の タイル MS_SIGN + 13
.TileRow
	ld a, b
	call .VPut
	push bc
	ld c, 18
	ld a, MS_SIGN + 13
.trow
	call .VPut
	dec c
	jr nz, .trow
	pop bc
	ld a, c
	jp .VPut

.VPut
	jp MapSign_VPut

; 名前（MS_BUF の 2行）を わくの 中に（クリスタルの PlaceMapNameCenterAlign。空白の ますは そのまま）
MapSign_PutName:
	ld hl, $9c00 + 32 + 1
	ld de, MS_BUF + 1
	call .row
	ld hl, $9c00 + 64 + 1
	ld de, MS_BUF + 20 + 1
.row
	ld c, 18
.loop
	ld a, [de]
	inc de
	cp $7f
	jr z, .skip
	call MapSign_VPut
	dec hl
.skip
	inc hl
	dec c
	jr nz, .loop
	ret

; a を [hl+] へ（VRAM に 書ける とき まで まつ）
MapSign_VPut:
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
MapSign_Skip: db $ff, $00, $11, $3a, $43, $45, $59, $fe

MapSign_FrameGFX:
	INCBIN "gfxdata/map_entry_sign.2bpp"      ; クリスタルの gfx/frames/map_entry_sign.png（14タイル）
