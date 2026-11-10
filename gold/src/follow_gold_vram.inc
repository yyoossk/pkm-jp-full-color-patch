; 連れ歩き（金）：人の 絵の 並び（wUsedSprites）・VRAM・白い 下じき（follow_gold.asm から INCLUDE）


; a ＝ スプライト → de・b・c（GetSprite と 同じ。c ＝ タイルの 数）。hl は こわさない
Fw_GetSpriteGfx:
	ld [wFwRet], a
	push hl
	fw_farcall $05, F5_GetSpriteW
	pop hl
	ret
; a ＝ スプライト → e ＝ タイルの 数（0 なら 0）。bc・hl は こわさない
Fw_SpriteLen:
	and a
	jr z, .zero
	cp FW_SPRITE
	jr z, .fw
	push bc
	call Fw_GetSpriteGfx
	ld e, c
	pop bc
	ret
.fw
	ld e, 12
	ret
.zero
	ld e, 0
	ret
; a ＝ スプライト：止まりの 絵（STILL_SPRITE。歩きの 絵が ない）なら carry
Fw_IsStill:
	cp $80                            ; SPRITE_POKEMON から 上は 歩きの 絵も 写す
	jr nc, .walk
	and a
	ret z
	push hl
	push de
	dec a
	ld l, a
	ld h, 0
	ld e, l
	ld d, h
	add hl, hl
	add hl, de
	add hl, hl                        ; × 6
	ld de, FW_OverworldSprites + 4    ; 種類
	add hl, de
	ld a, $05
	call FW_GetFarByte2
	pop de
	pop hl
	cp 3                              ; STILL_SPRITE
	jr z, .still
.walk
	and a
	ret
.still
	scf
	ret

; hl ＝ wUsedSprites の c 番め
Fw_EntryAddr:
	ld a, c
	add a
	add LOW(wUsedSprites)
	ld l, a
	ld a, 0
	adc HIGH(wUsedSprites)
	ld h, a
	ret

; c 番めの 組を けして、後ろ（〜9）を 1つ ずつ 前へ（10・11 の 止まりの 絵は さわらない）
Fw_RemoveEntry:
	call Fw_EntryAddr
	ld d, h
	ld e, l
	inc hl
	inc hl
.loop
	ld a, c
	cp 9
	jr nc, .last
	ld a, [hli]
	ld [de], a
	inc de
	ld a, [hli]
	ld [de], a
	inc de
	inc c
	jr .loop
.last
	xor a
	ld [de], a
	inc de
	ld [de], a
	ret

; c 番めの 組を b 番めへ（b ≦ c。b〜c-1 は 1つ ずつ 後ろへ）
Fw_MoveEntry:
	ld a, c
	cp b
	ret z
	call Fw_EntryAddr                 ; hl = c 番め
	ld a, [hli]
	ld d, a
	ld a, [hld]
	ld e, a                           ; de = うごかす 組
.shift
	dec hl
	ld a, [hld]                       ; 1つ前の タイル
	push af
	ld a, [hl]                        ; 1つ前の スプライト
	inc hl
	inc hl
	ld [hli], a
	pop af
	ld [hld], a
	dec hl
	dec hl
	dec c
	ld a, c
	cp b
	jr nz, .shift
	ld [hl], d
	inc hl
	ld [hl], e
	ret

; a = スプライト。この マップの 人（マップオブジェクト 2〜15）が 使って いれば carry
Fw_IsSpriteOnMap:
	ld d, a
	ld hl, wMapObjects + $20 + MAPOBJ_SPRITE    ; （金の 人は 2〜15番）
	ld e, 14
.loop
	ld a, [hl]
	cp d
	jr z, .yes
	push de
	ld de, $10
	add hl, de
	pop de
	dec e
	jr nz, .loop
	and a
	ret
.yes
	scf
	ret

; この マップの 人が 使わない 組を 後ろから さがす（c = 番号 2〜9。なければ carry）
Fw_FindRemovable:
	ld c, 9
.loop
	call Fw_EntryAddr
	ld a, [hl]
	and a
	jr z, .next
	cp FW_SPRITE
	jr z, .next
	push bc
	call Fw_IsSpriteOnMap
	pop bc
	jr nc, .found
