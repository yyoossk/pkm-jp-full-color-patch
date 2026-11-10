; 連れ歩き（赤緑青ピカチュウ連れ歩きキット）
;   手持ちのポケモン（手持ちの画面で SELECT でえらんだもの。はじめは先頭）が主人公の後ろを歩く。
;   青には連れ歩きのしくみがないので、マップの人のスロットは使わず、PrepareOAMData の最後で
;   OAM に4枚（＋白い下じき4枚）を足してかく。動きは画面のスクロールから作る
;   （主人公が1歩あるきだすとき、主人公のいたマスへ同じ速さで歩く）。
;   絵と下じきは VRAM バンク1 の OBJ タイル 0〜47、色は OBJ パレット6（下じきはパレット5 の色1 = 白）。
;   状態は WRAM バンク7（$D010〜。$D000〜$D008 は看板）。
;   ★ WRAM バンク7 にしているあいだの call / push / pop は、同じバンクのあいだに対にする
;     （割りこみは SVBK を元にもどすので、そのまま使える）。WRAM バンク1 の値は rd1 で読む。

INCLUDE "charmap.inc"

IF HAS_FOLLOW

DEF FOLLOW_BANK EQU $35
DEF FOLLOW_GFX_BANK EQU $36       ; $36〜$39（1バンク 42匹）
DEF FOLLOW_MASK_BANK EQU $3A      ; $3A〜$3D
DEF FOLLOW_PER_BANK EQU 42

DEF rLY EQU $FF44
DEF rSTAT EQU $FF41
DEF rVBK EQU $FF4F
DEF rHDMA1 EQU $FF51
DEF rHDMA2 EQU $FF52
DEF rHDMA3 EQU $FF53
DEF rHDMA4 EQU $FF54
DEF rHDMA5 EQU $FF55
DEF hSCX EQU $FFAE
DEF hSCY EQU $FFAF

; ゲームの RAM
DEF wFollowSel EQU $C20F          ; 連れ歩く手持ちの番号（0〜5、$FF = だれも）。主人公のスプライトのデータの空き（セーブされる）
DEF wPlayerFacing EQU $C109       ; 主人公の向き（0 下・4 上・8 左・$C 右）
DEF wPartyCount EQU $D123
DEF wPartySpecies EQU $D124
DEF wPartyMon1HP EQU $D12C
DEF PARTYMON_LEN EQU 44
DEF wCurMap EQU $D2DD
DEF wYCoord EQU $D2E0
DEF wXCoord EQU $D2E1
DEF wGrassTile EQU $D4B4
DEF wWalkBikeSurfState EQU $D67F
DEF POKEDEX_ORDER EQU $6783       ; バンク$10：内部の番号−1 → ずかん番号

; カラー化（WRAM バンク2）
DEF W2_ObjPals EQU $D040          ; もとの色（8本）
DEF W2_ObjPalsNow EQU $D744       ; 今の色
DEF W2_ObjPalSend EQU $D785       ; 1 にすると VBlank で OBJ パレットを送る
DEF W2_ObjPalRecalc EQU $D789     ; 1 にすると もとの色から今の色を作りなおす
DEF FW_PAL EQU 6                  ; 連れ歩きの OBJ パレット
DEF FW_MASK_PAL EQU 5             ; 下じき（色1 が白）

; WRAM バンク7
DEF W7 EQU 7
DEF wFwMark EQU $D010             ; $F0,$0F
DEF wFwSCX EQU $D012
DEF wFwSCY EQU $D013
DEF wFwOX EQU $D014               ; 主人公から見た連れ歩きの場所（ピクセル、符号つき）
DEF wFwOY EQU $D015
DEF wFwTX EQU $D016               ; 歩いていく先
DEF wFwTY EQU $D017
DEF wFwDir EQU $D018              ; 向き（0 下・4 上・8 左・$C 右）
DEF wFwShown EQU $D019            ; 1 = 出ている（あらわれてから1歩あるいた）
DEF wFwMap EQU $D01A
DEF wFwAnim EQU $D01B             ; 歩いたピクセル
DEF wFwLoaded EQU $D01C           ; 読んだ種類（内部の番号、$FF = まだ）
DEF wFwGdma EQU $D01D             ; 1 = VBlank で VRAM へ送る（見せたまま）、2 = 送るまでかくす
DEF wFwFrame EQU $D01E            ; VBlank ごとに +1
DEF wFwLastFrame EQU $D01F
DEF wFwY EQU $D020
DEF wFwX EQU $D021
DEF wFwRide EQU $D022             ; 前のフレームで自転車・なみのりだった
DEF wFwDex EQU $D023
DEF wFwGapNow EQU $D024           ; このフレームは 間があいたあと（メニュー・戦闘）
DEF wFwBallNext EQU $D025         ; 1 = 次に出るときはボールから
DEF wFwBallT EQU $D026            ; ボールから出るアニメののこり（0 = なし）
DEF BALL_TIME EQU 12
DEF wFwJump EQU $D038             ; 主人公が段差をとんでいる
DEF wFwHop EQU $D039              ; 1 = 次に追いつくとき段差をとぶ
DEF wFwHopping EQU $D03A          ; 1 = とんでいるところ、2 = 追いつくだけ
DEF wFwLandWait EQU $D03B         ; なみのりからおりたとき 1歩待つ
DEF wFwPalPend EQU $D03C          ; 1 = 次の VBlank でパレット6 の色1・色2 をじかに書く
DEF wFwPalNew EQU $D044           ; その4バイト
DEF rOCPS EQU $FF6A
DEF rOCPD EQU $FF6B
DEF BALL_TILE EQU 48              ; ボールの絵（VRAM1 タイル 48〜59：開いた・半分・とじた）
DEF wFwPals EQU $D028             ; 8: 正面の色1・色2、後ろ・横の色1・色2
DEF wFwBuf EQU $D100              ; 絵 384 ＋ 下じき 384（VBlank で VRAM1 $8000 へ）

; WRAM バンク1 の値を読む（a はこわれる）
MACRO rd1 ; レジスタ, 番地
	xor a
	ldh [rSVBK], a
	ld a, [\2]
	ld \1, a
	ld a, W7
	ldh [rSVBK], a
ENDM
MACRO rd1hl ; レジスタ（[hl] を WRAM バンク1 で）
	xor a
	ldh [rSVBK], a
	ld a, [hl]
	ld \1, a
	ld a, W7
	ldh [rSVBK], a
ENDM

; --- 絵・下じき ---------------------------------------------------------------
FOR N, 4
SECTION "連れ歩きの絵 {d:N}", ROMX[$4000], BANK[FOLLOW_GFX_BANK + N]
IF N < 3
	INCBIN "obj/follow_gfx.bin", N * FOLLOW_PER_BANK * 384, FOLLOW_PER_BANK * 384
