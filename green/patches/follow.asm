; 連れ歩き（全ポケモン）— 赤緑青ピカチュウ連れ歩きキット を 緑の しくみで 作ったもの
; 入れる 版：金銀グラフィックの 完全版・60fps版・151匹そろう版・151匹そろう版 60fps（ED_0・ED_4・ED_8・ED_10）
;
; しくみ（初代の 人の スプライトの スロットは 使わない）
;   ・連れ歩きの 絵は OAM に じぶんで 足す（PrepareOAMData の さいご = KitOAMSignHide の はじめ）。
;     主人公の 画面の 位置 ＋ 「主人公からの ずれ」 に かく。ずれは、主人公の 歩き（画面の スクロール）と
;     連れ歩きの 歩き（主人公が いた ますへ、主人公と 同じ はやさで）で 毎フレーム かわる。
;   ・絵（24 タイル）と 白い 下じき（24 タイル）は VRAMバンク1 の $8000〜$82FF に、
;     ポケモンが かわった ときだけ HDMA で 読む（データは バンク $2E〜$31・$32・$36・$38・$39）。
;   ・色は OBJ パレット 6（外では 使われて いない）に 手持ちの アイコンと 同じ 色、下じきは パレット 5（色1 が 白）。
;   ・ドア・そらをとぶ などで マップを 読んだら（LoadMapData）、主人公と 同じ ますに して かくし、1歩 あるくと 出る。
;   ・自転車・なみのり・ひんし・手持ちなし の ときは かくす。
;   ・状態は WRAMバンク7（$D010〜）。バンクを かえて いる あいだは call / push / pop を しない。

DEF hSCX_             EQU $ffae
DEF hSCY_             EQU $ffaf
DEF wPlayerYStep      EQU $c103
DEF wPlayerYPixels    EQU $c104
DEF wPlayerXStep      EQU $c105
DEF wPlayerXPixels    EQU $c106
DEF wPartyCount       EQU $d123
DEF wPartySpecies     EQU $d124
DEF wPartyMon1HP      EQU $d12c
DEF PARTYMON_LEN      EQU 44
DEF wWalkBikeSurfState EQU $d67f
DEF FW_PAL            EQU 6      ; 連れ歩きの OBJ パレット
DEF FW_MASK_PAL       EQU 5      ; 下じき（色1 が 白）
DEF FW_VRAM_GFX       EQU $8000  ; VRAMバンク1 の タイル $00〜$17
DEF FW_VRAM_MASK      EQU $8180  ; VRAMバンク1 の タイル $18〜$2F
DEF FW_VRAM_STAR      EQU $8300  ; VRAMバンク1 の タイル $30（手持ちの 画面の ★）
DEF wFollowSlot       EQU $d689  ; 連れ歩く 手持ちの 番号（レポートに 書かれる 所。0 = 1 匹め、$FF = だれも）
DEF wCurrentMenuItem  EQU $cc26
DEF wMenuItemToSwap   EQU $cc35
DEF wPartyMenuType    EQU $d05a
DEF wIsInBattle_      EQU $d034
; WRAMバンク2（カラー化の パレット）
DEF w2ObPal6Src       EQU $d040 + FW_PAL * 8 + 2
DEF w2ObPal6Cur       EQU $d744 + FW_PAL * 8 + 2
DEF w2ObjPalDirty     EQU $d785  ; 1 に すると VBlank で OBJ パレットを 送る
; WRAMバンク7
DEF FW_SIG            EQU $d010  ; $A5,$5A
DEF FW_OY             EQU $d012  ; 主人公からの ずれ（ドット、符号つき）
DEF FW_OX             EQU $d013
DEF FW_DY             EQU $d014  ; 1歩の 向き（-1・0・1）
DEF FW_DX             EQU $d015
DEF FW_PROG           EQU $d016  ; 1歩の すすみ（0〜15）
DEF FW_FACE           EQU $d017  ; 0 下・1 上・2 左・3 右
DEF FW_LSCX           EQU $d018
DEF FW_LSCY           EQU $d019
DEF FW_FLAGS          EQU $d01a  ; bit0 位置を もどす・bit1 絵を 読みなおす
DEF FW_DEX            EQU $d01b  ; VRAM に ある 絵の ずかん番号（0 = なし）
DEF FW_WANT           EQU $d01c  ; 連れ歩く ずかん番号（0 = なし）
DEF FW_REQ            EQU $d01d  ; 絵を 読む ずかん番号
DEF FW_ATTR           EQU $d01e
DEF FW_FLIP           EQU $d01f
DEF FW_MAP            EQU $d020  ; 前の フレームの マップ・たて・横（戦闘から もどった ときは 位置を そのまま に）
DEF FW_MY             EQU $d021
DEF FW_MX             EQU $d022
DEF FW_NMAP           EQU $d023  ; この フレームの マップ・たて・横
DEF FW_NMY            EQU $d024
DEF FW_NMX            EQU $d025
DEF wCurMap_          EQU $d2dd
DEF wYCoord_          EQU $d2e0
DEF wXCoord_          EQU $d2e1

