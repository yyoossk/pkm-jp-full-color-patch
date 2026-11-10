; 連れ歩き（手持ちの ポケモンが 主人公の 後ろを 歩く）… 金 日本版
;
; 金銀連れ歩きキット（クリスタルで 入れた follow_crystal.asm）を 金に 入れた もの。動きは クリスタルと 同じ（説明書 1章）。
; ・ピカチュウ方式は 金に 入って いなかったので、クリスタルと 同じく この 連れ歩きを 直接 入れた（ピカチュウも この しくみで 歩き、
;   話しかけると ピカチュウフルカラーと 同じ 表情の 絵が 出る）。
; ・カラーの ゲームボーイ だけ（白黒では 連れ歩かない。色・下じき・表情の 絵が カラー前提の ため）。
;
; 金と クリスタルの ちがい（説明書 3章）
; ・金銀の 人の 絵の VRAM：wUsedSprites は 12組（0 ＝ 主人公、1〜9 ＝ 歩く 人、10・11 ＝ 止まりの 絵 $78・$7c）。
;   GetUsedSprites が 0〜9 の 組を 順に タイル 0 から 長さ ずつ 置き（歩きの 絵は ＋$80）、$78 を こえる ことは できない。
;   ArrangeUsedSprites は ない。VRAM バンク1 も 使わない。
;   → 人の 絵を 読む 前（LoadUsedSpritesGFX）に 連れ歩き（$e2）を 1つめ（主人公の 次、タイル $0c〜$17・歩き $8c〜$97）に 入れ、
;     $78 に 入らなければ この マップの 人が 使わない 組を けす。あまった 所（12タイル）が あれば 白い 下じきを そこに 置く。
; ・金銀の スタックは WRAM バンク1 に ある（$df03〜）ので WRAM の バンクは 切りかえない。変数は レポートに 書かれる 使われて いない
;   所（wEventFlags の 前の 空き $d740〜$d78f）。色は WRAM0（wOBPals1 $c240・wOBPals2 $c2c0、hCGBPalUpdate $ffe7）。
; ・つなぎ：バンク $05・$01・$14・$03 には 空きが ないので、元の 関数を まるごと 連れ歩きの バンクに うつして
;   （LoadMapObjects・LoadUsedSpritesGFX・GetFollowerNextMovementIndex）、あいた 所に つなぎを 置いた。
;   使われていない StopRTC（$05:$4000、25バイト）も 使う。手持ちの 画面の つなぎは 元の 命令を farcall に おきかえた。
; ・まいフレームの 見張り（Fw_Update）は HandleMapObjects（場所の 名前の 札 mapsign.asm が もう つないで いる）から 呼ぶ。
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
DEF FW_TILE            EQU $0c       ; 連れ歩きの 絵の タイル（主人公の 次）
DEF FW_SPRITE_LIMIT    EQU $78       ; 歩く 人の 絵は ここまで（$78・$7c は 止まりの 絵）

