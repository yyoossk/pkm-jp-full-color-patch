; 連れ歩き（手持ちの ポケモンが 主人公の 後ろを 歩く）… 銀 日本版（後期版）
;   金銀連れ歩きキット（クリスタルで 入れた follow_crystal.asm）を 金銀の しくみに あわせて 移した もの。
;
; ・えらんだ ポケモン（はじめは 1匹目。手持ちの 画面で SELECT）が 主人公の 後ろを 歩く。タマゴも 歩く。
;   ひんし・じてんしゃ・なみのり など（wPlayerState ≠ 0）では ボールに もどって かくれる。白黒の ゲームボーイでは 出さない。
; ・正面は 手持ちの アイコンと 同じ 絵と 色、後ろ・横は 向きの ある 歩行グラフィック（gfxdata/follow_icon）。
; ・話しかけると ふりむいて 鳴き、気持ちの アイコンと 会話（follow_talk.inc）。ピカチュウは 表情の 絵（follow_pika.inc）。
;
; 金銀で クリスタルと ちがう 所
; ・クリスタルは 連れ歩きの 絵を 人の 絵の 表（wUsedSprites）に 入れて いたが、金銀の 表は 人の 絵で いっぱい（外の マップは
;   歩く 人 9つ ＝ $00〜$77 ぜんぶ）なので、連れ歩きの 絵は 金銀が 使わない VRAM の バンク1 に 置く：
;     止まり タイル $66〜$71（$8660）、歩き $e6〜$f1（$8e60）、白い したじき $00〜$17（$8000）。
;   連れ歩きの オブジェクトの OBJECT_SPRITE_TILE を $66 に し、InitSprite の パレットの and %111 を and %1111 に して
;   OBJECT_PALETTE の ビット3 で OAM の バンク1 を 出す。_UpdateSprites が OAM を 作った あと（Fw_FixOAM）に、
;   連れ歩きの 4枚の 後ろに したじきを 足す。人の 絵の 表を かえないので、つながりで 人の 絵が かわる・画面が 止まる ことも ない。
;   ポケギアは VRAM の バンク1 を けすので、人の 絵を 読みなおす とき（LoadUsedSpritesGFX の さいご）にも 読む。
; ・金銀は スタックが WRAM バンク1 に あるので WRAM の バンクを 切りかえない。変数は セーブの 使われていない 所（$d786〜）。
; ・色は WRAM バンク0（wOBPals1 $c240・wOBPals2 $c2c0）。
;
; 連れ歩きの コード・会話の もとは fellowship-of-the-roms/pokecrystal の follow-mons（Vulcandth・AtmaBuster）、
; 見た目と 動きは Pokémon Crystal Crunch（gomojoeb）。

INCLUDE "src/charmap_jp.inc"

DEF FW_BANK            EQU $4b
DEF FW_SPRITE          EQU $e2       ; 使われていない スプライトの 番号
DEF FW_GFX_BANK        EQU $50       ; 絵（follow_data.inc）
DEF FW_MASK_BANK       EQU $57       ; したじき
DEF FW_PER_BANK        EQU 42
DEF FW_TYPE            EQU 3         ; OBJECTTYPE_3
DEF FW_MOVEMENT        EQU $06       ; SPRITEMOVEDATA_STANDING_DOWN
DEF FW_EGG             EQU $fd
DEF FW_UNOWN           EQU 201

; --- ホーム（銀）
DEF FW_GetObjectStruct EQU $192f
DEF FW_GetMapObject    EQU $171c
DEF FW_Unmask          EQU $17a0     ; UnmaskCopyMapObjectStruct
DEF FW_DeleteObjectStruct EQU $17e9
DEF FW_Random          EQU $305e
DEF FW_CallScript      EQU $26f5
DEF FW_UpdateSprites2  EQU $191c     ; UpdateSprites
DEF FW_RunMapCallback  EQU $2711
DEF FW_GetSpriteDirection EQU $1951
DEF FW_GetFarByte2     EQU $30e4     ; GetFarByte
DEF FW_EventFlagAction EQU $2eeb
; --- バンクつき
DEF FW_StartFollow     EQU $5779     ; バンク1
DEF FW_IsNPCAtCoord    EQU $7b30     ; バンク1
DEF FW_LoadObjectMasks EQU $4488     ; バンク9
DEF FW_InitializeVisibleSprites EQU $4767 ; バンク2
; --- RAM
DEF wMapObjects        EQU $d438     ; 16 × 16バイト（0 = 主人公）
DEF wObjectStructs     EQU $d1f0     ; 13 × $28バイト（0 = 主人公）
DEF wPlayerMapX        EQU $d200
DEF wPlayerMapY        EQU $d201
DEF wObjectFollow_Leader   EQU $d1e7
DEF wObjectFollow_Follower EQU $d1e8
DEF wFollowMovementQueue EQU $d1eb     ; 5バイト（$d1ea は 長さ）
DEF wPlayerState       EQU $d675
DEF wPlayerStepDirection EQU $ce7a
DEF wScriptMode        EQU $d150
DEF hMapEntryMethod    EQU $ffa1
DEF hMapObjectIndex    EQU $ffb1
DEF wPartyCount        EQU $d9e8
DEF wPartySpecies      EQU $d9e9
DEF wPartyMon1         EQU $d9f0
DEF wSpriteFlags       EQU $d035
DEF wShadowOAM         EQU $c300
DEF hUsedSpriteIndex   EQU $ffbf
DEF hCGB               EQU $ffe8
DEF MAPSETUP_CONNECTION EQU $f7
; 変数（セーブの 使われていない 所。wEventFlags $d7aa の 前。$d6e5〜$d70c は 場所の 名前の 札、$d740〜$d76f は むしとり大会、
; $d7a0〜$d7a2 は ほかの 機能）
DEF wFwSlot            EQU $d7a3     ; 連れ歩く 手持ちの 番号（レポートに 書かれる）：0 ＝ 1匹目（はじめ）、1〜6、$ff ＝ だれも
DEF wFwLoaded          EQU $d786     ; VRAM に 読んで いる 絵の 番号（2バイト。$ffff ＝ まだ）
DEF wFwLoadedPal       EQU $d788     ; 読みこんで いる 色
DEF wFwBall            EQU $d789     ; ボールの アニメ（0 なし・1 もどる・2 出る・3 まつ）
DEF wFwBallT           EQU $d78a     ; のこり フレーム
DEF wFwHidden          EQU $d78b     ; ボールに もどった（次に 出る ときは ボールから）
DEF wFwLoadedFace      EQU $d78c     ; 今の 色が 正面用（0）か 後ろ・横用（1）か