DEF wShadowOAM        EQU $c300

; 16×16 を OAM に 4 枚（hl = OAM、b = Y、c = X、d = タイル、FW_FLIP・FW_ATTR）
MACRO FW_OBJ
	FW_ONE 0, 0, 0
	FW_ONE 0, 8, 1
	FW_ONE 8, 0, 2
	FW_ONE 8, 8, 3
ENDM
MACRO FW_ONE ; たて, 横, タイル（0 左上・1 右上・2 左下・3 右下）
	ld a, b
IF \1
	add \1
ENDC
	ld [hli], a
	ld a, c
IF \2
	add \2
ENDC
	ld [hli], a
	ld a, [FW_FLIP]       ; はんてん なら 左右の タイルを 入れかえる
IF (\3) & 1
	xor 1
ENDC
	add d
IF (\3) & 2
	add 2
ENDC
	ld [hli], a
	ld a, [FW_ATTR]
	ld [hli], a
ENDM

SECTION "連れ歩き マップを 読む 所", ROM0[$2b7f]
	ld b, $37
	ld hl, FwOnWarp
SECTION "連れ歩き 人の 絵を 読みなおす 所", ROM0[$3d27]
	ld b, $37
	ld hl, FwOnReload
SECTION "連れ歩き 手持ち SELECT も 見る", ROM0[$2d36]
	db PAD_A | PAD_B | 4
SECTION "連れ歩き 手持ち ボタン", ROM0[$2d4c]
	ld hl, FwPartyInput
	ld b, $37
	call $3500
	ld b, e
	nop
	nop
SECTION "連れ歩き 手持ち ならびかえ", ROM0[$2db2]
	ld b, $37
	ld hl, FwSwap
SECTION "連れ歩き 手持ち かく", ROM0[$2dbd]
	dw FwDrawParty
SECTION "連れ歩き 手持ち かきなおす", ROM0[$2dc2]
	dw FwRedrawParty
SECTION "連れ歩き 手持ち かく バンク", ROM0[$2dc5]
	db $37

; 1 匹 ぶん（24 タイル）を VRAMバンク1 に 読む（e = バンクの 中の 番号。Bankswitch が bc を こわすので e で わたす）
MACRO FW_DATA_BANK
SECTION "連れ歩き データ \1", ROMX[$4000], BANK[\1]
FwBankLoad\@:
	ld a, e
	ld hl, $4100
	ld bc, 24 * 16
.mul\@
	and a
	jr z, .got\@
	add hl, bc
	dec a
	jr .mul\@