.next
	dec c
	ld a, c
	cp 2
	jr nc, .loop
	scf
	ret
.found
	and a
	ret

; 0〜9 の 組の タイルの 合計 → a（$ff ＝ こえた）
Fw_TotalLen:
	ld c, 0
	ld b, 0
.loop
	call Fw_EntryAddr
	ld a, [hl]
	call Fw_SpriteLen                 ; e
	ld a, b
	add e
	jr c, .over
	ld b, a
	inc c
	ld a, c
	cp 10
	jr c, .loop
	ld a, b
	ret
.over
	ld a, $ff
	ret

;---------------------------------------------------------------------
; 人の 絵を 読む 前（LoadUsedSpritesGFX）：wUsedSprites に 連れ歩き（$e2）を 入れる
;   1つめ（主人公の 次。タイル $0c〜$17、歩き $8c〜$97）に 入れ、そのあと この マップの 人が 使う 組を 前に よせる。
;   $78 に 入らなければ この マップの 人が 使わない 組を 後ろから けす（それでも 入らなければ 連れ歩きを けす）。
;   12タイル あまれば そこを 白い 下じきに する（wFwMaskTile）
Fw_Prepare:
	xor a
	ld [wFwMaskTile], a
	call Fw_NoCGB
	ret c
	ld a, [wPartyCount]
	and a
	ret z
	ld c, 1
.find
	call Fw_EntryAddr
	ld a, [hl]
	cp FW_SPRITE
	jr z, .have
	inc c
	ld a, c
	cp 10
	jr c, .find
	; ない：空きの はじめに 足す（9 まで うまって いれば 使わない 組を けす）
	ld c, 9
	call Fw_EntryAddr
	ld a, [hl]
	and a
	jr z, .room
	call Fw_FindRemovable
	ret c                             ; けせる 組が ない：連れ歩かない
	call Fw_RemoveEntry
.room
	ld c, 1
.empty
	call Fw_EntryAddr
	ld a, [hl]
	and a
	jr z, .put
	inc c
	jr .empty
.put
	ld [hl], FW_SPRITE
.have
	ld b, 1
	call Fw_MoveEntry                 ; c 番めを 1 番めへ
	; この マップの 人が 使う 組を 前に よせる
	ld b, 2
	ld c, 2
.sort
	call Fw_EntryAddr
	ld a, [hl]
	and a
	jr z, .fit
	push bc
	call Fw_IsSpriteOnMap
	pop bc
	jr nc, .snext
	push bc
	call Fw_MoveEntry
	pop bc
	inc b
.snext
	inc c
	ld a, c
	cp 10
	jr c, .sort
.fit
	; $78 に 入るまで 使わない 組を けす
	call Fw_TotalLen
	cp FW_SPRITE_LIMIT + 1
	jr c, .fits
	call Fw_FindRemovable
	jr c, .nofit
	call Fw_RemoveEntry
	jr .fit
.nofit
	ld c, 1                           ; 連れ歩きを けす
	jp Fw_RemoveEntry
.fits
	; 白い 下じき（12タイル）が 入るか（入らなければ この マップの 人が 使わない 組を けして あける）
	ld b, a
	add 12
	cp FW_SPRITE_LIMIT + 1
	jr c, .mask
	call Fw_FindRemovable
	ret c                             ; あけられない：下じきなし
	call Fw_RemoveEntry
	call Fw_TotalLen
	jr .fits
.mask
	ld a, b
	ld [wFwMaskTile], a
	ret

;---------------------------------------------------------------------
; この マップの 人（wMapObjects 2〜15）の 絵が ぜんぶ wUsedSprites に あるか（carry ＝ ある）
Fw_MapSpritesOK:
	ld hl, wMapObjects + $20 + MAPOBJ_SPRITE
	ld c, 14
.obj
	ld a, [hl]
	and a
	jr z, .next
	push hl
	ld e, a
	ld hl, wUsedSprites
	ld b, 12
.find
	ld a, [hli]
	cp e
	jr z, .found
	inc hl
	dec b
	jr nz, .find
	pop hl
	and a                             ; ない
	ret