; 種類の 番号（オブジェクト・マップオブジェクト）
DEF OBJ_MAP_OBJECT_INDEX EQU $01
DEF OBJ_SPRITE_TILE    EQU $02
DEF OBJ_FLAGS1         EQU $04
DEF OBJ_PALETTE        EQU $06
DEF OBJ_DIR_WALKING    EQU $07       ; 歩いて いる 向き（$ff = 止まって いる）
DEF OBJ_DIRECTION      EQU $08       ; 向き（0 下・4 上・8 左・$c 右）
DEF OBJ_STEP_FRAME     EQU $0c
DEF OBJ_FACING         EQU $0d
DEF OBJ_SPRITE_Y_OFFSET EQU $1a
DEF OBJ_RANGE          EQU $20       ; 連れ歩きでは ボールの コマ（0 = ポケモン）
DEF OBJ_MAP_X          EQU $10
DEF OBJ_MAP_Y          EQU $11
DEF MAPOBJ_SPRITE      EQU $01
DEF MAPOBJ_Y           EQU $02
DEF MAPOBJ_X           EQU $03
DEF MAPOBJ_COLOR_TYPE  EQU $08
DEF MAPOBJ_EVENT_FLAG  EQU $0c
; ポケモン 固有の 色
DEF FW_OWN_PAL         EQU 7         ; PAL_OW_ROCK（連れ歩き 専用に する）
DEF FW_MASK_PAL        EQU 5         ; PAL_OW_EMOTE（色1 が 白）
DEF FW_SPRITE_ROCK     EQU $59
DEF FW_SPRITE_BOULDER  EQU $5a
DEF FW_wOBPals1        EQU $c240
DEF FW_wOBPals2        EQU $c2c0
DEF FW_hCGBPalUpdate2  EQU $ffe7
DEF hJoyDown           EQU $ffaa
DEF FW_B_BUTTON        EQU %00000010
DEF FW_D_PAD           EQU %11110000
; VRAM バンク1（OBJ の タイル）
; 連れ歩きの オブジェクトの OBJECT_SPRITE_TILE を $66 に して、止まりの 絵は タイル $66〜$71（$8660）、歩きの 絵は ＋$80 の
; $e6〜$f1（$8e60）に 置く（$e6〜$f5 は 場所の 名前の 札で 使わない 字の 番号。札は 字の 絵を VRAM バンク1 の 字の 番号の 所に 写す）。
; 白い したじきは $00〜$17（$8000）。OAM の バンク1 の ビットは InitSprite の and %111 を and %1111 に して、
; 連れ歩きの オブジェクトの OBJECT_PALETTE の ビット3 から 出す（ほかの オブジェクトは ビット3 が 0）。
DEF FW_TILE            EQU $66
DEF FW_VT_STAND        EQU $8000 + FW_TILE * 16
DEF FW_VT_WALK         EQU $8000 + (FW_TILE + $80) * 16
DEF FW_VT_MASK         EQU $8000     ; タイル $00〜$17

MACRO fw_farcall ; bank, addr
	ld a, \1
	ld hl, \2
	rst $08
ENDM

;---------------------------------------------------------------------
; つなぎ
;---------------------------------------------------------------------
; LoadMapObjects（$05:$5560。18バイト ＋ 使われていない MapSetup_DummyFunction の ret）を まるごと 書きかえる
SECTION "follow loadmapobjects", ROMX[$5560], BANK[$05]
	fw_farcall FW_BANK, Fw_LoadMapObjects
	ret

; LoadUsedSpritesGFX の さいごの call LoadMiscTiles（$05:$4204）
SECTION "follow loadusedspritesgfx hook", ROMX[$4204], BANK[$05]
	call F0_SpritesGFX

; 岩・かいりきの 岩の スプライトの 色を いわ（7）から ちゃ（3）に（7本目を 連れ歩き 専用に する ため）
; OverworldSprites（$05:$47b0、6バイトずつ、6バイト目 ＝ パレット）
SECTION "follow rock pal", ROMX[$47b0 + (FW_SPRITE_ROCK - 1) * 6 + 5], BANK[$05]
	db 3
SECTION "follow boulder pal", ROMX[$47b0 + (FW_SPRITE_BOULDER - 1) * 6 + 5], BANK[$05]
	db 3

; HandleMap の call HandleMapObjects（$25:$66cd）
SECTION "follow handlemap hook", ROMX[$66cd], BANK[$25]
	call F25_Objects
; 話しかけ：ObjectEventTypeArray（$25:$6921）の OBJECTTYPE_3 の 行き先（元は .three の xor a / ret）
SECTION "follow talk ptr", ROMX[$6921 + 3 * 3 + 1], BANK[$25]
	dw F25_Talk
SECTION "follow bank25", ROMX[$7e10], BANK[$25]
F25_Objects:
	call $6716                        ; HandleMapObjects（場所の 名前の 札の 処理も ここ）
	fw_farcall FW_BANK, Fw_Update
	ret
F25_Talk:
	ld a, FW_BANK
	ld hl, FollowerTalkScript
	jp FW_CallScript

; 色：LoadMapPals の OBJ の 色を 写す call CopyBytes（$02:$7623）
SECTION "follow mappals hook", ROMX[$7623], BANK[$02]
	call F2_OBPals
SECTION "follow bank2", ROMX[$7f00], BANK[$02]
F2_OBPals:
	call $30d6                        ; CopyBytes
	fw_farcall FW_BANK, Fw_OwnPalToPals1
	ret

; 主人公の ぶつかり（DoPlayerMovement .CheckNPC の farcall IsNPCAtCoord $04:$435a）
SECTION "follow player collision", ROMX[$435a], BANK[$04]
	ld a, FW_BANK
	ld hl, Fw_IsNPCAtCoord

; InitSprite の OBJECT_PALETTE の and %111（$01:$5992）を and %1111 に（ビット3 ＝ VRAM バンク1 を OAM に 出す）
SECTION "follow initsprite bank bit", ROMX[$5992 + 1], BANK[$01]
	db %00001111

; スプライトを 並べた あと（_UpdateSprites の call InitSprites $01:$58a6）
SECTION "follow updatesprites hook", ROMX[$58a6], BANK[$01]
	call F1_InitSprites

; 動き（Crystal Crunch の SetFacingFollowerStep・Run・Idle）：ObjectActionPairPointers（$01:$4460）の
; STAND（1）・STEP（2）を、連れ歩き（スプライト $e2）の とき だけ 連れ歩きの 動きに する。
SECTION "follow action stand", ROMX[$4460 + 1 * 4], BANK[$01]
	dw F1_StandAction
