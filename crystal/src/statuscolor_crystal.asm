; 状態異常の 文字に 色・PP の のこりで 色（クリスタル 日本版。ピカチュウ版フルカラーと 同じ 考え）
;
; ・戦闘の HP の わくの 状態異常（どく むらさき・やけど 赤・こおり 水色・まひ 黄色・ねむり 灰色）と、
;   手持ちの 画面の 状態異常（同じ 色。手持ちの 画面で 色が つくのは 3種類まで ＝ あいて いる 色が 3本）。
; ・戦闘で わざを えらぶ とき、右下の わくの PP（「15／30」）が のこり 4分の1 いか なら 黄色、0 なら 赤。
;
; 色の わりあて（戦闘。BG の 色は 8本 しか なく、7本は つかって いる）
;   ・5本目（つかまえた 印。src/redballs.asm）：印の 黒（色3）を 色1 に うつし、色3 を 相手の 状態異常の 色に。
;     相手の 状態異常の ます（8〜10, 1）を 5本目に。
;   ・6本目（あいて いる）：色3 を 自分の 状態異常の 色に。自分の 状態異常の ます（16〜18, 8）を 6本目に。
;   ・わざを えらぶ 間は 6本目の 色3 を PP の 色に し、自分の 状態異常の ますを 3本目（HP の わく ＝ 黒）に する
;     （えらぶ 間 だけ 状態異常は 黒）。VRAM の 色の ます（バンク1）も STAT を 見て かく。
;     わざを えらび おわったら（MoveSelectionScreen の あと）もとに もどす。
;     （けいけんちの バーの 4本目は 色3 を バーの 下の 線が つかうので つかえない）
;   状態異常が ない とき・PP が 多い ときは 色3 ＝ 黒（レベルの 数字など ほかの 文字と 同じ）。
;   ・ますの 色（attr）は 戦闘の 画面の 色を きめる 所（_CGB_FinishBattleScreenLayout の おわり ＝ redballs の
;     RedBalls_BattlePals）で いつも その 色に する（PP の ます 14〜18, 13 も 6本目）。
;     色3 は HP の わくを かく とき（PlaceNonFaintStatus）・わざの わくを かく とき（MovePower_Draw の はじめ）に かきかえる。
; 手持ちの 画面：_CGB_PartyMenu の おわり（ApplyAttrmap の 前）で、状態異常の ます（8〜10, 2×i）を
;   4〜6本目に し、出て くる 順に 色を わりあてる（4種類め からは 黒の まま）。

INCLUDE "src/charmap_jp.inc"

DEF SC_BANK              EQU $76
DEF SC_ADDR              EQU $7800
DEF SC_wTilemap          EQU $c4a0
DEF SC_wAttrmap          EQU $cdcd
DEF SC_wBGPals1          EQU $d000     ; WRAM バンク5
DEF SC_hCGBPalUpdate     EQU $ffe5
DEF SC_wBattleMode       EQU $d25e
DEF SC_wBattleMonStatus  EQU $c630
DEF SC_wEnemyMonStatus   EQU $d245
DEF SC_wPartyCount       EQU $dc9d
DEF SC_wPartySpecies     EQU $dc9e
DEF SC_wPartyMon1Status  EQU $dcc5     ; wPartyMon1 $dca5 ＋ $20
DEF SC_TMP               EQU $d06e     ; wStringBuffer2 ＋ 8〜＋11（手持ちの 色を きめる 間 だけ）
DEF SC_PLAYER_CELL       EQU 8 * 20 + 16
DEF SC_ENEMY_CELL        EQU 1 * 20 + 8
DEF SC_PP_CELL           EQU 13 * 20 + 14
DEF SC_VRAM_PLAYER_CELL  EQU $9800 + 8 * 32 + 16
DEF SC_PAL_PLAYER_HP     EQU 3
DEF SC_PAL_PARTY0        EQU 4
DEF SC_PAL_ENEMY         EQU 5
DEF SC_PAL_PLAYER        EQU 6
DEF SC_PAL_PP            EQU 6

; HP の わくの 状態異常：PlaceNonFaintStatus（$14:$4dca「ld a, [de] / bit 3, a」）を つぎへ
SECTION "statuscolor hud hook", ROMX[$4dca], BANK[$14]
	jp StatusColor_HUDStub
SECTION "statuscolor hud stub", ROMX[$7c00], BANK[$14]
StatusColor_HUDStub:
	push bc
	ld b, h
	ld c, l
	call .orig
	push af
	push hl
	push de
	ld a, [de]
	ld d, a
	ld a, SC_BANK
	ld hl, StatusColor_HUD
	rst $08
	pop de
	pop hl
	pop af
	pop bc
	ret
.orig
	ld a, [de]
	bit 3, a
	jp $4dcd

; 手持ちの 画面：_CGB_PartyMenu の さいごの「call ApplyAttrmap / ret」（$02:$519d）
SECTION "statuscolor party hook", ROMX[$519d], BANK[$02]
	jp StatusColor_PartyStub
