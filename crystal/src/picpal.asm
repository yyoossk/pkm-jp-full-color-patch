; ずかんの一覧と パソコン（ポケモンを あずける・つれていく・うごかす）の ポケモンの絵を、
; 手持ちのポケモンと同じように 白い背景に そのポケモンの色（カラフル）で出す（金 日本版）
;
; 元のゲーム：この2つの画面は 絵の色を 決まった1色の色の組にしている（wCurPartySpecies = $ff で 画面の色を作る）。
;   ずかん = 緑（PokedexQuestionMarkPalette）、パソコン = オレンジ（BillsPCOrangePalette）。
;   カーソルを動かしても 絵だけ 読みかえて、色は変えない。
; 変えたあと：
;   ・ずかん：Pokedex_LoadSelectedMonTiles（選んでいるポケモンの絵を読む）の頭で、見たことのあるポケモンなら その種類、
;     見たことがなければ 0 を wDexPicSpecies にしまい、絵の色（背景のパレット1）を そのポケモンの色にする。
;     見たことがない（？の絵）ときは 今までどおり 緑。
;   ・パソコン：PCMonInfo（選んでいるポケモンの絵と名前を出す）で 絵を読んだあとに、そのポケモンの色（色ちがいは色ちがいの色）にする。
;   ・画面の色を作る所（_CGB_Pokedex_Init・_CGB_BillsPC）の「$ff なら 決まった色」も、しまった種類の色にする
;     （画面を開いたとき・ほかの画面から もどったときも 同じ色になる）。
;   ・ずかんの説明のページ・パソコンの「つよさをみる」などは 元から そのポケモンの色なので 変わらない。
;
; しくみ
;   ・色を作る処理は 戦闘・ずかんの色の処理と同じバンク（$02）の空きに置く（GetMonPalettePointer などを そのまま呼ぶ）。
;   ・ずかん（バンク$10）・パソコン（バンク$38）には空きがないので、ホームの空きに 小さな入口を置いて farcall する。
;   ・絵の色は 背景のパレット1。wBGPals1 に書き、画面に出ている色（wBGPals2）にも写して hCGBPalUpdate。

;---------------------------------------------------------------------
; ROM ごとにちがう所（金 日本版）
;---------------------------------------------------------------------
IF !DEF(PP_DEX_HOOK)
; ずかん（バンク$10）
DEF PP_DEX_BANK             EQU $10
DEF PP_DEX_HOOK             EQU $5170   ; Pokedex_LoadSelectedMonTiles の call Pokedex_GetSelectedMon（3バイト）
DEF PP_Pokedex_GetSelectedMon EQU $4a7d
DEF PP_Pokedex_CheckSeen    EQU $4a9c
; パソコン（バンク$38）
DEF PP_PC_BANK              EQU $38
DEF PP_PC_HOOK              EQU $7305   ; PCMonInfo の predef GetMonFrontpic のつぎ：xor a / ld [wBillsPC_MonHasMail], a（4バイト）
DEF PP_wBillsPC_MonHasMail  EQU $ca32
; 色（バンク$02）
DEF PP_CGB_BANK             EQU $02
DEF PP_DEX_FF               EQU $54f2   ; _CGB_Pokedex_Init の ld hl, PokedexQuestionMarkPalette / call LoadHLPaletteIntoDE（6バイト）
DEF PP_PC_FF                EQU $5536   ; _CGB_BillsPC の ld hl, BillsPCOrangePalette / call LoadHLPaletteIntoDE（6バイト）
DEF PP_PokedexQuestionMarkPalette EQU $551c
DEF PP_BillsPCOrangePalette EQU $5563
DEF PP_LoadHLPaletteIntoDE  EQU $5a68
DEF PP_LoadPalette_White_Col1_Col2_Black EQU $5a71
DEF PP_GetMonPalettePointer EQU $5b7a   ; a = 種類
DEF PP_GetPlayerOrMonPalettePointer EQU $5b61   ; a = 種類、bc = 個体値（色ちがい）
DEF PP_CGB_FREE             EQU $7c00   ; バンク$02 の空き（$7bc0〜）
; ホームの空き（ずかんの入口 26バイト・パソコンの入口 11バイト）
DEF PP_HOME_DEX             EQU $3fe0
DEF PP_HOME_PC              EQU $3f8a
; WRAM
DEF PP_wTempSpecies         EQU $d143
DEF PP_wCurPartySpecies     EQU $cffe
DEF PP_wTempMonDVs          EQU $d01a
DEF PP_wBGPals1             EQU $c200
DEF PP_wBGPals2             EQU $c280
DEF PP_hCGBPalUpdate        EQU $ffe7
DEF PP_wDexPicSpecies       EQU $de3e   ; 使われていない WRAM（$de3b〜$de3d は つよさをみる、$de40〜 は 60fps）
DEF PP_wPCPicSpecies        EQU $de3f
ENDC
; 色を WRAM のバンクに置いている版（クリスタル：wBGPals1・wBGPals2 が バンク5）は PP_PALS_WRAMBANK EQU 5
IF !DEF(PP_PALS_WRAMBANK)
DEF PP_PALS_WRAMBANK EQU 0
ENDC
; wDexPicSpecies・wPCPicSpecies を WRAM のバンク（$d000〜）に置くときは PP_VARS_WRAMBANK EQU そのバンク
; （クリスタル日本版：バンク1 に使われていない所が見つからないので、60fps の作業用と同じ バンク2 の空きに置く）
IF !DEF(PP_VARS_WRAMBANK)
DEF PP_VARS_WRAMBANK EQU 0
ENDC

; a を \1 にしまう（hl をこわす）
MACRO pp_store
IF PP_VARS_WRAMBANK
	ld l, a
	ldh a, [$ff70]
	ld h, a
	ld a, PP_VARS_WRAMBANK
	ldh [$ff70], a
	ld a, l
	ld [\1], a
	ld a, h
	ldh [$ff70], a
