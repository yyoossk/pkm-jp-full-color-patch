; 連れ歩き（金）：マップを 読む とき・まいフレーム・ボール・手持ちの 画面（follow_gold.asm から INCLUDE）
; クリスタル（follow_crystal.asm）と 同じ 処理。金は WRAM の バンクを かえない（スタックが WRAMX に ある）

DEF FW_PlaySFX         EQU $3d45
DEF FW_SFX_READ_TEXT_2 EQU $08
DEF FW_WaitBGMap2      EQU $33b8


; 連れ歩くか（carry = 連れ歩かない）
Fw_DesiredNow:
Fw_Desired:
	call Fw_NoCGB
	ret c
	call Fw_Index
	jr c, .no
	ld a, [wPlayerState]
	and a                             ; PLAYER_NORMAL だけ
	jr nz, .no
	call Fw_Species
	cp FW_EGG
	jr z, .yes
	call Fw_HP
	ld a, [hli]
	or [hl]
	jr z, .no
.yes
	and a
	ret
.no
	scf
	ret

; 連れ歩きを 置く 番号（a）。金の マップの 人は 2番から（ReadObjectEvents が wMap2Object から 書く。1番は 使われない）
; ので 人の 数＋2。14人 いれば、かくれて いる 人の 番号を 借りる（後ろから）。なければ carry
Fw_FreeSlot:
	ld a, [wCurMapObjectEventCount]
	add 2
	cp 16
	ccf
	ret nc
	ld a, 15
.loop
	push af
	call FW_GetMapObject
	ld hl, MAPOBJ_EVENT_FLAG
	add hl, bc
	ld a, [hli]
	ld e, a
	ld d, [hl]
	and d
	inc a
	jr z, .next                       ; $ffff（いつも いる）
	ld b, 2                           ; CHECK_FLAG
	call FW_EventFlagAction
	ld a, c
	and a
	jr z, .next
	pop af
	and a
	ret
.next
	pop af
	dec a
	cp 2
	jr nc, .loop
	scf
	ret

; 連れ歩きの マップオブジェクトを さがす（a = 番号、bc = マップオブジェクト。なければ carry）
Fw_FindSlot:
	; ふつうは 人の 数＋2 の 番号（Fw_FreeSlot）なので 先に そこを 見る
	ld a, [wCurMapObjectEventCount]
	add 2
	cp 16
	jr nc, .scan
	push af
	swap a
	ld c, a
	ld b, 0
	ld hl, wMapObjects
	add hl, bc
	ld b, h
	ld c, l
	inc hl                            ; MAPOBJ_SPRITE
	ld a, [hl]
	cp FW_SPRITE
	jr z, .found
	pop af
.scan
	ld bc, wMapObjects + $20
	ld a, 2
.loop
	push af
	ld hl, MAPOBJ_SPRITE
	add hl, bc
	ld a, [hl]
	cp FW_SPRITE
	jr z, .found
	ld hl, $10
	add hl, bc
	ld b, h
	ld c, l
	pop af
	inc a
	cp 16
	jr nz, .loop
	scf
	ret
.found
	pop af
	and a
	ret

; a = マップオブジェクトの 番号、d = X、e = Y：連れ歩きの マップオブジェクトを 書く
Fw_WriteMapObject:
	push de
	push af
	call Fw_GetLead
	jr nc, .pal
	xor a
.pal
	or 8
	swap a
	or FW_TYPE
	ld e, a                           ; e = 色・種類
	pop af
	push de
	call FW_GetMapObject              ; bc
	pop de
	ld a, e
	pop de                            ; d = X、e = Y
	ld h, b
	ld l, c
	ld [hl], $ff                      ; まだ オブジェクトに なって いない
	inc hl
	ld [hl], FW_SPRITE
	inc hl
	ld [hl], e                        ; Y
	inc hl
	ld [hl], d                        ; X
	inc hl
	; 主人公と 同じ 向きで 立つ（つながりで 一瞬 正面を 向かない ように）
	push af
	ld a, [wObjectStructs + OBJ_DIRECTION]
	and %1100
	rrca
	rrca
	add FW_MOVEMENT                   ; STANDING_DOWN・UP・LEFT・RIGHT
	ld [hl], a
	pop af
	inc hl
	ld [hl], 0                        ; 動く はんい
	inc hl
	ld [hl], $ff                      ; いつでも
	inc hl
	ld [hl], $ff
	inc hl
	ld [hli], a                       ; 色・種類
	xor a
	ld [hli], a                       ; 見る きょり
	ld [hli], a                       ; スクリプト
	ld [hli], a
	ld a, $ff
	ld [hli], a                       ; イベントフラグ なし
	ld [hli], a
	xor a
	ld [hli], a
	ld [hl], a
	ret