ELSE
	INCBIN "obj/follow_gfx.bin", N * FOLLOW_PER_BANK * 384
ENDC
SECTION "連れ歩きの下じき {d:N}", ROMX[$4000], BANK[FOLLOW_MASK_BANK + N]
IF N < 3
	INCBIN "obj/follow_mask.bin", N * FOLLOW_PER_BANK * 384, FOLLOW_PER_BANK * 384
ELSE
	INCBIN "obj/follow_mask.bin", N * FOLLOW_PER_BANK * 384
ENDC
ENDR

SECTION "連れ歩き", ROMX[$4000], BANK[FOLLOW_BANK]

; ずかん番号−1 ごとに 8バイト（正面の色1・色2、後ろ・横の色1・色2）
FwPalTable:
	INCBIN "obj/follow_pals.bin"

; --- PrepareOAMData の最後（看板の処理の前）から ------------------------------
FollowerTick::
	ld a, W7
	ldh [rSVBK], a
	call FwTick
	xor a
	ldh [rSVBK], a
	ret

FwTick:
	xor a
	ld [wFwDrawn], a
	ld a, [wFwMark]
	cp $F0
	jr nz, .init
	ld a, [wFwMark + 1]
	cp $0F
	jr z, .inited
.init
	ld a, $F0
	ld [wFwMark], a
	ld a, $0F
	ld [wFwMark + 1], a
	ld a, $FF
	ld [wFwLoaded], a
	ld [wFwMap], a
	xor a
	ld [wFwGdma], a
	ld [wFwRide], a
	ld a, [wFwFrame]
	ld [wFwLastFrame], a
	call FwReset
.inited
; メニュー・戦闘などで間があいたら、絵を読みなおす（ほかの画面が VRAM1 を使ったかもしれない）
	ld a, [wFwLastFrame]
	ld b, a
	ld a, [wFwFrame]
	ld [wFwLastFrame], a
	sub b
	ld c, 0
	cp 8
	jr c, .gapSet
	inc c
.gapSet
	ld a, c
	ld [wFwGapNow], a
	and a
	jr z, .noGap
	ld a, [wFwLoaded]
	cp $FF
	jr z, .noGap
	call FwLoad
	ld a, [wFwGdma]
	and a
	jr z, .noGap
	ld a, 1                       ; 同じ絵なので見せたまま
	ld [wFwGdma], a
.noGap

; 連れ歩くポケモン → wFwCur（e = 種類 0 = なし、d = 1 ならひんし）
	call FwWant
	ld a, e
	and a
	jr z, .noLoad
	ld a, [wFwLoaded]
	cp e
	jr z, .noLoad
	ld a, e
	ld [wFwLoaded], a
	push de
	call FwLoad
	pop de
.noLoad

; 自転車・なみのり：ボールにもどる。おりたら主人公の所から
	rd1 c, wWalkBikeSurfState
	ld a, c
	and a
	jr z, .walking
	ld a, c
	ld [wFwRide], a               ; 1 自転車・2 なみのり
	ld a, 1
	ld [wFwBallNext], a
	call FwReset
	call FwSaveScroll
	ret
.walking
	ld a, [wFwRide]
	and a
	jr z, .notOff
	cp 2
	jr nz, .offBike
	ld [wFwLandWait], a           ; なみのりからおりた：水のマスでは出ない
.offBike
	xor a
	ld [wFwRide], a
	call FwReset
.notOff

	push de
	call FwMove
	pop de

; かく
	ld a, e
	and a
	ret z                         ; だれも連れ歩かない
	ld a, d
	and a
	ret nz                        ; ひんし
	ld a, [wFwShown]
	and a
	ret z
	ld a, [wFwGdma]
	cp 2
	ret z                         ; 絵を読んでいるところ
	jp FwDraw

; e = 連れ歩く種類（0 = なし）、d = 1 ならひんし
FwWant:
	ld de, 0
	ld a, [wFollowSel]
	cp 6
	ret nc
	ld b, a
	rd1 c, wPartyCount
	ld a, b
	cp c
	jr c, .ok
	ld a, c
	and a
	ret z
	xor a                         ; いない番号なら先頭
	ld b, a
.ok
	ld a, b
	ld [wFwSel], a
	ld hl, wPartySpecies
	ld a, b
	add l
	ld l, a
	jr nc, .nc
	inc h
.nc
	rd1hl e
	ld hl, wPartyMon1HP
	ld a, b
	and a
	jr z, .hp
	push de
	ld de, PARTYMON_LEN
.hpLoop
	add hl, de
	dec b
	jr nz, .hpLoop
	pop de
.hp
	rd1hl c
	inc hl
	rd1hl b
	ld a, b
	or c
	ret nz
	inc d
	ret

; 場所を主人公にそろえて、かくす（1歩あるくと出てくる）
FwReset:
	xor a
	ld [wFwJump], a
	ld [wFwHop], a
	ld [wFwHopping], a
	ld [wFwOX], a
	ld [wFwOY], a
	ld [wFwTX], a
	ld [wFwTY], a
	ld [wFwShown], a
	ld [wFwAnim], a
	ld a, [wPlayerFacing]
	and $0C
	ld [wFwDir], a
	ret

FwSaveScroll:
	ldh a, [hSCX]
	ld [wFwSCX], a
	ldh a, [hSCY]
	ld [wFwSCY], a
	rd1 c, wCurMap
	ld a, c
	ld [wFwMap], a
	rd1 c, wYCoord
	ld a, c
	ld [wFwY], a
	rd1 c, wXCoord
	ld a, c
	ld [wFwX], a
	ret

; --- うごき -----------------------------------------------------------------
FwMove:
	; メニュー・戦闘のあと：同じマップの同じ場所なら そのまま（スクロールは読みなおしでかわる）
	ld a, [wFwGapNow]
	and a
	jr z, .noGap
	rd1 c, wCurMap
	ld a, [wFwMap]
	cp c
	jp nz, .reset
	rd1 c, wYCoord
	ld a, [wFwY]
	cp c
	jp nz, .reset
	rd1 c, wXCoord
	ld a, [wFwX]
	cp c
	jp nz, .reset
	ld de, 0
	jp .done
