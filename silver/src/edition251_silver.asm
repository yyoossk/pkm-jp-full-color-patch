; 251ひき そろう版 … 銀 日本版（後期版）用
;   251匹そろう版キット（金銀用）の 2〜5 を 銀に 入れた もの。クリスタルの edition251_crystal.asm と 同じ きまり。
;  ・つうしん こうかんで しんかする ポケモンは Lv37 で しんかする
;     （ヤドンだけは Lv37 で ヤドラン。おうじゃのしるしを もたせて Lv37 なら ヤドキング）
;  ・ウツギ はかせの けんきゅうじょで 3びき とも もらえる
;     （まえの 版の セーブデータで すでに 1ぴき もらって いる ときは、ウツギ はかせに はなしかけると のこりの 2ひきを くれる）
;  ・殿堂入りの あと：
;     アルフの いせきの けんきゅうじょで オムナイトと カブトを もらえる（Lv30）
;     シロガネやまの いちばん おく（レッドの へや）に ミュウツー（Lv70）
;     グレンじまに ミュウ（Lv50）
;     ミュウツー・ミュウは はなしかけると 戦う。まけた ときは また いる
;  ・コガネデパート 4F で しんかの いし 6つ と おうじゃのしるし（2100円）
;  ・もらった／会った しるしは wEdFlags（ビット0 ミュウツー・1 ミュウ・2 オムナイト・3 カブト・4 ヒノアラシ・5 ワニノコ・6 チコリータ）（$d7a4。wEventFlags の 前の 使われていない 所。レポートに 書かれる）
;
; 銀で クリスタルと ちがう 所
;  ・しんか：銀の バンク$10 は いっぱいなので、ED_TradeCheck を 別に 置かず、.trade（$641f〜$6445、39バイト）を
;    同じ 長さに 書きなおした。のこる つうしん しんかは ヤドン（おうじゃのしるし）だけ なので、
;    「どうぐ なしで しんか」と「タイムカプセルでは どうぐで しんか しない」の 所は なくした。
;    かわかずの いし の しらべも なくした（おうじゃのしるしを もって いる ときしか しんか しないので いらない）。
;  ・コガネデパート 4F の 表は バンク$05 に 空きが ないので、マスターボールの 店と 同じ しくみ（src/masterball.asm の
;    MasterBallMart。表の バンクを b で かえす）で この バンクの 表に かえる（src/masterball251_silver.asm）。
;  ・ミュウツー・ミュウの 絵：連れ歩きの 絵（バンク$53。149 ミュウツー $6280・150 ミュウ $6400）を
;    使われて いない 絵の 番号 $34（SPRITE_SURFING_PIKACHU）・$44（SPRITE_CAL）に。
;    グレンじまは 外の マップ（グループ 6）なので、その 絵の 表（$05:$46b3）の SPRITE_TEACHER（グループ 6 の マップで 使われて いない
;    歩く 絵）を $44 に。
;  ・wMapObjects：0 主人公・1 連れ歩き・2 から 人。レッドの へや は レッド 2・ミュウツー 3、グレンじま は グリーン 2・ミュウ 3。
;    disappear の 番号は スロットの まま（legends と 同じ）。
INCLUDE "includes.asm"
INCLUDE "src/charmap_jp.inc"

DEF ED_BANK            EQU $4f        ; あいている バンク
DEF ED_wLinkMode       EQU $d03c
DEF ED_wForceEvolution EQU $d0c4
DEF ED_wTempMonLevel   EQU $d024
DEF ED_wTempMonItem    EQU $d006
DEF ED_TRADE_LEVEL     EQU 37

; ---- しんか ----------------------------------------------------------------
; EVOLVE_TRADE（03, どうぐ, しゅるい） → EVOLVE_LEVEL（01, 37, しゅるい）
MACRO ed_evo_level
SECTION "ed251 evo \1", ROMX[\1], BANK[$10]
	db $01, ED_TRADE_LEVEL
