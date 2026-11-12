; 殿堂入りの あとに セレビィと カントーの 伝説の 鳥に 会える（金 日本版）
;
; ・セレビィ：ウバメのもりの ほこらを しらべると あらわれる（Lv30。1回だけ）。
; ・フリーザー：うずまきじまの いちばん おく（地下2階。ルギアの へやの 入口の よこ）（Lv50）
; ・サンダー：イワヤマトンネルの 地下1階（Lv50）
; ・ファイヤー：シロガネやまの 中（2つめの へや）（Lv50）
;   鳥は 殿堂入りの あと その場所に 立っていて、はなしかけると 戦う。戦った あとは いなくなる（つかまえても たおしても）。
;   まけて 目の前が まっくらに なった ときは また いる。
; ・会ったか どうかは レポートに 書かれる 使われていない バイト（wLegendFlags）の ビット 0〜3。
;
; しくみ
;   ・ほこら：ウバメのもりの イベントの 表の ほこら（bg_event）の スクリプトの 場所を、
;     バンク$28 の おわりの 空き（5バイト）に 置いた「farsjump CelebiShrine」に かえる。
;   ・鳥：その マップの callback（MAPCALLBACK_OBJECTS）で、殿堂入り・まだ 会って いない なら
;     wMapObjects の あいて いる ばんごうに 鳥を 書き、AddSpriteGFX・LoadUsedSpritesGFX で 絵を 読みこむ
;     （SPRITE_MOLTRES ＝ 鳥の ポケモンの 絵。色は 青・茶・赤）。
;     ・うずまきじま 地下2階・イワヤマトンネル 地下1階・シロガネやま 2：スクリプト・文・イベントの かたまり（MapScripts から イベントの 表の おわりまで）を
;       新しい バンクの 同じ 場所に 写し、MapAttributes の スクリプトの バンクと 場所を 新しい バンクに
;       （MapScripts は 元の scene の まま callback を 足した 新しい もの）。
;   ・鳥は 中の マップ（どうくつ・たてもの）に だけ 置ける。外の マップは マップの グループごとに 使う 絵が
;     きまって いて（OutdoorSprites）、鳥の 絵を 足す 所が ないため。
;
; 銀・クリスタルに 入れるとき：下の DEF を その ROM の 値に する
;   （銀は 金と ほぼ 同じ。クリスタルは マップの 番号・スクリプトの 場所・空きを 調べなおす。
;     クリスタル日本版の セレビィ（GSボール）は モバイルアダプタで しか もらえないので、ほこらの セレビィも 入れて よい。
;     その ときは ほこらの 元の スクリプト（GSボールの イベント）を こわさないように する）
;   ・写す かたまりの 中に ほかの パッチ（バグ修正・再戦 など）が ない ことを .map で 確かめる
;     （かたまりが 写せない ときは、その バンクの 空きに MapScripts と farsjump だけ 置く 方法も ある）

IF !DEF(LG_NO_INCLUDES)          ; クリスタルは src/legends_crystal.asm で 先に 読みこむ
INCLUDE "includes.asm"
ENDC
INCLUDE "src/charmap_jp.inc"

IF !DEF(LG_BANK)
DEF LG_BANK            EQU $46        ; 新しい バンク
DEF LG_ADDR            EQU $6000
DEF LG_wEventFlags     EQU $d7aa
DEF LG_EVENT_BEAT_E4   EQU $0044      ; EVENT_BEAT_ELITE_FOUR（日本版の 番号）
DEF wLegendFlags       EQU $d7a1      ; wEventFlags の 前の 空き（レポートに 書かれる。$d7a0 は ガンテツ）
DEF LG_wScriptVar      EQU $d165
DEF LG_wMapObjects     EQU $d438      ; 16バイトずつ（日本版は 1人めが 2番）
; ウバメのもり
DEF LG_ILEX_BANK       EQU $28
DEF LG_ILEX_SHRINE_PTR EQU $60d3      ; ほこらの bg_event の スクリプトの 場所（dw）
DEF LG_ILEX_FREE       EQU $7ffb      ; バンク$28 の 空き（4バイト 使う）
DEF LG_ILEX_SHRINE_TEXT EQU $608d     ; 元の ほこらの 文（バンク$28）
; うずまきじま 地下2階（WHIRL_ISLAND_B2F）
DEF LG_WI_ATTR         EQU $5ae9
DEF LG_WI_SRC_BANK     EQU $2d
DEF LG_WI_START        EQU $44b2      ; MapScripts（scene 0・callback 0）
DEF LG_WI_EVENTS       EQU $44ba
DEF LG_WI_END          EQU $44fb
DEF LG_WI_SLOT         EQU 5          ; 人（どうぐ）3つ の つぎ
; イワヤマトンネル 地下1階（ROCK_TUNNEL_B1F）
DEF LG_RT_ATTR         EQU $5c51
DEF LG_RT_SRC_BANK     EQU $2f
DEF LG_RT_START        EQU $6ecf      ; MapScripts（scene 0・callback 0）
DEF LG_RT_EVENTS       EQU $6eda
DEF LG_RT_END          EQU $6f20
DEF LG_RT_SLOT         EQU 5
; シロガネやま 2（SILVER_CAVE_ROOM_2）
DEF LG_SC_ATTR         EQU $5b0d
DEF LG_SC_SRC_BANK     EQU $2d
DEF LG_SC_START        EQU $45ad
DEF LG_SC_EVENTS       EQU $45b2
DEF LG_SC_END          EQU $45d1
DEF LG_SC_SLOT         EQU 2
DEF LG_ATTR_BANK       EQU $25
DEF LG_AddSpriteGFX    EQU $41c7      ; バンク$05（and a / ret z / ld c, a の つぎから 呼ぶ：c = 絵）
DEF LG_LoadUsedSpritesGFX EQU $41f8
DEF LG_SPRITE_BANK     EQU $05
ENDC

