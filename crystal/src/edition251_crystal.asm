; 251ひき そろう版 … クリスタル（日本版）用
;  ・つうしん こうかんで しんかする ポケモンは Lv37 で しんかする
;     （ヤドンだけは Lv37 で ヤドラン。おうじゃのしるしを もたせて Lv37 なら ヤドキング）
;  ・ウツギ はかせの けんきゅうじょで 3びき とも もらえる
;  ・殿堂入りの あと：
;     アルフの いせきの けんきゅうじょで オムナイトと カブトを もらえる（Lv30）
;     シロガネやまの いちばん おく（レッドの へや）に ミュウツー（Lv70）
;     グレンじまに ミュウ（Lv50）
;     ミュウツー・ミュウは はなしかけると 戦う。まけた ときは また いる
;  ・もらった／会った しるしは wEdFlags（$d837。wTimeOfDayPal の あとの 使われていない バイト。レポートに 書かれる）
INCLUDE "src/safari/crystal_includes.asm"   ; pokecrystal の 定数・マクロ（スクリプトの 命令の 番号は 英語版 金銀）
INCLUDE "src/charmap_jp.inc"

DEF ED_BANK            EQU $6e        ; あいている バンク
DEF ED_wLinkMode       EQU $c2dc
DEF ED_wForceEvolution EQU $d21a
DEF ED_wTempMonLevel   EQU $d0ed
DEF ED_TRADE_LEVEL     EQU 37

; ---- しんか ----------------------------------------------------------------
; EVOLVE_TRADE（03, どうぐ, しゅるい） → EVOLVE_LEVEL（01, 37, しゅるい）
MACRO ed_evo_level
SECTION "ed251 evo \1", ROMX[\1], BANK[$10]
	db $01, ED_TRADE_LEVEL
ENDM
	ed_evo_level $6e2f   ; ニョロゾ → ニョロトノ
	ed_evo_level $6e5d   ; ユンゲラー → フーディン
	ed_evo_level $6ea5   ; ゴーリキー → カイリキー
	ed_evo_level $6f5e   ; ゴローン → ゴローニャ
	ed_evo_level $70f6   ; ゴースト → ゲンガー
	ed_evo_level $7125   ; イワーク → ハガネール
	ed_evo_level $7317   ; シードラ → キングドラ
	ed_evo_level $739a   ; ストライク → ハッサム
	ed_evo_level $74bd   ; ポリゴン → ポリゴン2

; ヤドン： こうかん（おうじゃのしるし）→ ヤドキング を 先に、Lv37 → ヤドラン を あとに
SECTION "ed251 evo slowpoke", ROMX[$6fc6], BANK[$10]
	db $03, $52, $c7     ; おうじゃのしるし → ヤドキング
	db $01, ED_TRADE_LEVEL, $50   ; Lv37 → ヤドラン

; EvolveAfterBattle の .trade（$10:$641c）の「つうしん していなければ しんかしない」を
; 「つうしん中、または（どうぐで しんか では なく）Lv37 いじょう なら すすむ」に かえる
SECTION "ed251 trade hook", ROMX[$641c], BANK[$10]
	call ED_TradeCheck   ; z = しんかしない
	jp z, $6567
	nop

SECTION "ed251 trade check", ROMX[$7fa0], BANK[$10]
ED_TradeCheck:
	ld a, [ED_wLinkMode]
	and a
	ret nz
	ld a, [ED_wForceEvolution]
	and a
	jr nz, .no
	ld a, [ED_wTempMonLevel]
	cp ED_TRADE_LEVEL
	jr c, .no
	or 1
	ret
.no
	xor a
	ret

; ---- ごさんけ 3びき ---------------------------------------------------------
; ElmsLab の givepoke（5バイト）を farscall（4バイト）＋ waitsfx に かえる
MACRO ed_starter_hook
SECTION "ed251 starter hook \1", ROMX[\1], BANK[$1b]
	db $01, ED_BANK
	dw \2
	db $85               ; waitsfx（なにも しない）
ENDM
	ed_starter_hook $62b7, ED_GotCyndaquil
	ed_starter_hook $62f9, ED_GotTotodile
	ed_starter_hook $6335, ED_GotChikorita

; 日本版の スクリプト命令： givepoke $2d, getmonname $40, farwritetext $4b, writetext $4c,
; promptbutton $54, disappear $6d（番号は ウツギ 2、じょしゅ 3、ボール 4・5・6）, playsound $84, waitsfx $85, end $90
MACRO ed_give
	db $40, \1, $00                  ; getmonname
	db $4b, $1b
	dw $68ba                         ; 「〜を もらった！」
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
	db $90
ED_GotTotodile:
	db $2d, $9e, 5, $ad, $00
	ed_rest 4, 6
	ed_give $9b
	ed_give $98
	db $90
ED_GotChikorita:
	db $2d, $98, 5, $ad, $00
	ed_rest 4, 5
	ed_give $9b
	ed_give $9e
	db $90