ENDM
	ed_evo_level $7039   ; ニョロゾ → ニョロトノ
	ed_evo_level $7067   ; ユンゲラー → フーディン
	ed_evo_level $70af   ; ゴーリキー → カイリキー
	ed_evo_level $7168   ; ゴローン → ゴローニャ
	ed_evo_level $72fe   ; ゴースト → ゲンガー
	ed_evo_level $732d   ; イワーク → ハガネール
	ed_evo_level $751f   ; シードラ → キングドラ
	ed_evo_level $75a2   ; ストライク → ハッサム
	ed_evo_level $76c5   ; ポリゴン → ポリゴン2

; ヤドン： こうかん（おうじゃのしるし）→ ヤドキング を 先に、Lv37 → ヤドラン を あとに
SECTION "ed251 evo slowpoke", ROMX[$71d0], BANK[$10]
	db $03, $52, $c7     ; おうじゃのしるし → ヤドキング
	db $01, ED_TRADE_LEVEL, $50   ; Lv37 → ヤドラン

; EvolveAfterBattle の .trade（hl ＝ どうぐの 場所）
;   つうしん中、または（いしを つかって いない・Lv37 いじょう）で、おうじゃのしるし を もって いれば しんか（しるしは なくなる）
DEF ED_DONT_EVOLVE_2 EQU $6563       ; hl を 2つ すすめて つぎの しんかへ
DEF ED_PROCEED       EQU $646e
SECTION "ed251 trade", ROMX[$641f], BANK[$10]
ED_Trade:
	ld a, [ED_wLinkMode]
	and a
	jr nz, .linked
	ld a, [ED_wForceEvolution]
	and a
	jp nz, ED_DONT_EVOLVE_2
	ld a, [ED_wTempMonLevel]
	cp ED_TRADE_LEVEL
	jp c, ED_DONT_EVOLVE_2
.linked
	ld a, [ED_wTempMonItem]
	cp [hl]
	jp nz, ED_DONT_EVOLVE_2
	inc hl
	xor a
	ld [ED_wTempMonItem], a
	jr ED_PROCEED
	ds $6446 - @, 0
	assert @ == $6446

; ---- ごさんけ 3びき ---------------------------------------------------------
; ElmsLab（バンク$13）の givepoke（5バイト）を farscall（4バイト）＋ waitsfx に かえる
MACRO ed_starter_hook
SECTION "ed251 starter hook \1", ROMX[\1], BANK[$13]
	db $01, ED_BANK
	dw \2
	db $85               ; waitsfx（なにも しない）
ENDM
	ed_starter_hook $65bb, ED_GotCyndaquil
	ed_starter_hook $65fd, ED_GotTotodile
	ed_starter_hook $6639, ED_GotChikorita

; 銀の スクリプト命令（英語版 金銀と 同じ 番号）： givepoke $2d, getmonname $40, farwritetext $4b, writetext $4c,
; promptbutton $54, disappear $6d（ボールは 4・5・6）, playsound $84, waitsfx $85, end $90
DEF ED_GOT_TEXT EQU $6a87            ; 「〜を もらった！」（バンク$13）
MACRO ed_give
	db $40, \1, $00                  ; getmonname
	db $4b, $13
	dw ED_GOT_TEXT
	db $84, $02, $00                 ; playsound SFX_CAUGHT_MON
	db $85
	db $54
	db $2d, \1, 5, $00, $00          ; givepoke （もちものなし）
ENDM
MACRO ed_rest
	db $4c
	dw ED_RestText
	db $54
	db $6d, \1
	db $6d, \2
ENDM

SECTION "ed251 starters", ROMX[$4000], BANK[ED_BANK]
ED_GotCyndaquil:
	db $2d, $9b, 5, $ad, $00         ; ヒノアラシ（きのみ）
	ed_rest 5, 6
	ed_give $9e                      ; ワニノコ
	ed_give $98                      ; チコリータ
	callasm Ed_SetElmAll
	db $90