.noGap
	ldh a, [hSCX]
	ld hl, wFwSCX
	sub [hl]
	ld d, a                       ; dx
	ldh a, [hSCY]
	inc hl
	sub [hl]
	ld e, a                       ; dy
	; 8 ピクセルより大きくとんだら（ワープ・マップを読みなおした）
	ld a, d
	add 8
	cp 17
	jp nc, .reset
	ld a, e
	add 8
	cp 17
	jp nc, .reset
	; マップがかわった：スクロールしていなければワープ（つながりはスクロールしたまま）
	rd1 c, wCurMap
	ld a, [wFwMap]
	cp c
	jr z, .sameMap
	ld a, d
	or e
	jp z, .reset
	; ワープは新しいマップを読むとスクロールが 0,0 になる
	ldh a, [hSCX]
	ld c, a
	ldh a, [hSCY]
	or c
	jp z, .reset
	jr .go
.sameMap
	; 同じマップで 2マス以上とんだ
	rd1 c, wYCoord
	ld a, [wFwY]
	sub c
	inc a
	cp 3
	jp nc, .reset
	rd1 c, wXCoord
	ld a, [wFwX]
	sub c
	inc a
	cp 3
	jp nc, .reset
.go
	ld a, d
	or e
	jp z, .done
	; 1歩のはじめ（前のスクロールがマスにそろっていた）
	ld a, [wFwSCX]
	ld b, a
	ld a, [wFwSCY]
	or b
	and $0F
	jp nz, .notStart
	; 段差：とびはじめはいつもどおり、とんでいるあいだのマスでは行く先をかえない
	;（連れ歩きは主人公がとんだ所で待ち、主人公が次に歩くと 2マスを とんで追いつく）
	rd1 c, wMovementFlags
	bit 6, c
	jr z, .noJump
	ld a, [wFwJump]
	and a
	jp nz, .notStart
	ld a, 1
	ld [wFwJump], a
	ld [wFwHop], a
	jr .stepStart
.noJump
	xor a
	ld [wFwJump], a
.stepStart
	ld a, [wFwTX]
	ld [wFwOX], a
	ld a, [wFwTY]
	ld [wFwOY], a
	xor a
	ld [wFwTX], a
	ld [wFwTY], a
	ld a, [wFwShown]
	and a
	jr nz, .notStart
	ld a, [wFwLandWait]           ; なみのりからおりた1歩め（いたのは水のマス）
	and a
	jr z, .appear
	xor a
	ld [wFwLandWait], a
	jr .notStart
.appear
	ld a, 1
	ld [wFwShown], a
	xor a
	ld [wFwAnim], a
	ld a, [wPlayerFacing]         ; 出てきたときは主人公と同じ向き
	and $0C
	ld [wFwDir], a
	ld a, [wFwBallNext]           ; 自転車・なみのりのあとはボールから
	and a
	jr z, .notStart
	xor a
	ld [wFwBallNext], a
	ld a, BALL_TIME
	ld [wFwBallT], a
.notStart
	; 主人公がうごいたぶん
	ld hl, wFwOX
	ld a, [hl]
	sub d
	ld [hli], a
	ld a, [hl]
	sub e
	ld [hli], a
	ld a, [hl]
	sub d
	ld [hli], a
	ld a, [hl]
	sub e
	ld [hl], a
	; 速さ c = |dx| + |dy|
	ld a, d
	bit 7, a
	jr z, .ax
	cpl
	inc a
.ax
	ld c, a
	ld a, e
	bit 7, a
	jr z, .ay
	cpl
	inc a
.ay
	add c
	ld c, a
	; 行く先が 1マスより遠ければ 着くまで 2倍の速さ（段差のあと）。段差なら とぶ
	ld a, [wFwHopping]
	and a
	jr nz, .fast
	ld a, [wFwTX]
	ld hl, wFwOX
	sub [hl]
	add 16
	cp 33
	jr nc, .far
	ld a, [wFwTY]
	inc hl
	sub [hl]
	add 16
	cp 33
	jr c, .near
.far
	ld a, [wFwHop]
	and a
	ld a, 2                       ; 2 = 追いつくだけ
	jr z, .setHop
	xor a
	ld [wFwHop], a
	inc a                         ; 1 = とぶ
.setHop
	ld [wFwHopping], a
.fast
	sla c
.near
	ld b, 0                       ; うごいたら 1
	; 横
	ld hl, wFwOX
	ld a, [wFwTX]
	sub [hl]
	jr z, .yMove
	bit 7, a
	jr nz, .left
	cp c
	jr c, .r1
	ld a, c
.r1
	add [hl]
	ld [hl], a
	ld a, $0C
	jr .xSet
.left
	cpl
	inc a
	cp c
	jr c, .l1
	ld a, c
.l1
	cpl
	inc a
	add [hl]
	ld [hl], a
	ld a, $08
.xSet
	ld [wFwDir], a
	inc b
.yMove
	ld hl, wFwOY
	ld a, [wFwTY]
	sub [hl]
	jr z, .moved
	bit 7, a
	jr nz, .up
	cp c
	jr c, .d1
	ld a, c
.d1
	add [hl]
	ld [hl], a
	xor a
	jr .ySet
.up
	cpl
	inc a
	cp c
	jr c, .u1
	ld a, c
.u1
	cpl
	inc a
	add [hl]
	ld [hl], a
	ld a, $04
.ySet
	ld [wFwDir], a
	inc b
.moved
	ld a, b
	and a
	jr z, .done
	ld a, [wFwAnim]
	add c
	ld [wFwAnim], a
.done
	; とまって、行く先についたら止まりの絵
	ld a, [wFwOX]
	ld b, a
	ld a, [wFwTX]
	cp b
	jr nz, .save
	ld a, [wFwOY]
	ld b, a
	ld a, [wFwTY]
	cp b
	jr nz, .save
	xor a
	ld [wFwHopping], a
	ld a, d
	or e
	jr nz, .save
	xor a
	ld [wFwAnim], a
.save
	jp FwSaveScroll
.reset
	call FwReset
	jp FwSaveScroll

; --- かく -------------------------------------------------------------------
DEF wFwT_Y EQU $D030
DEF wFwT_X EQU $D031
DEF wFwT_Tile EQU $D032
DEF wFwT_Attr EQU $D033
DEF wFwT_Pri EQU $D034
DEF wFwT_Lim EQU $D035

FwDraw:
	; はなれすぎていたら かかない（念のため）
	ld a, [wFwOX]
	add 32
	cp 65
	ret nc
	ld a, [wFwOY]
	add 32
	cp 65
	ret nc
	; OAM の空き（段差・つりのときは最後の4枚を使わない）
	rd1 c, wMovementFlags
	ld a, $A0
	bit 6, c
	jr z, .lim
	ld a, $90
.lim
	ld [wFwT_Lim], a
	ld b, a
	ldh a, [hOAMBufferOffset]
	cp b
	ret nc
	add 16
	cp b
	jr z, .fit
	ret nc
