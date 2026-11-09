; 連れ歩き（手持ちの 先頭の ポケモンが 主人公の 後ろを 歩く）… クリスタル（日本版）
;
; ・先頭の ポケモン（ひんしでない とき。タマゴも 歩く）が 主人公の 後ろを ついて 歩く。
;   じてんしゃ・なみのり などの ときと、先頭が ひんしの ときは かくれる（ボールの 中で まつ）。
; ・絵は 連れ歩きキットの 歩行グラフィック（向きごとの 止まり・歩きの 6コマ、24タイル）。バンク $60〜$66 に 置いた（follow_data.inc）。
; ・色は ポケモン 固有の 色（手持ちの アイコンと 同じ 2色。色ちがいは 色ちがいの 2色）。フィールドの スプライトの パレット 8本の うち
;   いわ（PAL_OW_ROCK = 7。いわくだき・かいりきの 岩 だけが 使う）を 連れ歩き 専用に して、岩は ちゃ（3）の 色に した
;   （どこでも 同じ 色）。色の ならびは tools/follow_gen.py で 決める（アイコンの 色を、元の キットの フィールド色に 近い 方が
;   歩行グラフィックの 色2 に なる ように）。
;   LoadMapPals（$02:$71de）が OBJ の 色を wOBPals1 に 写した あと（$02:$7203）に、7本目を ポケモンの 色に する。
;   夜も ほかの 人と 同じく 色は かえない（クリスタルの 人の 色は 夜も 同じ）。
; ・話しかけると 鳴いて、気持ちの アイコンを 出して、場所・タイプ・状態で かわる 会話（follow_talk.inc）。
;
; しくみ（元の ゲームの「follow」の しくみを 使う）
; ・マップを 読む とき（LoadMapObjects $05:$5573 の さいしょ）に、マップの 人の 数＋1 の 番号の マップオブジェクトを
;   連れ歩き用に 作る（スプライト $e2・種類 OBJECTTYPE_3）。ドアなどでは 主人公と 同じ 場所、つながりでは 主人公の 後ろ。
; ・まいフレーム（HandleMap の HandleMapObjects の あと $25:$6788）Fw_Update が、主人公を 先頭に した follow
;   （StartFollow $01:$5803。主人公の 1歩ずつを 1歩 おくれで たどる）を して いるか 見て、して いなければ しなおす。
;   イベントの follow で とられた あとも、スクリプトが おわれば もどる。かくす ときは DeleteObjectStruct、出す ときは
;   主人公の 場所に おいて UnmaskCopyMapObjectStruct。
; ・スプライト $e2 は GetMonSprite（$05:$424a）で 先頭の ポケモンの 絵に する（WALKING_SPRITE・12タイル ×2）。
;   絵を 置く VRAM は、ArrangeUsedSprites の 前（$05:$42d2）に 並べかえて、主人公の 次（タイル 12〜23、歩きの 絵は ＋$80）に する。
;   そのあと、この マップの 人が 使う スプライトを 前に よせる（使わない スプライトを 後ろの 表（歩けない 所）に まわす）。
; ・主人公が 歩く ときの ぶつかり（DoPlayerMovement .CheckNPC の farcall IsNPCAtCoord $20:$435a）では 連れ歩きを 見ない
;   （ふりかえって 歩くと 入れかわる）。
; ・話しかけ：TryObjectEvent の 種類の 表の OBJECTTYPE_3（$25:$6a30、元は xor a / ret）を 連れ歩きの スクリプトに。
;   4〜6（どれも xor a / ret）は $25:$69ec の xor a / ret に。
; ・先頭が かわったら（ならびかえ・あずける・タマゴが かえる など）、その 場で 絵（GetUsedSprite）と 色を 読みなおす。
; ・マップの 人が 15人 いる マップ（コガネシティ）では、いま かくれて いる 人（イベントフラグが 立って いる）の 番号を 借りる。
;   そのため マップの OBJECTS の コールバック（人を 出す・けす）を 先に して から 連れ歩きを 書く。
; ・Bダッシュ（B を おしながら 歩く）の 間も、主人公と はなれず いっしょに 走る。
;
; 連れ歩きの コード・会話の もとは fellowship-of-the-roms/pokecrystal の follow-mons（Vulcandth・AtmaBuster）、
; 歩行グラフィックも 同じ ブランチの もの。組み込みの 記録は Crystal Crunch（joseph-bayer / gomojoeb）。

INCLUDE "src/charmap_jp.inc"

DEF FW_BANK            EQU $79
DEF FW_SPRITE          EQU $e2       ; 使われていない スプライトの 番号（GetMonSprite の $e0・$e1 の 次）
DEF FW_GFX_BANK        EQU $60
DEF FW_PER_BANK        EQU 42
DEF FW_TYPE            EQU 3         ; OBJECTTYPE_3
DEF FW_MOVEMENT        EQU $06       ; SPRITEMOVEDATA_STANDING_DOWN
DEF FW_EGG             EQU $fd
DEF FW_UNOWN           EQU 201

