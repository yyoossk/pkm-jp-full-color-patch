; 状態異常の 文字に 色・PP の のこりで 色（金 日本版。クリスタル追加機能キットの 55・56 を 金に 合わせた）
;
; ・戦闘の HP の わくの 状態異常（どく むらさき・やけど 赤・こおり 水色・まひ 黄色・ねむり 灰色）と、
;   手持ちの 画面の 状態異常（同じ 色。5種類 ぜんぶ）。
; ・戦闘で わざを えらぶ とき、右下の わくの PP（「15／30」）が のこり 4分の1 いか なら 黄色、0 なら 赤。
; 色の わりあて・しくみは クリスタルと 同じ（src/redballs.asm の RB_STATUSCOLOR・src/movepower.asm の MP_PPCOLOR）。
;
; 金で ちがう 所
;   ・色は WRAM0（wBGPals1 $c200・wBGPals2 $c280）。WRAM の バンクは かえない。
;   ・PlaceNonFaintStatus（$14:$543c）は バンク$14 に 空きが ない ので、頭を「bc ＝ ます で この バンクの
;     SC_PlaceNonFaintStatus を farcall」に して、元の 処理（文字を かく）も こちらで する。
;   ・わざを えらび おわった あと：BattleTurn の call MoveSelectionScreen（$0f:$4419）を、使われて いない
;     SwapBattlerLevels（$0f:$6a25）に 置いた StatusColor_MoveSelect に（ROM0 は 空きが ない）。
;   ・movepower（$45:$6400）からは 同じ バンクの つなぎ StatusColor_PP（$45:$63d0）から farcall する。

INCLUDE "src/charmap_jp.inc"

DEF SC_BANK              EQU $49     ; 使われて いない バンク
DEF SC_ADDR              EQU $4000
DEF SC_wTilemap          EQU $c3a0
DEF SC_wAttrmap          EQU $cccd
DEF SC_wBGPals1          EQU $c200     ; WRAM0（wBGPals2 は ＋$80）
DEF SC_hCGBPalUpdate     EQU $ffe7
DEF SC_wBattleMode       EQU $d108
DEF SC_wBattleMonStatus  EQU $cb10
DEF SC_wEnemyMonStatus   EQU $d0ef
DEF SC_wPartyCount       EQU $d9e8
DEF SC_wPartySpecies     EQU $d9e9
DEF SC_wPartyMon1Status  EQU $da10     ; wPartyMon1 $d9f0 ＋ $20
DEF SC_TMP               EQU $cf9a     ; wStringBuffer2 ＋ 8〜＋11（手持ちの 色を きめる 間 だけ）
DEF SC_PLAYER_CELL       EQU 8 * 20 + 16
DEF SC_ENEMY_CELL        EQU 1 * 20 + 8
DEF SC_PP_CELL           EQU 13 * 20 + 14
DEF SC_VRAM_PLAYER_CELL  EQU $9800 + 8 * 32 + 16
DEF SC_PAL_PLAYER_HP     EQU 3
DEF SC_PAL_PARTY0        EQU 4
DEF SC_PAL_ENEMY         EQU 5
DEF SC_PAL_PLAYER        EQU 6
DEF SC_PAL_PP            EQU 6
DEF SC_PLAYER_TILE       EQU $7c   ; VRAM バンク1 $97c0〜

; HP の わくの 状態異常：PlaceNonFaintStatus（$14:$543c。hl ＝ ます、de ＝ 状態）
SECTION "statuscolor hud hook", ROMX[$543c], BANK[$14]
	push bc
	ld b, h
	ld c, l
	ld a, SC_BANK
	ld hl, SC_PlaceNonFaintStatus
	rst $08                          ; hl・f は そのまま もどる
	pop bc
	ret

; 手持ちの 画面：_CGB_PartyMenu の さいごの「call ApplyAttrmap / ret」（$02:$56ff）
SECTION "statuscolor party hook", ROMX[$56ff], BANK[$02]
	jp StatusColor_PartyStub
SECTION "statuscolor party stub", ROMX[$7bd0], BANK[$02]
StatusColor_PartyStub:
	ld a, SC_BANK
	ld hl, StatusColor_Party
	rst $08
	jp $5acb                         ; ApplyAttrmap

; わざを えらび おわった あと：BattleTurn の call MoveSelectionScreen（$0f:$4419）
SECTION "statuscolor pp hook", ROMX[$4419], BANK[$0f]
	call StatusColor_MoveSelect
SECTION "statuscolor pp stub", ROMX[$6a25], BANK[$0f]   ; 使われて いない SwapBattlerLevels（17バイト）
StatusColor_MoveSelect:
	call $6303                       ; MoveSelectionScreen
	push af
	ld a, SC_BANK
	ld hl, StatusColor_PPReset
	rst $08
	pop af
	ret