.got\@
	ld a, h
	ldh [$ff51], a
	ld a, l
	ldh [$ff52], a
	ld a, HIGH(\3)
	ldh [$ff53], a
	ld a, LOW(\3)
	ldh [$ff54], a
	ld a, 1
	ldh [$ff4f], a
	ldh a, [$ff40]
	bit 7, a
	ld a, 24 - 1
	jr z, .now\@
	or $80                ; HBlank DMA（1 行に 16 バイト）
	ldh [$ff55], a
.wait\@
	ldh a, [$ff55]
	inc a
	jr nz, .wait\@
	jr .done\@
.now\@
	ldh [$ff55], a        ; 画面が 切れて いる ときは すぐ
.done\@
	xor a
	ldh [$ff4f], a
	ret
SECTION "連れ歩き データ \1 中身", ROMX[$4100], BANK[\1]
	INCBIN \2
ENDM
	FW_DATA_BANK $2e, "follow/gfx0.bin", FW_VRAM_GFX
	FW_DATA_BANK $2f, "follow/gfx1.bin", FW_VRAM_GFX
	FW_DATA_BANK $30, "follow/gfx2.bin", FW_VRAM_GFX
	FW_DATA_BANK $31, "follow/gfx3.bin", FW_VRAM_GFX
	FW_DATA_BANK $32, "follow/mask0.bin", FW_VRAM_MASK
	FW_DATA_BANK $36, "follow/mask1.bin", FW_VRAM_MASK
	FW_DATA_BANK $38, "follow/mask2.bin", FW_VRAM_MASK
	FW_DATA_BANK $39, "follow/mask3.bin", FW_VRAM_MASK

SECTION "連れ歩き", ROMX[$6000], BANK[$37]
; ---------------------------------------------------------------- マップを 読む とき（画面が 切れて いる）
FwOnWarp:
	ld a, 3                ; 位置を もどす ＋ 絵を 読みなおす
	jr FwSetFlags
FwOnReload:
	ld a, 2                ; 絵を 読みなおす（メニューから もどった など）
FwSetFlags:
	ld c, a
	di
	ldh a, [rSVBK_]
	ld e, a
	ld a, 7
	ldh [rSVBK_], a
	ld a, [FW_FLAGS]
	or c
	ld [FW_FLAGS], a
	ld a, e
	ldh [rSVBK_], a
	ei
	ld b, $05
	ld hl, $7840           ; InitMapSprites（元の よび出し）
	jp $3500

; 連れ歩く 手持ちの 番号（0〜5、$FF = だれも）
FwGetSlot:
	ld a, [wFollowSlot]
	ret

; ---------------------------------------------------------------- 手持ちの 画面
; SELECT で 連れ歩く ポケモンを えらぶ（もう一度 おすと だれも 連れ歩かない）
; HandlePartyMenuInput の HandleMenuInput_ ・ PlaceUnfilledArrowMenuCursor の かわり（おされた ボタンを e で かえす）
FwPartyInput:
	call $39ec             ; HandleMenuInput_
	call $3afc             ; PlaceUnfilledArrowMenuCursor
	ld e, a
	bit 2, a               ; SELECT
	jr z, .done
	ld a, [wMenuItemToSwap]
	and a
	jr nz, FwPartyInput    ; ならびかえ の とちゅう
	ld a, [wPartyMenuType]
	and a
	jr nz, FwPartyInput    ; どうぐを つかう など
	ld a, [wIsInBattle_]
	and a
	jr nz, FwPartyInput
	ld a, [wCurrentMenuItem]
	ld b, a
	ld a, [wFollowSlot]
	cp b
	ld a, b
	jr nz, .set
	ld a, $ff
.set
	ld [wFollowSlot], a
	call FwStar
	jr FwPartyInput
.done
	xor a
	ld [$d078], a          ; wPartyMenuAnimMonEnabled（元の 処理）
	ret

; ならびかえ（SwitchPartyMon）で 連れ歩く 番号も 入れかえる
FwSwap:
	ld a, [wMenuItemToSwap]
	dec a
	ld d, a
	ld a, [wCurrentMenuItem]
	ld e, a
	ld a, [wFollowSlot]
	cp d
	jr nz, .notD
	ld a, e
	jr .set