SECTION "statuscolor party stub", ROMX[$7c00], BANK[$02]
StatusColor_PartyStub:
	ld a, SC_BANK
	ld hl, StatusColor_Party
	rst $08
	jp $5670                         ; ApplyAttrmap

; わざを えらび おわった あと：BattleMenu_Fight の call MoveSelectionScreen（$0f:$4461）
SECTION "statuscolor pp hook", ROMX[$4461], BANK[$0f]
	call StatusColor_MoveSelect
SECTION "statuscolor pp stub 1", ROM0[$3ff6]
StatusColor_MoveSelect:
	call $64c0                       ; MoveSelectionScreen（バンク$0f）
	push af
	jp StatusColor_MoveSelect2
SECTION "statuscolor pp stub 2", ROM0[$00e6]
StatusColor_MoveSelect2:
	ld a, SC_BANK
	ld hl, StatusColor_PPReset
	rst $08
	pop af
	ret

SECTION "statuscolor", ROMX[SC_ADDR], BANK[SC_BANK]
; a ＝ 状態 → a ＝ 0 なし・1 どく・2 やけど・3 こおり・4 まひ・5 ねむり（b を つかう）
SC_Kind:
	ld b, a
	ld a, 1
	bit 3, b
	ret nz
	ld a, 2
	bit 4, b
	ret nz
	ld a, 3
	bit 5, b
	ret nz
	ld a, 4
	bit 6, b
	ret nz
	ld a, b
	and 7
	ret z
	ld a, 5
	ret

; e ＝ 色の 番号、a ＝ 種類 → wBGPals1（d が 0 で ない なら wBGPals2 も）の 色3
SC_SetColor3:
	push de
	add a
	ld c, a
	ld b, 0
	ld hl, SC_Colors
	add hl, bc
	ld a, [hli]
	ld c, a
	ld b, [hl]
	pop de
	ldh a, [$ff70]
	push af
	ld a, 5
	ldh [$ff70], a
	ld a, e
	add a
	add a
	add a
	add 6
	ld l, a
	ld h, HIGH(SC_wBGPals1)
	ld [hl], c
	inc hl
	ld [hl], b
	ld a, d
	and a
	jr z, .done
	ld a, l
	add $80 - 1
	ld l, a
	ld [hl], c
	inc hl
	ld [hl], b
.done
	pop af
	ldh [$ff70], a
	ret

; e ＝ 色の 番号 の 色0〜2 を 白・白・はい色 に（wBGPals1）
SC_SetBase:
	ldh a, [$ff70]
	push af
	ld a, 5
	ldh [$ff70], a
	ld a, e
	add a
	add a
	add a
	ld l, a
	ld h, HIGH(SC_wBGPals1)
	ld a, $ff
	ld [hli], a
	ld a, $7f
	ld [hli], a
	ld a, $ff
	ld [hli], a
	ld a, $7f
	ld [hli], a
	ld a, $ce
	ld [hli], a
	ld a, $39
	ld [hl], a
	pop af
	ldh [$ff70], a
	ret

SC_Colors:
	dw $0000                         ; なし（黒）
	dw $5892                         ; どく（むらさき）
	dw $089c                         ; やけど（赤）
	dw $7e46                         ; こおり（水色）
	dw $029a                         ; まひ（黄色）
	dw $39ce                         ; ねむり（灰色）

; 戦闘の 画面の 色を きめた あと（redballs の RedBalls_BattlePals から。wBGPals1 だけ）
StatusColor_BattleLayout::
	ld hl, SC_wAttrmap + SC_PLAYER_CELL
	ld a, SC_PAL_PLAYER
	ld [hli], a
	ld [hli], a
	ld [hl], a
	ld hl, SC_wAttrmap + SC_ENEMY_CELL
	ld a, SC_PAL_ENEMY
	ld [hli], a
	ld [hli], a
	ld [hl], a
	ld hl, SC_wAttrmap + SC_PP_CELL
	ld a, SC_PAL_PP
	ld [hli], a
	ld [hli], a
	ld [hli], a
	ld [hli], a
	ld [hl], a
	ld e, SC_PAL_PLAYER
	call SC_SetBase
	ld a, [SC_wBattleMonStatus]
	call SC_Kind
	ld de, SC_PAL_PLAYER
	call SC_SetColor3
	ld a, [SC_wEnemyMonStatus]
	call SC_Kind
	ld de, SC_PAL_ENEMY
	jp SC_SetColor3

; HP の わくを かいた とき：bc ＝ かいた 場所、d ＝ 状態
StatusColor_HUD:
	ld a, [SC_wBattleMode]
	and a
	ret z
	ld hl, SC_wTilemap + SC_PLAYER_CELL
	call .cmp
	ld e, SC_PAL_PLAYER
	jr z, .set
	ld hl, SC_wTilemap + SC_ENEMY_CELL
	call .cmp
	ld e, SC_PAL_ENEMY
	ret nz