; --- ホーム
DEF FW_GetObjectStruct EQU $1ab0
DEF FW_GetMapObject    EQU $189d
DEF FW_Unmask          EQU $1921     ; UnmaskCopyMapObjectStruct
DEF FW_DeleteObjectStruct EQU $196a
DEF FW_GetSpriteVTile  EQU $17d9
DEF FW_Random          EQU $2f5e
DEF FW_CallScript      EQU $25e2
DEF FW_UpdateSprites2  EQU $1a9d
; --- バンクつき
DEF FW_StartFollow     EQU $5803     ; バンク1
DEF FW_IsNPCAtCoord    EQU $79d7     ; バンク1
DEF FW_GetUsedSprite   EQU $43b9     ; バンク5
DEF FW_RefreshSprites  EQU $4159     ; バンク5
DEF FW_ArrangeUsedSprites EQU $4346  ; バンク5
DEF FW_RunMapCallback  EQU $25fe
; --- RAM
DEF wUsedSprites       EQU $d185
DEF wSpriteFlags       EQU $d0fe
DEF hUsedSpriteIndex   EQU $ffbd
DEF hUsedSpriteTile    EQU $ffbe
DEF wMapObjects        EQU $d711     ; 16 × 16バイト（0 = 主人公）
DEF wCurMapObjectEventCount EQU $dbca
DEF wObjectStructs     EQU $d4c9     ; 13 × $28バイト（0 = 主人公）
DEF wPlayerMapX        EQU $d4d9
DEF wPlayerMapY        EQU $d4da
DEF wObjectFollow_Leader   EQU $d4c0
DEF wObjectFollow_Follower EQU $d4c1
DEF wFollowMovementQueue EQU $d4c4     ; 5バイト（$d4c3 は 長さ）
DEF wPlayerState       EQU $d950
DEF wPlayerStepDirection EQU $d121
DEF wScriptMode        EQU $d428
DEF hMapEntryMethod    EQU $ff9f
DEF hMapObjectIndex    EQU $ffaf
DEF wPartyCount        EQU $dc9d
DEF wPartySpecies      EQU $dc9e
DEF wPartyMon1         EQU $dca5
DEF wPartyMon1DVs      EQU wPartyMon1 + $15
DEF wPartyMon1Status   EQU wPartyMon1 + $20
DEF wPartyMon1HP       EQU wPartyMon1 + $22
DEF MAPSETUP_CONNECTION EQU $f7
; WRAM バンク2（$dfb0 は 手持ちの見た目、$dfc0〜 は ほかの 機能）
DEF FW_VARS_WRAMBANK   EQU 2
DEF wFwLoaded          EQU $dfb8     ; 読みこんで いる 絵の 番号（2バイト）
DEF wFwSlot           EQU $d833     ; 連れ歩く 手持ちの 番号（レポートに 書かれる。wPILast $d832 の 次の 使われて いない 1バイト）
DEF wFwLoadedPal       EQU $dfba     ; 読みこんで いる 色（$ff = まだ）
DEF wFwBall            EQU $dfbb     ; ボールの アニメ（0 なし・1 もどる・2 出る）
DEF wFwBallT           EQU $dfbc     ; のこり フレーム
DEF wFwHidden          EQU $dfbd     ; ボールに もどった（次に 出る ときは ボールから）
DEF wFwLoadedFace      EQU $dfbe     ; 今の 色が 正面用（0）か 後ろ・横用（1）か
DEF wFwMaskOK          EQU $dfbf     ; したじきの VRAM（バンク0 タイル $64〜$7b）を あけられた か

; 種類の 番号（オブジェクト・マップオブジェクト）
DEF OBJ_MAP_OBJECT_INDEX EQU $01
DEF OBJ_FLAGS1         EQU $04
DEF OBJ_PALETTE        EQU $06
DEF OBJ_DIR_WALKING    EQU $07       ; 歩いて いる 向き（$ff = 止まって いる）
DEF OBJ_STEP_FRAME     EQU $0c
DEF OBJ_FACING         EQU $0d
DEF OBJ_SPRITE_Y_OFFSET EQU $1a
DEF OBJ_RANGE          EQU $20       ; 連れ歩きでは ボールの コマ（0 = ポケモン）
DEF OBJ_MAP_X          EQU $10
DEF OBJ_MAP_Y          EQU $11
DEF OBJ_SPRITE_X       EQU $17
DEF OBJ_SPRITE_Y       EQU $18
DEF MAPOBJ_SPRITE      EQU $01
DEF MAPOBJ_Y           EQU $02
DEF MAPOBJ_X           EQU $03
DEF MAPOBJ_COLOR_TYPE  EQU $08
DEF MAPOBJ_EVENT_FLAG  EQU $0c
; ポケモン 固有の 色
DEF FW_wTimeOfDayPal  EQU $d834
DEF FW_POKEPALS_BANK   EQU $7b       ; 固有の 色（follow_data.inc。tools/follow_gen.py が 作る）
DEF FW_PokemonPalettes EQU $6000     ; FollowerOwnPals 0 = タマゴ、1〜251 × 8バイト（ふつうの 色1・色2、色ちがいの 色1・色2）
DEF FW_WalkPalettes    EQU $67e0     ; FollowerWalkPals 後ろ・横（歩行グラフィック）用の 色。ならびは 同じ
DEF FW_GetFarByte2     EQU $3019
DEF FW_FarCopyWRAM     EQU $3037
DEF FW_OWN_PAL         EQU 7         ; PAL_OW_ROCK
DEF FW_SPRITE_ROCK     EQU $59
DEF FW_SPRITE_BOULDER  EQU $5a
DEF FW_wOBPals1        EQU $d040     ; WRAM バンク5
DEF FW_wOBPals2        EQU $d0c0
DEF FW_hCGBPalUpdate2  EQU $ffe5
DEF FW_EventFlagAction EQU $2e41
DEF hJoyDown           EQU $ffa8
DEF FW_B_BUTTON        EQU %00000010
DEF FW_D_PAD           EQU %11110000

MACRO fw_farcall ; bank, addr
	ld a, \1
	ld hl, \2
	rst $08
ENDM

;---------------------------------------------------------------------
; つなぎ
;---------------------------------------------------------------------
SECTION "follow getmonsprite hook", ROMX[$424e], BANK[$05]
	jp F5_GetMonSprite                ; 元は cp $e0 / jr z, .BreedMon1
SECTION "follow arrange hook", ROMX[$42d2], BANK[$05]
	call F5_Prepare                   ; 元は call ArrangeUsedSprites
SECTION "follow loadusedspritesgfx hook", ROMX[$4202], BANK[$05]
	call F5_Misc                      ; 元は call LoadMiscTiles（LoadUsedSpritesGFX の さいご）