.notD
	cp e
	jr nz, .call
	ld a, d
.set
	ld [wFollowSlot], a
.call
	ld b, $04
	ld hl, $610b           ; SwitchPartyMon
	call $3500
	jr FwStar

; 手持ちの 画面を かく 所（DrawPartyMenu・RedrawPartyMenu）の あとに ★
FwDrawParty:
	ld b, $04
	ld hl, $6680
	call $3500
	jr FwStar
FwRedrawParty:
	ld b, $04
	ld hl, $6691
	call $3500
	; fallthrough

; 連れ歩く ポケモンの 行の 「：Ｌ」の 右上に 赤い ★（OAM の 40 枚めを 使う。パレット5 の 色2 が 赤）
FwStar:
	ld hl, FwStarGfx
	ld de, FW_VRAM_STAR
	ld c, 8
.gfx
	di
	ld a, 1
	ldh [rVBK_], a
	ldh a, [$ff40]
	bit 7, a
	jr z, .write           ; 画面が 切れて いる
	ldh a, [$ff44]
	cp $90
	jr nc, .write
.w1
	ldh a, [$ff41]
	and 2
	jr z, .w1
.w2
	ldh a, [$ff41]
	and 2
	jr nz, .w2
.write
	ld a, [hli]
	ld [de], a
	inc de
	ld a, [hli]
	ld [de], a
	inc de
	xor a
	ldh [rVBK_], a
	ei
	dec c
	jr nz, .gfx
	ld hl, wShadowOAM + 39 * 4
	ld a, [wFollowSlot]
	cp 6
	jr nc, .hide
	ld c, a
	ld a, [wPartyCount]
	dec a
	cp c
	jr c, .hide
	ld a, c
	swap a
	add 16                 ; 名前の 行（2 × 番号 行め）
	ld [hli], a
	ld a, 10 * 8 + 8       ; 10 マスめ
	ld [hli], a
	ld a, LOW(FW_VRAM_STAR / 16)
	ld [hli], a
	ld [hl], $08 | FW_MASK_PAL
	ret
.hide
	ld [hl], $a0
	ret

FwStarGfx:
	db $00, $10, $00, $38, $00, $fe, $00, $7c, $00, $38, $00, $6c, $00, $44, $00, $00

; ---------------------------------------------------------------- 毎フレーム（VBlank、PrepareOAMData の さいご）
FwFrame:
; 1. 連れ歩く ポケモンの ずかん番号を d に（0 = なし）
	ld d, 0
	ld a, [wWalkBikeSurfState]
	and a
	jr nz, .gotWant
	call FwGetSlot
	cp 6
	jr nc, .gotWant
	ld c, a
	ld a, [wPartyCount]
	dec a
	cp c
	jr c, .gotWant
	ld b, 0
	ld hl, wPartySpecies
	add hl, bc
	ld e, [hl]
	ld hl, wPartyMon1HP
	ld a, c
	ld bc, PARTYMON_LEN
.mul
	and a
	jr z, .hp
	add hl, bc
	dec a
	jr .mul
.hp
	ld a, [hli]
	or [hl]
	jr z, .gotWant          ; ひんし
	ld a, e
	and a
	jr z, .gotWant
	cp 190 + 1
	jr nc, .gotWant
	ld c, a
	ld b, 0
	ld hl, FwDexTable - 1
	add hl, bc
	ld d, [hl]
.gotWant

	ld a, [wCurMap_]
	ld b, a
	ld a, [wYCoord_]
	ld c, a
	ld a, [wXCoord_]
	ld l, a