; --- ホーム（金 日本版）
DEF FW_GetObjectStruct EQU $192f
DEF FW_GetMapObject    EQU $171c
DEF FW_Unmask          EQU $17a0     ; UnmaskCopyMapObjectStruct
DEF FW_DeleteObjectStruct EQU $17e9
DEF FW_GetSpriteVTile  EQU $1658
DEF FW_Random          EQU $305e
DEF FW_CallScript      EQU $26f5
DEF FW_UpdateSprites2  EQU $191c
DEF FW_GetSpriteDirection EQU $1951
DEF FW_RunMapCallback  EQU $2711
DEF FW_GetFarByte2     EQU $30e4
DEF FW_CopyBytes       EQU $30d6
DEF FW_FarCopyBytes    EQU $0db6
DEF FW_EventFlagAction EQU $2eeb
DEF FW_StaticMenuJoypad EQU $1a13
DEF FW_PlaceHollowCursor EQU $1a38
; --- バンクつき
DEF FW_StartFollow     EQU $5779     ; バンク1
DEF FW_IsNPCAtCoord    EQU $7b6b     ; バンク1
DEF FW_SetFacingStandAction EQU $44b2 ; バンク1
DEF FW_SetFacingStepAction EQU $44be ; バンク1
DEF FW_SetFacingCurrent EQU $44a7    ; バンク1
DEF FW_GetMovementObject EQU $4fdf   ; バンク1 _GetMovementObject
DEF FW_InitSprites     EQU $58fe     ; バンク1
DEF FW_GetUsedSprites  EQU $4208     ; バンク5
DEF FW_LoadStillSpriteTiles EQU $4237 ; バンク5
DEF FW_LoadMiscTiles   EQU $4260     ; バンク5
DEF FW_GetSprite       EQU $4281     ; バンク5
DEF FW_RefreshSprites  EQU $413f     ; バンク5
DEF FW_RefreshList     EQU $4146     ; バンク5 RefreshSprites.Refresh（並びを 作る）
DEF FW_OverworldSprites EQU $47b0    ; バンク5（6バイトずつ。2 ＝ 長さ（上4ビット）、3 ＝ バンク）
DEF FW_GetMonSprite_Cont EQU $42a5   ; バンク5 GetMonSprite の cp SPRITE_DAY_CARE_MON_2
DEF FW_GetMonSprite_Breed1 EQU $42bf ; バンク5 GetMonSprite.BreedMon1
DEF FW_LoadObjectMasks EQU $4488     ; バンク9
DEF FW_InitializeVisibleSprites EQU $4767 ; バンク2
; --- RAM
DEF wUsedSprites       EQU $d04f     ; 12組
DEF wVariableSprites   EQU $d548
DEF hUsedSpriteIndex   EQU $ffbf
DEF hUsedSpriteTile    EQU $ffc0
DEF wMapObjects        EQU $d438     ; 16 × 16バイト（0 = 主人公）
DEF wCurMapObjectEventCount EQU $d914
DEF wObjectStructs     EQU $d1f0     ; 13 × $28バイト（0 = 主人公）
DEF wPlayerMapX        EQU $d200
DEF wPlayerMapY        EQU $d201
DEF wObjectFollow_Leader   EQU $d1e7
DEF wObjectFollow_Follower EQU $d1e8
DEF wFollowerMovementQueueLength EQU $d1ea
DEF wFollowMovementQueue EQU $d1eb     ; 5バイト
DEF wPlayerState       EQU $d675
DEF wPlayerStepDirection EQU $ce7a
DEF wScriptMode        EQU $d150
DEF hMapEntryMethod    EQU $ffa1
DEF hMapObjectIndex    EQU $ffb1
DEF wPartyCount        EQU $d9e8
DEF wPartySpecies      EQU $d9e9
DEF wPartyMon1         EQU $d9f0
DEF MAPSETUP_CONNECTION EQU $f7
DEF hCGB_              EQU $ffe8
DEF hJoyDown           EQU $ffaa
DEF FW_B_BUTTON        EQU %00000010
DEF FW_D_PAD           EQU %11110000

; 変数（wEventFlags $d7aa の 前の 使われて いない 所。レポートに 書かれる）
DEF wFwSlot            EQU $d780     ; 連れ歩く 手持ちの 番号（0 = 1匹目〔はじめ・前の レポート〕、1〜6、$ff = だれも）
DEF wFwLoaded          EQU $d781     ; 読みこんで いる 絵の 番号（2バイト）
DEF wFwLoadedPal       EQU $d783     ; 読みこんで いる 色（$ff = まだ）
DEF wFwBall            EQU $d784     ; ボールの アニメ（0 なし・1 もどる・2 出る・3 まつ）
DEF wFwBallT           EQU $d785     ; のこり フレーム
DEF wFwHidden          EQU $d786     ; ボールに もどった（次に 出る ときは ボールから）
DEF wFwLoadedFace      EQU $d787     ; 今の 色が 正面用（0）か 後ろ・横用（1）か
DEF wFwMaskTile        EQU $d788     ; 白い 下じきの タイル（0 ＝ なし）
DEF wFwPrevMask        EQU $d789     ; つながりの 前の 下じきの タイル
DEF wFwRet             EQU $d78a     ; farcall の こたえ
; つながりで 絵を 読みなおす 間 だけ（Fw_Remap）
DEF FW_O               EQU $d740     ; 前の 並び 24バイト
DEF FW_USED            EQU $d758     ; 前の 組を 使った 印 12
DEF FW_RES             EQU $d764     ; 新しい 組の タイル 12
DEF FW_PEND            EQU $d770     ; 新しい 組を 読む 印 12
DEF FW_LENI            EQU $d77c
DEF FW_TAIL            EQU $d77d
DEF FW_TMPEND          EQU $d77e
DEF FW_COPYBUF         EQU $c6e8     ; 1タイル（16バイト）を 写す 所（wUnusedMapBuffer）