;---------------------------------------------------------------------
; マップを 読む とき（LoadMapObjects の さいしょ）
Fw_MapLoad:
	ld a, $ff
	ld [wObjectFollow_Leader], a
	ld [wObjectFollow_Follower], a
	; 人の 絵が たりなければ 読みなおす（つながりは 画面を 止めない Fw_RefreshConn）
	call Fw_MapSpritesOK
	jr c, .spritesok
	ldh a, [hMapEntryMethod]
	cp MAPSETUP_CONNECTION
	jr z, .conn
	call Fw_RefreshAll
	jr .spritesok
.conn
	call Fw_RefreshConn
.spritesok
	call Fw_Desired
	ret c
	call Fw_FreeSlot
	ret c
	push af
	ld a, [wPlayerMapX]
	ld d, a
	ld a, [wPlayerMapY]
	ld e, a
	ldh a, [hMapEntryMethod]
	cp MAPSETUP_CONNECTION
	jr nz, .write
	ld a, [wPlayerStepDirection]
	and a
	jr z, .down
	dec a
	jr z, .up
	dec a
	jr z, .left
	dec a
	jr nz, .write
	dec d                             ; 右へ 来た → 左に
	jr .write
.down
	dec e
	jr .write
.up
	inc e
	jr .write
.left
	inc d
.write
	pop af
	jp Fw_WriteMapObject

; 主人公が 歩く ときの ぶつかり：連れ歩きは 見ない
Fw_IsNPCAtCoord:
	fw_farcall $01, FW_IsNPCAtCoord
	ret nc
	push bc
	ld hl, OBJ_MAP_OBJECT_INDEX
	add hl, bc
	ld a, [hl]
	call FW_GetMapObject
	ld hl, MAPOBJ_SPRITE
	add hl, bc
	ld a, [hl]
	pop bc
	cp FW_SPRITE
	scf
	ret nz
	and a
	ret

;---------------------------------------------------------------------
; まいフレーム（HandleMapObjects の あと。mapsign.asm の MapSign_Frame から）
Fw_Update::
	ld a, [wPartyCount]
	and a
	ret z
	call Fw_NoCGB
	ret c
	call Fw_FastQueue
	call Fw_BallTick
	ret c                             ; ボールの アニメ中
	; 主人公が 歩いて いる 途中で、連れ歩きが follow して 見えて いる 間は ほかに する ことが ない（60fps版で
	; まいフレーム ぜんぶ 調べて いると 1歩ごとに 1フレーム おくれて いた）
	ld a, [wObjectStructs + OBJ_DIR_WALKING]
	inc a
	jr z, .full
	ld a, [wObjectFollow_Leader]
	and a
	jr nz, .full
	ld a, [wObjectFollow_Follower]
	cp $ff
	jr z, .full
	call FW_GetObjectStruct
	ld a, [bc]
	cp FW_SPRITE
	jr nz, .full
	ld hl, OBJ_FLAGS1
	add hl, bc
	bit 0, [hl]                       ; INVISIBLE_F
	ret z
.full
	call Fw_FindSlot
	jp c, Fw_SpawnHere
	ld d, a                           ; d = 番号
	push de
	push bc
	call Fw_DesiredNow
	pop bc
	pop de
	jr nc, .want
	; 連れ歩かない：出て いれば ボールに もどす
	ld a, [bc]
	cp $ff
	ret z
	ld a, 1                           ; もどる
	jp Fw_BallStart