SECTION "follow action step", ROMX[$4460 + 2 * 4], BANK[$01]
	dw F1_StepAction
; follow の 次の 動き（MovementFunction_Follow の ld hl, GetFollowerNextMovementIndex $01:$4879）
SECTION "follow next move ptr", ROMX[$4879 + 1], BANK[$01]
	dw F1_NextMove
SECTION "follow bank1", ROMX[$7f64], BANK[$01]
; ふつうの 歩き（step $0c〜$0f）・はやい 歩き（big_step $10〜$13）を、いまの 主人公の 速さ（Bダッシュ中か）に あわせて わたす
F1_NextMove:
	; 連れ歩き（スプライト $e2）の とき だけ 速さを あわせる。イベントの follow（キキョウシティの せんせい など、人が 先頭で
	; 主人公が ついて いく・主人公が 先頭で 人が ついて いく）では 元の まま（せんせいの はやい 歩きを ふつうに して いて、
	; 主人公が おくれて はなれ、主人公と せんせいの オブジェクトが こわれ、連れ歩きも 出なく なって いた）
	ld a, [bc]                        ; OBJECT_SPRITE（bc ＝ 動いて いる オブジェクト）
	cp FW_SPRITE
	jp nz, $5485                      ; GetFollowerNextMovementIndex（元の まま）
	call $5485                        ; GetFollowerNextMovementIndex
	ret c
	cp $0c
	ret c
	cp $14
	ret nc
	and 3
	ld e, a
	ldh a, [hJoyDown]
	and FW_B_BUTTON
	jr z, .walk
	ldh a, [hJoyDown]
	and FW_D_PAD
	ld a, $10
	jr nz, .add
.walk
	ld a, $0c
.add
	add e
	and a
	ret
F1_Facing:
	ld d, a
	call FW_GetSpriteDirection
	or d
	ld hl, OBJ_FACING
	add hl, bc
	ld [hl], a
	ret

; 動き（Crystal Crunch の SetFacingFollowerStep・Run・Idle）。まいフレーム 通るので バンク1 に 置く
;   （使われていない IsNPCAtPlayerCoord $01:$7c02〜$7c5f の 所）
;   歩く：絵の 2コマ（止まり・歩き）だけを かわるがわる（元の 4コマ目は 歩きの 左右反転で、アイコンが 歩く たびに 裏返った）。
;         止まりの コマで 1ドット 上げて はねて 歩く。Bダッシュ中は はやく かえる。
;   止まって いる：16フレームごとに 2コマを かえる（手持ちの 画面の アイコンと 同じ）。スクリプト中は 止まりの コマ。
SECTION "follow bank1 actions", ROMX[$7c02], BANK[$01]
F1_StandAction:
	ld a, [bc]                        ; OBJECT_SPRITE
	cp FW_SPRITE
	jp nz, $44b2                      ; SetFacingStandAction
	call F1_BallAct
	ret c
	ld hl, OBJ_SPRITE_Y_OFFSET
	add hl, bc
	ld [hl], 0
	ld a, [wScriptMode]
	and a
	ld a, 0
	jp nz, F1_Facing
	ld hl, OBJ_STEP_FRAME
	add hl, bc
	inc [hl]
	ld a, [hl]
	swap a
	and 1
	jp F1_Facing
F1_StepAction:
	ld a, [bc]
	cp FW_SPRITE
	jp nz, $44be                      ; SetFacingStepAction
	call F1_BallAct
	ret c
	ld hl, OBJ_FLAGS1
	add hl, bc
	bit 3, [hl]                       ; SLIDING_F
	jp nz, $44a7                      ; SetFacingCurrent
	ld hl, OBJ_STEP_FRAME
	add hl, bc
	inc [hl]
	ld a, [hl]
	rrca
	rrca
	ld e, a
	ldh a, [hJoyDown]
	and FW_B_BUTTON
	jr z, .walk
	ldh a, [hJoyDown]
	and FW_D_PAD
	jr nz, .run
.walk
	rrc e
.run
	ld a, e
	and 1
	ld d, a
	ld hl, OBJ_SPRITE_Y_OFFSET
	add hl, bc
	dec a                             ; 止まりの コマ（0）は −1（はねる）、歩き（1）は 0
	ld [hl], a
	ld a, d
	jp F1_Facing
; ボールの アニメ中（OBJECT_RANGE ≠ 0）：1 とじた ＝ 横（$08）、2 半分 ＝ 上（$04）、3 開いた ＝ 下（$00）。carry
;   （使われていない IsObjectFacingSomeoneElse $01:$7b04〜$7b2f の 所）
SECTION "follow bank1 ball", ROMX[$7b04], BANK[$01]
F1_BallAct:
	ld hl, OBJ_RANGE
	add hl, bc
	ld a, [hl]
	and a
	ret z
	ld e, $08
	dec a
	jr z, .set
	ld e, $04
	dec a
	jr z, .set
	ld e, $00
.set
	ld hl, OBJ_SPRITE_Y_OFFSET
	add hl, bc
	ld [hl], 0
	ld hl, OBJ_FACING
	add hl, bc
	ld [hl], e
	scf
	ret
SECTION "follow bank1 b", ROMX[$7fa6], BANK[$01]
F1_InitSprites:
	call $58fe                        ; InitSprites
	fw_farcall FW_BANK, Fw_FixOAM
	ret

; 手持ちの 画面：InitPartyMenuWithCancel の wMenuJoypadFilter（$14:$4390 の ld a, 3）を A・B・SELECT に、
; PartyMenuSelect（$14:$43c0）の call StaticMenuJoypad を SELECT なら えらんで もう一度 まつ ものに。
SECTION "follow party filter", ROMX[$4390 + 1], BANK[$14]
	db %0111                          ; PAD_A | PAD_B | PAD_SELECT
SECTION "follow party select hook", ROMX[$43c0], BANK[$14]
	call F0_PartyJoypad
; 手持ちの ならびかえ（_SwitchPartyMons の call .SwapMonAndMail $14:$562c）
SECTION "follow party swap hook", ROMX[$562c], BANK[$14]
	call F0_Swap
; 手持ちから ぬける とき（RemoveMonFromPartyOrBox の ld hl, wPartyCount $03:$62e2）
SECTION "follow remove hook", ROMX[$62e2], BANK[$03]
	call F0_Remove