SECTION "follow loadmapobjects hook", ROMX[$5573], BANK[$05]
	call F5_LoadObjects               ; 元は ld a, MAPCALLBACK_OBJECTS / call RunMapCallback
	nop
	nop

SECTION "follow bank5", ROMX[$7e00], BANK[$05]
F5_GetMonSprite:
	cp $e0
	jp z, $426a
	cp FW_SPRITE
	jp nz, $4252
	fw_farcall FW_BANK, Fw_GetSprite
	ret                               ; carry・de・bc・hl は Fw_GetSprite の もの
F5_Misc:
	call $4206                        ; LoadMiscTiles
	fw_farcall FW_BANK, Fw_ReloadMask
	ret
F5_Prepare:
	fw_farcall FW_BANK, Fw_Prepare
	jp FW_ArrangeUsedSprites
F5_LoadObjects:
	ld a, 2                           ; MAPCALLBACK_OBJECTS（先に。人を 出す・けす の あとで 空きを 決める）
	call FW_RunMapCallback
	fw_farcall FW_BANK, Fw_MapLoad
	ret

; スプライトを 並べた あと（_UpdateSprites $01:$5920 の call InitSprites $01:$5930）に Fw_Underlay
SECTION "follow updatesprites hook", ROMX[$5930], BANK[$01]
	call F1_InitSprites
SECTION "follow bank1 underlay", ROMX[$7fe8], BANK[$01]
F1_InitSprites:
	call $5991                        ; InitSprites
	fw_farcall FW_BANK, Fw_Underlay
	ret

SECTION "follow handlemap hook", ROMX[$6788], BANK[$25]
	call F25_Objects                  ; 元は call HandleMapObjects
SECTION "follow bank25", ROMX[$7fe0], BANK[$25]
F25_Objects:
	call $67d1                        ; HandleMapObjects
	fw_farcall FW_BANK, Fw_Update
	ret

; 話しかけ：OBJECTTYPE_3
SECTION "follow talk hook", ROMX[$6a30], BANK[$25]
	ld a, FW_BANK
	ld hl, FollowerTalkScript
	jp FW_CallScript
SECTION "follow talk table", ROMX[$69fb], BANK[$25]
	dw $69ec                          ; OBJECTTYPE_4 → xor a / ret
	db 5
	dw $69ec
	db 6
	dw $69ec

; 岩・かいりきの 岩の スプライトの 色を いわ（7）から ちゃ（3）に（7本目を 連れ歩き 専用に する ため）
; OverworldSprites（$05:$4727、6バイトずつ、6バイト目 ＝ パレット）
SECTION "follow rock pal", ROMX[$4727 + (FW_SPRITE_ROCK - 1) * 6 + 5], BANK[$05]
	db 3
SECTION "follow boulder pal", ROMX[$4727 + (FW_SPRITE_BOULDER - 1) * 6 + 5], BANK[$05]
	db 3

; 動き（Crystal Crunch の SetFacingFollowerStep・Run・Idle）：ObjectActionPairPointers（$01:$445f）の
; STAND（1）・STEP（2）を、連れ歩き（スプライト $e2）の とき だけ 連れ歩きの 動きに する。
;   歩く：絵の 2コマ（止まり・歩き）だけを かわるがわる（元の 4コマ目は 歩きの 左右反転で、アイコンが 歩く たびに 裏返った）。
;         止まりの コマで 1ドット 上げて はねて 歩く。Bダッシュ中は はやく かえる。
;   止まって いる：16フレームごとに 2コマを かえる（手持ちの 画面の アイコンと 同じ）。スクリプト中は 止まりの コマ。
SECTION "follow action stand", ROMX[$445f + 1 * 4], BANK[$01]
	dw F1_StandAction
SECTION "follow action step", ROMX[$445f + 2 * 4], BANK[$01]
	dw F1_StepAction
; follow の 次の 動き（MovementFunction_Follow の ld hl, GetFollowerNextMovementIndex $01:$48a0）：ふつうの 歩き（step $0c〜$0f）・
; はやい 歩き（big_step $10〜$13）を、いまの 主人公の 速さ（Bダッシュ中か）に あわせて から わたす（1歩 おくれで たどるので、
; 記録した ときの 速さの ままだと、ダッシュの はじめは 1マス おくれて はなれ、ダッシュを やめた あとは 追いついて かさなって いた）
SECTION "follow next move ptr", ROMX[$48a0 + 1], BANK[$01]
	dw F1_NextMove
SECTION "follow bank1", ROMX[$7f40], BANK[$01]
F1_NextMove:
	call $54e6                        ; GetFollowerNextMovementIndex
	ret c
	cp $0c
	ret c
	cp $14
	ret nc
	; ふつうの 歩き（$0c〜$0f）・はやい 歩き（$10〜$13）は、いまの 主人公に あわせる（Bダッシュ中なら はやく、そうで なければ ふつう）
	and 3
	ld e, a
	ldh a, [hJoyDown]
	and FW_B_BUTTON
	jr z, .walk
	ldh a, [hJoyDown]
	and FW_D_PAD
	jr z, .walk
	ld a, e
	add $10
	and a
	ret
.walk
	ld a, e
	add $0c
	and a
	ret
F1_StandAction:
	ld a, [bc]                        ; OBJECT_SPRITE
	cp FW_SPRITE
	jp nz, $44b5                      ; SetFacingStandAction
	call F1_Ball
	ret c
	ld hl, OBJ_SPRITE_Y_OFFSET
	add hl, bc
	ld [hl], 0
	ld a, [wScriptMode]
	and a
	ld a, 0
	jr nz, F1_Facing
	ld hl, OBJ_STEP_FRAME
	add hl, bc
	inc [hl]
	ld a, [hl]
	swap a
	and 1
	jr F1_Facing