; movepower（MovePower_Draw の はじめ。バンク$45）から call される つなぎ（a・de・hl は こわれる。b・c は そのまま）
SECTION "statuscolor pp far", ROMX[$63d0], BANK[$45]
StatusColor_PP::
	ld a, SC_BANK
	ld hl, StatusColor_PPBody
	rst $08
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
	ld a, e
	add a
	add a
	add a
	add 6
.off
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
	ret

; e ＝ 色の 番号、a ＝ 種類 → 色1（d が 0 で ない なら wBGPals2 も）
SC_SetColor1:
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
	ld a, e
	add a
	add a
	add a
	add 2
	jr SC_SetColor3.off

; e ＝ 色の 番号 の 色0〜2 を 白・白・はい色 に（wBGPals1）
SC_SetBase:
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
	ret

SC_Colors:
	dw $0000                         ; なし（黒）
	dw $5892                         ; どく（むらさき）
	dw $089c                         ; やけど（赤）
	dw $7e46                         ; こおり（水色）
	dw $029a                         ; まひ（黄色）
	dw $39ce                         ; ねむり（灰色）

; 文字の 絵を 色1 で かいた もの（色3 → 色1）を VRAM の バンク1 に 作る
;   de ＝ 3文字（SC_Strings）、hl ＝ バンク1 の 置き場所（タイル 3枚）。もとの 文字は バンク0
;   （$80〜 は $8800〜、$00〜$7f は $9000〜。戦闘・手持ちの 画面は LCDC の bit4 ＝ 0）。
SC_MakeGlyphs:
	ld b, 3
.char
	push bc
	push hl
	ld a, [de]
	inc de
	push de
	ld l, a
	ld h, 0
	add hl, hl
	add hl, hl
	add hl, hl
	add hl, hl                       ; × 16
	bit 7, a
	ld de, $9000
	jr z, .low
	ld de, $8000
.low
	add hl, de                       ; もとの 文字
	ld d, h
	ld e, l
	pop bc                           ; bc ＝ つぎの 文字
	pop hl                           ; hl ＝ 置き場所
	push bc
	ld b, 8
.row
	xor a
	ldh [$ff4f], a
	call SC_ReadVRAM                 ; a ＝ [de]（下の 面）
	inc de
	inc de
	ld c, a
	ld a, 1
	ldh [$ff4f], a
	ld a, c
	call SC_WriteVRAM                ; 下の 面 ＝ そのまま
	xor a
	call SC_WriteVRAM                ; 上の 面 ＝ 0（色3 → 色1）
	dec b
	jr nz, .row
	pop de                           ; de ＝ つぎの 文字
	pop bc
	dec b
	jr nz, .char
	xor a
	ldh [$ff4f], a
	ret

SC_ReadVRAM:                         ; a ＝ [de]
	di
.wait
	ldh a, [$ff41]
	and %10
	jr nz, .wait
	ld a, [de]
	ei
	ret

SC_WriteVRAM:                        ; [hl+] ＝ a（a は そのまま）
	push bc
	ld c, a
	di
.wait
	ldh a, [$ff41]
	and %10
	jr nz, .wait
	ld [hl], c
	ei
	inc hl
	ld a, c
	pop bc
	ret

; 自分の 状態異常の ます（16〜18, 8）を「色1 の 文字（バンク1 $7c〜$7e）・6本目」か「もとの 文字・3本目」に
;   a ＝ 0：もとに（HP の わくの 3本目）、0 以外：文字を 作って 6本目＋バンク1
SC_PlayerCells:
	and a
	jr z, .plain
	call SC_String
	ld hl, $9000 + SC_PLAYER_TILE * 16
	call SC_MakeGlyphs
	ld hl, SC_wTilemap + SC_PLAYER_CELL
	ld a, SC_PLAYER_TILE
	ld [hli], a
	inc a
	ld [hli], a
	inc a
	ld [hl], a
	; BG の ますも すぐ かえる（1フレーム ちがう 絵が 出ない ように）
	xor a
	ldh [$ff4f], a
	ld hl, SC_VRAM_PLAYER_CELL
	ld a, SC_PLAYER_TILE
	call SC_WriteVRAM
	inc a
	call SC_WriteVRAM
	inc a
	call SC_WriteVRAM
	ld a, SC_PAL_PLAYER | 8
	jr .attr
.plain
	ld a, SC_PAL_PLAYER_HP
