; ずかんの「ぶんぷをみる」に、つりざおで釣れる場所も出す
; （ピカチュウ版フルカラーと同じ考え方。金・銀・クリスタル 共通。アドレスは下の「ROM ごとにちがう所」だけ変える）
;
; ・釣りの場所のマークは 青。草むら・水の上（なみのり）で出る場所と同じ所は、今までのマークが優先（青は出さない）。
; ・釣りができる所 = マップに 釣りのグループ があり、そのマップに水がある所（src/fishnest_maps.inc。
;   tools/fishnest_maps.py で、ゲームのマップ・タイル・釣りのデータから作った表）。
; ・ボロ・いい・すごいつりざお、朝昼・夜 のどれかで釣れれば出す。
; ・コイキング・トサキント・ニョロモも、ゲームのデータどおり 釣れる所だけに出す
;   （金銀クリスタルでは、コイキングは 釣りのできる所 全部、トサキントは みずうみ、ニョロモは いけ の釣りのグループだけ）。
;   FISHNEST_ALL_SPOTS EQU 1 を先に書くと、この3匹を 釣りのできる所 全部に出す（ピカチュウ版と同じ）。
; ・マークは全部で 40個まで（スプライトの数）。
;
; しくみ
;   Pokedex_GetArea.GetAndPlaceNest の「farcall FindNest」を、新しい処理の farcall と「jr .done_nest」に書きかえる。
;   新しい処理は FindNest（今までの場所）を呼んだあと、釣りの場所を別の表にためて、
;   今までのマーク（色 0）→ 釣りのマーク（色 FISHNEST_PAL）の順に スプライトにする。
;   白黒のゲームボーイ（hCGB = 0）では色は変えない（同じマークになる）。

;---------------------------------------------------------------------
; ROM ごとにちがう所（金 日本版 後期版の値）
;   tools/fishnest_find.py ROM で、金・銀・クリスタルのどれでも、色以外の値を出せる。
;---------------------------------------------------------------------
IF !DEF(FISHNEST_HOOK)
DEF FISHNEST_HOOK              EQU $5ec4   ; Pokedex_GetArea.GetAndPlaceNest の farcall FindNest
DEF FISHNEST_HOOK_BANK         EQU $24
DEF FISHNEST_DONE_NEST         EQU $5eef   ; Pokedex_GetArea.done_nest
DEF FISHNEST_FindNest          EQU $6616
DEF FISHNEST_FindNest_BANK     EQU $0a
DEF FISHNEST_GetLandmarkCoords EQU $6489
DEF FISHNEST_GetLandmarkCoords_BANK EQU $24
DEF FISHNEST_wTilemap          EQU $c3a0
DEF FISHNEST_wShadowOAM        EQU $c300
DEF FISHNEST_wNamedObjectIndex EQU $d143
DEF FISHNEST_KANTO_LANDMARK    EQU $2e     ; pret の constants/landmark_constants.asm の KANTO_LANDMARK（クリスタルは $2f）
; 色（クリスタルは wOBPals が WRAM バンク5 にある → FISHNEST_PALS_WRAMBANK EQU 5、hCGB は 0）
DEF FISHNEST_wOBPals1          EQU $c240
DEF FISHNEST_wOBPals2          EQU $c2c0
DEF FISHNEST_PALS_WRAMBANK     EQU 0       ; 0 = WRAM のバンクを切りかえない（金・銀）
DEF FISHNEST_hCGB              EQU $ffe8   ; 0 = カラー専用（クリスタル）
DEF FISHNEST_hCGBPalUpdate     EQU $ffe7
; 新しい処理を置く所（約200バイト＋表）
DEF FISHNEST_BANK              EQU $3f
DEF FISHNEST_ADDR              EQU $7900
ENDC

IF !DEF(FISHNEST_ALL_SPOTS)
DEF FISHNEST_ALL_SPOTS EQU 0
ENDC
IF !DEF(FISHNEST_MAPS)
DEF FISHNEST_MAPS EQUS "src/fishnest_maps.inc"
ENDC
; サファリゾーン（src/safari/）の ポケモンを セキチクシティに 出す。
; FISHNEST_EXTRA に 表のファイル（FishNestExtraGrass・FishNestExtraFish）を 書くと 使う（サファリを 入れないときは 書かない）
IF !DEF(FISHNEST_EXTRA)
DEF FISHNEST_EXTRA EQUS "src/safari/safari_nest.inc"
ENDC
IF !DEF(FISHNEST_EXTRA_LANDMARK)
DEF FISHNEST_EXTRA_LANDMARK EQU $5f   ; サファリゾーン（金に ない 番号。座標は safari.asm の SafariLandmarkCoords が 返す）
ENDC