ED_GotTotodile:
	db $2d, $9e, 5, $ad, $00
	ed_rest 4, 6
	ed_give $9b
	ed_give $98
	callasm Ed_SetElmAll
	db $90
ED_GotChikorita:
	db $2d, $98, 5, $ad, $00
	ed_rest 4, 5
	ed_give $9b
	ed_give $9e
	callasm Ed_SetElmAll
	db $90

ED_RestText:
	db $00, "のこりの　", $f8, "ひきも", $4f, "いっしょに　つれていって　くれ！", $57

; ---- 殿堂入りの あとの ポケモン ---------------------------------------------
DEF ED_wEventFlags     EQU $d7aa
DEF ED_EVENT_BEAT_E4   EQU $0044
DEF wEdFlags           EQU $d7a4
DEF ED_wScriptVar      EQU $d165
DEF ED_wMapObjects     EQU $d438      ; 16バイトずつ（0 は 主人公、1 は 連れ歩き、人は 2番から）
DEF ED_wObjectMasks    EQU $d538
DEF ED_AddSpriteGFX    EQU $41c7      ; バンク$05（and a / ret z / ld c, a の つぎから 呼ぶ：c = 絵）
DEF ED_LoadUsedSpritesGFX EQU $41f8
DEF ED_ATTR_BANK       EQU $25
DEF ED_OWSPRITES       EQU $47b0      ; OverworldSprites（バンク$05。6バイトずつ）

DEF ED_MEWTWO  EQU 0                  ; wEdFlags の ビット
DEF ED_MEW     EQU 1
DEF ED_OMANYTE EQU 2
DEF ED_KABUTO  EQU 3

; 絵：連れ歩きの 絵（24タイル。歩く 絵も ある）を そのまま 使う。番号は マップで 使われていない もの
DEF ED_SPRITE_MEWTWO   EQU $34        ; SPRITE_SURFING_PIKACHU（銀の マップでは 使われていない）
DEF ED_SPRITE_MEW      EQU $44        ; SPRITE_CAL
SECTION "ed251 sprite mewtwo", ROMX[ED_OWSPRITES + (ED_SPRITE_MEWTWO - 1) * 6], BANK[$05]
	dw $6280                          ; 連れ歩きの 絵 149（バンク$53）
	db 12 * 16, $53, WALKING_SPRITE, PAL_OW_PINK
SECTION "ed251 sprite mew", ROMX[ED_OWSPRITES + (ED_SPRITE_MEW - 1) * 6], BANK[$05]
	dw $6400                          ; 連れ歩きの 絵 150
	db 12 * 16, $53, WALKING_SPRITE, PAL_OW_PINK
; グレンじまは 外の マップ（グループ 6 の 絵の 表 $05:$46b3）なので 使わない SPRITE_TEACHER（歩く 絵）を ミュウに かえる
SECTION "ed251 cinnabar sprites", ROMX[$46b3], BANK[$05]
	db ED_SPRITE_MEW

; マップの スクリプト・イベントを 新しい バンクの 同じ 場所に 写し、MapAttributes の スクリプトの バンク・場所を かえる
MACRO ed_map_copy ; 名前, MapAttributes, 元の バンク, MapScripts, イベント, おわり
SECTION "ed251 \1 attr", ROMX[\2 + 6], BANK[ED_ATTR_BANK]
	db ED_BANK
	dw Ed\1_MapScripts
	dw \5
SECTION "ed251 \1 copy", ROMX[\4], BANK[ED_BANK]
	INCBIN "base.gbc", (\3) * $4000 + (\4) - $4000, (\6) - (\4)
ENDM
	ed_map_copy SC3, $5b19, $2d, $45d1, $463e, $4656     ; シロガネやま 3（3-68）
	ed_map_copy CI,  $53b1, $36, $6cfe, $6ed1, $6efd     ; グレンじま（6-8）

