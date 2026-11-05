; ずかんの「ぶんぷ」を とじる とき、黒い 画面を はさまずに すぐ ずかんの 説明に もどる（銀 日本版。金は 値を 確かめて 入れる）
;
; 元の ゲーム：ぶんぷを B で とじると、画面を 黒く して（Pokedex_BlackOutBG）から 説明の 画面を かき、
;   ポケモンの 絵を よみこみ、WaitBGMap で うつして から 色を もどす（約 20コマ 黒い 画面）。
; これ：DexEntryScreen の .Area の Pokedex_GetArea の あと（Pokedex_BlackOutBG から ret まで）を DA_Close に：
;   ・ぶんぷの 画面を 出した まま、説明の 画面を WRAM に かく（hBGMapMode = 0 なので まだ うつらない）。
;   ・ポケモンの 絵は、ぶんぷを 出した まま のばす（predef GetMonFrontpic の 行き先を SRAM の sDecompressScratch $a000
;     そのものに する。VRAM は さわらない。VRAM バンク1 の $8000 は フィールドの 人の 絵が のこって いるので つかわない）。
;   ・LCD を 切って、SRAM の 絵を $9000 に 写し、画面（タイル と 色の わりあて）・色を
;     いっぺんに 書いて、LCD を つける（LCD を 切って いる のは 1コマ ほど）。
;   　（LCD を 切って いる 間は DelayFrame を よばない。ApplyAttrmap は LCD が 切れて いれば すぐ 書く）
;   ・ほかの 所（説明の 画面・ページ・なきごえ など）は 元の まま。
;   ・白黒の ゲームボーイ（hCGB = 0）では VRAM バンク1 が ないので 元の とおりに する（.dmg）。

IF !DEF(DA_HOOK)
DEF DA_HOOK            EQU $4264      ; バンク$10 .Area の call Pokedex_BlackOutBG（の あと ret まで 34バイト）
DEF DA_DEX_BANK        EQU $10
DEF DA_RedisplayDexEntry EQU $42cc
DEF DA_LoadSelectedMonTiles EQU $5170
DEF DA_GetSelectedMon  EQU $4a7d
DEF DA_DisableLCD      EQU $0432
DEF DA_EnableLCD       EQU $0454
DEF DA_GetSGBLayout    EQU $34e5
DEF DA_DmgToCgbBGPals  EQU $0c4a
DEF DA_DmgToCgbObjPal0 EQU $0c8f
DEF DA_UpdateCGBPals   EQU $0bcc
DEF DA_wTempSpecies    EQU $d143
DEF DA_wCurPartySpecies EQU $cffe
DEF DA_wTilemap        EQU $c3a0
DEF DA_hBGMapMode      EQU $ffd6
DEF DA_hWY             EQU $ffd4
DEF DA_GetBaseData     EQU $39dd
DEF DA_Predef          EQU $2e05
DEF DA_OpenSRAM        EQU $309d
DEF DA_CloseSRAM       EQU $30ad
DEF DA_wFirstUnownSeen EQU $dbd3
DEF DA_wUnownLetter    EQU $d110
DEF DA_BlackOutBG      EQU $5140
DEF DA_DelayFrame      EQU $032e
DEF DA_WaitBGMap       EQU $33ae
DEF DA_hCGB            EQU $ffe8
DEF DA_BANK            EQU $48
DEF DA_ADDR            EQU $7500
ENDC

SECTION "dexarea hook", ROMX[DA_HOOK], BANK[DA_DEX_BANK]
	ld a, BANK(DA_Close)
	ld hl, DA_Close
	rst $08
	ret

SECTION "dexarea", ROMX[DA_ADDR], BANK[DA_BANK]
DA_Close:
	ldh a, [DA_hCGB]
	and a
	jp z, .dmg
	xor a
	ldh [DA_hBGMapMode], a
	ld a, DA_DEX_BANK
	ld hl, DA_RedisplayDexEntry       ; 説明の 画面を WRAM に
	rst $08
	ld a, DA_DEX_BANK
	ld hl, DA_GetSelectedMon
	rst $08
	ld a, [DA_wTempSpecies]
	ld [DA_wCurPartySpecies], a
	; 絵（元の Pokedex_LoadSelectedMonTiles と 同じ。行き先だけ SRAM の $a000）
	ld a, [DA_wFirstUnownSeen]
	ld [DA_wUnownLetter], a
	call DA_GetBaseData
	ld de, $a000                      ; 行き先を SRAM の 絵 そのものに（VRAM には 書かない）
	ld a, $3c                         ; predef GetMonFrontpic
	call DA_Predef
	call DA_DisableLCD
	ld a, $90
	ldh [DA_hWY], a
	ldh [$ff4a], a                    ; rWY（ウインドウ（カントーの 地図）を かくす）
	; SRAM の 絵 → $9000（7×7 タイル）
	xor a
	call DA_OpenSRAM
	ld hl, $a000
	ld de, $9000
	ld bc, 7 * 7 * 16
.pic
	ld a, [hli]
	ld [de], a
	inc de
	dec bc
	ld a, b
	or c
	jr nz, .pic
	call DA_CloseSRAM
	; タイル（wTilemap → $9800、20×18）
	xor a
	ldh [$ff4f], a                    ; rVBK = 0
	ld hl, DA_wTilemap
	ld de, $9800
	ld b, 18
.row
	ld c, 20
.col
	ld a, [hli]
	ld [de], a
	inc de
	dec c
	jr nz, .col
	ld a, e
	add 32 - 20
	ld e, a
	jr nc, .ok
	inc d
.ok
	dec b
	jr nz, .row
	; 色（元の Pokedex_GetSGBLayout と 同じ。色の わりあては ApplyAttrmap が すぐ 書く）
	ld b, 4                           ; SCGB_POKEDEX
	call DA_GetSGBLayout
	ld a, $e4
	call DA_DmgToCgbBGPals
	ld a, $e0
	call DA_DmgToCgbObjPal0
	call DA_UpdateCGBPals             ; 色の レジスタに すぐ 書く
	call DA_EnableLCD
	ld a, 1
	ldh [DA_hBGMapMode], a
	ret

.dmg                                  ; 元の .Area の あと と 同じ
	ld a, DA_DEX_BANK
	ld hl, DA_BlackOutBG
	rst $08
	call DA_DelayFrame
	xor a
	ldh [DA_hBGMapMode], a
	ld a, $90
	ldh [DA_hWY], a
	ld a, DA_DEX_BANK
	ld hl, DA_RedisplayDexEntry
	rst $08
	ld a, DA_DEX_BANK
	ld hl, DA_LoadSelectedMonTiles
	rst $08
	call DA_WaitBGMap
	ld a, DA_DEX_BANK
	ld hl, DA_GetSelectedMon
	rst $08
	ld a, [DA_wTempSpecies]
	ld [DA_wCurPartySpecies], a
	ld b, 4
	call DA_GetSGBLayout
	ld a, $e4
	call DA_DmgToCgbBGPals
	ld a, $e0
	jp DA_DmgToCgbObjPal0