; 金・銀・クリスタル 共通
DEF FISHNEST_PAL        EQU 7          ; 釣りのマークの OBJ パレット
DEF FISHNEST_MAX        EQU 40         ; スプライトの数
DEF FISHNEST_NEST_TILE  EQU $7f
DEF FISHNEST_LIST       EQU FISHNEST_wTilemap + $100   ; 釣りの場所をためる所（FindNest が 0 にした所の後ろ）
DEF FISHNEST_MAGIKARP   EQU $81
DEF FISHNEST_GOLDEEN    EQU $76
DEF FISHNEST_POLIWAG    EQU $3c
DEF FISHNEST_rSVBK      EQU $ff70

;---------------------------------------------------------------------
SECTION "fishnest hook", ROMX[FISHNEST_HOOK], BANK[FISHNEST_HOOK_BANK]
	ld a, FISHNEST_BANK
	ld hl, FishNest_GetAndPlaceNest
	rst $08
	jr FISHNEST_DONE_NEST       ; スプライトを wTilemap にうつす所（点めつ用）

;---------------------------------------------------------------------
SECTION "fishnest main", ROMX[FISHNEST_ADDR], BANK[FISHNEST_BANK]
; e = 0：ジョウト、1：カントー / [wNamedObjectIndex] = ポケモン
FishNest_GetAndPlaceNest:
	push de
	ld a, FISHNEST_FindNest_BANK
	ld hl, FISHNEST_FindNest
	rst $08                     ; 今までの場所 → wTilemap（0 でおわり）
	pop de
	push de
	call FishNest_FindFish      ; 釣りの場所 → FISHNEST_LIST
	pop de
	call FishNest_Extra         ; サファリゾーン
	call FishNest_SetPal
	ld hl, FISHNEST_wShadowOAM
	ld c, FISHNEST_MAX
	ld de, FISHNEST_wTilemap
	ld b, 0                     ; 今までのマーク（色 0）
	call .place
	ld de, FISHNEST_LIST
	ld b, FISHNEST_PAL          ; 釣りのマーク
	; fallthrough
; de = 地名の表（0 でおわり）、b = 色、c = のこりの数、hl = スプライト
.place
	ld a, c
	and a
	ret z
	ld a, [de]
	and a
	ret z
	push de
	push bc
	ld e, a
	push hl
	ld a, FISHNEST_GetLandmarkCoords_BANK
	ld hl, FISHNEST_GetLandmarkCoords
	rst $08                     ; d = Y、e = X
	pop hl
	pop bc
	ld a, d
	sub 4
	ld [hli], a
	ld a, e
	sub 4
	ld [hli], a
	ld a, FISHNEST_NEST_TILE
	ld [hli], a
	ld a, b
	ld [hli], a
	dec c
	pop de
	inc de
	jr .place

; e = 地方 → FISHNEST_LIST に 釣りの場所（今までの場所にあるもの・同じものは入れない）
FishNest_FindFish:
	xor a
	ld [FISHNEST_LIST], a
	ld hl, FishNestMaps
.loop
	ld a, [hli]
	and a
	ret z
	ld d, a                     ; 地名
	ld a, [hli]
	ld b, a                     ; 釣りのグループ
	push hl
	push de
; 地方が同じか
	ld a, d
	cp FISHNEST_KANTO_LANDMARK
	ld a, e
	jr nc, .kanto
	and a
	jr nz, .skip
	jr .region_ok
.kanto
	and a
	jr z, .skip
.region_ok
	ld a, b
	call FishNest_GroupHasMon
	jr nc, .skip
	pop de
	push de
	ld c, d
	call FishNest_Add
.skip
	pop de
	pop hl
	jr .loop