.fit
	ld a, [wFwBallT]
	and a
	jp nz, FwDrawBall
	; 向きの色
	ld a, [wFwDir]
	and a
	ld hl, wFwPals
	jr z, .front
	ld hl, wFwPals + 4
.front
	call FwSetPal
	; 絵（タイル）: 向き（下0・上4・横8）＋ 歩き 12
	ld a, [wFwDir]
	cp $0C
	jr nz, .notRight
	ld a, $08
.notRight
	ld c, a                       ; タイル
	ld e, FW_PAL | %00001000      ; 属性（VRAM バンク1）
	ld a, [wFwAnim]
	srl a
	srl a
	srl a
	inc a
	and 3
	bit 0, a
	jr z, .stand
	; 歩き
	ld b, a
	ld a, c
	add 12
	ld c, a
	; 上の 2回目の歩きは左右反転（下はアイコンなので反転しない）
	bit 1, b
	jr z, .stand
	ld a, [wFwDir]
	cp $04
	jr nz, .stand
	set 5, e
.stand
	ld a, [wFwDir]
	cp $0C
	jr nz, .noFlip
	ld a, e
	xor %00100000
	ld e, a
.noFlip
	ld a, c
	ld [wFwT_Tile], a
	ld a, e
	ld [wFwT_Attr], a
	call FwGrass                  ; d = $80 / 0
	ld a, d
	ld [wFwT_Pri], a
	call FwHopY                   ; b = とんでいる高さ
	ld a, [wFwOY]
	add 76
	sub b
	ld [wFwT_Y], a
	ld a, [wFwOX]
	add 72
	ld [wFwT_X], a
	call FwPut4
	ld a, 1
	ld [wFwDrawn], a
	call FwPutEmote
	; 白い下じき（OAM に空きがあり、パレット5 の色1 が白のとき）
	ld a, [wFwT_Lim]
	ld b, a
	ldh a, [hOAMBufferOffset]
	add 16
	cp b
	jr z, .fit2
	ret nc
.fit2
	ld a, 2
	ldh [rSVBK], a
	ld hl, W2_ObjPals + FW_MASK_PAL * 8 + 2
	ld a, [hli]
	ld b, a
	ld a, [hl]
	ld c, a
	ld a, W7
	ldh [rSVBK], a
	ld a, b
	cp $FF
	ret nz
	ld a, c
	cp $7F
	ret nz
	ld a, [wFwT_Tile]
	add 24
	ld [wFwT_Tile], a
	ld a, [wFwT_Attr]
	and %11100000
	or FW_MASK_PAL | %00001000
	ld [wFwT_Attr], a
	jp FwPut4

; b = 段差をとんでいる高さ（のこりの きょり r から、(32−r)×r / 32）
FwHopY:
	ld b, 0
	ld a, [wFwHopping]
	cp 1
	ret nz
	ld hl, wFwOX
	ld a, [wFwTX]
	sub [hl]
	jr nc, .x
	cpl
	inc a
.x
	ld c, a
	inc hl
	ld a, [wFwTY]
	sub [hl]
	jr nc, .y
	cpl
	inc a
.y
	or c                          ; どちらかは 0
	jr nz, .air
	xor a
	ld [wFwHopping], a
	ret
.air
	cp 32
	ret nc
	srl a
	ld hl, FwHopTable
	add l
	ld l, a
	jr nc, .nc
	inc h
.nc
	ld b, [hl]
	ret
FwHopTable: ; r/2 = 0〜15
	db 0, 2, 3, 5, 6, 6, 7, 7, 8, 7, 7, 6, 6, 5, 3, 2

; 気持ちのアイコン：OAM のはじめに入れる（主人公より手前に出すため、ほかを4枚うしろへずらす）
FwPutEmote:
	ld a, [wFwEmote]
	and a
	ret z
	ld a, [wFwT_Lim]
	ld b, a
	ldh a, [hOAMBufferOffset]
	add 16
	cp b
	jr z, .fit
	ret nc
.fit
	ldh [hOAMBufferOffset], a
	; うしろからずらす
	sub 16
	ld c, a                       ; ずらすバイト数
	ld h, HIGH(wShadowOAM)
	ld l, a
	dec l                         ; もとの最後
	ld d, h
	add 16 - 1
	ld e, a                       ; 新しい最後
	ld a, c
	and a
	jr z, .put
.move
	ld a, [hld]
	ld [de], a
	dec e
	dec c
	jr nz, .move
.put
	ld hl, wShadowOAM
	ld a, [wFwT_Y]
	sub 16
	ld b, a
	ld a, [wFwT_X]
	ld c, a
	ld d, EMOTE_TILE
	ld e, FW_MASK_PAL | %00001000
	call .row
	ld a, b
	add 8
	ld b, a
.row
	ld a, b
	ld [hli], a
	ld a, c
	ld [hli], a
	ld a, d
	ld [hli], a
	inc d
	ld a, e
	ld [hli], a
	ld a, b
	ld [hli], a
	ld a, c
	add 8
	ld [hli], a
	ld a, d
	ld [hli], a
	inc d
	ld a, e
	ld [hli], a
	ret

; ボールから出る（とじた → 半分 → 開いた。4フレームずつ）
FwDrawBall:
	dec a
	ld [wFwBallT], a
	ld hl, FwBallPal
	call FwSetPal
	ld a, [wFwBallT]
	cp BALL_TIME - 1
	ret z                         ; はじめの1フレームは色だけ（色がおくれて前の色で見えないように）
	srl a
	srl a                         ; 2,1,0
	add a
	add a
	add BALL_TILE
	ld [wFwT_Tile], a
	ld a, FW_PAL | %00001000
	ld [wFwT_Attr], a
	call FwGrass
	ld a, d
	ld [wFwT_Pri], a
	ld a, [wFwOY]
	add 76
	ld [wFwT_Y], a
	ld a, [wFwOX]
	add 72
	ld [wFwT_X], a
	; fallthrough

; wFwT_* の 16×16 を OAM に4枚
FwPut4:
	ldh a, [hOAMBufferOffset]
	ld l, a
	ld h, HIGH(wShadowOAM)
	ld a, [wFwT_Attr]
	ld e, a
	ld a, [wFwT_Tile]
	ld c, a
	ld a, [wFwT_Y]
	ld b, a
	ld a, [wFwT_X]
	ld d, a
	call .row
	ld a, [wFwT_Pri]
	or e
	ld e, a
	ld a, b
	add 8
	ld b, a
	inc c
	inc c
	call .row
	ld a, l
	ldh [hOAMBufferOffset], a
	ret