; 種類の 番号（オブジェクト・マップオブジェクト）
DEF OBJ_MAP_OBJECT_INDEX EQU $01
DEF OBJ_SPRITE_TILE    EQU $02
DEF OBJ_FLAGS1         EQU $04
DEF OBJ_PALETTE        EQU $06
DEF OBJ_DIR_WALKING    EQU $07       ; 歩いて いる 向き（$ff = 止まって いる）
DEF OBJ_DIRECTION      EQU $08       ; 向き（0 下・4 上・8 左・$c 右）
DEF OBJ_ACTION         EQU $0b
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
DEF FW_POKEPALS_BANK   EQU $7b       ; 固有の 色（follow_data.inc。tools/follow_gen.py が 作る）
DEF FW_PokemonPalettes EQU $6000     ; FollowerOwnPals 0 = タマゴ、1〜251 × 8バイト（ふつうの 色1・色2、色ちがいの 色1・色2）
DEF FW_WalkPalettes    EQU $67e0     ; FollowerWalkPals 後ろ・横（歩行グラフィック）用の 色。ならびは 同じ
DEF FW_OWN_PAL         EQU 7         ; PAL_OW_ROCK
DEF FW_SPRITE_ROCK     EQU $59
DEF FW_SPRITE_BOULDER  EQU $5a
DEF FW_wOBPals1        EQU $c240
DEF FW_wOBPals2        EQU $c2c0
DEF FW_hCGBPalUpdate2  EQU $ffe7

MACRO fw_farcall ; bank, addr
	ld a, \1
	ld hl, \2
	rst $08
ENDM

;---------------------------------------------------------------------
; つなぎ（バンク5）
;---------------------------------------------------------------------
; LoadMapObjects（18バイト）を まるごと Fw_LoadMapObjects に（あいた 所は つなぎに 使う）
SECTION "follow loadmapobjects", ROMX[$5560], BANK[$05]
	fw_farcall FW_BANK, Fw_LoadMapObjects
	ret
; LoadUsedSpritesGFX（16バイト）を まるごと Fw_LoadUsedSpritesGFX に
SECTION "follow loadusedspritesgfx", ROMX[$41f8], BANK[$05]
	fw_farcall FW_BANK, Fw_LoadUsedSpritesGFX
	ret
; GetMonSprite の cp SPRITE_DAY_CARE_MON_1 / jr z, .BreedMon1 → $e2 なら 連れ歩きの 絵
SECTION "follow getmonsprite hook", ROMX[$42a1], BANK[$05]
	jp F5_MonSprite
	nop
; バンク5 の GetSprite を 呼ぶ つなぎ（LoadUsedSpritesGFX の あいた 所）：wFwRet ＝ スプライト → de・b・c（c ＝ タイルの 数）
SECTION "follow bank5 getsprite", ROMX[$41ff], BANK[$05]
F5_GetSpriteW:
	ld a, [wFwRet]
	jp FW_GetSprite
; 使われて いない StopRTC（25バイト）
SECTION "follow bank5 stoprtc", ROMX[$4000], BANK[$05]
F5_MonSprite:
	cp FW_SPRITE
	jr z, .fw
	cp $e0                            ; SPRITE_DAY_CARE_MON_1
	jp z, FW_GetMonSprite_Breed1
	jp FW_GetMonSprite_Cont
.fw
	push hl
	fw_farcall FW_BANK, Fw_GetSprite
	pop hl
	ret