.want
	; 主人公と 同じ 場所に いる 間（ドアから 出た すぐあと など）は 見えなく する
	ld a, [bc]
	cp $ff
	jp z, .noshow
	push de
	call FW_GetObjectStruct
	pop de
	ld hl, OBJ_MAP_X
	add hl, bc
	ld a, [wPlayerMapX]
	cp [hl]
	jr nz, .show
	inc hl
	ld a, [wPlayerMapY]
	cp [hl]
	jr nz, .show
	ld hl, OBJ_FLAGS1
	add hl, bc
	set 0, [hl]                       ; INVISIBLE_F
	ld hl, OBJ_FACING
	add hl, bc
	ld [hl], $ff                      ; STANDING
	jr .noshow
.show
	ld hl, OBJ_FLAGS1
	add hl, bc
	res 0, [hl]
	ld a, [wFwBall]
	cp 3
	jr nz, .noshow
	ld a, 2                           ; ボールから 出る
	jp Fw_BallStart
.noshow
	ld a, [wScriptMode]
	and a
	ret nz                            ; スクリプトの 間は さわらない
	; 先頭が かわったか は 主人公が 止まって いる ときだけ 見る
	ld a, [wObjectStructs + OBJ_DIR_WALKING]
	inc a
	jr nz, .noreload
	push de
	call Fw_CheckReload
	pop de
.noreload
	ld a, d
	call FW_GetMapObject
	ld a, [bc]
	cp $ff
	jr z, .place
	; 出て いる：follow して いるか
	ld e, a                           ; e = オブジェクトの 番号
	ld hl, wObjectFollow_Follower
	cp [hl]
	jr nz, .resync
	ld a, [wObjectFollow_Leader]
	and a
	jr nz, .resync
	; follow して いる：止まって いるのに 2マス 以上 はなれて いれば 主人公の 後ろに おきなおす
	push de
	ld a, e
	call FW_GetObjectStruct
	pop de
	ld hl, OBJ_DIR_WALKING
	add hl, bc
	ld a, [hl]
	inc a
	ret nz                            ; 歩いて いる 途中
	call Fw_Dist
	cp 2
	ret c
	jr .far
.resync
	ld a, [wObjectStructs + OBJ_DIR_WALKING]
	inc a
	ret nz                            ; 主人公が 歩いて いる 途中は まつ
	push de
	ld a, e
	call FW_GetObjectStruct
	pop de
	call Fw_Dist
	cp 2
	jr c, .start
.far
	ld a, [wObjectStructs + OBJ_DIR_WALKING]
	inc a
	ret nz
	ld a, d
	push de
	call FW_DeleteObjectStruct
	pop de
	; 主人公の 後ろ（歩いた 向きの 反対）に おきなおす
	ld a, [wPlayerMapX]
	ld l, a
	ld a, [wPlayerMapY]
	ld h, a
	ld a, [wPlayerStepDirection]
	and a
	jr nz, .bup
	dec h                             ; 下へ 歩いた → 上に
	jr .bput
.bup
	dec a
	jr nz, .bleft
	inc h
	jr .bput
.bleft
	dec a
	jr nz, .bright
	inc l
	jr .bput
.bright
	dec l
.bput
	push hl
	ld a, d
	call FW_GetMapObject
	pop hl
	push hl
	ld hl, MAPOBJ_Y
	add hl, bc
	pop bc                            ; b = Y、c = X
	ld [hl], b
	inc hl
	ld [hl], c
	jr .unmask
.place
	ld a, [wObjectStructs + OBJ_DIR_WALKING]
	inc a
	ret nz
	; 主人公の 場所に おいて 出す
	ld a, d
	call FW_GetMapObject
	ld hl, MAPOBJ_Y
	add hl, bc
	ld a, [wPlayerMapY]
	ld [hli], a
	ld a, [wPlayerMapX]
	ld [hl], a
.unmask
	ld a, d
	push de
	call FW_Unmask
	pop de
	; ボールに もどって いた あとなら、ボールの 絵で まって、主人公が 1歩 はなれて 見える ように なった ときに ボールから 出る
	ld a, [wFwHidden]
	and a
	jr z, .start
	xor a
	ld [wFwHidden], a
	ld a, 3
	ld [wFwBall], a
.start
	ld b, 0                           ; 主人公
	ld c, d
	fw_farcall $01, FW_StartFollow
	ret