.row
	; 反転なら 左右のタイルを入れかえる
	ld a, b
	ld [hli], a
	ld a, d
	ld [hli], a
	ld a, c
	bit 5, e
	jr z, .l
	inc a
.l
	ld [hli], a
	ld a, e
	ld [hli], a
	ld a, b
	ld [hli], a
	ld a, d
	add 8
	ld [hli], a
	ld a, c
	bit 5, e
	jr nz, .r
	inc a
.r
	ld [hli], a
	ld a, e
	ld [hli], a
	ret

; d = 連れ歩きの足もとが草なら $80
FwGrass:
	ld d, 0
	ld a, [wFwOY]
	add 60 + 4
	and $F0
	srl a
	srl a
	srl a                         ; 画面のタイルの行
	inc a
	ld l, a
	ld h, 0
	push bc
	ld b, h
	ld c, l
	add hl, hl
	add hl, hl
	add hl, bc
	add hl, hl
	add hl, hl                    ; × 20
	ld a, [wFwOX]
	add 64
	srl a
	srl a
	srl a
	ld c, a
	ld b, 0
	add hl, bc
	ld bc, wTileMap
	add hl, bc
	ld a, [hl]
	ld b, a
	rd1 c, wGrassTile
	ld a, b
	cp c
	pop bc
	ret nz
	ld d, $80
	ret

; hl = 色1・色2（4バイト）。パレット6 がちがっていたら書く（マップを読みなおすと元にもどるので毎回見る）
FwSetPal:
	ld a, [hli]
	ld b, a
	ld a, [hli]
	ld c, a
	ld a, [hli]
	ld d, a
	ld e, [hl]
	ld a, 2
	ldh [rSVBK], a
	ld hl, W2_ObjPals + FW_PAL * 8 + 2
	ld a, [hli]
	cp b
	jr nz, .write
	ld a, [hli]
	cp c
	jr nz, .write
	ld a, [hli]
	cp d
	jr nz, .write
	ld a, [hli]
	cp e
	jr nz, .write
	ld a, [hli]
	or [hl]
	jr z, .back
.write
	ld hl, W2_ObjPals + FW_PAL * 8
	call .put
	ld hl, W2_ObjPalsNow + FW_PAL * 8
	call .put
	ld a, 1
	ld [W2_ObjPalSend], a
	ld [W2_ObjPalRecalc], a
	; カラー化の転送は1フレームおくれるので、新しい絵の OAM と同じ VBlank でじかにも書く
	;（クリスタルの「色を切りかえるときは絵とずれないように次の VBlank で書く」）
	ld a, W7
	ldh [rSVBK], a
	ld hl, wFwPalNew
	ld a, b
	ld [hli], a
	ld a, c
	ld [hli], a
	ld a, d
	ld [hli], a
	ld [hl], e
	ld a, 1
	ld [wFwPalPend], a
	ret
.back
	ld a, W7
	ldh [rSVBK], a
	ret
.put
	ld a, $FF
	ld [hli], a
	ld a, $7F
	ld [hli], a
	ld a, b
	ld [hli], a
	ld a, c
	ld [hli], a
	ld a, d
	ld [hli], a
	ld a, e
	ld [hli], a
	xor a
	ld [hli], a
	ld [hl], a
	ret

; --- 絵と色を読む（wFwLoaded の種類）→ wFwBuf、VBlank で VRAM1 へ -----------------
FwLoad:
	; ずかん番号
	ld a, [wFwLoaded]
	dec a
	ld l, a
	ld h, 0
	ld bc, POKEDEX_ORDER
	add hl, bc
	ld de, wFwDex
	ld bc, 1
	ld a, $10
	call FarCopyData
	ld a, [wFwDex]
	and a
	jr z, .bad
	cp 152
	jr c, .ok
.bad
	ld a, 1
	ld [wFwDex], a
.ok
	; 色
	ld a, [wFwDex]
	dec a
	ld l, a
	ld h, 0
	add hl, hl
	add hl, hl
	add hl, hl
	ld bc, FwPalTable
	add hl, bc
	ld de, wFwPals
	ld bc, 8
	call CopyData8
	; 絵：バンク = $36 + (番号 / 42)、場所 = $4000 + (番号 % 42) × 384
	ld a, [wFwDex]
	dec a
	ld b, 0
.div
	cp FOLLOW_PER_BANK
	jr c, .divd
	sub FOLLOW_PER_BANK
	inc b
	jr .div
.divd
	ld l, a
	ld h, 0
	ld d, h
	ld e, l
	add hl, hl
	add hl, de                    ; × 3
	add hl, hl
	add hl, hl
	add hl, hl
	add hl, hl
	add hl, hl
	add hl, hl
	add hl, hl                    ; × 384
	ld de, $4000
	add hl, de
	push hl
	push bc
	ld a, b
	add FOLLOW_GFX_BANK
	ld de, wFwBuf
	ld bc, 384
	call FarCopyData
	pop bc
	pop hl
	ld a, b
	add FOLLOW_MASK_BANK
	ld de, wFwBuf + 384
	ld bc, 384
	call FarCopyData
	ld hl, FwBallGfx
	ld de, wFwBuf + 768
	ld bc, 12 * 16
	call CopyData8
	ld a, 2
	ld [wFwGdma], a
	ret

FwBallPal: ; ボールの色（クリスタルの PAL_OW_RED の色1・色2）
	dw 31 | 19 << 5 | 10 << 10, 31 | 7 << 5 | 1 << 10

FwBallGfx:
	INCBIN "kit/follow/ball.2bpp", 0, 12 * 16

CopyData8:
	ld a, [hli]
	ld [de], a
	inc de
	dec bc
	ld a, b
	or c
	jr nz, CopyData8
	ret

; --- VBlank（看板の VBlank の前に） ----------------------------------------------
FollowerVBlank::
	ldh a, [rSVBK]
	ld e, a
	ld a, W7
	ldh [rSVBK], a
	ld hl, wFwFrame
	inc [hl]
	; パレット6 の色1・色2
	ld a, [wFwPalPend]
	and a
	jr z, .noPal
	xor a
	ld [wFwPalPend], a
	ld a, $80 | (FW_PAL * 8 + 2)
	ldh [rOCPS], a
	ld hl, wFwPalNew
	ld c, 4
.palByte                          ; VBlank がおそくなって画面をかきはじめていても、絵をかいている間（モード3）はさける
	ldh a, [rSTAT]
	and 3
	cp 3
	jr z, .palByte
	ld a, [hli]
	ldh [rOCPD], a
	dec c
	jr nz, .palByte