DEF ED_SC3_SLOT EQU 3                 ; レッド（2）の つぎ
DEF ED_CI_SLOT  EQU 3                 ; グリーン（2）の つぎ

SECTION "ed251 main", ROMX[$6800], BANK[ED_BANK]
EdSC3_MapScripts:
	def_scene_scripts
	def_callbacks
	callback MAPCALLBACK_OBJECTS, EdMewtwo_Callback

EdCI_MapScripts:
	def_scene_scripts
	def_callbacks
	callback MAPCALLBACK_NEWMAP, $6d03   ; 元の とびさきの しるしを つける callback（写しの 中）
	callback MAPCALLBACK_OBJECTS, EdMew_Callback

; callasm：wScriptVar = 1（殿堂入り・c の ビットが まだ）
Ed_Check:
	xor a
	ld [ED_wScriptVar], a
	ld a, [ED_wEventFlags + ED_EVENT_BEAT_E4 / 8]
	bit ED_EVENT_BEAT_E4 % 8, a
	ret z
	call Ed_Mask
	ld a, [wEdFlags]
	and b
	ret nz
	ld a, 1
	ld [ED_wScriptVar], a
	ret

Ed_Set:
	call Ed_Mask
	ld a, [wEdFlags]
	or b
	ld [wEdFlags], a
	ret

Ed_Mask:  ; c → b = 1 << c
	ld b, 1
	ld a, c
	and a
	ret z
.loop
	sla b
	dec a
	jr nz, .loop
	ret

; hl = wMapObjects の 場所、de = データ、c = 絵（0 なら 読みこまない：外の マップは グループの 表で 読んで いる）
Ed_PutObject:
	push bc
	ld a, -1
	ld [hli], a
	ld c, 13
.copy
	ld a, [de]
	inc de
	ld [hli], a
	dec c
	jr nz, .copy
	pop bc
	ld a, c
	and a
	ret z
	ld a, $05
	ld hl, ED_AddSpriteGFX + 3
	rst $08
	ld a, $05
	ld hl, ED_LoadUsedSpritesGFX
	rst $08
	ret

MACRO ed_legend ; 名前, ビット, ポケモン, レベル, スロット, x, y, 絵, 文, 色, 読みこむ 絵（0 なし）
Ed\1_Callback:
	callasm .check
	iffalse .done
	callasm .put
.done
	endcallback
.check
	ld c, \2
	jp Ed_Check
.put
	ld hl, ED_wMapObjects + (\5) * 16
	ld de, .data
	ld c, \<11>
	jp Ed_PutObject
.data
	db \8, (\7) + 4, (\6) + 4, SPRITEMOVEDATA_STANDING_DOWN, 0, -1, -1
	db (\<10>) << 4 | OBJECTTYPE_SCRIPT, 0
	dw Ed\1_Script, -1

Ed\1_Script:
	opentext
	writetext \9
	cry \3
	pause 15
	closetext
	loadwildmon \3, \4
	startbattle
	ifequal 1, .lose                 ; まけた（LOSE）ときは いる まま
	disappear \5
	callasm .set
.lose
	reloadmapafterbattle
	end
.set
	ld a, -1                         ; イベントの フラグが ないので マップを 読みなおしても 出ないように
	ld [ED_wObjectMasks + (\5)], a
	ld c, \2
	jp Ed_Set
ENDM

	ed_legend Mewtwo, ED_MEWTWO, MEWTWO, 70, ED_SC3_SLOT, 12, 8, ED_SPRITE_MEWTWO, EdMewtwo_Text, PAL_NPC_PINK, ED_SPRITE_MEWTWO
	ed_legend Mew,    ED_MEW,    MEW,    50, ED_CI_SLOT,   6, 6, ED_SPRITE_MEW,    EdMew_Text,    PAL_NPC_PINK, 0