.found
	pop hl
.next
	ld de, $10
	add hl, de
	dec c
	jr nz, .obj
	scf
	ret

; スプライトを ぜんぶ 読みなおして、出て いる 人の タイルの 番号も なおす
Fw_RefreshAll:
	fw_farcall $05, FW_RefreshSprites
Fw_RefreshTiles:
	ld a, 1
	ldh [hMapObjectIndex], a
	ld bc, wObjectStructs + $28
	ld e, 12
.loop
	ld a, [bc]
	and a
	jr z, .next
	push de
	call FW_GetSpriteVTile
	pop de
	ld hl, OBJ_SPRITE_TILE
	add hl, bc
	ld [hl], a
.next
	ld hl, $28
	add hl, bc
	ld b, h
	ld c, l
	dec e
	jr nz, .loop
	ret

;---------------------------------------------------------------------
; つながり（となりの マップへ 歩いて 入った）で 絵が たりない とき：並びを 作りなおして、前と 同じ 絵は 前と 同じ タイルの
; まま 読まず、たりない 絵だけを 前の マップで 使って いて 新しい マップで 使わない 組の 場所（長さが たりる 所）か、
; 前の 並びの おわりの 後ろ（$78 まで）に 入れて 読む。入らない ときは ぜんぶ 読む。
; 読む ときは 画面を 止めずに 書く（HBlank・VBlank の 間に すぐ 書く。1フレームに 8タイル ずつ の Get2bpp を 使わない）。
; 絵が かわる 人（SPRITE_VARS 以上）は いつも 読む。
DEF FW_SPRITE_VARS     EQU $f0
Fw_RefreshConn:
	; 前の 並び と 下じき
	ld a, [wFwMaskTile]
	ld [wFwPrevMask], a
	ld hl, wUsedSprites
	ld de, FW_O
	ld bc, 24
	call FW_CopyBytes
	fw_farcall $05, FW_RefreshList    ; 新しい マップの 並び
	ld a, 4                           ; MAPCALLBACK_SPRITES
	call FW_RunMapCallback
	call Fw_Prepare
	call Fw_Remap
	jr nc, .full
	; 前の 場所の まま（読む 印の ある 組 だけ 読む）
	ld c, 0
.rloop
	ld hl, FW_PEND
	ld b, 0
	add hl, bc
	ld a, [hl]
	and a
	jr z, .rnext
	push bc
	call Fw_LoadEntry
	pop bc
.rnext
	inc c
	ld a, c
	cp 10
	jr c, .rloop
	jr .still
.full
	; 入らなかった：GetUsedSprites と 同じ ならびで ぜんぶ 読む（画面を 止めずに）
	ld c, 0
	ld b, 0                           ; タイル
.floop
	call Fw_EntryAddr
	ld a, [hli]
	and a
	jr z, .fnext
	push hl
	call Fw_SpriteLen
	pop hl
	ld [hl], b
	ld a, b
	add e
	ld b, a
	push bc
	call Fw_LoadEntry
	pop bc
.fnext
	inc c
	ld a, c
	cp 10
	jr c, .floop
.still
	; 止まりの 絵（10・11）：かわって いれば 読む
	ld c, 10
.sloop
	call Fw_EntryAddr
	ld a, [hli]
	ld d, a
	ld a, c
	sub 10
	add a
	add a
	add $78
	ld [hl], a                        ; $78・$7c
	ld a, c
	add a
	ld e, a
	push bc
	ld b, 0
	ld c, e
	ld hl, FW_O
	add hl, bc
	pop bc
	ld a, [hl]
	cp d
	jr z, .snext
	ld a, d
	and a
	jr z, .snext
	push bc
	call Fw_LoadEntry
	pop bc
.snext
	inc c
	ld a, c
	cp 12
	jr c, .sloop
	; 下じき：前と 同じ 所に あれば 読まない
	ld a, [wFwMaskTile]
	and a
	jr z, .tiles
	ld b, a
	ld a, [wFwPrevMask]
	cp b
	call nz, Fw_ReloadMask
.tiles
	jp Fw_RefreshTiles