.noPal
	ld a, [wFwGdma]
	and a
	jr z, .done
	ld a, [wFwMark]
	cp $F0
	jr nz, .done
	ldh a, [rLY]
	cp 144
	jr c, .done
	cp 148
	jr nc, .done
	ldh a, [rHDMA5]
	bit 7, a
	jr z, .done                   ; ほかの HDMA の最中
	ldh a, [rVBK]
	ld d, a
	ld a, 1
	ldh [rVBK], a
	ld a, HIGH(wFwBuf)
	ldh [rHDMA1], a
	ld a, LOW(wFwBuf)
	ldh [rHDMA2], a
	ld a, $80
	ldh [rHDMA3], a
	xor a
	ldh [rHDMA4], a
	ld a, (768 + 12 * 16) / 16 - 1
	ldh [rHDMA5], a
	ld a, d
	ldh [rVBK], a
	xor a
	ld [wFwGdma], a
.done
	ld a, e
	ldh [rSVBK], a
	ret

; --- 手持ちの画面：SELECT で連れ歩くポケモンをえらぶ（赤い ★） -------------------------
;   HandlePartyMenuInput（$00:$1474）の「call HandleMenuInput_ / call PlaceUnfilledArrowMenuCursor /
;   ld b, a / xor a」を、ここをよぶ形にする。SELECT ならえらんでもう一度まつ。ほかのキーなら
;   b = キーで $1489 にもどる。★はレベルの右（hlcoord 11, 名前の行）に OAM の 40枚目（VRAM1 タイル 60・パレット6。パレットはぬけるときにもどす）。
DEF wMenuWatchedKeysInit EQU $1467 ; PartyMenuInit の「ld a, A_BUTTON | B_BUTTON」
DEF wCurrentMenuItem EQU $CC26
DEF wMenuItemToSwap EQU $CC35
DEF wPartyMenuAnimMonEnabled EQU $D078
DEF wWhichPokemon EQU $CF79
DEF wRemoveMonFromBox EQU $CF7C
DEF STAR_TILE EQU 60
DEF STAR_OAM EQU wShadowOAM + 39 * 4
DEF wFwSavedPal EQU $D040         ; WRAM7：手持ちの画面に入るときのパレット6
DEF SFX_SELECT EQU $90

SECTION "連れ歩き 手持ちの SELECT を見る", ROM0[$1467]
	ld a, PAD_A | PAD_B | 4

SECTION "連れ歩き 手持ちの入力", ROM0[$147E]
	ld b, BANK(FwPartyInput)
	ld hl, FwPartyInput
	call Bankswitch

SECTION "連れ歩き 手持ちの入れかえ", ROM0[$14E4]
	ld b, BANK(FwPartySwap)
	ld hl, FwPartySwap
	call Bankswitch

SECTION "連れ歩き 手持ちからのぞく", ROM0[RemovePokemonStub]
	ld hl, FwRemoveMon
	ld b, BANK(FwRemoveMon)
	jp Bankswitch

SECTION "連れ歩き 手持ち", ROMX[$7000], BANK[FOLLOW_BANK]
FwPartyInput:
	call FwStarStart
.loop
	call FwStarPut
	call HandleMenuInput_
	call PlaceUnfilledArrowMenuCursor
	ld b, a
	bit 2, b                      ; SELECT
	jr z, .out
	ld a, [wMenuItemToSwap]
	and a
	jr nz, .loop                  ; 入れかえの相手をえらんでいるとき
	ld a, [wPartyCount]
	and a
	jr z, .loop
	ld a, [wCurrentMenuItem]
	ld c, a
	ld a, [wFollowSel]
	cp c
	ld a, c
	jr nz, .set
	ld a, $FF                     ; もう一度で だれも連れ歩かない
.set
	ld [wFollowSel], a
	ld a, SFX_SELECT
	call PlaySound
	jr .loop
.out
	push bc
	call FwStarEnd
	pop bc
	xor a
	ld [wPartyMenuAnimMonEnabled], a
	pop hl                        ; Bankswitch のもどり先
	pop af                        ; もとのバンク
	pop hl                        ; $1486
	ld hl, $1489
	push hl
	jp Bankswitch + $10           ; ldh [hLoadedROMBank], a / ld [$2000], a / ret

; ★の絵と色
FwStarStart:
	; 絵（VRAM1 タイル 60）
	di
	ldh a, [rVBK]
	ld e, a
	ld a, 1
	ldh [rVBK], a
	ld hl, $8000 + STAR_TILE * 16
	ld bc, FwStarGfx
	ld d, 16
.tile
	ldh a, [rSTAT]
	and 2
	jr nz, .tile
	ld a, [bc]
	ld [hli], a
	inc bc
	dec d
	jr nz, .tile
	ld a, e
	ldh [rVBK], a
	ei
	; 色（パレット6 をとっておいて赤に）
	; W2 → W7 へ 8バイト（バンクを1バイトずつかえる）
	ld hl, W2_ObjPals + FW_PAL * 8
	ld c, 8
	ld de, wFwSavedPal
.save
	ld a, 2
	ldh [rSVBK], a
	ld a, [hli]
	ld b, a
	ld a, W7
	ldh [rSVBK], a
	ld a, b
	ld [de], a
	inc de
	dec c
	jr nz, .save
	xor a
	ldh [rSVBK], a
	ld hl, FwStarPal
	jp FwPutPal6

; hl = 8バイトをパレット6（もとの色・今の色）に書いて送る。WRAM バンクは 0 にしてもどる
FwPutPal6:
	xor a
	ldh [rSVBK], a
	ld de, W2_ObjPals + FW_PAL * 8
	push hl
	call .copy
	pop hl
	ld de, W2_ObjPalsNow + FW_PAL * 8
	call .copy
	ld a, 2
	ldh [rSVBK], a
	ld a, 1
	ld [W2_ObjPalSend], a
	xor a
	ldh [rSVBK], a
	ret
.copy
	ld c, 8
.c1
	ld a, W7                      ; hl は ROM か WRAM7
	ldh [rSVBK], a
	ld a, [hli]
	ld b, a
	ld a, 2
	ldh [rSVBK], a
	ld a, b
	ld [de], a
	inc de
	dec c
	jr nz, .c1
	xor a
	ldh [rSVBK], a
	ret

FwStarEnd:
	ld a, $A0
	ld [STAR_OAM], a
	ld hl, wFwSavedPal
	jp FwPutPal6

FwStarPut:
	ld a, [wFollowSel]
	ld c, a
	ld a, [wPartyCount]
	ld b, a
	ld a, c
	cp b
	ld a, $A0
	jr nc, .y
	ld a, c
	swap a                        ; × 16
	add 16 + 8                    ; 名前の行（状態異常の行には「どく」などが出るのでさける）