F1_StepAction:
	ld a, [bc]
	cp FW_SPRITE
	jp nz, $44c1                      ; SetFacingStepAction
	call F1_Ball
	ret c
	ld hl, OBJ_FLAGS1
	add hl, bc
	bit 3, [hl]                       ; SLIDING_F
	jp nz, $44aa                      ; SetFacingCurrent
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
F1_Facing:
	ld d, a
	call $1ad2                        ; GetSpriteDirection
	or d
	ld hl, OBJ_FACING
	add hl, bc
	ld [hl], a
	ret
; ボールの アニメ中（OBJECT_RANGE ≠ 0）：1 とじた ＝ 横（$08）、2 半分 ＝ 上（$04）、3 開いた ＝ 下（$00）。carry
F1_Ball:
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

; 連れ歩く ポケモンを えらぶ（Crystal Crunch と 同じ）：手持ちの 画面で SELECT。もう えらんで いる ポケモンで SELECT
; なら だれも 連れ歩かない。えらんだ ポケモンには 赤い ★（名前の 左）。
;   InitPartyMenuWithCancel（$14:$43f9）の wMenuJoypadFilter を A・B → A・B・SELECT に、
;   PartyMenuSelect（$14:$444b）の call StaticMenuJoypad を、SELECT なら えらんで もう一度 まつ ものに。
SECTION "follow party filter", ROMX[$441b + 1], BANK[$14]
	db %0111                          ; PAD_A | PAD_B | PAD_SELECT
SECTION "follow party select hook", ROMX[$444b], BANK[$14]
	call F14_MenuJoypad
SECTION "follow party swap hook", ROMX[$4fba], BANK[$14]
	call F14_Swap                     ; 元は call .SwapMonAndMail
SECTION "follow bank14", ROMX[$7b00], BANK[$14]
F14_MenuJoypad:
	call $1b94                        ; StaticMenuJoypad
	ldh a, [$ffa9]                    ; hJoyLast
	bit 2, a                          ; SELECT
	ret z
	fw_farcall FW_BANK, Fw_PartySelect
	jr F14_MenuJoypad
F14_Swap:
	fw_farcall FW_BANK, Fw_SwapSlots
	jp $4ff8                          ; .SwapMonAndMail
; 手持ちから ぬける とき（あずける・にがす・そだてや など ぜんぶ RemoveMonFromPartyOrBox を 通る）
SECTION "follow remove hook", ROMX[$628f], BANK[$03]
	call F3_Remove                    ; 元は ld hl, wPartyCount
SECTION "follow bank3", ROMX[$7fc0], BANK[$03]
F3_Remove:
	push bc
	push de
	fw_farcall FW_BANK, Fw_RemoveSlot
	pop de
	pop bc
	ld hl, wPartyCount
	ret

; 色：LoadMapPals の OBJ の 色を 写す call FarCopyWRAM（$02:$7203）
SECTION "follow mappals hook", ROMX[$7203], BANK[$02]
	call F2_OBPals
SECTION "follow bank2", ROMX[$7f80], BANK[$02]
F2_OBPals:
	call FW_FarCopyWRAM
	fw_farcall FW_BANK, Fw_OwnPalToPals1
	ret

; 主人公の ぶつかり
SECTION "follow player collision", ROMX[$435a], BANK[$20]
	ld a, FW_BANK
	ld hl, Fw_IsNPCAtCoord

;---------------------------------------------------------------------
SECTION "follow main", ROMX[$4000], BANK[FW_BANK]

; bank2 の 変数を さわる 前後
MACRO fw_wram2
	ldh a, [$ff70]
	push af
	ld a, FW_VARS_WRAMBANK
	ldh [$ff70], a
ENDM
MACRO fw_wram_back
	pop af
	ldh [$ff70], a
ENDM

; 連れ歩く ポケモン（Crystal Crunch と 同じく 手持ちで SELECT を おして えらぶ）
;   wFwSlot（$d833。レポートに 書かれる）：0 = 1匹目（はじめ・前の レポート）、1〜6 = その 番目、$ff = だれも 連れ歩かない
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
	fw_wram2
	ld a, [wFwBall]
	ld e, a
	fw_wram_back
	ld a, e
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
	push af
	push de
	call Fw_OwnPalMode
	pop de
	jr c, .field
	pop af
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
.field
	pop af
	and a
	ret

; 固有の 色を 使うか（手持ちが いれば nc。どこでも 使う）
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
	ld hl, $08                        ; OBJECT_DIRECTION（下 0・上 4・左 8・右 12）
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

; まいフレーム：向きが 正面 ⇔ 後ろ・横 で かわったら 色を 書きなおす
Fw_FaceCheck:
	fw_wram2
	ld a, [wFwBall]
	ld e, a
	ld a, [wFwLoadedFace]
	ld d, a
	fw_wram_back
	ld a, e
	and a
	ret nz                            ; ボールの 間は ボールの 色
	call Fw_FaceClass
	cp d
	ret z
	; 色は すぐ 書かず、次の VBlank で 新しい 向きの 絵（OAM）と いっしょに かわる ように する（すぐ 書くと 1コマ 前の 絵が
	; 新しい 色で 見えた：アリゲイツの 後ろ姿が 一瞬 赤い）
	ld e, a
	fw_wram2
	ld a, e
	ld [wFwLoadedFace], a
	fw_wram_back
	call Fw_OwnPalMode
	ret c
	ld hl, FW_wOBPals1 + FW_OWN_PAL * 8
	call Fw_PutOwnPal
	ld hl, FW_wOBPals2 + FW_OWN_PAL * 8
	call Fw_PutOwnPal
	ld a, 1
	ldh [FW_hCGBPalUpdate2], a
	ret

Fw_OwnPalMode:
	ld a, [wPartyCount]
	and a
	scf
	ret z
	and a
	ret