; 岩・かいりきの 岩の スプライトの 色を いわ（7）から ちゃ（3）に（7本目を 連れ歩き 専用に する ため）
SECTION "follow rock pal", ROMX[FW_OverworldSprites + (FW_SPRITE_ROCK - 1) * 6 + 5], BANK[$05]
	db 3
SECTION "follow boulder pal", ROMX[FW_OverworldSprites + (FW_SPRITE_BOULDER - 1) * 6 + 5], BANK[$05]
	db 3

;---------------------------------------------------------------------
; つなぎ（バンク1）
;---------------------------------------------------------------------
; GetFollowerNextMovementIndex（67バイト）を まるごと Fw_NextMove に（あいた 所は つなぎに 使う）
SECTION "follow nextmove", ROMX[$5485], BANK[$01]
	fw_farcall FW_BANK, Fw_NextMove
	ld a, [wFwRet]                    ; （farcall の あと a は こわれる ので こたえは wFwRet。フラグは そのまま）
	ret
; 動き：ObjectActionPairPointers（$01:$4460）の STAND（1）・STEP（2）の ふつうの 動きを F1_Action に
;   （連れ歩きの とき だけ 連れ歩きの 動き。ちがえば 元の SetFacingStandAction・SetFacingStepAction）
SECTION "follow action stand", ROMX[$4460 + 1 * 4], BANK[$01]
	dw F1_Action
SECTION "follow action step", ROMX[$4460 + 2 * 4], BANK[$01]
	dw F1_Action
; スプライトを 並べた あと（_UpdateSprites の call InitSprites）に 白い 下じき
SECTION "follow updatesprites hook", ROMX[$58a6], BANK[$01]
	call F1_InitSprites
SECTION "follow bank1", ROMX[$548f], BANK[$01]
F1_Action:
	; 連れ歩き でなければ 元の 動き（ほかの 人は バンクを かえない。まいフレーム 人の 数 だけ 呼ばれる）
	ld a, [bc]
	cp FW_SPRITE
	jr z, .fw
	ld hl, OBJ_ACTION
	add hl, bc
	ld a, [hl]
	cp 2                              ; OBJECT_ACTION_STEP
	jp z, FW_SetFacingStepAction
	jp FW_SetFacingStandAction
.fw
	fw_farcall FW_BANK, Fw_Action
	ret
F1_InitSprites:
	call FW_InitSprites
	fw_farcall FW_BANK, Fw_Underlay
	ret

;---------------------------------------------------------------------
; つなぎ（ほか）
;---------------------------------------------------------------------
; 色：LoadMapPals の OBJ の 色を 写す call CopyBytes（$02:$7623）
SECTION "follow mappals hook", ROMX[$7623], BANK[$02]
	call F2_OBPals
SECTION "follow bank2", ROMX[$7bc0], BANK[$02]
F2_OBPals:
	call FW_CopyBytes
	fw_farcall FW_BANK, Fw_OwnPalToPals1
	ret

; 主人公の ぶつかり（DoPlayerMovement .CheckNPC の farcall IsNPCAtCoord）
SECTION "follow player collision", ROMX[$435a], BANK[$04]
	ld a, FW_BANK
	ld hl, Fw_IsNPCAtCoord

; 話しかけ：TryObjectEvent の 種類の 表（ObjectEventTypeArray $25:$6921）の OBJECTTYPE_3（.three $6963、xor a / ret ×4）
SECTION "follow talk hook", ROMX[$6963], BANK[$25]
	ld a, FW_BANK
	ld hl, FollowerTalkScript
	jp FW_CallScript
SECTION "follow talk table", ROMX[$6921 + 3 * 4 + 1], BANK[$25]
	dw $6970                          ; OBJECTTYPE_4 → xor a / ret
	db 5
	dw $6970
	db 6
	dw $6970

; 連れ歩く ポケモンを えらぶ（Crystal Crunch と 同じ）：手持ちの 画面で SELECT
;   InitPartyMenuWithCancel の wMenuJoypadFilter を A・B → A・B・SELECT に、
;   PartyMenuSelect（$14:$43c0）の call StaticMenuJoypad / call PlaceHollowCursor を、SELECT なら えらんで もう一度 まつ ものに。
SECTION "follow party filter", ROMX[$4390 + 1], BANK[$14]
	db %0111                          ; PAD_A | PAD_B | PAD_SELECT