;---------------------------------------------------------------------
; ボールの アニメ（Crystal Crunch の StepFunction_PokeballClosing・Opening）
; a = 1 もどる・2 出る、d = マップオブジェクトの 番号
Fw_BallStart:
	ld [wFwBall], a
	ld e, a
	ld a, 12
	ld [wFwBallT], a
	ld a, e
	dec a
	jr nz, Fw_BallFrame
	ld a, 1
	ld [wFwHidden], a                 ; 次に 出る ときは ボールから
	jr Fw_BallFrame

; まいフレーム：アニメ中なら carry
Fw_BallTick:
	ld a, [wFwBall]
	and a
	ret z
	call Fw_FindSlot
	jr c, .end                        ; マップが かわった など
	ld d, a
	ld a, [bc]
	cp $ff
	jr z, .end
	push de
	call Fw_CheckReload               ; ボールの 絵と 色（Fw_GetLead が ボールを かえす）
	pop de
	ld a, [wFwBall]
	cp 3
	jr z, .wait3
	ld a, [wFwLoaded]                 ; ボールの 絵が 読みこまれるまで まつ
	cp LOW(278)
	jr nz, .loading
	ld a, [wFwLoaded + 1]
	cp HIGH(278)
	jr nz, .loading
	ld hl, wFwBallT
	dec [hl]
	jr z, .done
	call Fw_BallFrame
	scf
	ret
.done
	ld a, [wFwBall]
	ld e, a
	xor a
	ld [wFwBall], a
	push de
	call Fw_BallSetRange0
	pop de
	ld a, e
	dec a
	jr nz, .shown
	ld a, d                           ; もどった：けす
	call FW_DeleteObjectStruct
	scf
	ret
.shown
	scf                               ; 出た：次の フレームで ポケモンの 絵に もどる
	ret
.loading
	scf
	ret
.wait3
	call Fw_BallFrame                 ; とじた ボール（見えない 間 まつ）
	and a
	ret
.end
	xor a
	ld [wFwBall], a
	ret

; d = マップオブジェクトの 番号：いまの コマを OBJECT_RANGE に
Fw_BallFrame:
	ld a, [wFwBallT]
	ld c, a
	ld a, [wFwBall]
	ld b, a
	; 段（12〜9 → 0、8〜5 → 1、4〜1 → 2）
	ld a, c
	dec a
	srl a
	srl a                             ; 2,1,0
	ld c, a
	ld a, 2
	sub c                             ; 0,1,2（はじめ → おわり）
	ld c, a
	ld a, b
	cp 3
	ld a, 1
	jr z, .put                        ; まって いる：とじた
	ld a, b
	dec a
	jr z, .closing
	; 出る：とじた(1)・半分(2)・開いた(3)
	ld a, c
	inc a
	jr .put
.closing
	; もどる：開いた(3)・半分(2)・とじた(1)
	ld a, 3
	sub c
.put
	ld e, a
	push de
	ld a, d
	call FW_GetMapObject
	ld a, [bc]
	pop de
	cp $ff
	ret z
	call FW_GetObjectStruct
	ld hl, OBJ_RANGE
	add hl, bc
	ld [hl], e
	ret
Fw_BallSetRange0:
	ld a, d
	call FW_GetMapObject
	ld a, [bc]
	cp $ff
	ret z
	call FW_GetObjectStruct
	ld hl, OBJ_RANGE
	add hl, bc
	ld [hl], 0
	ret

; Bダッシュ中は、連れ歩きの 歩く 予定の ふつうの 歩き（step $0c〜$0f）を はやい 歩き（big_step $10〜$13）に する。
; スクリプトの 間（wScriptMode ≠ 0）と、人が 先頭の follow（wObjectFollow_Leader ≠ 0。イベントで 主人公が 人に ついて いく）
; では なにも しない（wFollowMovementQueue は イベントの follow でも 使う。かえると 主人公の 歩きが 先頭と ずれる。
; クリスタルの キキョウシティの せんせいの バグと 同じ しくみ）
Fw_FastQueue:
	ld a, [wScriptMode]
	and a
	ret nz
	ld a, [wObjectFollow_Leader]
	and a
	ret nz
	ldh a, [hJoyDown]
	and FW_B_BUTTON
	ret z
	ldh a, [hJoyDown]
	and FW_D_PAD
	ret z
	ld hl, wFollowMovementQueue
	ld c, 5