; 先頭の ポケモンの 固有の 2色 → bc・de（色1 = bc、色2 = de）
Fw_OwnColors:
	fw_wram2
	ld a, [wFwBall]
	ld e, a
	fw_wram_back
	ld a, e
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
	push hl
	call Fw_FaceClass                 ; 正面は 手持ちと 同じ 色、後ろ・横は 歩行グラフィックに あう 色
	pop hl
	ld de, FW_PokemonPalettes
	and a
	jr z, .front
	ld de, FW_WalkPalettes
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
	ld a, FW_POKEPALS_BANK
	push hl
	push bc
	push de
	call FW_GetFarByte2
	pop de
	pop bc
	pop hl
	inc hl
	ret

; hl = パレットの はじめ（WRAM バンク5）に 色1・色2・くろ を 書く（色0 は そのまま）
Fw_PutOwnPal:
	push hl
	call Fw_OwnColors
	pop hl
	ldh a, [$ff70]
	push af
	ld a, 5
	ldh [$ff70], a
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
	pop af
	ldh [$ff70], a
	ret

; LoadMapPals の あと：7本目（wOBPals1）を 先頭の ポケモンの 色に
Fw_OwnPalToPals1:
	call Fw_OwnPalMode
	ret c
	ld hl, FW_wOBPals1 + FW_OWN_PAL * 8
	jp Fw_PutOwnPal

; 先頭が かわった とき：7本目（wOBPals1・wOBPals2）を 書いて 画面に
Fw_OwnPalNow:
	call Fw_OwnPalMode
	ret c
	call Fw_FaceClass
	ld e, a
	fw_wram2
	ld a, e
	ld [wFwLoadedFace], a
	fw_wram_back
	ld hl, FW_wOBPals1 + FW_OWN_PAL * 8
	call Fw_PutOwnPal
	ld hl, FW_wOBPals2 + FW_OWN_PAL * 8
	call Fw_PutOwnPal
	ld a, 1
	ldh [FW_hCGBPalUpdate2], a
	; 画面の 色にも すぐ 書く（絵は 読みこみ おわりの VBlank で もう かわって いる。hCGBPalUpdate は ほかの 転送が
	; ある と おくれて、何フレームか 前の 色の まま 新しい 絵が 見えた）。VBlank を まって OCPD に 8バイト
	ldh a, [$ff40]
	bit 7, a
	ret z                             ; 画面が きえて いる
	ldh a, [$ff70]
	push af
	ld a, 5
	ldh [$ff70], a
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
	pop af
	ldh [$ff70], a
	ret

; フィールドの 色（一覧.csv）
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

; GetMonSprite から（a = FW_SPRITE）：de = 絵、b = バンク、c = 12、l = WALKING_SPRITE、h = 0、carry
Fw_GetSprite:
	call Fw_GetLead
	jr nc, .ok
	ld de, 24                         ; 手持ちが いない とき（ここには 来ない）：ピカチュウ
	xor a
.ok
	ld c, a
	fw_wram2
	ld a, e
	ld [wFwLoaded], a
	ld a, d
	ld [wFwLoaded + 1], a
	ld a, c
	ld [wFwLoadedPal], a
	fw_wram_back
	call Fw_LoadMask                  ; 白い したじき（VRAM バンク0 タイル $64〜$7b）
	call Fw_IndexToGfx
	ld c, 12
	ld l, 1                           ; WALKING_SPRITE
	ld h, 0
	scf
	ret

;---------------------------------------------------------------------
; ArrangeUsedSprites の 前：wUsedSprites（スプライト・種類 の 組）を 並べかえる
;   1番め（主人公の 次）を 連れ歩き（$e2。なければ 足す）に、そのあと この マップの 人が 使う 歩く・立つ スプライトを 前に よせる
Fw_Prepare:
	fw_wram2
	xor a
	ld [wFwMaskOK], a
	fw_wram_back
	ld a, [wPartyCount]
	and a
	ret z
	ld hl, wUsedSprites
	ld c, 0
.find
	ld a, [hl]
	and a
	jr z, .append
	cp FW_SPRITE
	jr z, .have
	inc hl
	inc hl
	inc c
	ld a, c
	cp 32
	jr nz, .find
	ret                               ; いっぱい（ない はず）
.append
	ld a, c
	cp 31
	ret nc
	ld [hl], FW_SPRITE
	inc hl
	ld [hl], 1                        ; WALKING_SPRITE
.have
	ld b, 1
	call Fw_MoveEntry                 ; c 番めを b 番めへ
	ld b, 2                           ; 次に 入れる 所
	ld c, 2
.loop
	ld a, c
	cp 32
	jp nc, Fw_FixOverflow
	call Fw_EntryAddr                 ; hl = c 番め
	ld a, [hli]
	and a
	jp z, Fw_FixOverflow
	ld d, a
	ld a, [hl]                        ; 種類
	cp 3                              ; STILL_SPRITE は 4タイル（そのまま）
	jr nc, .next
	ld a, d
	call Fw_IsSpriteOnMap
	jr nc, .next
	push bc
	call Fw_MoveEntry
	pop bc
	inc b
.next
	inc c
	jr .loop

; 連れ歩きを 足した ぶん VRAM に のらない とき（元の ArrangeUsedSprites は のらない 組の タイルを 決めない まま にし、
; GetUsedSprites が 種類の 数を タイルと して 読みこみ、主人公の 絵を こわす）、この マップで 使わない 組を けす
; さらに 正面の 白い したじき用に 2つめの 表の $f0〜$f7（VRAM バンク0 タイル $70〜$77）を あける（使わない 組を けす。
; けせる 組が なく なったら あきらめて wFwMaskOK = 0）
Fw_FixOverflow:
	fw_wram2
	ld a, 1
	ld [wFwMaskOK], a
	fw_wram_back
.again
	ld e, $e5                         ; 2つめの 表は $e4 まで
	call Fw_Overflows
	ret nc
	call Fw_FindRemovable
	jr c, .full
	call Fw_RemoveEntry
	jr .again
.full
	fw_wram2
	xor a
	ld [wFwMaskOK], a
	fw_wram_back