EdMewtwo_Text:
	db $00, "…………！", $57
EdMew_Text:
	db $00, "ミュウ！", $57

; ---- アルフの いせきの けんきゅうじょ（3-28）の はかせ（2人め。うろうろ する 人）------
DEF ED_RC_SCRIPT EQU $47d9            ; 元の はかせの スクリプト（バンク$26）
SECTION "ed251 fossil ptr", ROMX[$4afb + 9], BANK[$26]
	dw $7ffc
SECTION "ed251 fossil stub", ROMX[$7ffc], BANK[$26]
	farsjump EdFossilScript

SECTION "ed251 fossil", ROMX[$6c00], BANK[ED_BANK]
EdFossilScript:
	callasm .check_omanyte
	iftrue .give
	callasm .check_kabuto
	iffalse .normal
.give
	faceplayer
	opentext
	writetext EdFossil_Text1
	promptbutton
	callasm .check_omanyte
	iffalse .kabuto
	writetext EdFossil_GotOmanyte
	playsound SFX_CAUGHT_MON
	waitsfx
	promptbutton
	givepoke OMANYTE, 30
	ifequal 2, .full
	callasm .set_omanyte
.kabuto
	writetext EdFossil_GotKabuto
	playsound SFX_CAUGHT_MON
	waitsfx
	promptbutton
	givepoke KABUTO, 30
	ifequal 2, .full
	callasm .set_kabuto
	writetext EdFossil_Text2
	waitbutton
	closetext
	end
.full
	writetext EdFossil_FullText
	waitbutton
	closetext
	end
.normal
	db farsjump_command, $26          ; 元の はかせの スクリプト
	dw ED_RC_SCRIPT
.check_omanyte
	ld c, ED_OMANYTE
	jp Ed_Check
.check_kabuto
	ld c, ED_KABUTO
	jp Ed_Check
.set_omanyte
	ld c, ED_OMANYTE
	jp Ed_Set
.set_kabuto
	ld c, ED_KABUTO
	jp Ed_Set

EdFossil_Text1:
	db $00, "でんどういり　おめでとう！", $51
	db "おいわいに　かせきから", $4f
	db "ふっかつさせた　ポケモンを", $55
	db "あげよう！", $57
EdFossil_GotOmanyte:
	db $00, $52, "は", $4f, "オムナイトを　もらった！", $57
EdFossil_GotKabuto:
	db $00, $52, "は", $4f, "カブトを　もらった！", $57
EdFossil_Text2:
	db $00, "どちらも　むかしの　ポケモンだ", $51
	db "だいじに　そだてて　くれよ！", $57
EdFossil_FullText:
	db $00, "おや　もう　もてないようだね", $51
	db "ボックスを　あけて　また　おいで", $57

; ---- しんかの いし・おうじゃのしるし を 買える -------------------------------
; 表は src/masterball251_silver.asm（MasterBallMart で コガネデパート 4F の 表を かえる）。
; ねだん（ItemAttributes $01:$6b58、7バイトずつ。さいしょの 2バイト）：つきのいし 0円 → 2100円、おうじゃのしるし 100円 → 2100円
SECTION "ed251 price moon", ROMX[$6b58 + (MOON_STONE - 1) * 7], BANK[$01]
	dw 2100
SECTION "ed251 price kingsrock", ROMX[$6b58 + (KINGS_ROCK - 1) * 7], BANK[$01]
	dw 2100