; c ＝ wUsedSprites の 組（タイルは 決まって いる）の 絵を 画面を 止めずに 読む
Fw_LoadEntry:
	call Fw_EntryAddr
	ld a, [hli]
	push af
	ld a, [hl]                        ; タイル
	ld l, a
	ld h, 0
	add hl, hl
	add hl, hl
	add hl, hl
	add hl, hl
	ld de, $8000
	add hl, de                        ; hl ＝ VRAM
	pop af
	push af
	call Fw_GetSpriteGfx              ; de・b・c
	push bc
	push de
	push hl
	call Fw_CopyTiles                 ; 止まりの 絵
	pop hl
	pop de
	pop bc
	pop af
	call Fw_IsStill
	ret c
	; 歩きの 絵（de ＋ c × 16 → タイル ＋ $80）
	ld a, h
	add $08
	ld h, a
	push hl
	ld l, c
	ld h, 0
	add hl, hl
	add hl, hl
	add hl, hl
	add hl, hl
	add hl, de
	ld d, h
	ld e, l
	pop hl
	jp Fw_CopyTiles

; b:de の c タイルを VRAM hl に 画面を 止めずに 写す（1タイルずつ WRAM に 写して、HBlank・VBlank の 間に 書く）
Fw_CopyTiles:
	ld a, c
	and a
	ret z
.tile
	push bc
	push hl
	push de
	ld a, b
	ld h, d
	ld l, e
	ld de, FW_COPYBUF
	ld bc, 16
	call FW_FarCopyBytes
	pop de
	pop hl
	ld bc, FW_COPYBUF
	ld a, 16
.byte
	push af
	di
.wait
	ldh a, [$ff41]
	and 2
	jr nz, .wait
	ld a, [bc]
	ld [hli], a
	ei
	inc bc
	pop af
	dec a
	jr nz, .byte
	ld a, e
	add 16
	ld e, a
	jr nc, .nc
	inc d
.nc
	pop bc
	dec c
	jr nz, .tile
	ret

; 新しい 並び（wUsedSprites 0〜9）の 組を、前の 並び（FW_O）と 同じ タイルに おきなおす。
;   前に あった 絵 → 前と 同じ タイル（読まない。かわる 絵 SPRITE_VARS〜 だけ 読む）
;   前に なかった 絵 → 前の 並びで 新しい 並びに ない 組の うち、長さが たりる 所、なければ 前の おわりの 後ろ（$78・下じきの 前 まで）
;   入る 所が なければ キャリーなし（wUsedSprites は かえない）
Fw_Remap:
	xor a
	ld hl, FW_USED
	ld bc, FW_TMPEND - FW_USED
.clr
	ld [hli], a
	dec c
	jr nz, .clr
	; 1：同じ 絵
	ld c, 0
.p1
	call Fw_EntryAddr
	ld a, [hl]
	and a
	jr z, .p2start
	ld d, a
	call .findold                     ; a ＝ タイル、e ＝ 番号（carry ＝ ある）
	jr nc, .p1pend
	push af
	ld hl, FW_RES
	ld b, 0
	add hl, bc
	pop af
	ld [hl], a
	ld hl, FW_USED
	ld b, 0
	push de
	ld d, 0
	add hl, de
	pop de
	ld [hl], 1
	ld a, d
	cp FW_SPRITE_VARS
	jr c, .p1next
	ld hl, FW_PEND
	ld b, 0
	add hl, bc
	ld [hl], 2
	jr .p1next
.p1pend
	ld hl, FW_PEND
	ld b, 0
	add hl, bc
	ld [hl], 1
.p1next
	inc c
	ld a, c
	cp 10
	jr c, .p1
.p2start
	; 前の 並びの おわり
	xor a
	ld [FW_TAIL], a
	ld e, 0
.tl
	ld d, 0
	ld hl, FW_O
	add hl, de
	add hl, de
	ld a, [hli]
	and a
	jr z, .tldone
	push hl
	push de
	call Fw_SpriteLen
	ld b, e
	pop de
	pop hl
	ld a, [hl]                        ; タイル
	add b
	ld c, a
	ld a, [FW_TAIL]
	cp c
	jr nc, .tlnext
	ld a, c
	ld [FW_TAIL], a