.again2
	ld e, 0
	call Fw_Overflows
	ret nc
	; けせる 組が ない：連れ歩きを けす
	ld c, 1
	jp Fw_RemoveEntry

; ArrangeUsedSprites と 同じ 数え方で、のらなければ carry（e ≠ 0 なら 2つめの 表の おわりが e 以上でも carry）
Fw_Overflows:
	ld hl, wUsedSprites
	ld b, 0
	ld c, 32
.first
	ld a, [hli]
	and a
	ret z
	ld a, [hli]
	call .len
	add b
	cp $80
	jr z, .fok
	jr nc, .second
.fok
	ld b, a
	dec c
	jr nz, .first
	and a
	ret
.second
	ld b, $80
	dec hl
	dec hl
.sloop
	ld a, [hli]
	and a
	ret z
	ld a, [hli]
	call .len
	add b
	ret c
	ld d, a
	ld a, e
	and a
	ld a, d
	jr z, .nolim
	cp e
	jr nc, .ovf
.nolim
	ld b, a
	dec c
	jr nz, .sloop
	and a
	ret
.ovf
	scf
	ret
.len
	cp 3
	ld a, 4
	ret z
	ld a, 12
	ret

; この マップの 人が 使わない 組を 後ろから さがす（c = 番号。なければ carry）
Fw_FindRemovable:
	ld c, 31
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

; c 番めの 組を けして、後ろを 1つ ずつ 前へ
Fw_RemoveEntry:
	call Fw_EntryAddr
	ld d, h
	ld e, l
	inc hl
	inc hl
.loop
	ld a, c
	cp 31
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

; hl = wUsedSprites の c 番め
Fw_EntryAddr:
	ld a, c
	add a
	add LOW(wUsedSprites)
	ld l, a
	ld a, 0
	adc HIGH(wUsedSprites)
	ld h, a
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
	ld a, [hld]                       ; 1つ前の 種類
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

; a = スプライト。この マップの 人（マップオブジェクト 1〜15）が 使って いれば carry
Fw_IsSpriteOnMap:
	ld d, a
	ld hl, wMapObjects + $10 + MAPOBJ_SPRITE
	ld e, 15
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

;---------------------------------------------------------------------
; いま 出すか（carry = 出さない）。Bダッシュの 間も 主人公と いっしょに 走る（かくさない）
Fw_DesiredNow:
	jr Fw_Desired

; 連れ歩くか（carry = 連れ歩かない）
Fw_Desired:
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

; 連れ歩きを 置く 番号（a）。人の 数＋1。15人 いれば、かくれて いる 人の 番号を 借りる（後ろから）。なければ carry
Fw_FreeSlot:
	ld a, [wCurMapObjectEventCount]
	inc a
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
	jr nz, .loop
	scf
	ret

; 連れ歩きの マップオブジェクトを さがす（a = 番号、bc = マップオブジェクト。なければ carry）
Fw_FindSlot:
	ld bc, wMapObjects + $10
	ld a, 1
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
	ld [hl], FW_MOVEMENT
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

;---------------------------------------------------------------------
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
	push de
	push bc                           ; bc（マップの 人）を まもる（Fw_DesiredNow で こわれて、かさなりの チェックが 主人公を 見て いた）
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
	; ふりかえって 主人公と 入れかわる ときは 見えた まま（主人公が 手前に かかれ、連れ歩きは 奥を とおる。ユーザーの 希望）
.notahead
	ld hl, OBJ_MAP_X
	add hl, bc
	ld a, [wPlayerMapX]
	cp [hl]
	jr nz, .show
	inc hl
	ld a, [wPlayerMapY]
	cp [hl]
	jr nz, .show
.hide
	ld hl, OBJ_FLAGS1
	add hl, bc
	set 0, [hl]                       ; INVISIBLE_F
	ld hl, OBJ_FACING
	add hl, bc
	ld [hl], $ff                      ; STANDING（この コマから 絵を 出さない。INVISIBLE だけだと 次の HandleMapObjects まで 出て いた）
	jr .noshow
.show
	ld hl, OBJ_FLAGS1
	add hl, bc
	res 0, [hl]
	fw_wram2
	ld a, [wFwBall]
	ld e, a
	fw_wram_back
	ld a, e
	cp 3
	jr nz, .noshow
	ld a, 2                           ; ボールから 出る
	push de
	call Fw_BallStart
	pop de
	ret
.noshow
	push de
	call Fw_FaceCheck                 ; 正面 ⇔ 後ろ・横 で 色を かえる
	pop de
	ld a, [wScriptMode]
	and a
	ret nz                            ; スクリプトの 間は さわらない
	push de
	call Fw_CheckReload
	pop de
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
	; follow して いる：止まって いるのに 2マス 以上 はなれて いれば（Bダッシュで ふりかえって 主人公と 入れかわった あとなど、
	; 1歩目だけ 歩く 速さに なって 1マス おくれた まま 走って いた）、主人公の 後ろに おきなおす
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
	; 主人公の となり か 同じ 場所 なら そのまま follow、はなれて いれば 主人公の 所に おきなおす
	push de
	ld a, e
	call FW_GetObjectStruct
	pop de
	call Fw_Dist
	cp 2
	jr c, .start
.far
	ld a, d
	push de
	call FW_DeleteObjectStruct
	pop de
	; はなれた とき（Bダッシュで つながりを こえた すぐあと など）は、主人公の 後ろ（歩いた 向きの 反対）に おきなおす
	; （主人公の 場所に おくと、主人公が 走って いる 間 1歩 おくれて 2マス はなれて 見えた）
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
	; ボールに もどって いた（じてんしゃ・なみのり・ひんし など）あとなら、ボールの 絵で まって（主人公と かさなって
	; 見えない 間）、主人公が 1歩 はなれて 見える ように なった ときに ボールから 出る（.show）
	fw_wram2
	ld a, [wFwHidden]
	and a
	jr z, .nohide
	xor a
	ld [wFwHidden], a
	ld a, 3
	ld [wFwBall], a