SECTION "follow party select hook", ROMX[$43c0], BANK[$14]
	fw_farcall FW_BANK, Fw_MenuJoypad
; 手持ちの ならびかえ（_SwitchPartyMons $14:$561a の ld a, [wSwitchMon] / dec a / ld [wSwitchMonFrom], a / ld b, a）
SECTION "follow party swap hook", ROMX[$561a], BANK[$14]
	fw_farcall FW_BANK, Fw_SwitchPre  ; c ＝ wSwitchMonFrom（farcall の あと a ＝ c）
	ld b, a
	nop
; 手持ちから ぬける とき（RemoveMonFromPartyOrBox $03:$62e2 の ld hl, wPartyCount / ld a, [wPokemonWithdrawDepositParameter]）
SECTION "follow remove hook", ROMX[$62e2], BANK[$03]
	fw_farcall FW_BANK, Fw_RemovePre  ; hl ＝ wPartyCount、c ＝ wPokemonWithdrawDepositParameter（a ＝ c）

;---------------------------------------------------------------------
SECTION "follow main", ROMX[$4000], BANK[FW_BANK]

; カラーの ゲームボーイで なければ carry
Fw_NoCGB:
	ldh a, [hCGB_]
	and a
	ret nz
	scf
	ret

; LoadMapObjects（元の 処理 ＋ 連れ歩き）
Fw_LoadMapObjects:
	ld a, 2                           ; MAPCALLBACK_OBJECTS（先に。人を 出す・けす の あとで 空きを 決める）
	call FW_RunMapCallback
	call Fw_MapLoad
	fw_farcall $09, FW_LoadObjectMasks
	fw_farcall $02, FW_InitializeVisibleSprites
	jp Fw_AfterObjects

; LoadUsedSpritesGFX（元の 処理 ＋ 連れ歩きを 並びに 入れる・白い 下じき）
Fw_LoadUsedSpritesGFX:
	ld a, 4                           ; MAPCALLBACK_SPRITES
	call FW_RunMapCallback
	call Fw_Prepare
	fw_farcall $05, FW_GetUsedSprites
	ret c
	fw_farcall $05, FW_LoadStillSpriteTiles
	fw_farcall $05, FW_LoadMiscTiles
	jp Fw_ReloadMask

; GetFollowerNextMovementIndex（元の 処理）：follow の 次の 動き。ふつうの 歩き（step $0c〜$0f）・はやい 歩き
; （big_step $10〜$13）は、いまの 主人公の 速さ（Bダッシュ中か）に あわせて から わたす（1歩 おくれで たどるので、
; 記録した ときの 速さの ままだと、ダッシュの はじめは 1マス おくれて はなれ、ダッシュを やめた あとは 追いついて かさなって いた）。
; farcall の あとは a が こわれる ので、こたえは wFwRet に 入れる（つなぎが 読む。bc は こわさない）
Fw_NextMove:
	call .orig
	ld [wFwRet], a
	ret
.orig
	ld hl, wFollowerMovementQueueLength
	ld a, [hl]
	and a
	jr z, .done
	cp -1
	jr z, .done
	dec [hl]
	ld e, a
	ld d, 0
	ld hl, wFollowMovementQueue
	add hl, de
	inc e
	ld a, -1
.loop
	ld d, [hl]
	ld [hld], a
	ld a, d
	dec e
	jr nz, .loop
	; 連れ歩き の ときは 速さを あわせる
	call Fw_IsFollowerBC
	ret nz
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
	jr z, .walk
	ld a, e
	add $10
	ret
.walk
	ld a, e
	add $0c
	ret
.done
	call .cancel
	ret c
	ld a, $3e                         ; movement_step_sleep
	ret
.cancel
	ld a, [wObjectFollow_Leader]
	cp -1
	jr z, .nope
	push bc
	call FW_GetObjectStruct
	ld a, [bc]                        ; OBJECT_SPRITE
	pop bc
	and a
	jr z, .nope
	and a                             ; nc
	ret