.tlnext
	inc e
	ld a, e
	cp 10
	jr c, .tl
.tldone
	; 2：新しい 絵
	ld c, 0
.p2
	ld hl, FW_PEND
	ld b, 0
	add hl, bc
	ld a, [hl]
	cp 1
	jr nz, .p2next
	call Fw_EntryAddr
	ld a, [hl]
	push bc
	call Fw_SpriteLen                 ; e ＝ 長さ
	pop bc
	ld a, e
	ld [FW_LENI], a
	ld e, 0
.p2j
	ld d, 0
	ld hl, FW_USED
	add hl, de
	ld a, [hl]
	and a
	jr nz, .p2jnext
	ld hl, FW_O
	add hl, de
	add hl, de
	ld a, [hl]
	and a
	jr z, .tail
	push bc
	push de
	call Fw_SpriteLen
	ld b, e
	pop de
	ld a, [FW_LENI]
	cp b
	pop bc
	jr z, .take
	jr c, .take
.p2jnext
	inc e
	ld a, e
	cp 10
	jr c, .p2j
.tail
	; 前の おわりの 後ろ（$78 まで）
	ld a, [FW_LENI]
	ld b, a
	ld a, [FW_TAIL]
	ld d, a
	add b
	ld b, a                           ; おわり
	ld a, FW_SPRITE_LIMIT
	cp b
	jr c, .tfail
	ld a, b
	ld [FW_TAIL], a
	ld a, d
	jr .tset
.tfail
	and a                             ; 入る 所が ない（キャリーなし）
	ret
.take
	ld d, 0
	ld hl, FW_USED
	add hl, de
	ld [hl], 1
	ld hl, FW_O + 1
	add hl, de
	add hl, de
	ld a, [hl]
.tset
	ld hl, FW_RES
	ld b, 0
	add hl, bc
	ld [hl], a
.p2next
	inc c
	ld a, c
	cp 10
	jp c, .p2
	; 3：書く
	ld c, 0
.cm
	call Fw_EntryAddr
	ld a, [hli]
	and a
	jr z, .cmdone
	push hl
	ld hl, FW_RES
	ld b, 0
	add hl, bc
	ld a, [hl]
	pop hl
	ld [hl], a
	inc c
	ld a, c
	cp 10
	jr c, .cm
.cmdone
	; 白い 下じき：前の 所が 新しい おわりより 後ろなら そのまま、ちがえば おわりの 後ろ（入らなければ なし）
	ld a, [FW_TAIL]
	ld b, a
	ld a, [wFwPrevMask]
	and a
	jr z, .newmask
	cp b
	jr c, .newmask
	jr .setmask
.newmask
	ld a, b
	add 12
	cp FW_SPRITE_LIMIT + 1
	ld a, 0
	jr nc, .setmask
	ld a, b
.setmask
	ld c, a
	ld a, [wFwMaskTile]
	and a
	ld a, c
	jr nz, .keep
	xor a                             ; Fw_Prepare で 下じきなし（手持ちが いない など）
.keep
	ld [wFwMaskTile], a
	scf
	ret

; d ＝ 絵の 番号 が FW_O（0〜9）に あれば キャリー、a ＝ タイル、e ＝ 何番め
.findold
	ld hl, FW_O
	ld e, 0
.fo
	ld a, [hli]
	and a
	ret z
	cp d
	jr nz, .fonext
	ld a, [hl]
	scf
	ret
.fonext
	inc hl
	inc e
	ld a, e
	cp 10
	jr c, .fo
	and a
	ret

;---------------------------------------------------------------------
; 正面の 白い 下じき
; 手持ちの アイコンは 目・顔の 白を 透明（色0）で かいて いる（手持ちの 画面は 背景が 白）。スプライトは 透明＋3色 なので、
; 外と つながって いない 透明の 所（あな）だけ 色1 の 絵（gfxdata/follow_icon/mask.bin、1匹 384バイト ＝ 止まり 12・歩き 12タイル）を
; 人の 絵の あまった 所（wFwMaskTile。止まり ＋0〜11、歩き ＋$80〜）に 置き、連れ歩きの 絵の 4枚の 後ろに 白
; （OBJ パレット5 の 色1 ＝ 白）で かさねる。あまりが なければ 下じきなし。