; 2. WRAMバンク7 で 動きと OAM（ここでは call / push / pop を しない）
	ldh a, [rSVBK_]
	ld e, a
	ld a, 7
	ldh [rSVBK_], a
	ld a, b
	ld [FW_NMAP], a
	ld a, c
	ld [FW_NMY], a
	ld a, l
	ld [FW_NMX], a
	ld a, [FW_SIG]
	cp $a5
	jr nz, .init
	ld a, [FW_SIG + 1]
	cp $5a
	jr z, .inited
.init
	ld hl, FW_SIG
	ld a, $a5
	ld [hli], a
	ld a, $5a
	ld [hli], a
	xor a
	ld b, FW_FLIP - FW_OY + 1
.zero
	ld [hli], a
	dec b
	jr nz, .zero
	ldh a, [hSCX_]
	ld [FW_LSCX], a
	ldh a, [hSCY_]
	ld [FW_LSCY], a
	ld a, 2
	ld [FW_FLAGS], a
.inited
	; マップ・位置が 前の フレームと 同じなら（戦闘・メニューから もどった）、位置は もどさない
	ld a, [FW_NMAP]
	ld b, a
	ld a, [FW_NMY]
	ld c, a
	ld a, [FW_NMX]
	ld l, a
	ld h, 0
	ld a, [FW_MAP]
	cp b
	jr nz, .moved
	ld a, [FW_MY]
	cp c
	jr nz, .moved
	ld a, [FW_MX]
	cp l
	jr z, .samePlace
.moved
	inc h
.samePlace
	ld a, b
	ld [FW_MAP], a
	ld a, c
	ld [FW_MY], a
	ld a, l
	ld [FW_MX], a
	ld a, h
	and a
	jr nz, .keepReset
	ld a, [FW_FLAGS]
	and $fe
	ld [FW_FLAGS], a
.keepReset
	; 連れ歩かない → 連れ歩く に かわったら、主人公と 同じ ますから（1歩 あるくと 出る）
	ld a, [FW_WANT]
	ld b, a
	ld a, d
	ld [FW_WANT], a
	and a
	jr z, .wantOk
	ld a, b
	and a
	jr nz, .wantOk
	ld a, [FW_FLAGS]
	or 1
	ld [FW_FLAGS], a
.wantOk
	; 画面の スクロール（= 主人公の 動き）
	ldh a, [hSCX_]
	ld hl, FW_LSCX
	ld c, [hl]
	ld [hl], a
	sub c
	ld c, a                ; c = 横の 動き
	ldh a, [hSCY_]
	ld hl, FW_LSCY
	ld b, [hl]
	ld [hl], a
	sub b
	ld b, a                ; b = たての 動き
	ld a, [FW_FLAGS]
	bit 0, a
	jr z, .noReset
	and $fe
	ld [FW_FLAGS], a
	xor a
	ld [FW_OY], a
	ld [FW_OX], a
	ld [FW_PROG], a
	jp .moveDone
.noReset
	ld a, [wPlayerYStep]   ; 主人公が 歩いて いない（エレベーターの ゆれ など）なら 動かない
	ld h, a
	ld a, [wPlayerXStep]
	or h
	jp z, .moveDone
	ld a, b
	or c
	jp z, .moveDone
	ld a, [FW_PROG]
	and a
	jr nz, .inStep
	; 1歩の はじめ：主人公が いた ます（今の ずれの 反対）へ
	ld h, 0
	ld a, [FW_OY]
	and a
	jr z, .dy
	ld h, 1
	bit 7, a
	jr nz, .dy
	ld h, $ff
.dy
	ld l, 0
	ld a, [FW_OX]
	and a
	jr z, .dx
	ld l, 1
	bit 7, a
	jr nz, .dx
	ld l, $ff
.dx
	ld a, h
	ld [FW_DY], a
	ld a, l
	ld [FW_DX], a
	; 向き
	ld a, h
	or l
	jr nz, .faceDir
	; かくれて いた（ずれ 0）：主人公の 進む 向き
	ld h, b
	ld l, c
