; 戦闘と ずかん の「ボールの印」を、モンスターボールの赤と白にする（ポケットモンスターピカチュウフルカラーと同じ考え方）
;   1. トレーナー戦の 手持ちの数のボール（戦闘の始まり・相手の入れかえのとき、HP の枠の上に並ぶボール）
;   2. 野生のポケモンとの戦闘で、つかまえたことのあるポケモンの名前の左に出る印
;   3. ずかんの一覧で、つかまえたポケモンの左に出る印
; 金 日本版（後期版）の値。銀・クリスタルは 下の「ROM ごとにちがう所」を tools/redballs_find.py で調べた値にする。
;
; 1. 手持ちの数のボール（OBJ。タイル $31 元気・$32 状態異常・$33 ひんし・$34 空き。元は 4つとも 黄色の OBJ パレット）
;    ・元気のボール（$31）の絵を ピカチュウ版の絵（上が赤・下が白・まん中に黒い帯とボタン）にして、
;      パレットを 赤（PAL_BATTLE_OB_RED。白・ピンク・赤・黒）にする。白い所は 色0（すきま）にして、うしろの白を見せる
;      （赤のパレットの 色1 はピンクなので）。
;    ・状態異常・ひんし・空きは 元のまま（黄色。ピカチュウ版も 空きは 黄色のまま）。
;    ・LoadTrainerHudOAM の「ld a, PAL_BATTLE_OB_YELLOW / ld [hli], a」を、タイルを見て パレットを決める処理へ。
; 2. つかまえた印（背景のタイル $5d。ExpBarGFX の 9枚目。元は 黒と白だけ）
;    ・絵を 上が赤・まん中が黒い帯・下が白 にして、戦闘画面で使っていない 背景のパレット5 にボールの色を入れ、
;      印の場所（1, 1）を パレット5 にする（_CGB_FinishBattleScreenLayout のおわり）。
;      （1, 1）は 印がないときは 空白なので、いつもパレット5 でよい。
; 3. ずかんの印（タイル $4f。ずかんの絵 PokedexLZ の中。ずかんのパレット0 = 白・オレンジ・赤・黒、うしろは黒）
;    ・LZ の中では ほかのタイルからもコピーされているので、データは変えずに、展開したあとで VRAM のタイル $4f を書きかえる
;      （ずかんを開くとき＝画面を消している、と オプションなどからもどるとき＝Request2bpp の2か所）。
;    ・絵は 上が赤（ハイライトは白）・黒い帯と白いボタン・下が白。パレットは そのまま。

;---------------------------------------------------------------------
; ROM ごとにちがう所（金 日本版）
;---------------------------------------------------------------------
IF !DEF(RB_HUD_ATTR)
DEF RB_STATUSCOLOR       EQU 1
DEF RB_DEXINFO           EQU 1        ; ずかんの SELECT（src/dexinfo_gold.asm）の つなぎを dex load1 に 置く        ; 状態異常の 色（src/statuscolor_gold.asm）を 入れて いる
DEF RB_BALLGFX_BANK      EQU $0b      ; LoadBallIconGFX の .gfx（手持ちの数のボール 4タイル、そのままの 2bpp）
DEF RB_BALLGFX           EQU $5255
DEF RB_HUD_ATTR          EQU $5236    ; LoadTrainerHudOAM の ld a, PAL_BATTLE_OB_YELLOW / ld [hli], a（3バイト）
DEF RB_HUD_FREE          EQU $7c80    ; 同じバンクの空き（10バイト）
DEF RB_CAUGHT_BANK       EQU $3e      ; ExpBarGFX + 8 タイル（つかまえた印）
DEF RB_CAUGHT_GFX        EQU $4c82
DEF RB_BATTLEPAL_BANK    EQU $02      ; _CGB_FinishBattleScreenLayout の おわり：
DEF RB_BATTLEPAL_HOOK    EQU $5429    ;   ld hl, BattleObjectPals / ld de, wOBPals1 palette 2 / ld bc, 6 palettes / call CopyBytes / call ApplyAttrmap / ret（16バイト）
DEF RB_BattleObjectPals  EQU $5b9f    ; バンク RB_BATTLEPAL_BANK
DEF RB_ApplyAttrmap      EQU $5acb    ; バンク RB_BATTLEPAL_BANK
DEF RB_DEX_BANK          EQU $10
DEF RB_DEX_LOAD1         EQU $44f9    ; ld hl, PokedexLZ / ld de, vTiles2 tile $31 / lb bc, BANK, 49 / call DecompressRequest2bpp / ret（13バイト）
DEF RB_DEX_LOAD2         EQU $5217    ; ld hl, PokedexLZ / ld de, vTiles2 tile $31 / call Decompress（9バイト。画面を消しているとき）
DEF RB_PokedexLZ         EQU $5245
DEF RB_DEX_TILES         EQU 49       ; DecompressRequest2bpp のタイルの数（日本版 金は 49）
DEF RB_wOBPals1          EQU $c240
DEF RB_wBGPals1          EQU $c200
DEF RB_wAttrmap          EQU $cccd
DEF RB_BANK              EQU $3f      ; 新しい処理を置くバンク
DEF RB_ADDR              EQU $6f40
ENDC