.nohide
	fw_wram_back
.start
	ld b, 0                           ; 主人公
	ld c, d
	fw_farcall 1, FW_StartFollow
	ret

;---------------------------------------------------------------------
; ボールの アニメ（Crystal Crunch の StepFunction_PokeballClosing・Opening）
;   もどる：開いた → 半分 → とじた（4フレームずつ）→ けす。出る：とじた → 半分 → 開いた → ポケモンの 絵。
;   その 間、連れ歩きの 絵を ボールの 絵（番号 278）・色を あか（PAL_OW_RED の 2色）に して、コマは オブジェクトの
;   OBJECT_RANGE（$20。連れ歩きでは 使わない）に 入れる（F1_StandAction・StepAction が 見る：1 とじた・2 半分・3 開いた）。
; a = 1 もどる・2 出る、d = マップオブジェクトの 番号
Fw_BallStart:
	ld e, a
	fw_wram2
	ld a, e
	ld [wFwBall], a
	ld a, 12
	ld [wFwBallT], a
	ld a, e
	dec a
	jr nz, .out
	ld a, 1
	ld [wFwHidden], a                 ; 次に 出る ときは ボールから
.out
	fw_wram_back
	jp Fw_BallFrame

; まいフレーム：アニメ中なら carry
Fw_BallTick:
	fw_wram2
	ld a, [wFwBall]
	ld e, a
	fw_wram_back
	ld a, e
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
	fw_wram2
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
	ld a, [hl]
	ld e, a
	fw_wram_back
	ld a, e
	and a
	jr z, .done
	call Fw_BallFrame
	scf
	ret
.done
	fw_wram2
	ld a, [wFwBall]
	ld e, a
	xor a
	ld [wFwBall], a
	fw_wram_back
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
	fw_wram_back
	scf
	ret
.wait3
	fw_wram_back
	call Fw_BallFrame                 ; とじた ボール（見えない 間 まつ）
	and a
	ret
.end
	fw_wram2
	xor a
	ld [wFwBall], a
	fw_wram_back
	and a
	ret

; d = マップオブジェクトの 番号：いまの コマを OBJECT_RANGE に
Fw_BallFrame:
	fw_wram2
	ld a, [wFwBallT]
	ld c, a
	ld a, [wFwBall]
	ld b, a
	fw_wram_back
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
; はやい 歩き（big_step $10〜$13。自転車・Bダッシュと 同じ 速さ）に する。ふりかえって 主人公と 入れかわった あとや
; follow を しなおした あとの 1歩目が ふつうの 速さに なって、走って いる 間 1マス おくれて いた
Fw_FastQueue:
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
DEF FW_wMenuCursorY    EQU $cf9d
DEF FW_wSwitchMonFrom  EQU $d21d
DEF FW_wSwitchMonTo    EQU $d21c
DEF FW_wCurPartyMon    EQU $d0c9
DEF FW_wPokemonWithdrawDepositParameter EQU $d0cb
DEF FW_PlaySFX         EQU $3bb0
DEF FW_SFX_READ_TEXT_2 EQU $08
DEF FW_WaitBGMap2      EQU $31cc      ; WaitBGMap2（タイルと 色の 番号 両方）
DEF FW_MARK_PAL        EQU 6
DEF FW_MARK_TILE       EQU $5e        ; 色ちがいの ★の 絵（partyshiny.asm が 手持ちの 画面を かく たびに 読む）
DEF FW_hCGBPalUpdate3  EQU $ffe5

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
;   Crystal Crunch は 名前の 下だが、日本語の 画面は 名前の 上の 行が だくてんの 行で、名前の 左は 道具の 印の 絵と かさなる。
;   赤は HP の 赤の パレット（BG 3）の 色2 で かく（手持ちの 画面が かならず 読む パレット）。★の 絵は タイル $5f に 書く
;   （$5e は 色ちがいの ★。$5f も 戦闘・手持ちの 画面で 使われて いない。町では 手持ちを とじる とき 読みなおす）。
DEF FW_MARK_TILE2      EQU $5f
DEF FW_MARK_PAL2       EQU 3
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
	ld hl, $c4a0 + 9                  ; hlcoord 9, 0
	ld de, $cdcd + 9
	ld b, 0
.slot
	ld a, [wPartyCount]
	cp b
	jr z, .clearall
	jr c, .clearall
	ld a, b
	cp c
	jr nz, .clear
	ld [hl], FW_MARK_TILE2
	ld a, [de]
	and %11111000
	or FW_MARK_PAL2
	ld [de], a
	jr .next
.clearall
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
	ld c, 32
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
	fw_farcall 1, FW_StartFollow
	ret

; スプライトを ぜんぶ 読みなおして、出て いる 人の タイルの 番号も なおす
Fw_RefreshAll:
	fw_farcall 5, FW_RefreshSprites
	ld a, 1
	ldh [hMapObjectIndex], a
	ld bc, wObjectStructs + $28
	ld e, 12
.loop
	ld a, [bc]
	and a
	jr z, .next
	call FW_GetSpriteVTile
	ld hl, 2                          ; OBJECT_SPRITE_TILE
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
;---------------------------------------------------------------------
; 正面の 白い したじき
; 手持ちの アイコンは 目・顔の 白を 透明（色0）で かいて いる（手持ちの 画面は 背景が 白）。スプライトは 透明＋3色 なので、
; 外と つながって いない 透明の 所（あな）だけ 色1 の 絵（tools/follow_gen.py → gfxdata/follow_icon/mask.bin、バンク $67〜$69、
; 1匹 384バイト。正面・後ろ・横 24タイル）を VRAM バンク0 の タイル $64〜$7b（人の 絵の 2つめの 表の $e4〜$fb。$7c〜 は
; ポケモンセンターの 回復の 絵。Fw_FixOverflow で あけて おく。
; あけられない マップ（使う 人の 絵が 多すぎる）では wFwMaskOK = 0 で したじきを 出さない）に 置き、連れ歩きの 絵の 4枚の 後ろに 白（OBJ パレット5 の 色1 ＝ 白。
; 朝・昼・夜・暗い 所 とも 白）で かさねる。あなから だけ 白が 見えて、手持ちの 画面と 同じ 見た目に なる（ユーザーの 希望）。

