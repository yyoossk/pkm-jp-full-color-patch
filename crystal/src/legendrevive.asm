; 倒して しまった 伝説の ポケモンに、殿堂入り するたびに もう いちど 会える（金 日本版）
;
; ・殿堂入りの とき、つぎの ポケモンを 倒した（にげた）けど つかまえて いない（ずかんで「つかまえた」に なって いない）なら、もとに もどす：
;     ホウオウ（スズのとう の おくじょう。にじいろのはね が いるのは 元と 同じ）
;     ルギア（うずまきじま の いちばん おく。ぎんいろのはね が いるのは 元と 同じ）
;     ライコウ・エンテイ・スイクン（やけたとう で にげだした あと なら、また はじめの 場所から あるきまわる。レベル 40）
;   つかまえた ポケモンは もどさない（2ひきめ は 出ない）。
;
; しくみ
;   ・HallOfFame の「farcall SaveGameData」（6バイト）を 新しい バンクの LegendRevive への farcall に。
;     LegendRevive は もどして から SaveGameData を 呼ぶ（もどした ことも レポートに のこる）。
;   ・ホウオウ・ルギア：EVENT_FOUGHT_HO_OH（$317）・EVENT_FOUGHT_LUGIA（$318）を けす（会う ときに たつ イベント）。
;   ・ライコウたち：EVENT_RELEASED_THE_BEASTS（$7b）が たって いて、wRoamMon の しゅるいが 0（倒した・つかまえた）なら、
;     InitRoamMons と 同じ 値（しゅるい・レベル 40・はじめの マップ・HP 0 ＝ 個体値を 作りなおす）を 入れる。
;   ・日本版 金の イベントの 番号は スクリプトの checkevent / setevent から 調べた もの。
;
; 銀・クリスタルに 入れるとき：下の DEF を その ROM の 値に する
;   （銀は ホウオウ・ルギアの レベルが 金と 逆なだけで 作りは 同じ。クリスタルは スイクンが あるきまわらず、
;     ライコウ・エンテイ だけ。スイクンは EVENT_FOUGHT_SUICUNE を けす）

IF !DEF(LR_HOOK)
DEF LR_HOOK            EQU $65f1      ; バンク$21 HallOfFame の farcall SaveGameData
DEF LR_HOOK_BANK       EQU $21
DEF LR_Save_BANK       EQU $05
DEF LR_Save            EQU $4bf5      ; SaveGameData
DEF LR_wEventFlags     EQU $d7aa
DEF LR_wPokedexCaught  EQU $db78
DEF LR_wRoamMon1       EQU $dc90      ; 7バイト ずつ（しゅるい・レベル・グループ・マップ・HP・個体値 2）
DEF EVENT_FOUGHT_HO_OH_J EQU $317
DEF EVENT_FOUGHT_LUGIA_J EQU $318
DEF EVENT_RELEASED_THE_BEASTS_J EQU $7b
DEF LR_BANK            EQU $45
DEF LR_ADDR            EQU $7900
ENDC

IF !DEF(LR_NUM_ROAMERS)
DEF LR_NUM_ROAMERS     EQU 3          ; あるきまわる ポケモンの 数（クリスタルは 2：ライコウ・エンテイ）
DEF LR_RAIKOU_GROUP    EQU $02        ; 42ばんどうろ
DEF LR_RAIKOU_MAP      EQU $05
DEF LR_ENTEI_GROUP     EQU $0a        ; 37ばんどうろ
DEF LR_ENTEI_MAP       EQU $04
DEF LR_SUICUNE_GROUP   EQU $01        ; 38ばんどうろ
DEF LR_SUICUNE_MAP     EQU $0c
ENDC

DEF HO_OH_   EQU $fa
DEF LUGIA_   EQU $f9
DEF RAIKOU_  EQU $f3
DEF ENTEI_   EQU $f4
DEF SUICUNE_ EQU $f5

; イベント e の バイトと ビット
MACRO ev_byte
	DEF \1 EQU LR_wEventFlags + (\2) / 8
	DEF \3 EQU (\2) % 8
ENDM
; ずかんの「つかまえた」
MACRO dex_byte
	DEF \1 EQU LR_wPokedexCaught + ((\2) - 1) / 8
	DEF \3 EQU ((\2) - 1) % 8