.faceDir
	ld a, h
	and a
	jr z, .faceX
	bit 7, a
	ld a, 0                ; 下
	jr z, .setFace
	inc a                  ; 上
	jr .setFace
.faceX
	ld a, l
	bit 7, a
	ld a, 2                ; 左
	jr nz, .setFace
	inc a                  ; 右
.setFace
	ld [FW_FACE], a
.inStep
	; h = はやさ（|たて| ＋ |横|）
	ld a, b
	bit 7, a
	jr z, .ab
	cpl
	inc a
.ab
	ld h, a
	ld a, c
	bit 7, a
	jr z, .ac
	cpl
	inc a
.ac
	add h
	ld h, a
	; たて：ずれ = ずれ − 主人公の 動き ＋ 向き × はやさ
	ld a, [FW_DY]
	ld l, a
	ld a, [FW_OY]
	sub b
	bit 7, l
	jr nz, .yNeg
	dec l
	jr nz, .yDone
	add h
	jr .yDone
.yNeg
	sub h
.yDone
	ld [FW_OY], a
	ld a, [FW_DX]
	ld l, a
	ld a, [FW_OX]
	sub c
	bit 7, l
	jr nz, .xNeg
	dec l
	jr nz, .xDone
	add h
	jr .xDone
.xNeg
	sub h
.xDone
	ld [FW_OX], a
	ld a, [FW_PROG]
	add h
	cp 16
	jr c, .progOk
	xor a                  ; 1歩 おわり
.progOk
	ld [FW_PROG], a
.moveDone
	; 絵が VRAM に あるか
	ld a, d
	and a
	jp z, .noDraw
	ld hl, FW_DEX
	cp [hl]
	jr nz, .needGfx
	ld a, [FW_FLAGS]
	bit 1, a
	jr z, .gfxOk
.needGfx
	ld a, d
	ld [FW_REQ], a
	jp .noDraw
.gfxOk
	ld a, [FW_OY]
	ld b, a
	ld a, [FW_OX]
	ld c, a
	or b
	jp z, .noDraw          ; 主人公と 同じ ます
	ldh a, [hOAMBufOfs]
	cp $a0 - 8 * 4 + 1
	jp nc, .noDraw         ; OAM が たりない
	ld l, a
	ld h, HIGH(wShadowOAM)
	ld a, [wPlayerYPixels]
	add b
	add 16
	ld b, a
	ld a, [wPlayerXPixels]
	add c
	add 8
	ld c, a
	; 絵の コマ：0 下・1 上・2 横（＋3 で 歩き）
	ld a, [FW_FACE]
	cp 3
	jr c, .frame
	ld a, 2
.frame
	ld d, a
	ld a, [FW_PROG]
	cp 4
	jr c, .stand
	cp 12
	jr nc, .stand
	ld a, d
	add 3
	ld d, a
.stand
	ld a, d
	add a
	add a
	ld d, a                ; タイルの はじめ
	ld a, [FW_FACE]
	cp 3
	ld a, 0
	jr nz, .noFlip
	inc a
.noFlip
	ld [FW_FLIP], a
	and a
	ld a, $08 | FW_PAL     ; VRAMバンク1
	jr z, .attr
	or $20                 ; 右は 左向きを はんてん
.attr
	ld [FW_ATTR], a
	FW_OBJ
	ld a, d
	add 24                 ; 白い 下じき
	ld d, a
	ld a, [FW_ATTR]
	and $f8
	or FW_MASK_PAL
	ld [FW_ATTR], a
	FW_OBJ
	ld a, l
	ldh [hOAMBufOfs], a
.noDraw
	ld a, [FW_FACE]
	ld d, a                ; 向き（色を えらぶ）
	ld a, [FW_REQ]
	ld c, a
	xor a
	ld [FW_REQ], a
	ld a, [FW_WANT]
	ld b, a
	ld a, e
	ldh [rSVBK_], a