ELSE
	ld [\1], a
ENDC
ENDM

; \1 を a に読む（hl をこわす）
MACRO pp_load
IF PP_VARS_WRAMBANK
	ldh a, [$ff70]
	ld h, a
	ld a, PP_VARS_WRAMBANK
	ldh [$ff70], a
	ld a, [\1]
	ld l, a
	ld a, h
	ldh [$ff70], a
	ld a, l
ELSE
	ld a, [\1]
ENDC
ENDM

;---------------------------------------------------------------------
SECTION "picpal dex hook", ROMX[PP_DEX_HOOK], BANK[PP_DEX_BANK]
	call PicPal_DexEntry

SECTION "picpal pc hook", ROMX[PP_PC_HOOK], BANK[PP_PC_BANK]
	call PicPal_PCEntry
	nop

SECTION "picpal dex ff", ROMX[PP_DEX_FF], BANK[PP_CGB_BANK]
	call PicPal_DexInto
	nop
	nop
	nop

SECTION "picpal pc ff", ROMX[PP_PC_FF], BANK[PP_CGB_BANK]
	call PicPal_PCInto
	nop
	nop
	nop

;---------------------------------------------------------------------
SECTION "picpal home dex", ROM0[PP_HOME_DEX]
; ずかん（バンク$10 から呼ばれる）：元の call Pokedex_GetSelectedMon ＋ 絵の色
PicPal_DexEntry:
	call PP_Pokedex_GetSelectedMon
	push af
	call PP_Pokedex_CheckSeen    ; nz = 見たことがある
	jr z, .unseen
	ld a, [PP_wTempSpecies]
	jr .set
.unseen
	xor a
.set
	pp_store PP_wDexPicSpecies
	ld a, PP_CGB_BANK
	ld hl, PicPal_Dex
	rst $08
	pop af
	ret

SECTION "picpal home pc", ROM0[PP_HOME_PC]
; パソコン（バンク$38 から呼ばれる）：絵の色 ＋ 元の xor a / ld [wBillsPC_MonHasMail], a
PicPal_PCEntry:
	ld a, PP_CGB_BANK
	ld hl, PicPal_PC
	rst $08
	xor a
	ld [PP_wBillsPC_MonHasMail], a
	ret

;---------------------------------------------------------------------
SECTION "picpal main", ROMX[PP_CGB_FREE], BANK[PP_CGB_BANK]
; ずかん：選んでいるポケモンの色にする
PicPal_Dex:
	ld de, PP_wBGPals1 + 1 * 8
	call PicPal_DexInto
	jr PicPal_PushIfShown

; パソコン：選んでいるポケモンの色にする（wCurPartySpecies・wTempMonDVs は PCMonInfo が入れたもの）
PicPal_PC:
	ld a, [PP_wCurPartySpecies]
	pp_store PP_wPCPicSpecies
	ld de, PP_wBGPals1 + 1 * 8
	call PicPal_PCInto
	; fallthrough

; wBGPals1 のパレット1 を 画面に出ている色（wBGPals2）にもうつす。
; ただし 画面が まだ できあがって いない とき（開くときの 白い 画面・まっくらな 画面）は うつさない。
; うつすと、白や 黒の 画面の なかで 絵の ところ だけ 先に 色が ついて 一瞬 へんな 四角が 見えた。
; 画面が できあがって いるか どうかは、パレット0 が wBGPals1 と wBGPals2 で 同じか で 見る
; （このあと GetSGBLayout が 全部の 色を 作りなおして 両方 そろえる）
PicPal_PushIfShown:
PicPal_Push:
IF PP_PALS_WRAMBANK
	ldh a, [$ff70]               ; rSVBK
	push af
	ld a, PP_PALS_WRAMBANK
	ldh [$ff70], a
ENDC
	ld hl, PP_wBGPals1
	ld de, PP_wBGPals2
	ld c, 8
.cmp
	ld a, [de]
	cp [hl]
	jr nz, .done
	inc hl
	inc de
	dec c
	jr nz, .cmp
	; まっくら（Pokedex_BlackOutBG は wBGPals1 も 0 に する。ぶんぷから もどる とき）も うつさない
	ld a, [PP_wBGPals2]
	ld b, a
	ld a, [PP_wBGPals2 + 1]
	or b
	jr z, .done
	ld hl, PP_wBGPals1 + 1 * 8
	ld de, PP_wBGPals2 + 1 * 8
	ld c, 8
.copy
	ld a, [hli]
	ld [de], a
	inc de
	dec c
	jr nz, .copy
	ld a, 1
	ldh [PP_hCGBPalUpdate], a
.done
IF PP_PALS_WRAMBANK
	pop af
	ldh [$ff70], a
ENDC
	ret

; de = 書く所。見たことがないときは 元の緑（？の色）
PicPal_DexInto:
	pp_load PP_wDexPicSpecies
	and a
	jr nz, .mon
	ld hl, PP_PokedexQuestionMarkPalette
	jp PP_LoadHLPaletteIntoDE
.mon
	call PP_GetMonPalettePointer
	jp PP_LoadPalette_White_Col1_Col2_Black

; de = 書く所。まだ絵を出していないときは 元のオレンジ
PicPal_PCInto:
	pp_load PP_wPCPicSpecies
	and a
	jr z, .none
	cp $ff
	jr z, .none
	ld bc, PP_wTempMonDVs
	call PP_GetPlayerOrMonPalettePointer
	jp PP_LoadPalette_White_Col1_Col2_Black
.none
	ld hl, PP_BillsPCOrangePalette
	jp PP_LoadHLPaletteIntoDE