ED_RestText:
	db $00, "のこりの　", $f8, "ひきも", $4f, "いっしょに　つれていって　くれ！", $57

; ---- 殿堂入りの あとの ポケモン ---------------------------------------------
DEF ED_wEventFlags     EQU $da65
DEF ED_EVENT_BEAT_E4   EQU $0044
DEF wEdFlags           EQU $d837
DEF ED_wScriptVar      EQU $c2dd
DEF ED_wMapObjects     EQU $d711      ; 16バイトずつ（0 は 主人公、1人めが 1番）
DEF ED_wObjectMasks    EQU $d811
DEF ED_DISAPPEAR_OFS   EQU 1          ; 日本版の disappear は 番号 − 1 の 人
DEF ED_RefreshSprites  EQU $4159      ; バンク$05
DEF ED_ATTR_BANK       EQU $25
DEF ED_OWSPRITES       EQU $4727      ; OverworldSprites（バンク$05。6バイトずつ）

DEF ED_MEWTWO  EQU 0                  ; wEdFlags の ビット
DEF ED_MEW     EQU 1
DEF ED_OMANYTE EQU 2
DEF ED_KABUTO  EQU 3

; 絵：連れ歩きの 絵（24タイル。歩く 絵も ある）を そのまま 使う。番号は マップで 使われていない もの
DEF ED_SPRITE_MEWTWO   EQU $34        ; SPRITE_SURFING_PIKACHU（クリスタルでは 使われていない）
DEF ED_SPRITE_MEW      EQU $44        ; SPRITE_CAL
SECTION "ed251 sprite mewtwo", ROMX[ED_OWSPRITES + (ED_SPRITE_MEWTWO - 1) * 6], BANK[$05]
	dw $6280                          ; 連れ歩きの 絵 149（バンク$63）
	db 12 * 16, $63, WALKING_SPRITE, PAL_OW_SILVER
SECTION "ed251 sprite mew", ROMX[ED_OWSPRITES + (ED_SPRITE_MEW - 1) * 6], BANK[$05]
	dw $6400                          ; 連れ歩きの 絵 150
	db 12 * 16, $63, WALKING_SPRITE, PAL_OW_PINK
; グレンじまは 外の マップ（グループ 6 の 絵の 表）なので 使わない SPRITE_TEACHER（歩く 絵）を ミュウに かえる
SECTION "ed251 cinnabar sprites", ROMX[$4522 + 12], BANK[$05]
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
	ed_map_copy SC3, $5b40, $1c, $4bab, $4c18, $4c30     ; シロガネやま 3（3-76）
	ed_map_copy CI,  $5378, $28, $5ef4, $60c7, $60f3     ; グレンじま（6-8）

DEF ED_SC3_SLOT EQU 2                 ; レッド の つぎ
DEF ED_CI_SLOT  EQU 2                 ; グリーン の つぎ

SECTION "ed251 main", ROMX[$6800], BANK[ED_BANK]
EdSC3_MapScripts:
	def_scene_scripts
	def_callbacks
	callback MAPCALLBACK_OBJECTS, EdMewtwo_Callback

EdCI_MapScripts:
	def_scene_scripts
	def_callbacks
	callback MAPCALLBACK_NEWMAP, $5ef9   ; 元の とびさきの しるしを つける callback（写しの 中）
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

; hl = wMapObjects の 場所、de = データ
Ed_PutObject:
	ld a, -1
	ld [hli], a
	ld c, 13
.copy
	ld a, [de]
	inc de
	ld [hli], a
	dec c
	jr nz, .copy
	ld a, $05
	ld hl, ED_RefreshSprites
	rst $08
	ret

MACRO ed_legend ; 名前, ビット, ポケモン, レベル, スロット, x, y, 絵, 文
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
	jp Ed_PutObject
.data
	db \8, (\7) + 4, (\6) + 4, SPRITEMOVEDATA_POKEMON, 0, -1, -1
	db 0 << 4 | OBJECTTYPE_SCRIPT, 0
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
	disappear (\5) + ED_DISAPPEAR_OFS
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

	ed_legend Mewtwo, ED_MEWTWO, MEWTWO, 70, ED_SC3_SLOT, 12, 8, ED_SPRITE_MEWTWO, EdMewtwo_Text
	ed_legend Mew,    ED_MEW,    MEW,    50, ED_CI_SLOT,   6, 6, ED_SPRITE_MEW,    EdMew_Text

EdMewtwo_Text:
	db $00, "…………！", $57
EdMew_Text:
	db $00, "ミュウ！", $57

; ---- アルフの いせきの けんきゅうじょ（3-28）の はかせ（2人め。うろうろ する 人）------
SECTION "ed251 fossil ptr", ROMX[$52c2], BANK[$16]
	dw $7ff0
SECTION "ed251 fossil stub", ROMX[$7ff0], BANK[$16]
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
	db farsjump_command, $16          ; 元の はかせの スクリプト
	dw $4ea7
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