.y
	ld hl, STAR_OAM
	ld [hli], a
	ld a, 11 * 8 + 8              ; レベル（「：L100」まで）の右・HP の数字の左
	ld [hli], a
	ld a, STAR_TILE
	ld [hli], a
	ld [hl], FW_PAL | %00001000
	ret

FwStarPal:
	dw $7FFF, 31 | 2 << 5 | 2 << 10, 16 | 0 << 5 | 0 << 10, 0
FwStarGfx: ; ★（色1・ふちは色2）
	db %00010000, %00010000
	db %00010000, %00111000
	db %01111100, %11111110
	db %00111000, %01111100
	db %00111000, %01111100
	db %01101100, %11111110
	db %01000100, %11000110
	db %00000000, %00000000

; 入れかえ（$04:$67EB）のまわり：2つの番号を見て、えらんだポケモンの番号も入れかえる
FwPartySwap:
	ld a, [wMenuItemToSwap]
	and a
	jr z, .call                   ; 1つ目をえらんだだけ
	dec a
	ld d, a
	ld a, [wCurrentMenuItem]
	ld e, a
	push de
	call .call
	pop de
	ld a, d
	cp e
	ret z
	ld a, [wFollowSel]
	cp d
	jr nz, .notD
	ld a, e
	ld [wFollowSel], a
	ret
.notD
	cp e
	ret nz
	ld a, d
	ld [wFollowSel], a
	ret
.call
	ld b, $04
	ld hl, $67EB
	jp Bankswitch

; 手持ちからのぞく（あずける・にがす など）：えらんだポケモンより前がぬけたら番号を1つへらす
FwRemoveMon:
	ld a, [wRemoveMonFromBox]
	and a
	jr nz, .call
	ld a, [wWhichPokemon]
	ld c, a
	ld a, [wFollowSel]
	cp 6
	jr nc, .call
	cp c
	jr c, .call
	jr nz, .dec
	xor a                         ; 連れ歩いていたポケモン：先頭にする
	jr .set
.dec
	dec a
.set
	ld [wFollowSel], a
.call
	ld b, $01
	ld hl, $7D85
	jp Bankswitch

; --- 話しかける -------------------------------------------------------------------
;   A ボタンで前を調べる所（$00:$3F85 の call IsSpriteOrSignInFrontOfPlayer のあとの farcall $0A:$7800）を
;   ここにする。元の処理のあと、人・看板などがなく（hSpriteIndexOrTextID = 0）、連れ歩きが前にいれば、
;   ふりむいて鳴き、気持ちのアイコンを出して会話（会話文案.md）。テキストは DisplayTextID に
;   テキストの表をかえて出す（wTextPredefFlag の bit0 でマップのバンクにしない）。
DEF hSpriteIndexOrTextID EQU $FF8C
DEF hRandomAdd EQU $FFD3
DEF wTextPredefFlag EQU $CF0C
DEF wAutoTextBoxDrawingControl EQU $CF07 ; bit 0 = 1：DisplayTextIDInit が窓の枠をかかない
DEF wMapTextPtr EQU $D2EB
DEF wPartyMon1Status EQU $D12B + 4
DEF wPartyMonNicks EQU $D257
DEF PlayCry EQU $13EA
DEF FW_TEXT_ID EQU $81             ; 表の n 番目 = $81 + n（(ID−1)×2 の下8ビットが 2n になる）
DEF NUGGET EQU $31
DEF EMOTE_TILE EQU 61
DEF wFwEmote EQU $D027             ; WRAM7：気持ちのアイコン（0 = なし、1〜7）
DEF wFwDrawn EQU $D036             ; WRAM7：このフレームに連れ歩きをかいた
DEF wFwSel EQU $D037               ; WRAM7：FwWant の手持ちの番号

SECTION "連れ歩き 話しかける 入口", ROM0[FwTalkHookAddr]
	ld b, BANK(FwTalkCheck)
	ld hl, FwTalkCheck

SECTION "連れ歩き 話しかける", ROMX[$7400], BANK[FOLLOW_BANK]
FwTalkCheck:
	ld b, $0A
	ld hl, $7800
	call Bankswitch
	ldh a, [hSpriteIndexOrTextID]
	and a
	ret nz
	ld a, W7
	ldh [rSVBK], a
	call FwFront
	ld a, 0
	ldh [rSVBK], a
	ret nc
	call FwTalk
	xor a
	ldh [hSpriteIndexOrTextID], a
	ret

; WRAM7 で：連れ歩きが主人公のとなりで止まっていて見えていれば carry、c = 連れ歩きのいる向き（主人公から見て）
;   初代はその場でふりむくのがむずかしいので、前でなくても となりにいれば主人公がそちらを向いて話す
FwFront:
	ld a, [wFwDrawn]
	and a
	ret z
	ld a, [wFwBallT]
	and a
	ret nz
	ld hl, wFwOX
	ld a, [wFwTX]
	cp [hl]
	ret nz
	ld b, [hl]                    ; OX
	inc hl
	ld a, [wFwTY]
	cp [hl]
	ret nz
	ld e, [hl]                    ; OY
	ld d, b
	ld c, $00                     ; 下
	ld a, d
	and a
	jr nz, .side
	ld a, e
	cp 16
	jr z, .ok
	ld c, $04                     ; 上
	cp -16 & $FF
	jr z, .ok
	and a
	ret
.side
	ld a, e
	and a
	ret nz
	ld c, $08                     ; 左
	ld a, d
	cp -16 & $FF
	jr z, .ok
	ld c, $0C                     ; 右
	cp 16
	jr z, .ok
	and a
	ret
.ok
	push bc
	call FwWant
	pop bc
	ld a, e
	and a
	ret z
	ld a, d
	and a
	ret nz
	scf
	ret