; ホーム（使われていない PlaceBCDNumberSprite $3e9e〜$3edc）
SECTION "follow home", ROM0[$3e9e]
F0_SpritesGFX:
	call $4260                        ; LoadMiscTiles（バンク5 から 呼ばれる）
	fw_farcall FW_BANK, Fw_SpritesGFX
	ret
F0_PartyJoypad:
	fw_farcall FW_BANK, Fw_PartyJoypad
	ret
F0_Swap:
	fw_farcall FW_BANK, Fw_SwapSlots
	jp $566a                          ; .SwapMonAndMail（バンク$14）
F0_Remove:
	fw_farcall FW_BANK, Fw_RemoveSlot ; bc・de は farcall で のこる
	ld hl, wPartyCount
	ret

; VRAM バンク1 に 写す（使われていない FarDecompressBufferedPic $0d59〜$0d7f）
;   b ＝ ROM の バンク、de ＝ 元、hl ＝ VRAM、c ＝ タイルの 数。画面が ついて いても 止めずに 書く
SECTION "follow home copy", ROM0[$0d59]
F0_CopyVRAM1:
	ldh a, [$ff9f]                    ; hROMBank
	push af
	ld a, b
	rst $10                           ; Bankswitch
.tile
	ld b, 16
.byte
	di
.wait
	ldh a, [$ff41]                    ; rSTAT
	and 2
	jr nz, .wait
	inc a
	ldh [$ff4f], a                    ; rVBK = 1
	ld a, [de]
	ld [hli], a
	xor a
	ldh [$ff4f], a
	ei
	inc de
	dec b
	jr nz, .byte
	dec c
	jr nz, .tile
	pop af
	rst $10
	ret

;---------------------------------------------------------------------
SECTION "follow main", ROMX[$4000], BANK[FW_BANK]

; 連れ歩く ポケモン（Crystal Crunch と 同じく 手持ちで SELECT を おして えらぶ）
; a = 手持ちの 番号（0〜5）。いない とき carry（手持ちが いない・だれも えらんで いない）。手持ちの 数より 大きければ 1匹目
Fw_Index:
	ld a, [wPartyCount]
	and a
	scf
	ret z
	ld a, [wFwSlot]
	cp $ff
	scf
	ret z
	and a
	jr z, .ok
	dec a
	push bc
	ld b, a
	ld a, [wPartyCount]
	dec a
	cp b
	ld a, b
	pop bc
	jr nc, .ok
	xor a
.ok
	and a
	ret
; a = 連れ歩く ポケモンの 種類（いなければ 0 と carry）
Fw_Species:
	call Fw_Index
	jr c, .none
	push hl
	push de
	ld e, a
	ld d, 0
	ld hl, wPartySpecies
	add hl, de
	ld a, [hl]
	pop de
	pop hl
	and a
	ret
.none
	xor a
	scf
	ret
; hl = 連れ歩く ポケモンの データ（wPartyMon1 ＋ 番号 × 48。いなければ 1匹目）
Fw_MonAddr:
	call Fw_Index
	jr nc, .got
	xor a
.got
	push de
	ld hl, wPartyMon1
	ld de, 48
	and a
	jr z, .done
.loop
	add hl, de
	dec a
	jr nz, .loop
.done
	pop de
	ret
Fw_DVs:
	call Fw_MonAddr
	push de
	ld de, $15
	add hl, de
	pop de
	ret
Fw_HP:
	call Fw_MonAddr
	push de
	ld de, $22
	add hl, de
	pop de
	ret

; 先頭の ポケモンの 絵の 番号（de）と 色（a = PAL_OW_。固有の 色の ときは 7、色ちがいなら $0f）。手持ちが いなければ carry
Fw_GetLead:
	ld a, [wFwBall]
	and a
	jr z, .mon
	call Fw_Index
	ret c
	ld de, 278                        ; ボール
	ld a, FW_OWN_PAL
	and a
	ret
.mon
	call Fw_GetLeadField
	ret c
	call Fw_Species
	cp FW_EGG
	jr z, .normal
	call Fw_IsShiny
	ld a, FW_OWN_PAL
	jr nz, .normal2
	ld a, FW_OWN_PAL | 8
	and a
	ret
.normal
	ld a, FW_OWN_PAL
.normal2
	and a
	ret

; 連れ歩きの 向き：a = 0 正面（下向き・いない）、1 後ろ・横。bc・de・hl は こわさない
Fw_FaceClass:
	push bc
	push de
	push hl
	call Fw_FindSlot
	jr c, .zero
	ld a, [bc]
	cp $ff
	jr z, .zero
	call FW_GetObjectStruct
	ld hl, OBJ_DIRECTION
	add hl, bc
	ld a, [hl]
	and a
	jr z, .done
	ld a, 1
	jr .done
.zero
	xor a
.done
	pop hl
	pop de
	pop bc
	ret

; スプライトを 並べる たび（a ＝ OAM の 絵の 向き 0 正面・1 後ろ・横）：かわったら 色を 書きなおす
;   色は すぐ 書かず、次の VBlank で 新しい 向きの 絵（OAM）と いっしょに かわる ように する
Fw_FaceCheck:
	ld d, a
	ld a, [wFwLoadedFace]
	cp d
	ret z
	ld a, [wFwBall]
	and a
	ret nz                            ; ボールの 間は ボールの 色
	ld a, d
	ld [wFwLoadedFace], a
	ld hl, FW_wOBPals1 + FW_OWN_PAL * 8
	call Fw_PutOwnPal
	ld hl, FW_wOBPals2 + FW_OWN_PAL * 8
	call Fw_PutOwnPal
	ld a, 1
	ldh [FW_hCGBPalUpdate2], a
	ret

; 先頭の ポケモンの 固有の 2色 → bc・de（色1 = bc、色2 = de）
Fw_OwnColors:
	ld a, [wFwBall]
	and a
	jr z, .mon
	ld bc, 31 | 19 << 5 | 10 << 10    ; ボール（PAL_OW_RED の 色1・色2）
	ld de, 31 | 7 << 5 | 1 << 10
	ret
.mon
	call Fw_Species
	cp FW_EGG
	jr nz, .notegg
	xor a                             ; タマゴ = 0
.notegg
	ld l, a
	ld h, 0
	add hl, hl
	add hl, hl
	add hl, hl
	push af
	ld a, [wFwLoadedFace]             ; 正面は 手持ちと 同じ 色、後ろ・横は 歩行グラフィックに あう 色
	ld de, FollowerOwnPals
	and a
	jr z, .front
	ld de, FollowerWalkPals