IF !DEF(LG_DISAPPEAR_OFS)
DEF LG_DISAPPEAR_OFS EQU 0   ; disappear の 番号 ＝ スロット ＋ これ
ENDC

; 鳥の 場所（x, y）
IF !DEF(LG_WI_X)
DEF LG_WI_X EQU 9
DEF LG_WI_Y EQU 26
DEF LG_RT_X EQU 2
DEF LG_RT_Y EQU 10
DEF LG_SC_X EQU 8
DEF LG_SC_Y EQU 6
ENDC

DEF LEGEND_CELEBI   EQU 0
DEF LEGEND_ARTICUNO EQU 1
DEF LEGEND_ZAPDOS   EQU 2
DEF LEGEND_MOLTRES  EQU 3

;---------------------------------------------------------------- セレビィ
SECTION "legends ilex shrine ptr", ROMX[LG_ILEX_SHRINE_PTR], BANK[LG_ILEX_BANK]
	dw LG_ILEX_FREE
SECTION "legends ilex stub", ROMX[LG_ILEX_FREE], BANK[LG_ILEX_BANK]
	farsjump CelebiShrine

;---------------------------------------------------------------- うずまきじま・イワヤマトンネル・シロガネやま
MACRO legend_copy ; 名前
SECTION "legends \1 attr", ROMX[LG_\1_ATTR + 6], BANK[LG_ATTR_BANK]
	db LG_BANK
	dw Legend\1_MapScripts
	dw LG_\1_EVENTS
SECTION "legends \1 copy", ROMX[LG_\1_START], BANK[LG_BANK]
	INCBIN "base.gbc", LG_\1_SRC_BANK * $4000 + LG_\1_START - $4000, LG_\1_END - LG_\1_START
ENDM
IF !DEF(LG_NO_BIRDS)              ; LG_NO_BIRDS を DEF すると セレビィ だけ（伝説の 鳥の マップの 写し・鳥を 入れない）
	legend_copy WI
	legend_copy RT
	legend_copy SC
ENDC

;---------------------------------------------------------------- 本体
SECTION "legends", ROMX[LG_ADDR], BANK[LG_BANK]
IF !DEF(LG_NO_BIRDS)
LegendWI_MapScripts:
	def_scene_scripts
	def_callbacks
	callback MAPCALLBACK_OBJECTS, LegendArticuno_Callback

LegendRT_MapScripts:
	def_scene_scripts
	def_callbacks
	callback MAPCALLBACK_OBJECTS, LegendZapdos_Callback

LegendSC_MapScripts:
	def_scene_scripts
	def_callbacks
	callback MAPCALLBACK_OBJECTS, LegendMoltres_Callback
ENDC

; callasm：wScriptVar = 1（殿堂入り・まだ 会って いない）。c = ビット
Legend_Check:
	xor a
	ld [LG_wScriptVar], a
	ld a, [LG_wEventFlags + LG_EVENT_BEAT_E4 / 8]
	bit LG_EVENT_BEAT_E4 % 8, a
	ret z
	call Legend_Mask
	ld a, [wLegendFlags]
	and b
	ret nz
	ld a, 1
	ld [LG_wScriptVar], a
	ret

Legend_Set:
	call Legend_Mask
	ld a, [wLegendFlags]
	or b
	ld [wLegendFlags], a
	ret

Legend_Mask:  ; c → b = 1 << c
	ld b, 1
	ld a, c
	and a
	ret z
.loop
	sla b
	dec a
	jr nz, .loop
	ret