.loop
	ld a, [hl]
	cp $0c
	jr c, .next
	cp $10
	jr nc, .next
	add 4
	ld [hl], a
.next
	inc hl
	dec c
	jr nz, .loop
	ret

; bc = オブジェクト → a = 主人公との きょり（|dx|＋|dy|）
Fw_Dist:
	ld hl, OBJ_MAP_X
	add hl, bc
	ld a, [wPlayerMapX]
	sub [hl]
	jr nc, .dx
	cpl
	inc a
.dx
	ld b, a
	inc hl
	ld a, [wPlayerMapY]
	sub [hl]
	jr nc, .dy
	cpl
	inc a
.dy
	add b
	ret

;---------------------------------------------------------------------
; 連れ歩く ポケモンを えらぶ（手持ちの 画面の SELECT）
Fw_PartySelect:
	ld a, [wPartyCount]
	ld b, a
	ld a, [FW_wMenuCursorY]
	dec a
	cp b
	ret nc                            ; 「やめる」
	ld b, a
	call Fw_Index
	jr c, .set
	cp b
	jr nz, .set
	ld a, $ff                         ; もう えらんで いる → だれも 連れ歩かない
	jr .store
.set
	ld a, b
	inc a
.store
	ld [wFwSlot], a
	ld de, FW_SFX_READ_TEXT_2
	call FW_PlaySFX
	call Fw_PartyMark
	jp FW_WaitBGMap2

; 手持ちの 画面に 赤い ★（えらんだ ポケモンの HP の 数字の 右 hlcoord 19, 0 ＋ 2行 × 番号）。
;   状態異常の 文字（hlcoord 8〜10, 0）・色ちがいの ★（11, 0）と かさならない 所に おく
;   （9, 0 だと「ねむり」の「む」が ★の ますに なって こわれた）。手持ちの 画面を 開いた ときの 色は statuscolor_gold.asm の .marks
;   赤は HP の 赤の パレット（BG 3）の 色2 で かく。★の 絵は タイル $5f に 書く（$5e は 色ちがいの ★）
DEF FW_MARK_TILE2      EQU $5f
DEF FW_MARK_PAL2       EQU 3
Fw_PartyMark::
	call Fw_NoCGB
	ret c
	; ★の 絵（色2）
	ld de, FwStarGFX
	ld hl, $9000 + FW_MARK_TILE2 * 16
	ld c, 16
.copy
	di
.wait
	ldh a, [$ff41]
	and 2
	jr nz, .wait
	ld a, [de]
	ld [hli], a
	ei
	inc de
	dec c
	jr nz, .copy
	call Fw_Index
	ld c, a
	jr nc, .chosen
	ld c, $ff
.chosen
	ld hl, $c3a0 + 19                 ; hlcoord 19, 0
	ld de, $cccd + 19
	ld b, 0
.slot
	ld a, [wPartyCount]
	cp b
	jr z, .clear
	jr c, .clear
	ld a, b
	cp c
	jr nz, .clear
	ld [hl], FW_MARK_TILE2
	ld a, [de]
	and %11111000
	or FW_MARK_PAL2
	ld [de], a
	jr .next
.clear
	ld a, [hl]
	cp FW_MARK_TILE2
	jr nz, .next
	ld [hl], $7f
.next
	push bc
	ld bc, 40
	add hl, bc
	push hl
	ld h, d
	ld l, e
	add hl, bc
	ld d, h
	ld e, l
	pop hl
	pop bc
	inc b
	ld a, b
	cp 6
	jr c, .slot
	ret

FwStarGFX:  ; ★（色2 だけ）
	db $00, $10, $00, $10, $00, $38, $00, $fe, $00, $7c, $00, $38, $00, $6c, $00, $44

;---------------------------------------------------------------------
; マップに 連れ歩きが いない（はじめての ポケモンを もらった とき など）：空いた 番号に 作る
Fw_SpawnHere:
	call Fw_DesiredNow
	ret c
	ld a, [wScriptMode]
	and a
	ret nz
	call Fw_FreeSlot
	ret c
	push af
	; 絵が まだ 読みこまれて いなければ スプライトを ぜんぶ 読みなおす
	ld hl, wUsedSprites
	ld c, 12