; ---- まえの セーブデータ：ウツギ はかせが のこりの 2ひきを くれる ----------------
; EVENT_GOT_A_POKEMON_FROM_ELM（$1a）の あと、えらんで いない（EVENT_GOT_〜_FROM_ELM $1b・$1c・$1d が ない）で
; まだ もらって いない（wEdFlags ビット 4 ヒノアラシ・5 ワニノコ・6 チコリータ）ポケモンを くれる。
; 新しく はじめた ときは けんきゅうじょで 3びき もらった とき ビット 4〜6 を ぜんぶ たてる。
; ウツギ はかせ（ElmsLab の 1人め）の object_event の スクリプトの 場所（$13:$74ab。元は $64f9）を $13:$7ffc の farsjump EdElmScript に。
DEF ED_ELM0 EQU 4
DEF ED_ELM_SCRIPT EQU $64f9
SECTION "ed251 elm ptr", ROMX[$74ab], BANK[$13]
	dw $7ffc
SECTION "ed251 elm stub", ROMX[$7ffc], BANK[$13]
	farsjump EdElmScript

SECTION "ed251 elm", ROMX[$7000], BANK[ED_BANK]
Ed_SetElmAll:
	ld a, [wEdFlags]
	or %01110000
	ld [wEdFlags], a
	ret

; c = 0 ヒノアラシ・1 ワニノコ・2 チコリータ → wScriptVar = 1（くれる）
Ed_ElmNeed:
	xor a
	ld [ED_wScriptVar], a
	ld a, [ED_wEventFlags + $1a / 8]
	bit $1a % 8, a
	ret z
	push bc
	ld a, c
	add $1b % 8
	ld c, a
	call Ed_Mask
	ld a, [ED_wEventFlags + $1b / 8]
	and b
	pop bc
	ret nz
	ld a, c
	add ED_ELM0
	ld c, a
	call Ed_Mask
	ld a, [wEdFlags]
	and b
	ret nz
	ld a, 1
	ld [ED_wScriptVar], a
	ret

Ed_ElmNeedAny:
	ld c, 0
	call Ed_ElmNeed
	ld a, [ED_wScriptVar]
	and a
	ret nz
	ld c, 1
	call Ed_ElmNeed
	ld a, [ED_wScriptVar]
	and a
	ret nz
	ld c, 2
	jp Ed_ElmNeed

MACRO ed_elm_give ; 番号, ポケモン
	callasm .need\1
	iffalse .skip\1
	db $40, \2, $00                 ; getmonname
	db $4b, $13
	dw ED_GOT_TEXT                   ; 「〜を もらった！」
	db $84, $02, $00                 ; playsound SFX_CAUGHT_MON
	db $85
	db $54
	db $2d, \2, 5, $00, $00         ; givepoke
	ifequal 2, .full
	callasm .set\1
.skip\1
ENDM

EdElmScript:
	callasm Ed_ElmNeedAny
	iffalse .normal
	faceplayer
	opentext
	writetext EdElm_Text
	promptbutton
	ed_elm_give 0, $9b
	ed_elm_give 1, $9e
	ed_elm_give 2, $98
	writetext EdElm_Text2
	waitbutton
	closetext
	end
.full
	writetext EdElm_FullText
	waitbutton
	closetext
	end
.normal
	db farsjump_command, $13          ; 元の ウツギ はかせの スクリプト
	dw ED_ELM_SCRIPT
.need0
	ld c, 0
	jp Ed_ElmNeed
.need1
	ld c, 1
	jp Ed_ElmNeed
.need2
	ld c, 2
	jp Ed_ElmNeed
.set0
	ld c, ED_ELM0
	jp Ed_Set
.set1
	ld c, ED_ELM0 + 1
	jp Ed_Set
.set2
	ld c, ED_ELM0 + 2
	jp Ed_Set

EdElm_Text:
	db $00, "ウツギ『やあ　", $52, "くん！", $51
	db "じつは　のこりの　ポケモンも", $4f
	db "きみに　つれていって　ほしいんだ！", $57
EdElm_Text2:
	db $00, "ウツギ『みんな　だいじに", $4f
	db "そだてて　あげてね！", $57
EdElm_FullText:
	db $00, "ウツギ『おや　もう　もてない", $4f
	db "みたいだね", $51
	db "ボックスを　あけて　また　おいで", $57