; 戦闘の色を WRAM のバンクに置いている版（クリスタル：wBGPals1・wOBPals1 が バンク5）は RB_PALS_WRAMBANK EQU 5、
; _CGB_FinishBattleScreenLayout のおわりの長さ（金銀 16バイト、クリスタル 18バイト：FarCopyWRAM を使うため）は RB_BATTLEPAL_LEN
IF !DEF(RB_PALS_WRAMBANK)
DEF RB_PALS_WRAMBANK     EQU 0
ENDC
IF !DEF(RB_BATTLEPAL_LEN)
DEF RB_BATTLEPAL_LEN     EQU 16
ENDC

; 金・銀 共通（ホーム・定数）
IF !DEF(RB_FarCopyBytes)
DEF RB_FarCopyBytes      EQU $0db6
DEF RB_CopyBytes         EQU $30d6
DEF RB_FarDecompress     EQU $0ad9
DEF RB_DecompressRequest2bpp EQU $0d9c
DEF RB_Request2bpp       EQU $0de7
ENDC
DEF RB_PAL_YELLOW        EQU 3        ; PAL_BATTLE_OB_YELLOW
DEF RB_PAL_RED           EQU 4        ; PAL_BATTLE_OB_RED
DEF RB_BG_PAL            EQU 5        ; PAL_BATTLE_BG_5（戦闘画面で使っていない）
DEF RB_DEX_TILE          EQU $4f
DEF RB_VRAM_DEX_TILE     EQU $9000 + RB_DEX_TILE * 16   ; vTiles2 tile $4f

;---------------------------------------------------------------------
; 1. 手持ちの数のボール
SECTION "redballs hud gfx", ROMX[RB_BALLGFX], BANK[RB_BALLGFX_BANK]
	; 元気のボール（ピカチュウ版の絵。0 = すきま（うしろの白）、2 = 赤、3 = 黒）
	db %00000000, %00000000
	db %00011100, %00011100
	db %00100010, %00111110
	db %01000001, %01101111
	db %01110111, %01110111
	db %01000001, %01000001
	db %00100010, %00100010
	db %00011100, %00011100

SECTION "redballs hud attr", ROMX[RB_HUD_ATTR], BANK[RB_BALLGFX_BANK]
	call RedBalls_HudAttr

SECTION "redballs hud attr body", ROMX[RB_HUD_FREE], BANK[RB_BALLGFX_BANK]
; [de] = タイル → 元気のボール（$31）だけ 赤のパレット
RedBalls_HudAttr:
	ld a, [de]
	cp $31
	ld a, RB_PAL_YELLOW
	jr nz, .got
	ld a, RB_PAL_RED
.got
	ld [hli], a
	ret

;---------------------------------------------------------------------
; 2. つかまえた印の絵（0 = 白、2 = 赤、3 = 黒。パレット5）
SECTION "redballs caught gfx", ROMX[RB_CAUGHT_GFX], BANK[RB_CAUGHT_BANK]
IF DEF(RB_STATUSCOLOR)
	; 黒を 色1 に（色3 は 相手の 状態異常の 色。src/statuscolor_crystal.asm）
	db %00000000, %00000000
	db %01111000, %00000000
	db %10000100, %01011000
	db %10000100, %01111000
	db %11111100, %00000000
	db %10000100, %00000000
	db %01111000, %00000000
	db %00000000, %00000000
ELSE
	db %00000000, %00000000
	db %01111000, %01111000
	db %10000100, %11011100
	db %10000100, %11111100
	db %11111100, %11111100
	db %10000100, %10000100
	db %01111000, %01111000
	db %00000000, %00000000
ENDC

SECTION "redballs battle pal hook", ROMX[RB_BATTLEPAL_HOOK], BANK[RB_BATTLEPAL_BANK]
	ld a, RB_BANK
	ld hl, RedBalls_BattlePals
	rst $08
	jp RB_ApplyAttrmap
	ds RB_BATTLEPAL_LEN - 9, 0   ; のこりは使わない