.front
	pop af
	add hl, de
	and a
	jr z, .read
	push hl
	call Fw_IsShiny
	pop hl
	jr nz, .read
	ld de, 4
	add hl, de
.read
	call .byte
	ld c, a
	call .byte
	ld b, a
	call .byte
	ld e, a
	call .byte
	ld d, a
	; 夜・暗い 所でも 暗く しない（Crystal Crunch は 夜に 暗く するが、ユーザーの 希望で しない）
	ret
.byte
	ld a, BANK(FollowerOwnPals)
	push hl
	push bc
	push de
	call FW_GetFarByte2
	pop de
	pop bc
	pop hl
	inc hl
	ret

; hl = パレットの はじめ に 色1・色2・くろ を 書く（色0 は そのまま）
Fw_PutOwnPal:
	push hl
	call Fw_OwnColors
	pop hl
	inc hl
	inc hl
	ld [hl], c
	inc hl
	ld [hl], b
	inc hl
	ld [hl], e
	inc hl
	ld [hl], d
	inc hl
	xor a
	ld [hli], a
	ld [hl], a
	ret

; LoadMapPals の あと：7本目（wOBPals1）を 先頭の ポケモンの 色に
Fw_OwnPalToPals1:
	ld a, [wPartyCount]
	and a
	ret z
	ld hl, FW_wOBPals1 + FW_OWN_PAL * 8
	jp Fw_PutOwnPal

; 先頭が かわった とき：7本目（wOBPals1・wOBPals2）を 書いて 画面に
Fw_OwnPalNow:
	ld a, [wPartyCount]
	and a
	ret z
	call Fw_FaceClass
	ld [wFwLoadedFace], a
	ld hl, FW_wOBPals1 + FW_OWN_PAL * 8
	call Fw_PutOwnPal
	ld hl, FW_wOBPals2 + FW_OWN_PAL * 8
	call Fw_PutOwnPal
	ld a, 1
	ldh [FW_hCGBPalUpdate2], a
	; 画面の 色にも すぐ 書く（VBlank を まって OCPD に 8バイト）
	ldh a, [$ff40]
	bit 7, a
	ret z                             ; 画面が きえて いる
	ld hl, FW_wOBPals2 + FW_OWN_PAL * 8
	di
.vb
	ldh a, [$ff44]
	cp 144
	jr c, .vb
	ld a, $80 | FW_OWN_PAL * 8
	ldh [$ff6a], a
	ld c, 8
.copy
	ld a, [hli]
	ldh [$ff6b], a
	dec c
	jr nz, .copy
	ei
	ret

; フィールドの 色（一覧.csv）と 絵の 番号
Fw_GetLeadField:
	call Fw_Species
	ret c
	cp FW_EGG
	jr z, .egg
	cp FW_UNOWN
	jr z, .unown
	ld e, a
	dec e
	ld d, 0
	ld hl, FollowerPals
	add hl, de
	ld b, [hl]
	call Fw_IsShiny
	ld a, b
	jr z, .shiny
	swap a
.shiny
	and $0f
	ret                               ; carry なし（and）
.egg
	ld de, 251
	ld a, 2                           ; みどり
	and a
	ret
.unown
	call Fw_UnownLetter               ; a = 0〜25
	add LOW(252)
	ld e, a
	ld a, 0
	adc HIGH(252)
	ld d, a
	ld a, 1                           ; あお
	and a
	ret

; 先頭の ポケモンが 色ちがいなら z
Fw_IsShiny:
	call Fw_DVs
	ld a, [hli]
	ld c, a
	ld a, [hl]
	cp $aa
	ret nz
	ld a, c
	and $0f
	cp $0a
	ret nz
	bit 5, c
	jr z, .no
	xor a
	ret
.no
	or 1
	ret

; アンノーンの 文字（a = 0〜25）。pokecrystal の GetUnownLetter と 同じ 計算
Fw_UnownLetter:
	call Fw_DVs
	ld a, [hl]
	and %01100000
	sla a
	ld b, a
	ld a, [hli]
	and %00000110
	swap a
	srl a
	or b
	ld b, a
	ld a, [hl]
	and %01100000
	swap a
	sla a
	or b
	ld b, a
	ld a, [hl]
	and %00000110
	srl a
	or b
	ld c, 0
.div
	cp 10
	jr c, .done
	sub 10
	inc c
	jr .div
.done
	ld a, c
	ret

; de = 絵の 番号 → b = バンク、de = アドレス
Fw_IndexToGfx:
	ld b, FW_GFX_BANK
.bank
	ld a, d
	and a
	jr nz, .sub
	ld a, e
	cp FW_PER_BANK
	jr c, .got
.sub
	ld a, e
	sub FW_PER_BANK
	ld e, a
	jr nc, .nb
	dec d
.nb
	inc b
	jr .bank
.got
	; de = $4000 + e × 384（= e × 256 + e × 128）
	ld l, e
	ld h, 0
	add hl, hl
	add hl, hl
	add hl, hl
	add hl, hl
	add hl, hl
	add hl, hl
	add hl, hl                        ; × 128
	ld a, h
	add e                             ; ＋ e × 256
	add $40
	ld d, a
	ld e, l
	ret

; de = 絵の 番号、a = 色：絵と したじきを VRAM バンク1 に 読む（de は こわさない）
Fw_LoadGfx:
	ld [wFwLoadedPal], a
	ld a, e
	ld [wFwLoaded], a
	ld a, d
	ld [wFwLoaded + 1], a
	push de
	call Fw_IndexToGfx
	push bc
	push de
	ld hl, FW_VT_STAND
	ld c, 12
	push bc
	call F0_CopyVRAM1                 ; de は 12タイル ぶん すすむ
	pop bc
	ld hl, FW_VT_WALK
	call F0_CopyVRAM1
	pop de
	pop bc
	pop hl                            ; hl = 絵の 番号
	push hl
	ld a, h
	and a
	jr z, .mask
	ld a, l
	cp LOW(278)
	jr z, .done                       ; ボール（したじき なし。ボールの 間は 出さない）
.mask
	ld a, b
	add FW_MASK_BANK - FW_GFX_BANK
	ld b, a
	ld hl, FW_VT_MASK
	ld c, 24
	call F0_CopyVRAM1
.done
	pop de
	ret