.nope
	ld a, -1
	ld [wObjectFollow_Follower], a
	ld a, $47                         ; movement_step_end
	scf
	ret

; bc ＝ オブジェクト：連れ歩き（スプライト $e2）なら z（a は こわさない）
Fw_IsFollowerBC:
	push de
	ld d, a
	ld a, [bc]
	cp FW_SPRITE
	ld a, d
	pop de
	ret

; F1_Action（ObjectActionPairPointers の STAND・STEP）：bc ＝ オブジェクト
Fw_Action:
	ld a, [bc]
	cp FW_SPRITE
	jr z, .fw
	ld hl, OBJ_ACTION
	add hl, bc
	ld a, [hl]
	cp 2                              ; OBJECT_ACTION_STEP
	jr z, .step
	fw_farcall $01, FW_SetFacingStandAction
	ret
.step
	fw_farcall $01, FW_SetFacingStepAction
	ret
.fw
	ld hl, OBJ_ACTION
	add hl, bc
	ld a, [hl]
	cp 2
	jr z, Fw_StepAction
	; fallthrough
; 動き（Crystal Crunch の SetFacingFollowerStep・Run・Idle）
;   歩く：絵の 2コマ（止まり・歩き）だけを かわるがわる。止まりの コマで 1ドット 上げて はねて 歩く。Bダッシュ中は はやく かえる。
;   止まって いる：16フレームごとに 2コマを かえる（手持ちの 画面の アイコンと 同じ）。スクリプト中は 止まりの コマ。
Fw_StandAction:
	call Fw_BallFace
	ret c
	ld hl, OBJ_SPRITE_Y_OFFSET
	add hl, bc
	ld [hl], 0
	ld a, [wScriptMode]
	and a
	ld a, 0
	jr nz, Fw_Facing
	ld hl, OBJ_STEP_FRAME
	add hl, bc
	inc [hl]
	ld a, [hl]
	swap a
	and 1
	jr Fw_Facing
Fw_StepAction:
	call Fw_BallFace
	ret c
	ld hl, OBJ_FLAGS1
	add hl, bc
	bit 3, [hl]                       ; SLIDING_F
	jr z, .notslide
	fw_farcall $01, FW_SetFacingCurrent
	ret
.notslide
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
Fw_Facing:
	ld d, a
	call FW_GetSpriteDirection
	or d
	ld hl, OBJ_FACING
	add hl, bc
	ld [hl], a
	ret
; ボールの アニメ中（OBJECT_RANGE ≠ 0）：1 とじた ＝ 横（$08）、2 半分 ＝ 上（$04）、3 開いた ＝ 下（$00）。carry
Fw_BallFace:
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

; 手持ちの 画面：StaticMenuJoypad（SELECT なら 連れ歩く ポケモンを えらんで もう一度）・PlaceHollowCursor
Fw_MenuJoypad:
	call FW_StaticMenuJoypad
	ldh a, [$ffab]                    ; hJoyLast
	bit 2, a                          ; SELECT
	jr z, .done
	call Fw_PartySelect
	jr Fw_MenuJoypad
.done
	jp FW_PlaceHollowCursor

; _SwitchPartyMons の はじめ：c ＝ wSwitchMonFrom（元の 処理）、連れ歩く 番号も いっしょに 入れかえる
DEF FW_wSwitchMon      EQU $cfcd
DEF FW_wSwitchMonFrom  EQU $d0c7
DEF FW_wSwitchMonTo    EQU $d0c6
DEF FW_wMenuCursorY    EQU $cf14
Fw_SwitchPre:
	ld a, [FW_wSwitchMon]
	dec a
	ld [FW_wSwitchMonFrom], a
	push af
	ld b, a                           ; から
	ld a, [FW_wMenuCursorY]
	dec a                             ; へ
	cp b
	jr z, .done
	ld d, a
	call Fw_Index
	jr c, .done
	cp b
	jr nz, .to
	ld a, d
	inc a
	ld [wFwSlot], a
	jr .done
.to
	cp d
	jr nz, .done
	ld a, b
	inc a
	ld [wFwSlot], a