FwTalk:
	; 主人公が連れ歩きのほうを向く
	ld a, c
	ld [wPlayerFacing], a
	; 連れ歩きがふりむく
	xor $04
	ld b, a
	ld a, W7
	ldh [rSVBK], a
	ld a, b
	ld [wFwDir], a
	ld a, [wFwSel]
	ld b, a
	xor a
	ldh [rSVBK], a
	ld a, b
	ld [wWhichPokemon], a
	ld c, 4
	call DelayFrames
	; 鳴く
	ld a, [wWhichPokemon]
	ld hl, wPartySpecies
	call FwAddA
	ld a, [hl]
	ld [wFwTalkSpecies], a
	call PlayCry
	; 名前
	ld a, [wWhichPokemon]
	ld hl, wPartyMonNicks
	ld bc, 6
	call FwAddTimes
	ld de, wNameBuffer
	ld bc, 6
	call CopyData8
	; 会話をえらぶ → a = 文の番号
	call FwPickText
	ld [wFwTalkText], a
	; 気持ちのアイコン
	ld hl, FwTalkEmotes
	call FwAddA
	ld a, [hl]
	call FwShowEmote
	; テキスト
	ld hl, wMapTextPtr
	ld a, [hli]
	ld e, a
	ld a, [hl]
	ld d, a
	push de
	ld a, HIGH(FwTalkTexts)
	ld [hld], a
	ld [hl], LOW(FwTalkTexts)
	ld hl, wTextPredefFlag
	set 0, [hl]
	ld a, [wFwTalkText]
	add FW_TEXT_ID
	ldh [hSpriteIndexOrTextID], a
	; 窓の枠をかく。オーキド博士の研究所などは、マップのスクリプトが「枠をかかない」
	; （wAutoTextBoxDrawingControl の bit 0）にしているので、会話の間だけ 0 にして、あとで元にもどす
	; （この bit を読むのは DisplayTextIDInit（01:717D）だけ）
	ld a, [wAutoTextBoxDrawingControl]
	push af
	res 0, a
	ld [wAutoTextBoxDrawingControl], a
	call DisplayTextID
	pop af
	ld [wAutoTextBoxDrawingControl], a
	pop de
	ld hl, wMapTextPtr
	ld a, e
	ld [hli], a
	ld [hl], d
	ret

DEF wFwTalkSpecies EQU $CD68 + 8   ; wNameBuffer のうしろ（話しかけている間だけ）
DEF wFwTalkText EQU $CD68 + 9
DEF wFwTalkTypes EQU $CD68 + 12

FwAddA:
	add l
	ld l, a
	ret nc
	inc h
	ret

FwAddTimes: ; hl += a × bc
	and a
	ret z
.l
	add hl, bc
	dec a
	jr nz, .l
	ret

; 気持ちのアイコン a（0〜6）を 約40フレーム出す
FwShowEmote:
	push af
	; 絵（VRAM1 タイル 61〜64）
	ld l, a
	ld h, 0
	add hl, hl
	add hl, hl
	add hl, hl
	add hl, hl
	add hl, hl
	add hl, hl                    ; × 64
	ld bc, FwEmoteGfx
	add hl, bc
	ld b, h
	ld c, l
	di
	ldh a, [rVBK]
	ld e, a
	ld a, 1
	ldh [rVBK], a
	ld hl, $8000 + EMOTE_TILE * 16
	ld d, 64
.tile
	ldh a, [rSTAT]
	and 2
	jr nz, .tile
	ld a, [bc]
	ld [hli], a
	inc bc
	dec d
	jr nz, .tile
	ld a, e
	ldh [rVBK], a
	ei
	pop af
	inc a
	call .set
	ld c, 40
	call DelayFrames
	xor a
	call .set
	ld c, 2
	jp DelayFrames
.set
	ld b, a
	ld a, W7
	ldh [rSVBK], a
	ld a, b
	ld [wFwEmote], a
	xor a
	ldh [rSVBK], a
	ret

; 会話をえらぶ（a = 文の番号）
FwPickText:
	; 1. 状態異常
	ld a, [wWhichPokemon]
	ld hl, wPartyMon1Status
	ld bc, PARTYMON_LEN
	call FwAddTimes
	ld a, [hl]
	ld b, a
	and %111
	ld a, FWT_SLEEP
	ret nz
	bit 3, b
	ld a, FWT_POISON
	ret nz
	bit 4, b
	ld a, FWT_BURN
	ret nz
	bit 5, b
	ld a, FWT_FREEZE
	ret nz
	bit 6, b
	ld a, FWT_PARALYZE
	ret nz
	; 2. カントー（種類・タイプと場所）
	call FwGetTypes
	ld hl, FwTalkRules
.rule
	ld a, [hli]
	cp $FF
	jr z, .normal
	ld b, a                       ; 0 種類・1 タイプ
	ld c, 0                       ; あてはまったら 1
.val
	ld a, [hli]
	cp $FF
	jr z, .maps
	ld e, a
	ld a, b
	and a
	jr nz, .type
	ld a, [wFwTalkSpecies]
	cp e
	jr nz, .val
	ld c, 1
	jr .val
.type
	ld a, [wFwTalkTypes]
	cp e
	jr z, .tyOk
	ld a, [wFwTalkTypes + 1]
	cp e
	jr nz, .val
.tyOk
	ld c, 1
	jr .val
.maps
	ld a, [wCurMap]
	ld e, a
.map
	ld a, [hli]
	cp $FF
	jr z, .next
	cp e
	jr nz, .map
	ld a, c
	and a
	jr z, .map
	; あてはまった：文の数 [hl]、はじめ [hl+1] からランダム
.skip
	ld a, [hli]
	cp $FF
	jr nz, .skip
	ld a, [hli]
	ld b, a
	ld c, [hl]
	ldh a, [hRandomAdd]
.mod
	cp b
	jr c, .modd
	sub b
	jr .mod
.modd
	add c
	ret
.next
	inc hl
	inc hl
	jr .rule
.normal
	; 4. ふつう（たまに どうぐを見つける）
	ldh a, [hRandomAdd]
	and 31
	ld a, FWT_FOUND
	ret z
	ld a, FWT_NORMAL
	ret

; wFwTalkTypes に タイプ2つ（種族値の表：ずかん番号−1 × 28 ＋ 6。ミュウはバンク1）
FwGetTypes:
	ld a, [wFwTalkSpecies]
	dec a
	ld hl, POKEDEX_ORDER
	call FwAddA
	ld de, wFwTalkTypes
	ld bc, 1
	ld a, $10
	call FarCopyData
	ld a, [wFwTalkTypes]
	cp 151
	jr z, .mew
	dec a
	ld hl, $43DE + 6
	ld bc, 28
	call FwAddTimes
	ld a, $0E
	jr .copy
.mew
	ld hl, $4112 + 6
	ld a, $01
.copy
	ld de, wFwTalkTypes
	ld bc, 2
	jp FarCopyData

; どうぐを見つけた（テキストの中の TX_ASM から）
FwFoundAsm:
	ld hl, FwText_FoundMsg
	call PrintText
	call YesNoChoice
	ld a, [wCurrentMenuItem]
	and a
	jr nz, .end
	ld b, NUGGET
	ld c, 1
	call GiveItem
	jr nc, .end
	ld hl, FwText_Got
	call PrintText
.end
	ld hl, .at
	ret
.at
	db "@"

FwEmoteGfx:
	INCBIN "kit/follow/emotes.2bpp"

INCLUDE "follow_talk.inc"

ENDC