;---------------------------------------------------------------------
; 人の 絵を 読みこんだ あと（LoadUsedSpritesGFX の さいご）：VRAM バンク1 の 絵を 読みなおす
;   （マップに 入った とき・メニューから もどった とき。ポケギアは VRAM の バンク1 を けす）
;   止まりの 絵を 読まない とき（文の わくを とじた あとの 歩きの 絵 だけ）は 読まない
Fw_SpritesGFX:
	ldh a, [hCGB]
	and a
	ret z
	ld a, [wSpriteFlags]
	bit 7, a                          ; SPRITES_SKIP_STANDING_GFX_F
	ret nz
	ld a, [wPartyCount]
	and a
	ret z
	call Fw_GetLead
	ret c
	jp Fw_LoadGfx

;---------------------------------------------------------------------
; マップを 読む とき（LoadMapObjects を まるごと かえた もの）
Fw_LoadMapObjects:
	; 連れ歩きの オブジェクトは マップの コールバック（MAPCALLBACK_OBJECTS）より 先に 作る。
	; コールバックの スクリプト（29ばんどうろ など の appear・disappear）が スプライトを 並べなおすので、
	; その 前に 作って いないと、つながりを こえた とき 連れ歩きが 1フレーム きえた。
	; （金銀は 連れ歩きが いつも 1番 なので、クリスタルの ように 空きを コールバックの あとで 決めなくて よい）
	call Fw_MapLoad
	call Fw_MakeStruct
	ld a, 2                           ; MAPCALLBACK_OBJECTS
	call FW_RunMapCallback
	fw_farcall 9, FW_LoadObjectMasks
	fw_farcall 2, FW_InitializeVisibleSprites
	call Fw_MakeStruct
	jp Fw_AfterObjects

; 連れ歩きの オブジェクトを 作る（金銀の InitializeVisibleSprites は 2番から なので、1番は ここで 作る）。
;   主人公と 同じ 場所（ドアなど）なら 見えなく して おく（主人公が 1歩 歩くと 出る）
Fw_MakeStruct:
	call Fw_FindSlot
	ret c
	ld a, [bc]
	cp $ff
	ret nz                            ; もう ある
	ld a, 1
	call Fw_UnmaskSetup
	call Fw_FindSlot
	ld a, [bc]
	cp $ff
	ret z                             ; 作れなかった（オブジェクトが いっぱい）
	call FW_GetObjectStruct
	; すぐ 絵を 出す（つながりでは マップを 読んだ あと 何フレームか 人の 動きが 止まり、向きの 絵が 決まらず 見えなかった）
	ld hl, OBJ_DIRECTION
	add hl, bc
	ld a, [hl]
	ld hl, OBJ_FACING
	add hl, bc
	ld [hl], a                        ; 止まりの 絵（下 0・上 4・横 8・$c）
	ld hl, OBJ_MAP_X
	add hl, bc
	ld a, [wPlayerMapX]
	cp [hl]
	ret nz
	inc hl
	ld a, [wPlayerMapY]
	cp [hl]
	ret nz
	ld hl, OBJ_FLAGS1
	add hl, bc
	set 0, [hl]                       ; INVISIBLE_F
	ld hl, OBJ_FACING
	add hl, bc
	ld [hl], $ff                      ; STANDING（主人公と かさなって いる 間は 出さない）
	ret

;---------------------------------------------------------------------
; いま 出すか・連れ歩くか（carry = 連れ歩かない）
Fw_DesiredNow:
Fw_Desired:
	ldh a, [hCGB]
	and a
	jr z, .no                         ; 白黒の ゲームボーイでは 出さない
	ld a, [wPlayerState]
	and a                             ; PLAYER_NORMAL だけ
	jr nz, .no
	call Fw_Index
	jr c, .no
	ld e, a
	ld d, 0
	ld hl, wPartySpecies
	add hl, de
	ld a, [hl]
	cp FW_EGG
	jr z, .yes
	ld a, e
	call Fw_MonAddr.got
	ld de, $22
	add hl, de
	ld a, [hli]
	or [hl]
	jr z, .no
.yes
	and a
	ret
.no
	scf
	ret

; 連れ歩きを 置く 番号（a）。金銀は マップの 人が 2番から（wMap2Object〜）で、1番（wMap1Object）は 使われて いないので いつも 1
;   （クリスタルは 人の 数＋1 で、15人 いる マップでは かくれて いる 人の 番号を 借りて いた）
Fw_FreeSlot:
	ld a, 1
	and a
	ret

; 連れ歩きの マップオブジェクトを さがす（a = 番号、bc = マップオブジェクト。なければ carry）
Fw_FindSlot:
	ld bc, wMapObjects + $10
	ld a, [wMapObjects + $10 + MAPOBJ_SPRITE]
	cp FW_SPRITE
	ld a, 1
	ret z
	scf
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
	; 主人公と 同じ 向きで 立つ（つながりを こえた とき、連れ歩きが 一瞬 正面を 向かない ように）
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
; マップを 読む とき（MAPCALLBACK_OBJECTS の あと）
Fw_MapLoad:
	ld a, $ff
	ld [wObjectFollow_Leader], a
	ld [wObjectFollow_Follower], a
	; 1番は マップを 読んでも 書きかえられないので、前の マップの 連れ歩きを けして おく
	ld [wMapObjects + $10], a         ; オブジェクトに なって いない
	xor a
	ld [wMapObjects + $10 + MAPOBJ_SPRITE], a
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
	fw_farcall 1, FW_IsNPCAtCoord
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
; まいフレーム（HandleMapObjects の あと）
Fw_Update:
	ld a, [wPartyCount]
	and a
	ret z
	call Fw_FastQueue
	call Fw_BallTick
	ret c                             ; ボールの アニメ中
	call Fw_FindSlot
	jp c, Fw_SpawnHere
	ld d, a                           ; d = 番号
	ld a, [wObjectStructs + OBJ_DIR_WALKING]
	inc a
	jr z, .standing
	; 主人公が 歩いて いる 間（まいフレーム 通るので 軽く。連れ歩くか・follow の しなおし などは 止まって いる ときだけ 見る）：
	; 見えなく して いる 連れ歩き（ドアから 出た すぐあと など）を、主人公と はなれたら 出す だけ
	ld a, [bc]
	cp $ff
	ret z
	push de
	call FW_GetObjectStruct
	pop de
	ld hl, OBJ_FLAGS1
	add hl, bc
	bit 0, [hl]
	ret z
	jr .vis
.standing
	push de
	push bc                           ; bc（マップの 人）を まもる
	call Fw_DesiredNow
	pop bc
	pop de
	jr nc, .want
	; 連れ歩かない：出て いれば ボールに もどす（Crystal Crunch と 同じ ボールの アニメ）
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
.vis
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
	ld [hl], $ff                      ; STANDING（この コマから 絵を 出さない）
	jr .noshow