.find
	ld a, [hli]
	cp FW_SPRITE
	jr z, .loaded
	inc hl
	dec c
	jr nz, .find
	call Fw_RefreshAll
.loaded
	ld a, [wPlayerMapX]
	ld d, a
	ld a, [wPlayerMapY]
	ld e, a
	pop af
	push af
	call Fw_WriteMapObject
	pop af
	push af
	call FW_Unmask
	pop af
	ld c, a
	ld b, 0
	fw_farcall $01, FW_StartFollow
	ret

; つながりで 人の オブジェクトが できた あと（LoadMapObjects の さいご）：その 場で 主人公を follow する
Fw_AfterObjects:
	ldh a, [hMapEntryMethod]
	cp MAPSETUP_CONNECTION
	ret nz
	ld a, [wPartyCount]
	and a
	ret z
	call Fw_FindSlot
	ret c
	ld d, a
	call FW_GetMapObject
	ld a, [bc]
	cp $ff
	ret z                             ; オブジェクトに なって いない
	push af
	ld b, 0
	ld c, d
	fw_farcall $01, FW_StartFollow
	pop af
	; 絵の コマも すぐ 決める（マップを 読む 間の 何フレームか、まだ 動きが まわらず OBJECT_FACING が STANDING（$ff）の
	; まま で、東へ つながりを こえた とき 連れ歩きが きえて いた）
	call FW_GetObjectStruct
	xor a
	call Fw_Facing
	; OAM も 作りなおす（つながりの 前半で 人の オブジェクトを けした あとに スプライトが 並べられ、連れ歩きが きえた まま
	; マップを 読む 何フレームかが 出て いた）
	jp FW_UpdateSprites2

; 連れ歩きの INVISIBLE を 立てる・もどす（もどすのは 主人公と かさなって いない とき）
Fw_SetInvis:
	call Fw_FindSlot
	ret c
	ld a, [bc]
	cp $ff
	ret z
	call FW_GetObjectStruct
	ld hl, OBJ_FLAGS1
	add hl, bc
	set 0, [hl]
	ret
Fw_ClearInvis:
	call Fw_FindSlot
	ret c
	ld a, [bc]
	cp $ff
	ret z
	call FW_GetObjectStruct
	push bc
	call Fw_Dist
	pop bc
	and a
	ret z
	ld hl, OBJ_FLAGS1
	add hl, bc
	res 0, [hl]
	ret

; 先頭が かわって いたら 絵と 色を 読みなおす
Fw_CheckReload:
	call Fw_GetLead
	ret c
	ld c, a
	ld a, [wFwLoaded]
	xor e
	ld b, a
	ld a, [wFwLoaded + 1]
	xor d
	or b
	ld b, a
	ld a, [wFwLoadedPal]
	xor c
	or b
	ret z                             ; 同じ
	; 読みこむ 間は 見えなく する
	call Fw_SetInvis
	call FW_UpdateSprites2
	call .load
	jp Fw_ClearInvis
.load
	; 絵：wUsedSprites の $e2 の 組に 読みこむ（画面を 止めずに）
	ld c, 0
.find
	call Fw_EntryAddr
	ld a, [hl]
	cp FW_SPRITE
	jr z, .found
	inc c
	ld a, c
	cp 10
	jr c, .find
	call Fw_RefreshAll
	jr .pal
.found
	call Fw_LoadEntry
	call Fw_ReloadMask
.pal
	; 色
	call Fw_OwnPalNow                 ; 固有の 色（7本目）
	call Fw_FindSlot
	ret c
	push bc
	call Fw_GetLead                   ; a = 色
	pop bc
	push af
	and 7
	ld e, a
	pop af
	or 8
	swap a
	or FW_TYPE
	ld hl, MAPOBJ_COLOR_TYPE
	add hl, bc
	ld [hl], a
	ld a, [bc]                        ; オブジェクトの 番号
	cp $ff
	ret z
	call FW_GetObjectStruct
	ld hl, OBJ_PALETTE
	add hl, bc
	ld a, [hl]
	and %11111000
	or e
	ld [hl], a
	ret