; de = 絵の 番号（0〜278）。de は こわさない
Fw_LoadMask:
	ld a, [wFwMaskTile]
	and a
	ret z                             ; VRAM が あまって いない
	push de
	ld a, d
	and a
	jr z, .ok
	ld a, e
	cp 278 - 256
	jr nc, .done                      ; ボール（下じき なし）
.ok
	call Fw_IndexToGfx                ; 絵と 同じ 数え方（b = $60〜、de = 場所）
	ld a, b
	add $67 - FW_GFX_BANK
	ld b, a
	ld a, [wFwMaskTile]
	ld l, a
	ld h, 0
	add hl, hl
	add hl, hl
	add hl, hl
	add hl, hl
	push de
	ld de, $8000
	add hl, de
	pop de
	push bc
	push de
	push hl
	ld c, 12
	call FW_Get2bpp_
	pop hl
	pop de
	pop bc
	ld a, h
	add $08
	ld h, a
	ld a, e
	add LOW(12 * 16)
	ld e, a
	ld a, d
	adc HIGH(12 * 16)
	ld d, a
	ld c, 12
	call FW_Get2bpp_
.done
	pop de
	ret
DEF FW_Get2bpp_        EQU $0e5b

; 人の 絵を 読みこんだ あと（LoadUsedSpritesGFX の さいご）：下じきを 読みなおす（メニューから もどった とき など）
Fw_ReloadMask::
	ld a, [wPartyCount]
	and a
	ret z
	call Fw_GetLead
	ret c
	jp Fw_LoadMask

; スプライトを 並べた あと：連れ歩きの 絵（タイル $0c〜$17・歩き $8c〜$97、パレット7）の 4枚と 同じ 場所に、
; 下じき（パレット5）を 後ろに 足す
Fw_Underlay::
	call Fw_NoCGB
	ret c
	ld a, [wPartyCount]
	and a
	ret z
	; 向きの 色の 切りかえも ここで 見る（話しかけた とき など スクリプトの 間は Fw_Update が まわらない）
	call Fw_FaceCheck
	ld a, [wFwBall]
	and a
	ret nz                            ; ボールの 間は なし
	ld a, [wFwMaskTile]
	and a
	ret z
	ld b, a                           ; b ＝ 下じきの タイル
	ld d, $a0                         ; （金は いつも 40枚）
	ldh a, [hUsedSpriteIndex]
	add 3
	ld c, a                           ; もとの おわり（属性の 場所）
	ld e, 4                           ; のこり
	ld hl, $c300 + 3                  ; wShadowOAM の 属性
.loop
	ld a, l
	cp c
	ret nc
	ld a, [hl]
	and %00000111
	cp FW_OWN_PAL
	jr z, .cand
.next
	ld a, l
	add 4
	ld l, a
	jr .loop
.cand
	dec l
	ld a, [hli]                       ; タイル
	push af
	and $7f
	sub FW_TILE
	cp 12
	jr nc, .notfw
	add b                             ; 下じきの タイル
	ld [wFwRet], a
	pop af
	and $80
	push bc
	ld b, a
	ld a, [wFwRet]
	or b
	pop bc
	ld [wFwRet], a
	ldh a, [hUsedSpriteIndex]
	cp d
	ret nc                            ; OAM が いっぱい
	push bc
	push de
	push hl
	ld a, l
	sub 3
	ld l, a
	ld a, [hli]                       ; Y
	ld b, a
	ld a, [hli]                       ; X
	ld c, a
	inc l
	ld a, [hl]
	and %11100000                     ; 前後・反転 は 同じ
	or 5                              ; パレット5
	ld d, a
	ldh a, [hUsedSpriteIndex]
	ld l, a
	ld [hl], b
	inc l
	ld [hl], c
	inc l
	ld a, [wFwRet]
	ld [hl], a
	inc l
	ld [hl], d
	inc l
	ld a, l
	ldh [hUsedSpriteIndex], a
	pop hl
	pop de
	pop bc
	dec e
	ret z                             ; 4枚 おわり
	jr .next
.notfw
	pop af
	jr .next