.show
	ld hl, OBJ_FLAGS1
	add hl, bc
	res 0, [hl]
	ld a, [wFwBall]
	cp 3
	jr nz, .noshow
	ld a, 2                           ; ボールから 出る
	push de
	call Fw_BallStart
	pop de
	ret
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
	; follow して いる：止まって いるのに 2マス 以上 はなれて いれば、主人公の 後ろに おきなおす
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
	; 主人公の となり か 同じ 場所 なら そのまま follow、はなれて いれば 主人公の 所に おきなおす
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
	ret nz                            ; 主人公が 歩いて いる 途中は まつ
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
	ret nz                            ; 主人公が 歩いて いる 途中は まつ
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
	call Fw_UnmaskSetup
	pop de
	; ボールに もどって いた あとなら、ボールの 絵で まって、主人公が 1歩 はなれて 見える ように なった ときに ボールから 出る（.show）
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
	fw_farcall 1, FW_StartFollow
	ret

;---------------------------------------------------------------------
; ボールの アニメ（Crystal Crunch の StepFunction_PokeballClosing・Opening）
;   もどる：開いた → 半分 → とじた（4フレームずつ）→ けす。出る：とじた → 半分 → 開いた → ポケモンの 絵。
;   コマは オブジェクトの OBJECT_RANGE に 入れる（F1_StandAction・StepAction が 見る：1 とじた・2 半分・3 開いた）。
; a = 1 もどる・2 出る、d = マップオブジェクトの 番号
Fw_BallStart:
	ld [wFwBall], a
	dec a
	jr nz, .out
	ld a, 1
	ld [wFwHidden], a                 ; 次に 出る ときは ボールから
.out
	ld a, 12
	ld [wFwBallT], a
	jp Fw_BallFrame

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
.wait3
	call Fw_BallFrame                 ; とじた ボール（見えない 間 まつ）
	and a
	ret
.end
	xor a
	ld [wFwBall], a
	and a
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

; Bダッシュ中（B と 十字キー）は、連れ歩きの 歩く 予定（wFollowMovementQueue）の ふつうの 歩き（step $0c〜$0f）を
; はやい 歩き（big_step $10〜$13。自転車・Bダッシュと 同じ 速さ）に する
Fw_FastQueue:
	ld a, [wScriptMode]
	and a
	ret nz                            ; スクリプトの 間（イベントの follow）は さわらない
	ld a, [wObjectFollow_Leader]
	and a
	ret nz                            ; 人が 先頭の follow では さわらない
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
DEF FW_wMenuCursorY    EQU $cf14
DEF FW_wSwitchMonFrom  EQU $d0c7
DEF FW_wSwitchMonTo    EQU $d0c6
DEF FW_wCurPartyMon    EQU $cfff
DEF FW_wPokemonWithdrawDepositParameter EQU $d002
DEF FW_StaticMenuJoypad EQU $1a13
DEF FW_hJoyLast        EQU $ffab
DEF FW_PlaySFX         EQU $3d45
DEF FW_SFX_READ_TEXT_2 EQU $08
DEF FW_WaitBGMap2      EQU $33b8      ; WaitBGMap2（タイルと 色の 番号 両方）

; PartyMenuSelect の call StaticMenuJoypad：SELECT なら えらんで もう一度 まつ
Fw_PartyJoypad:
	call FW_StaticMenuJoypad
	ldh a, [FW_hJoyLast]
	bit 2, a                          ; SELECT
	ret z
	call Fw_PartySelect
	jr Fw_PartyJoypad

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

; 手持ちの 画面に 赤い ★（えらんだ ポケモンの「：Ｌ」の 右上 hlcoord 9, 0 ＋ 2行 × 番号。色ちがいの ★（hlcoord 8, 0）の となり）
;   赤は HP の 赤の パレット（BG 3）の 色2 で かく。★の 絵は タイル $5f に 書く（$5e は 色ちがいの ★）。
DEF FW_MARK_TILE2      EQU $5f
DEF FW_MARK_PAL2       EQU 3
DEF FW_wTilemap0       EQU $c3a0
DEF FW_wAttrmap0       EQU $cccd
Fw_PartyMark::
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
	ld hl, FW_wTilemap0 + 9           ; hlcoord 9, 0
	ld de, FW_wAttrmap0 + 9
	ld b, 0
.slot
	ld a, [wPartyCount]
	cp b
	jr z, .clear
	jr c, .clear
	ld a, b
	cp c
	jr nz, .clear
	ld a, [hl]                        ; 状態異常の 文字（「ねむり」の「む」など）が ある ますには 書かない
	cp $7f
	jr z, .mark
	cp FW_MARK_TILE2
	jr nz, .next
.mark
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

; 手持ちの ならびかえ（_SwitchPartyMons）：えらんだ 番号を いっしょに 入れかえる
Fw_SwapSlots:
	call Fw_Index
	ret c
	ld b, a
	ld a, [FW_wSwitchMonFrom]
	cp b
	jr nz, .to
	ld a, [FW_wSwitchMonTo]
	inc a
	ld [wFwSlot], a
	ret
.to
	ld a, [FW_wSwitchMonTo]
	cp b
	ret nz
	ld a, [FW_wSwitchMonFrom]
	inc a
	ld [wFwSlot], a
	ret

; 手持ちから 1匹 ぬける（RemoveMonFromPartyOrBox。wCurPartyMon）：その ポケモン なら 1匹目に、後ろ なら 1つ 前に
Fw_RemoveSlot:
	ld a, [FW_wPokemonWithdrawDepositParameter]
	and a
	ret nz                            ; ボックスから
	call Fw_Index
	ret c
	ld b, a
	ld a, [FW_wCurPartyMon]
	cp b
	jr z, .first
	ret nc                            ; 後ろの ポケモン
	ld a, b                           ; 1つ 前（0から 数えて b−1 → 1から 数えて b）
	ld [wFwSlot], a
	ret
.first
	ld a, 1
	ld [wFwSlot], a
	ret