; 3. 絵を 読む（c = ずかん番号）
	ld a, c
	and a
	jr z, .noLoad
	push bc
	dec a
	ld bc, 0               ; b = 何バンクめ、c = バンクの 中の 番号
	ld c, a
.div
	ld a, c
	cp 40
	jr c, .divDone
	sub 40
	ld c, a
	inc b
	jr .div
.divDone
	push bc
	ld e, c
	ld hl, FwGfxBanks
	ld a, b
	add l
	ld l, a
	jr nc, .gb
	inc h
.gb
	ld b, [hl]
	ld hl, $4000
	call $3500
	pop bc
	push bc
	ld e, c
	ld hl, FwMaskBanks
	ld a, b
	add l
	ld l, a
	jr nc, .mb
	inc h
.mb
	ld b, [hl]
	ld hl, $4000
	call $3500
	pop bc
	pop bc                 ; c = ずかん番号
	ldh a, [rSVBK_]
	ld e, a
	ld a, 7
	ldh [rSVBK_], a
	ld a, c
	ld [FW_DEX], a
	ld a, [FW_FLAGS]
	and $fd
	ld [FW_FLAGS], a
	ld a, e
	ldh [rSVBK_], a
.noLoad

; 4. 色（OBJ パレット 6 を 手持ちの アイコンと 同じ 色に）
	ld a, b
	and a
	ret z
	ld l, a
	ld h, 0
	add hl, hl
	add hl, hl
	ld bc, FwPals          ; 正面（下）：手持ちの アイコンと 同じ 色
	ld a, d
	and a
	jr z, .front
	ld bc, FwWalkPals      ; 後ろ・横：歩行グラフィック 用の 色
.front
	add hl, bc             ; hl = 色1・色2
	ldh a, [rSVBK_]
	ld e, a
	ld a, 2
	ldh [rSVBK_], a
	ld bc, w2ObPal6Src
	ld d, 4
.cmp
	ld a, [bc]
	cp [hl]
	jr nz, .write
	inc bc
	inc hl
	dec d
	jr nz, .cmp
	ld a, [w2ObPal6Src + 4]
	ld d, a
	ld a, [w2ObPal6Src + 5]
	or d
	jr z, .palDone
	dec hl
	dec hl
	dec hl
	dec hl
.write
	ld a, l                ; hl を 色1 に もどす
	and $fc
	ld l, a
	ld a, [hli]
	ld [w2ObPal6Src], a
	ld [w2ObPal6Cur], a
	ld a, [hli]
	ld [w2ObPal6Src + 1], a
	ld [w2ObPal6Cur + 1], a
	ld a, [hli]
	ld [w2ObPal6Src + 2], a
	ld [w2ObPal6Cur + 2], a
	ld a, [hl]
	ld [w2ObPal6Src + 3], a
	ld [w2ObPal6Cur + 3], a
	xor a                  ; 色3 = 黒
	ld [w2ObPal6Src + 4], a
	ld [w2ObPal6Cur + 4], a
	ld [w2ObPal6Src + 5], a
	ld [w2ObPal6Cur + 5], a
	ld a, 1
	ld [w2ObjPalDirty], a
.palDone
	ld a, e
	ldh [rSVBK_], a
	ret

FwGfxBanks:  db $2e, $2f, $30, $31
FwMaskBanks: db $32, $36, $38, $39

; 内部の 番号 → ずかん番号（pokered の PokedexOrder）
FwDexTable:
	INCBIN "follow/dex.bin"

; ずかん番号 × 4：色1・色2（緑の 手持ちの アイコンの 色 = 20:58c8 の 表）
	ds (4 - (@ & 3)) & 3, 0   ; 4 バイトの さかいめに
FwPals:
	INCBIN "follow/pals.bin"
; ずかん番号 × 4：後ろ・横 用の 色1・色2（キットの FollowerWalkPals）
FwWalkPals:
	INCBIN "follow/walkpals.bin"