;---------------------------------------------------------------------
; 3. ずかん
SECTION "redballs dex load1", ROMX[RB_DEX_LOAD1], BANK[RB_DEX_BANK]
IF DEF(RB_DEXINFO)
	; のこりの 6バイトに ずかんの SELECT（src/dexinfo_gold.asm）の farcall を いっしょに 置く（バンク$10 は 空きが ない）
	ld hl, RedBalls_DexLoadRequest
RedBalls_DexFar:
	ld a, RB_BANK
	rst $08
	ret
RedBalls_DexInfoSelect::             ; ＋7：DexInfo_Select の つなぎ（バンク RB_BANK）を farcall
	ld hl, DexInfo_SelectTramp
	jr RedBalls_DexFar
	ds 1, 0
ELSE
	ld a, RB_BANK
	ld hl, RedBalls_DexLoadRequest
	rst $08
	ret
	ds 13 - 7, 0
ENDC

SECTION "redballs dex load2", ROMX[RB_DEX_LOAD2], BANK[RB_DEX_BANK]
	ld a, RB_BANK
	ld hl, RedBalls_DexLoadLCDOff
	rst $08
	nop
	nop
	nop

;---------------------------------------------------------------------
SECTION "redballs main", ROMX[RB_ADDR], BANK[RB_BANK]
; 2. 戦闘画面の色（元の OBJ パレットのコピーのかわり ＋ パレット5 ＋ 印の場所）
RedBalls_BattlePals:
IF RB_PALS_WRAMBANK
	ldh a, [$ff70]               ; rSVBK
	push af
	ld a, RB_PALS_WRAMBANK
	ldh [$ff70], a
ENDC
	ld a, RB_BATTLEPAL_BANK
	ld hl, RB_BattleObjectPals
	ld de, RB_wOBPals1 + 2 * 8   ; palette PAL_BATTLE_OB_GRAY
	ld bc, 6 * 8
	call RB_FarCopyBytes
	ld hl, RedBalls_BallPal
	ld de, RB_wBGPals1 + RB_BG_PAL * 8
	ld bc, 8
	call RB_CopyBytes
IF RB_PALS_WRAMBANK
	pop af
	ldh [$ff70], a
ENDC
	ld a, RB_BG_PAL
	ld [RB_wAttrmap + 1 * 20 + 1], a   ; hlcoord 1, 1
IF DEF(RB_STATUSCOLOR)
	ld a, BANK(StatusColor_BattleLayout)
	ld hl, StatusColor_BattleLayout
	rst $08
ENDC
	ret

RedBalls_BallPal:
IF DEF(RB_STATUSCOLOR)
	dw $7fff, $0000, $109f, $0000   ; 白・黒・赤・（色3 は 相手の 状態異常）
ELSE
	dw $7fff, $7fff, $109f, $0000   ; 白・白・赤・黒（赤は ピカチュウ版・投げるボールと同じ）
ENDC

; 3. ずかんの絵を読む（画面を消しているとき）
RedBalls_DexLoadLCDOff:
	ld a, RB_DEX_BANK
	ld hl, RB_PokedexLZ
	ld de, $9310                 ; vTiles2 tile $31
	call RB_FarDecompress
	ld hl, RedBalls_DexTile
	ld de, RB_VRAM_DEX_TILE
	ld bc, 16
	jp RB_CopyBytes

; 3. ずかんの絵を読む（画面が出ているとき）
RedBalls_DexLoadRequest:
	ld hl, RB_PokedexLZ
	ld de, $9310
	ld bc, (RB_DEX_BANK << 8) | RB_DEX_TILES
	call RB_DecompressRequest2bpp
	ld de, RedBalls_DexTile
	ld hl, RB_VRAM_DEX_TILE
	ld bc, (RB_BANK << 8) | 1
	jp RB_Request2bpp

RedBalls_DexTile:
	; うしろは黒（3）。0 = 白、2 = 赤、3 = 黒
	db %11111111, %11111111
	db %11000111, %11000111
	db %10000011, %10111011
	db %00000001, %01101101
	db %01101101, %01101101
	db %00000001, %00000001
	db %10000011, %10000011
	db %11000111, %11000111

IF DEF(RB_DEXINFO)
SECTION "redballs dexinfo tramp", ROMX[$7e80], BANK[RB_BANK]
DexInfo_SelectTramp:
	ld a, BANK(DexInfo_Select)
	ld hl, DexInfo_Select
	rst $08
	ret
ENDC