; マップに 連れ歩きが いない（はじめての ポケモンを もらった とき など）：空いた 番号に 作る
Fw_SpawnHere:
	ld a, [wObjectStructs + OBJ_DIR_WALKING]
	inc a
	ret nz                            ; 主人公が 歩いて いる 途中は まつ
	call Fw_DesiredNow
	ret c
	ld a, [wScriptMode]
	and a
	ret nz
	call Fw_FreeSlot
	ret c
	push af
	; 絵と 色を 読む（はじめての ポケモンの とき は まだ 読まれて いない）
	call Fw_GetLead
	call Fw_LoadGfx
	call Fw_OwnPalNow
	ld a, [wPlayerMapX]
	ld d, a
	ld a, [wPlayerMapY]
	ld e, a
	pop af
	push af
	call Fw_WriteMapObject
	pop af
	push af
	call Fw_UnmaskSetup
	pop af
	ld c, a
	ld b, 0
	fw_farcall 1, FW_StartFollow
	ret

; つながりで 人の オブジェクトが できた あと（LoadMapObjects の さいご）：その 場で 主人公を follow する。
;   ここで して おかないと、マップを 読んだ あと 最初の フレームで 主人公が 先に 歩きだし、連れ歩きが 1マス 後ろで
;   止まった まま（はなれて 見えた）、止まった ときに おきなおして 一瞬 きえて いた
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
	ret z                             ; オブジェクトに なって いない（かくれて いる など）
	ld b, 0
	ld c, d
	fw_farcall 1, FW_StartFollow
	; スプライトを 並べなおす（つながりでは マップを 読んで いる 何フレームかの 間 スプライトが 並べなおされず、
	; 前の マップの 人が 消えた ときの 絵の まま で 連れ歩きが 見えなかった）
	jp FW_UpdateSprites2

; 連れ歩きの INVISIBLE を 立てる
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
; もどす（主人公と かさなって いない とき）
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

;---------------------------------------------------------------------
; スプライトを 並べた あと（_UpdateSprites の InitSprites の あと）：
;   パレット7（連れ歩き 専用）の OAM の タイルを VRAM バンク1 の 連れ歩きの 絵（止まり $00〜$0b・歩き $0c〜$17）に かえ、
;   同じ 場所の 後ろに 白い したじき（タイル $18〜$2f、パレット5 の 色1 ＝ 白）を 足す。
;   手持ちの アイコンは 目・顔の 白を 透明で かいて いるので、外と つながって いない 透明の 所（あな）だけ 白く 見せる。
Fw_FixOAM::
	ldh a, [hUsedSpriteIndex]
	and a
	ret z
	cp $a0
	jr c, .search
	; OAM が もう いっぱい（人が 多い 所）：したじきは おけないので OAM の 中は さがさない。
	; 向きの 色だけ 連れ歩きの オブジェクトの 向きで 見る（クリスタルの Fw_Underlay と 同じ）
	call Fw_FindSlot
	ret c
	call Fw_FaceClass
	jp Fw_FaceCheck
.search
	add 3
	ld c, a                           ; おわり ＋ 3（属性の 場所で くらべる）
	ld hl, wShadowOAM + 3
.find
	; 属性で さがす（まいフレーム 通るので 短く）
	ld a, [hl]
	and %00001111
	cp %00001000 | FW_OWN_PAL         ; VRAM バンク1・パレット7（連れ歩き）
	jr z, .found
	ld a, l
	add 4
	ld l, a
	cp c
	jr c, .find
	ret
.found
	; 正面（止まりの 下 $66〜$69・歩きの 下 $e6〜$e9）か 後ろ・横 か で 色を かえる（OAM と 同じ フレームで かわる）
	dec l
	ld a, [hli]
	and $7f
	sub FW_TILE
	push hl
	push bc
	cp 4
	ld a, 0
	adc a
	xor 1                             ; 0 ＝ 正面、1 ＝ 後ろ・横
	call Fw_FaceCheck
	pop bc
	pop hl
	ld a, [wFwBall]
	and a
	ret nz                            ; ボールの 間は したじき なし
	; 連れ歩きの 4枚（つづけて ならぶ）の 後ろに 白い したじきを 足す（パレット5 の 色1 ＝ 白）
	ldh a, [hUsedSpriteIndex]
	ld e, a
	ld d, HIGH(wShadowOAM)
	ld b, 4
.loop
	ld a, e
	cp $a0
	jr nc, .done                      ; OAM が いっぱい
	ld a, [hl]
	and %00001111
	cp %00001000 | FW_OWN_PAL
	jr nz, .done
	dec l
	dec l
	dec l
	ld a, [hli]                       ; Y
	ld [de], a
	inc e
	ld a, [hli]                       ; X
	ld [de], a
	inc e
	ld a, [hli]                       ; タイル（止まり $66〜$71 → $00〜$0b、歩き $e6〜$f1 → $0c〜$17）
	sub FW_TILE
	bit 7, a
	jr z, .st
	sub $80 - 12
.st
	ld [de], a
	inc e
	ld a, [hl]
	and %11100000                     ; 前後・反転 は 同じ
	or %00001000 | FW_MASK_PAL        ; VRAM バンク1・パレット5
	ld [de], a
	inc e
	ld a, l
	add 4
	ld l, a
	cp c
	jr nc, .done
	dec b
	jr nz, .loop
.done
	ld a, e
	ldh [hUsedSpriteIndex], a
	ret

;---------------------------------------------------------------------
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
	; 読みこむ 間は 見えなく する（INVISIBLE を 立てて UpdateSprites で OAM から けしてから 読みこみ、色を かえて から もどす）
	push bc
	push de
	call Fw_SetInvis
	call FW_UpdateSprites2
	pop de
	pop bc
	ld a, c
	call Fw_LoadGfx
	call Fw_OwnPalNow                 ; 固有の 色（7本目）
	call .objpal
	jp Fw_ClearInvis
.objpal
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
	and %11110000
	or e
	or %00001000                      ; VRAM バンク1
	ld [hl], a
	ret

; a ＝ マップオブジェクトの 番号：オブジェクトを 作って（UnmaskCopyMapObjectStruct）絵の タイルと バンクを 入れる（de は こわさない）
Fw_UnmaskSetup:
	push de
	call FW_Unmask
	call Fw_FindSlot
	jr c, .done
	ld a, [bc]
	cp $ff
	jr z, .done
	call FW_GetObjectStruct
	call Fw_SetupStruct
.done
	pop de
	ret

; bc = 連れ歩きの オブジェクト：絵の タイル（$66）と VRAM バンク1 の ビットを 入れる（作った すぐあと）
Fw_SetupStruct:
	ld hl, OBJ_SPRITE_TILE
	add hl, bc
	ld [hl], FW_TILE
	ld hl, OBJ_PALETTE
	add hl, bc
	set 3, [hl]
	ret

INCLUDE "src/follow_talk.inc"
INCLUDE "src/follow_data.inc"