; c = 地名 を FISHNEST_LIST に足す（今までの場所・釣りの場所に もうあれば足さない）
FishNest_Add:
	ld hl, FISHNEST_wTilemap
	call .find
	ret z
	ld hl, FISHNEST_LIST
	call .find
	ret z
	ld [hl], c
	inc hl
	ld [hl], 0
	ret
; hl = 表 → z：c がある / nz：ない（hl = おわりの 0）
.find
	ld a, [hl]
	and a
	jr z, .end
	cp c
	ret z
	inc hl
	jr .find
.end
	inc a
	ret

; e = 地方。カントーで サファリゾーンに 出る ポケモンなら セキチクシティに マーク
; （草むら → 今までの マーク（wTilemap の表）、つり → 釣りの マーク）
FishNest_Extra:
IF STRLEN("{FISHNEST_EXTRA}") > 0
	ld a, e
	and a
	ret z                       ; ジョウト
	ld a, [FISHNEST_wNamedObjectIndex]
	ld c, a
	ld hl, FishNestExtraGrass
	call .has
	jr nc, .fish
	ld a, c
	push af
	ld c, FISHNEST_EXTRA_LANDMARK
	ld hl, FISHNEST_wTilemap
	call FishNest_Add.find
	jr z, .grass_done
	ld [hl], c
	inc hl
	ld [hl], 0
.grass_done
	pop af
	ld c, a
.fish
	ld hl, FishNestExtraFish
	call .has
	ret nc
	ld c, FISHNEST_EXTRA_LANDMARK
	jp FishNest_Add
; hl = 0 で おわる 表 → キャリーあり：c が ある
.has
	ld a, [hli]
	and a
	ret z
	cp c
	jr nz, .has
	scf
	ret
INCLUDE "{FISHNEST_EXTRA}"
ELSE
	ret
ENDC

; a = 釣りのグループ → キャリーあり：[wNamedObjectIndex] が釣れる
FishNest_GroupHasMon:
	ld b, a
	ld a, [FISHNEST_wNamedObjectIndex]
	ld c, a
IF FISHNEST_ALL_SPOTS
	cp FISHNEST_MAGIKARP
	jr z, .yes
	cp FISHNEST_GOLDEEN
	jr z, .yes
	cp FISHNEST_POLIWAG
	jr z, .yes
ENDC
	ld a, b
	and a
	ret z                       ; キャリーなし
	dec a
	cp (FishNestGroupMons.end_ptrs - FishNestGroupMons) / 2
	ret nc                      ; 表にないグループ（キャリーなし）
	add a
	ld e, a
	ld d, 0
	ld hl, FishNestGroupMons
	add hl, de
	ld a, [hli]
	ld h, [hl]
	ld l, a
.scan
	ld a, [hli]
	and a
	ret z                       ; キャリーなし
	cp c
	jr nz, .scan
.yes
	scf
	ret

; 釣りのマークの色（OBJ パレット FISHNEST_PAL）
FishNest_SetPal:
IF FISHNEST_hCGB
	ldh a, [FISHNEST_hCGB]
	and a
	ret z
ENDC
IF FISHNEST_PALS_WRAMBANK
	ldh a, [FISHNEST_rSVBK]
	push af
	ld a, FISHNEST_PALS_WRAMBANK
	ldh [FISHNEST_rSVBK], a
ENDC
	ld hl, .pal
	ld de, FISHNEST_wOBPals1 + FISHNEST_PAL * 8
	call .copy
	ld hl, .pal
	ld de, FISHNEST_wOBPals2 + FISHNEST_PAL * 8
	call .copy
IF FISHNEST_PALS_WRAMBANK
	pop af
	ldh [FISHNEST_rSVBK], a
ENDC
	ld a, 1
	ldh [FISHNEST_hCGBPalUpdate], a
	ret
.copy
	ld b, 8
.copy_loop
	ld a, [hli]
	ld [de], a
	inc de
	dec b
	jr nz, .copy_loop
	ret
.pal
	; マークの絵は ほとんどが色3、少しが色2（今までのマークは 色3 = 黒・色2 = 赤）。
	; 釣りのマークは 色3 = こい青、色2 = 水色 にして、青いマークに見えるようにする（0・1 は使わない）
	dw $6ffb, $2a7f, $7f40, $4000

INCLUDE "{FISHNEST_MAPS}"