ENDM
	ev_byte EV_HOOH, EVENT_FOUGHT_HO_OH_J, EV_HOOH_BIT
	ev_byte EV_LUGIA, EVENT_FOUGHT_LUGIA_J, EV_LUGIA_BIT
	ev_byte EV_BEASTS, EVENT_RELEASED_THE_BEASTS_J, EV_BEASTS_BIT
	dex_byte DX_HOOH, HO_OH_, DX_HOOH_BIT
	dex_byte DX_LUGIA, LUGIA_, DX_LUGIA_BIT
IF DEF(EVENT_FOUGHT_SUICUNE_J)
	ev_byte EV_SUICUNE, EVENT_FOUGHT_SUICUNE_J, EV_SUICUNE_BIT
	dex_byte DX_SUICUNE, SUICUNE_, DX_SUICUNE_BIT
ENDC

SECTION "legendrevive hook", ROMX[LR_HOOK], BANK[LR_HOOK_BANK]
	ld a, BANK(LegendRevive)
	ld hl, LegendRevive
	rst $08

SECTION "legendrevive", ROMX[LR_ADDR], BANK[LR_BANK]
LegendRevive:
	; ホウオウ
	ld a, [DX_HOOH]
	bit DX_HOOH_BIT, a
	jr nz, .lugia
	ld hl, EV_HOOH
	res EV_HOOH_BIT, [hl]
.lugia
	ld a, [DX_LUGIA]
	bit DX_LUGIA_BIT, a
	jr nz, .beasts
	ld hl, EV_LUGIA
	res EV_LUGIA_BIT, [hl]
.beasts
IF DEF(EVENT_FOUGHT_SUICUNE_J)
	; クリスタル：スイクンは あるきまわらない（スズのとう で 会う）ので EVENT_FOUGHT_SUICUNE を けす
	ld a, [DX_SUICUNE]
	bit DX_SUICUNE_BIT, a
	jr nz, .roamers
	ld hl, EV_SUICUNE
	res EV_SUICUNE_BIT, [hl]
IF DEF(LR_wTinTower1FSceneID)
	xor a                             ; SCENE_TINTOWER1F_SUICUNE_BATTLE（入ると スイクンと 戦う）
	ld [LR_wTinTower1FSceneID], a
ENDC
.roamers
ENDC
	ld a, [EV_BEASTS]
	bit EV_BEASTS_BIT, a
	jr z, .save                       ; まだ にげだして いない
	ld hl, LR_wRoamMon1
	ld de, .Beasts
	ld c, LR_NUM_ROAMERS
.loop
	push bc
	ld a, [hl]
	and a
	jr nz, .next                      ; まだ あるきまわって いる
	ld a, [de]                        ; しゅるい
	call .Caught
	jr nz, .next                      ; つかまえた
	push hl
	ld a, [de]
	ld [hli], a                       ; しゅるい
	inc de
	ld a, [de]
	ld [hli], a                       ; レベル
	inc de
	ld a, [de]
	ld [hli], a                       ; グループ
	inc de
	ld a, [de]
	ld [hli], a                       ; マップ
	dec de
	dec de
	dec de
	xor a
	ld [hl], a                        ; HP 0（個体値を 作りなおす）
	pop hl
.next
	inc de
	inc de
	inc de
	inc de
	ld bc, 7
	add hl, bc
	pop bc
	dec c
	jr nz, .loop
.save
	ld a, LR_Save_BANK
	ld hl, LR_Save
	rst $08
	ret

; a = しゅるい → nz：ずかんで つかまえた
.Caught
	push hl
	push de
	dec a
	ld c, a
	srl a
	srl a
	srl a
	ld e, a
	ld d, 0
	ld hl, LR_wPokedexCaught
	add hl, de
	ld a, c
	and 7
	ld c, a
	ld a, [hl]
	inc c
.shift
	rrca
	dec c
	jr nz, .shift
	and $80                           ; 見た ビットが 7 に 来て いる
	pop de
	pop hl
	ret

; しゅるい・レベル・はじめの グループ・マップ（InitRoamMons と 同じ）
.Beasts
	db RAIKOU_,  40, LR_RAIKOU_GROUP, LR_RAIKOU_MAP
	db ENTEI_,   40, LR_ENTEI_GROUP, LR_ENTEI_MAP
	db SUICUNE_, 40, LR_SUICUNE_GROUP, LR_SUICUNE_MAP   ; （LR_NUM_ROAMERS が 2 なら 使わない）