.done
	pop af
	ld c, a
	ret

; RemoveMonFromPartyOrBox の はじめ：hl ＝ wPartyCount、c ＝ wPokemonWithdrawDepositParameter（元の 処理）。
; 手持ちから 1匹 ぬける（wCurPartyMon）とき：その ポケモン なら 1匹目に、後ろ なら 1つ 前に
DEF FW_wCurPartyMon    EQU $cfff
DEF FW_wPokemonWithdrawDepositParameter EQU $d002
Fw_RemovePre:
	ld a, [FW_wPokemonWithdrawDepositParameter]
	and a
	jr nz, .done                      ; ボックスから
	call Fw_Index
	jr c, .done
	ld b, a
	ld a, [FW_wCurPartyMon]
	cp b
	jr z, .first
	jr nc, .done                      ; 後ろの ポケモン
	ld a, b                           ; 1つ 前（0から 数えて b−1 → 1から 数えて b）
	ld [wFwSlot], a
	jr .done
.first
	ld a, 1
	ld [wFwSlot], a
.done
	ld a, [FW_wPokemonWithdrawDepositParameter]
	ld c, a
	ld hl, wPartyCount
	ret

; 連れ歩く ポケモン（Crystal Crunch と 同じく 手持ちで SELECT を おして えらぶ）
;   wFwSlot：0 = 1匹目（はじめ・前の レポート）、1〜6 = その 番目、$ff = だれも 連れ歩かない
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

; 先頭の ポケモンの 絵の 番号（de）と 色（a = 7、色ちがいなら $0f）。手持ちが いなければ carry
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
	call Fw_GetLeadGfx
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
	; follow して いれば その オブジェクト（はやい）
	ld a, [wObjectFollow_Follower]
	cp $ff
	jr z, .find
	call FW_GetObjectStruct
	ld a, [bc]
	cp FW_SPRITE
	jr z, .obj
.find
	call Fw_FindSlot
	jr c, .zero
	ld a, [bc]
	cp $ff
	jr z, .zero
	call FW_GetObjectStruct
.obj
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

; スプライトを 並べる たび：向きが 正面 ⇔ 後ろ・横 で かわったら 色を 書きなおす
;   色は すぐ 書かず、次の VBlank で 新しい 向きの 絵（OAM）と いっしょに かわる ように する（hCGBPalUpdate）
Fw_FaceCheck:
	ld a, [wFwBall]
	and a
	ret nz                            ; ボールの 間は ボールの 色
	ld a, [wFwLoadedFace]
	ld d, a
	call Fw_FaceClass
	cp d
	ret z
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
	; 画面の 色にも すぐ 書く（hCGBPalUpdate は ほかの 転送が ある と おくれて、前の 色の まま 新しい 絵が 見えた）。
	; VBlank を まって OCPD に 8バイト
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

; 絵の 番号（de）。手持ちが いなければ carry
Fw_GetLeadGfx:
	call Fw_Species
	ret c
	cp FW_EGG
	jr z, .egg
	cp FW_UNOWN
	jr z, .unown
	ld e, a
	dec e
	ld d, 0
	and a
	ret
.egg
	ld de, 251
	and a
	ret
.unown
	call Fw_UnownLetter               ; a = 0〜25
	add LOW(252)
	ld e, a
	ld a, 0
	adc HIGH(252)
	ld d, a
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

; GetMonSprite から（a = FW_SPRITE）：de = 絵、b = バンク、c = 12、carry
Fw_GetSprite:
	call Fw_GetLead
	jr nc, .ok
	ld de, 24                         ; 手持ちが いない とき（ここには 来ない）：ピカチュウ
	xor a
.ok
	ld c, a
	ld a, e
	ld [wFwLoaded], a
	ld a, d
	ld [wFwLoaded + 1], a
	ld a, c
	ld [wFwLoadedPal], a
	call Fw_IndexToGfx
	ld c, 12
	scf
	ret

INCLUDE "src/follow_gold_vram.inc"
INCLUDE "src/follow_gold_update.inc"
INCLUDE "src/follow_talk.inc"
INCLUDE "src/follow_data.inc"