; de = 絵の 番号（0〜278）。de は こわさない
Fw_LoadMask:
	fw_wram2
	ld a, [wFwMaskOK]
	ld l, a
	fw_wram_back
	ld a, l
	and a
	ret z                             ; VRAM を あけられなかった
	push de
	ld a, d
	and a
	jr z, .ok
	ld a, e
	cp 278 - 256
	jr nc, .done                      ; ボール（したじき なし）
.ok
	call Fw_IndexToGfx                ; 絵と 同じ 数え方（b = $60〜、de = 場所）
	ld a, b
	add $67 - FW_GFX_BANK
	ld b, a
	ld hl, $8640                      ; VRAM バンク0 の タイル $64（2つめの 表の $e4〜$fb）
	ld c, 24
	ldh a, [$ff4f]                    ; rVBK
	push af
	xor a
	ldh [$ff4f], a
	call FW_Get2bpp
	pop af
	ldh [$ff4f], a
.done
	pop de
	ret

; スプライトを 並べた あと：連れ歩きの 絵（止まり タイル $0c〜$17・歩き $8c〜$97、VRAM バンク1、パレット7）の
; 4枚と 同じ 場所に、したじき（タイル $64〜$7b、VRAM バンク0、パレット5）を 後ろに 足す
DEF FW_wStateFlags      EQU $d0ad
DEF FW_hUsedSpriteIndex EQU $ffbd
; 人の 絵を 読みこんだ あと（LoadUsedSpritesGFX の さいご）：したじきを 読みなおす（メニューから もどった とき など）
Fw_ReloadMask::
	ld a, [wPartyCount]
	and a
	ret z
	call Fw_GetLead
	ret c
	jp Fw_LoadMask

Fw_Underlay::
	ld a, [wPartyCount]
	and a
	ret z
	; 向きの 色の 切りかえも ここで 見る（話しかけた とき など スクリプトの 間は Fw_Update が まわらず、こちらを 向いた 正面の 絵が
	; 後ろ・横の 色の まま 出て 一瞬 色が かわって いた）。OAM と 色は 同じ VBlank で かわる
	call Fw_FaceCheck
	fw_wram2
	ld a, [wFwBall]
	ld e, a
	fw_wram_back
	ld a, e
	and a
	ret nz                            ; ボールの 間は なし
	fw_wram2
	ld a, [wFwMaskOK]
	ld e, a
	fw_wram_back
	ld a, e
	and a
	ret z
	ld a, [FW_wStateFlags]
	bit 1, a                          ; LAST_12_SPRITE_OAM_STRUCTS_RESERVED_F
	ld d, $a0
	jr z, .lim
	ld d, $70
.lim
	ldh a, [FW_hUsedSpriteIndex]
	ld c, a                           ; もとの おわり
	ld b, 0
.loop
	ld a, b
	cp c
	ret nc
	ld h, $c4                         ; wShadowOAM
	ld l, b
	inc l
	inc l
	ld a, [hli]                       ; タイル
	ld e, a
	ld a, [hl]                        ; 属性
	and %00001111
	cp %00001000 | 7                  ; VRAM バンク1・パレット7（連れ歩き）
	jr nz, .next
	ld a, e
	and $7f
	sub 12
	cp 12
	jr nc, .next                      ; 連れ歩きの 絵 では ない
	bit 7, e
	jr z, .stand
	add 12
.stand
	add $64
	ld e, a                           ; したじきの タイル
	ldh a, [FW_hUsedSpriteIndex]
	cp d
	ret nc                            ; OAM が いっぱい
	push bc
	push de
	ld h, $c4
	ld l, b
	ld a, [hli]                       ; Y
	ld b, a
	ld a, [hli]                       ; X
	ld c, a
	inc l
	ld a, [hl]
	and %11100000                     ; 前後・反転 は 同じ
	or 5                              ; VRAM バンク0・パレット5
	ld d, a
	ldh a, [FW_hUsedSpriteIndex]
	ld l, a
	ld [hl], b
	inc l
	ld [hl], c
	inc l
	ld [hl], e
	inc l
	ld [hl], d
	inc l
	ld a, l
	ldh [FW_hUsedSpriteIndex], a
	pop de
	pop bc
.next
	ld a, b
	add 4
	ld b, a
	jr .loop

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
	fw_wram2
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
	ld b, a
	fw_wram_back
	ld a, b
	and a
	ret z                             ; 同じ
	; 読みこむ 間は 見えなく する（絵は 何フレームか かけて かわり、色は その あとに なる ので、前の 色の 新しい 絵が
	; 見えた）。INVISIBLE を 立てて UpdateSprites で OAM から けしてから 読みこみ、色を かえて から もどす
	call Fw_SetInvis
	call FW_UpdateSprites2
	call .load
	call Fw_ClearInvis
	ret
.load
	; 絵：wUsedSprites の $e2 の タイルに 読みこむ
	ld hl, wUsedSprites
	ld b, 32
.find
	ld a, [hli]
	cp FW_SPRITE
	jr z, .found
	inc hl
	dec b
	jr nz, .find
	call Fw_RefreshAll
	jr .pal
.found
	ld a, [hl]
	ldh [hUsedSpriteTile], a
	ld a, FW_SPRITE
	ldh [hUsedSpriteIndex], a
	ld hl, wSpriteFlags
	res 5, [hl]                       ; SPRITES_VRAM_BANK_0_F
	fw_farcall 5, FW_GetUsedSprite
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

INCLUDE "src/follow_talk.inc"
INCLUDE "src/follow_data.inc"