.attr
	ld hl, SC_wAttrmap + SC_PLAYER_CELL
	ld [hli], a
	ld [hli], a
	ld [hl], a
	ld c, a
	ld a, 1
	ldh [$ff4f], a
	ld hl, SC_VRAM_PLAYER_CELL
	ld a, c
	call SC_WriteVRAM
	call SC_WriteVRAM
	call SC_WriteVRAM
	xor a
	ldh [$ff4f], a
	ret

; a ＝ 種類（1〜5）→ de ＝ その 文字（3つ）
SC_String:
	dec a
	ld e, a
	add a
	add e
	ld e, a
	ld d, 0
	ld hl, SC_Strings
	add hl, de
	ld d, h
	ld e, l
	ret
SC_Strings: ; PlaceNonFaintStatus と 同じ 文字
	db $70, $b8, $7f                 ; どく
	db $d4, $b9, $70                 ; やけど
	db $ba, $b5, $d8                 ; こおり
	db $cf, $cb, $7f                 ; まひ
	db $c8, $d1, $d8                 ; ねむり

; 戦闘の 画面の 色を きめた あと（redballs の RedBalls_BattlePals から。wBGPals1 だけ）
StatusColor_BattleLayout::
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
	; 自分の 状態異常：ますが もう 色1 の 文字（$7c）なら 6本目＋バンク1
	ld a, [SC_wTilemap + SC_PLAYER_CELL]
	cp SC_PLAYER_TILE
	ld a, SC_PAL_PLAYER | 8
	jr z, .player
	ld a, SC_PAL_PLAYER_HP
.player
	ld hl, SC_wAttrmap + SC_PLAYER_CELL
	ld [hli], a
	ld [hli], a
	ld [hl], a
	ld e, SC_PAL_PLAYER
	call SC_SetBase
	ld a, [SC_wBattleMonStatus]
	call SC_Kind
	ld de, SC_PAL_PLAYER
	call SC_SetColor1
	ld de, SC_PAL_PLAYER
	xor a
	call SC_SetColor3                ; PP（黒）
	ld a, [SC_wEnemyMonStatus]
	call SC_Kind
	ld de, SC_PAL_ENEMY
	jp SC_SetColor3

; HP の わくを かいた とき：bc ＝ かいた 場所、d ＝ 状態
StatusColor_HUD:
	ld a, [SC_wBattleMode]
	and a
	jr z, .party
	ld hl, SC_wTilemap + SC_PLAYER_CELL
	call .cmp
	jr z, .player
	ld hl, SC_wTilemap + SC_ENEMY_CELL
	call .cmp
	jr nz, .party
	ld a, d
	call SC_Kind
	ld de, $0100 | SC_PAL_ENEMY
	call SC_SetColor3
	jr .update
.player
	ld a, d
	call SC_Kind
	push af
	ld de, $0100 | SC_PAL_PLAYER
	call SC_SetColor1
	pop af
	call SC_PlayerCells
.update
	ld a, 1
	ldh [SC_hCGBPalUpdate], a
	ret
.party
	; 手持ちの 画面：ますの 色が バンク1（StatusColor_Party が まひ・ねむり に した）なら 色1 の 文字に
	ld hl, SC_wAttrmap - SC_wTilemap
	add hl, bc
	bit 3, [hl]
	ret z
	push bc
	ld a, d
	call SC_Kind                     ; b を つかう
	pop bc
	ld e, $72
	cp 4
	jr z, .p_make
	ld e, $75
	cp 5
	ret nz
.p_make
	push bc
	push de
	call SC_String
	pop hl
	push hl
	ld h, 0
	ld a, l
	ld l, a
	add hl, hl
	add hl, hl
	add hl, hl
	add hl, hl
	ld a, h
	add HIGH($9000)
	ld h, a
	call SC_MakeGlyphs
	pop de
	pop hl                           ; hl ＝ ます
	ld a, e
	ld [hli], a
	inc a
	ld [hli], a
	inc a
	ld [hl], a
	ret
.cmp
	ld a, h
	cp b
	ret nz
	ld a, l
	cp c
	ret

; わざの わく（MovePower_Draw の はじめ）：PP「cc／mm」（14〜18, 13）の 色（6本目の 色3）
StatusColor_PPBody:
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

; わざを えらび おわった あと：PP の 色を 黒に
StatusColor_PPReset:
	ld de, $0100 | SC_PAL_PP
	xor a
	call SC_SetColor3
	ld a, 1
	ldh [SC_hCGBPalUpdate], a
	ret