.set
	ld a, d
	push de
	call SC_Kind
	pop de
	ld d, 1
	call SC_SetColor3
	ld a, 1
	ldh [SC_hCGBPalUpdate], a
	ret
.cmp
	ld a, h
	cp b
	ret nz
	ld a, l
	cp c
	ret

; わざの わく（MovePower_Draw の はじめ）：PP「cc／mm」（14〜18, 13）の 色
StatusColor_PP::
	push bc
	ld hl, SC_wTilemap + SC_PP_CELL
	call .num2
	ld c, a                          ; のこり
	ld hl, SC_wTilemap + SC_PP_CELL + 3
	call .num2
	ld b, a                          ; さいだい
	ld a, c
	and a
	ld a, 2                          ; 0 → 赤（やけどと 同じ 色）
	jr z, .set
	ld a, c
	add a
	jr c, .normal
	add a
	jr c, .normal
	cp b                             ; のこり × 4 ≦ さいだい → 黄色（まひと 同じ 色）
	jr z, .yellow
	jr c, .yellow
.normal
	xor a
	jr .set
.yellow
	ld a, 4
.set
	ld de, $0100 | SC_PAL_PP
	call SC_SetColor3
	ld a, 1
	ldh [SC_hCGBPalUpdate], a
	ld a, SC_PAL_PLAYER_HP           ; 自分の 状態異常の ますは えらぶ 間 黒
	call SC_PlayerCellAttr
	pop bc
	ret
.num2                                ; hl の 2ます（$7f ＝ 0、$f6〜$ff ＝ 0〜9）→ a
	ld a, [hli]
	call .digit
	ld e, a
	add a
	add a
	add e
	add a                            ; ×10
	ld e, a
	ld a, [hl]
	call .digit
	add e
	ret
.digit
	sub $f6
	ret nc
	xor a
	ret

; わざを えらび おわった あと：自分の 状態異常の ますと 色を もどす
StatusColor_PPReset:
	ld a, SC_PAL_PLAYER
	call SC_PlayerCellAttr
	ld a, [SC_wBattleMonStatus]
	call SC_Kind
	ld de, $0100 | SC_PAL_PLAYER
	call SC_SetColor3
	ld a, 1
	ldh [SC_hCGBPalUpdate], a
	ret

; 自分の 状態異常の ます（16〜18, 8）の 色を a 本目に（wAttrmap と VRAM の バンク1）
SC_PlayerCellAttr:
	ld hl, SC_wAttrmap + SC_PLAYER_CELL
	ld [hli], a
	ld [hli], a
	ld [hl], a
	ld c, a
	ldh a, [$ff4f]
	push af
	ld a, 1
	ldh [$ff4f], a
	ld hl, SC_VRAM_PLAYER_CELL
	ld b, 3
.loop
	di
.wait
	ldh a, [$ff41]
	and %10
	jr nz, .wait
	ld [hl], c
	ei
	inc hl
	dec b
	jr nz, .loop
	pop af
	ldh [$ff4f], a
	ret

; 手持ちの 画面（_CGB_PartyMenu の おわり。wBGPals1）
StatusColor_Party:
	ld hl, SC_TMP
	xor a
	ld [hli], a
	ld [hli], a
	ld [hli], a
	ld [hl], a                       ; SC_TMP＋3 ＝ 何びきめ
.loop
	ld a, [SC_wPartyCount]
	ld b, a
	ld a, [SC_TMP + 3]
	cp b
	ret nc
	ld e, a
	ld d, 0
	ld hl, SC_wPartySpecies
	add hl, de
	ld a, [hl]
	cp $fd                           ; タマゴ
	jr z, .next
	ld hl, SC_wPartyMon1Status
	ld a, e
	and a
	jr z, .got
	ld bc, 48
.mul
	add hl, bc
	dec a
	jr nz, .mul
.got
	ld a, [hl]
	call SC_Kind
	and a
	jr z, .next
	ld b, a
	ld hl, SC_TMP
	ld e, SC_PAL_PARTY0              ; 4〜6本目
.find
	ld a, [hl]
	cp b
	jr z, .found
	and a
	jr z, .assign
	inc hl
	inc e
	ld a, e
	cp 7
	jr nz, .find
	jr .next                         ; 4種類め からは 色なし
.assign
	ld [hl], b
	push bc
	push de
	call SC_SetBase
	pop de
	push de
	ld a, b
	ld d, 0
	call SC_SetColor3
	pop de
	pop bc
.found
	; ます（8〜10, 2×i）を e 本目に
	ld a, [SC_TMP + 3]
	ld hl, SC_wAttrmap + 8
	ld bc, 40
	and a
	jr z, .attr
.row
	add hl, bc
	dec a
	jr nz, .row
.attr
	ld a, e
	ld [hli], a
	ld [hli], a
	ld [hl], a
.next
	ld hl, SC_TMP + 3
	inc [hl]
	jr .loop