; hl = wMapObjects の 場所、de = データ
; 書いた あと 鳥の 絵を つかう 絵に 足して 読みこむ（絵の 表は callback より 前に 作られて いる）
; ※ 中の マップ だけ（外の マップは グループで 絵が きまって いて 足せない）
Legend_PutObject:
	ld a, -1
	ld [hli], a
	ld c, 13
.copy
	ld a, [de]
	inc de
	ld [hli], a
	dec c
	jr nz, .copy
IF DEF(LG_RefreshSprites)
	; クリスタル：RefreshSprites（使う 絵の 表を 作りなおして 読みこむ。中の マップは wMapObjects から）
	ld a, LG_SPRITE_BANK
	ld hl, LG_RefreshSprites
	rst $08
ELSE
	ld c, SPRITE_MOLTRES
	ld a, LG_SPRITE_BANK
	ld hl, LG_AddSpriteGFX + 3
	rst $08
	ld a, LG_SPRITE_BANK
	ld hl, LG_LoadUsedSpritesGFX
	rst $08
ENDC
	ret

MACRO legend_bird ; 名前, ビット, ポケモン, スロット, x, y, 色, スクリプトの 場所（マップの スクリプトの バンクの 中）
Legend\1_Callback:
	callasm .check
	iffalse .done
	callasm .put
.done
	endcallback
.check
	ld c, \2
	jp Legend_Check
.put
	ld hl, LG_wMapObjects + (\4) * 16
	ld de, .data
	jp Legend_PutObject
.data
	db SPRITE_MOLTRES, (\6) + 4, (\5) + 4, SPRITEMOVEDATA_POKEMON, 0, -1, -1
	db (\7) << 4 | OBJECTTYPE_SCRIPT, 0
	dw \8, -1

Legend\1_Script:
	opentext
	writetext LegendBird_Text
	cry \3
	pause 15
	closetext
	loadwildmon \3, 50
	startbattle
	ifequal 1, .lose                 ; まけた（LOSE）ときは いる まま
	disappear (\4) + LG_DISAPPEAR_OFS
	callasm .set
.lose
	reloadmapafterbattle
	end
.set
IF DEF(LG_wObjectMasks)
	; クリスタル：鳥の 人には イベントの フラグが ない（-1）ので、disappear の あと マップを 読みなおすと
	; また 出てくる。かくす しるし（wObjectMasks）も たてる
	ld a, -1
	ld [LG_wObjectMasks + (\4)], a
ENDC
	ld c, \2
	jp Legend_Set
ENDM

IF !DEF(LG_NO_BIRDS)
	legend_bird Articuno, LEGEND_ARTICUNO, ARTICUNO, LG_WI_SLOT,  LG_WI_X,  LG_WI_Y,  PAL_NPC_BLUE,  LegendArticuno_Script
	legend_bird Zapdos,   LEGEND_ZAPDOS,   ZAPDOS,   LG_RT_SLOT,  LG_RT_X,  LG_RT_Y,  PAL_NPC_BROWN, LegendZapdos_Script
	legend_bird Moltres,  LEGEND_MOLTRES,  MOLTRES,  LG_SC_SLOT,  LG_SC_X,  LG_SC_Y,  PAL_NPC_RED,   LegendMoltres_Script
ENDC

LegendBird_Text:
	db $00, "ギャーーッ！", $57

CelebiShrine:
IF DEF(LG_ILEX_ORIG_SCRIPT)
	; クリスタル：森が さわがしい（GSボールの イベント）ときは 元の スクリプト
	checkevent LG_EVENT_FOREST_IS_RESTLESS
	iftrue .normal
ENDC
	callasm .check
	iffalse .normal
	opentext
	writetext CelebiShrine_Text
	promptbutton
	writetext CelebiShrine_AppearText
	cry CELEBI
	pause 15
	closetext
	loadwildmon CELEBI, 30
	startbattle
	ifequal 1, .lose                 ; まけた（LOSE）ときは また 会える
	callasm .set
.lose
	reloadmapafterbattle
	end
.normal
IF DEF(LG_ILEX_ORIG_SCRIPT)
	db farsjump_command               ; 元の ほこらの スクリプト（GSボールの イベントも そのまま）
	db LG_ILEX_BANK
	dw LG_ILEX_ORIG_SCRIPT
ELSE
	jumptext CelebiShrine_Text
ENDC
.check
	ld c, LEGEND_CELEBI
	jp Legend_Check
.set
	ld c, LEGEND_CELEBI
	jp Legend_Set

CelebiShrine_Text:  ; 元の ほこらの 文
	INCBIN "base.gbc", LG_ILEX_BANK * $4000 + LG_ILEX_SHRINE_TEXT - $4000, 27
CelebiShrine_AppearText:
	db $00, "…おや？", $4f
	db "ほこらの　おくから", $51
	db "なにかが　とびだしてきた！", $57