; 手持ちの 画面（_CGB_PartyMenu の おわり。wBGPals1）
;   どく 4本目 色3・やけど 5本目 色3・こおり 6本目 色3（ふつうの 文字）、
;   まひ 4本目 色1・ねむり 5本目 色1（ますの 色に バンク1 の しるしを つけ、状態を かく ときに
;   色1 の 文字を バンク1 $72〜$74・$75〜$77 に 作って ますを その タイルに する）。5種類 ぜんぶ 色が つく。
;   （_CGB_PartyMenu は HP の バーを かく ところで よばれ、状態は その あとに かかれる）
StatusColor_Party:
	ld e, 4
	call SC_SetBase
	ld e, 5
	call SC_SetBase
	ld e, 6
	call SC_SetBase
	ld de, 4
	ld a, 1
	call SC_SetColor3
	ld de, 5
	ld a, 2
	call SC_SetColor3
	ld de, 6
	ld a, 3
	call SC_SetColor3
	ld de, 4
	ld a, 4
	call SC_SetColor1
	ld de, 5
	ld a, 5
	call SC_SetColor1
	; 6ひき ぶんの ますの 色を 0 に（前に バンク1 の しるしが のこらない ように）
	;  （色ちがいの ★ $5e・連れ歩きの ★ $5f の ますは そのまま）
	ld hl, SC_wTilemap + 8
	ld e, 6 * 3
	ld d, 3
.clear
	ld a, [hl]
	cp $5e
	jr z, .keep
	cp $5f
	jr z, .keep
	push hl
	ld bc, SC_wAttrmap - SC_wTilemap
	add hl, bc
	ld [hl], 0
	pop hl
.keep
	inc hl
	dec d
	jr nz, .cnext
	ld bc, 40 - 3
	add hl, bc
	ld d, 3
.cnext
	dec e
	jr nz, .clear
	xor a
	ld [SC_TMP + 3], a               ; 何びきめ
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
	ld [SC_TMP + 2], a
	; ます（8〜10, 2×i）
	ld a, [SC_TMP + 3]
	ld hl, SC_wTilemap + 8
	ld bc, 40
	and a
	jr z, .cell
.row
	add hl, bc
	dec a
	jr nz, .row
.cell
	ld a, [SC_TMP + 2]
	cp 4
	jr nc, .bank1
	; どく・やけど・こおり：3本目〜（4・5・6）の 色3
	add 3
	call .attr
	jr .next
.bank1
	; まひ（4）→ 4本目、ねむり（5）→ 5本目 の 色1（バンク1 の 色1 の 文字。状態を かく 順が どちらでも
	; いい ように、ここでも PlaceNonFaintStatus の あとでも ますを その タイルに する）
	push af
	add 8
	call .attr
	pop af
	ld b, h
	ld c, l
	ld d, 1 << 6                     ; まひ
	cp 4
	jr z, .p
	ld d, 1                          ; ねむり
.p
	call StatusColor_HUD.party
.next
	ld hl, SC_TMP + 3
	inc [hl]
	jp .loop
.attr                                ; hl ＝ wTilemap の ます → wAttrmap の 同じ 所に a（★の ますは そのまま）
	push hl
	push de
	ld d, a
	ld e, 3
.aloop
	ld a, [hl]
	cp $5e
	jr z, .askip
	cp $5f
	jr z, .askip
	push hl
	ld bc, SC_wAttrmap - SC_wTilemap
	add hl, bc
	ld [hl], d
	pop hl
.askip
	inc hl
	dec e
	jr nz, .aloop
	pop de
	pop hl
	ret

; PlaceNonFaintStatus の 元の 処理（文字を かく）＋ 色。bc ＝ ます、de ＝ 状態 → hl ＝ ます ＋ 2、f は 元と 同じ
SC_PlaceNonFaintStatus:
	ld h, b
	ld l, c
	call .orig
	push af
	push hl
	push de
	ld a, [de]
	ld d, a
	call StatusColor_HUD
	pop de
	pop hl
	pop af
	ret
.orig
	ld a, [de]
	bit 3, a
	jr nz, .psn
	bit 4, a
	jr nz, .brn
	bit 5, a
	jr nz, .frz
	bit 6, a
	jr nz, .par
	and 7
	ret z
	ld a, $c8                        ; ねむり
	ld [hli], a
	ld a, $d1
	ld [hli], a
	ld [hl], $d8
	ret
.psn
	ld a, $70                        ; どく
	ld [hli], a
	ld [hl], $b8
	ret
.brn
	ld a, $d4                        ; やけど
	ld [hli], a
	ld a, $b9
	ld [hli], a
	ld [hl], $70
	ret
.frz
	ld a, $ba                        ; こおり
	ld [hli], a
	ld a, $b5
	ld [hli], a
	ld [hl], $d8
	ret
.par
	ld a, $cf                        ; まひ
	ld [hli], a
	ld [hl], $cb
	ret
