; カントーの 御三家（フシギダネ・ヒトカゲ・ゼニガメ）を もらえる（金 日本版）
; ピカチュウフルカラー（ピカチュウ版）と 同じ 人・同じ 文・同じ 色（青）で もらえる。どれも Lv10。
;
;   フシギダネ：ハナダシティの 家（ピカチュウ版で 女の人が いる 家 ＝ 金の こうかんの 話の 家）の 女の人
;               （ピカチュウ版は ピカチュウが なついて いないと くれないが、金には その しくみが ないので いつでも）
;   ヒトカゲ  ：24ばんどうろ（ゴールデンボールブリッジの 北の はし）の 男の人
;   ゼニガメ  ：クチバシティの ジュンサー（オレンジバッジを もって いると くれる）
;   文は ピカチュウ版の ものを そのまま（tools/starters_gen.py が ピカチュウフルカラーの ROM から 取り出して
;   src/starters_texts.inc を 作る。日本版 金と 同じ 文字コード）。
;   人の 絵：女の人は SPRITE_LASS、男の人は SPRITE_COOLTRAINER_M（ピカチュウ版の 女の子・エリートトレーナー♂に あたる 金の 絵）。
;            ジュンサーは 金に 絵が ないので ピカチュウフルカラーの 絵（24タイル）を 入れる。
;   色：3人とも 青（PAL_NPC_BLUE。ピカチュウフルカラーと 同じ）。
;
; しくみ
;   ・3つの マップの スクリプト・文・イベントの かたまり（MapScripts から イベントの 表の おわりまで）を
;     新しい バンクの 同じ 場所に 写し、イベントの 表は 人を 1人 足した ものを 作る。
;     MapAttributes の スクリプトの バンク・イベントの 場所を 新しい ものに。
;   ・ジュンサーの 絵：使われていない SPRITE_OLD_LINK_RECEPTIONIST（$58。SPRITE_UNUSED_GUY は fieldcolors が 使う）の OverworldSprites を ジュンサーの 絵（歩く 絵）に し、
;     クチバの グループの 外の 絵の 表（VermilionGroupSprites）の SPRITE_BIKER を その 番号に かえる
;     （BIKER は クチバの グループの 外の マップ（クチバシティ・6・11ばんどうろ）で 使われて いない）。
;   ・もらったか どうかは wLegendFlags（$d7a1。レポートに 書かれる）の ビット 4・5・6。
;
; 銀・クリスタルに 入れるとき：下の DEF を その ROM の 値に する
;   （クリスタルは ジュンサーが いない ので 絵の 入れかたは 同じ。マップの 番号・スクリプトの 場所・空き・
;     外の 絵の 表は 調べなおす）

IF !DEF(ST_NO_INCLUDES)          ; クリスタルは src/starters_crystal.asm で 先に 読みこむ
INCLUDE "includes.asm"
ENDC
INCLUDE "src/charmap_jp.inc"

IF !DEF(ST_BANK)
DEF ST_BANK_VER        EQU $47        ; クチバシティの 写し
DEF ST_BANK            EQU $48        ; ハナダの 家・24ばんどうろの 写しと 本体
DEF ST_ADDR            EQU $4000
DEF ST_ATTR_BANK       EQU $25
DEF wStarterFlags      EQU $d7a1      ; legends.asm と 同じ バイト（ビット 0〜3 は セレビィ・鳥）
DEF ST_wKantoBadges    EQU $d570
DEF ST_wScriptVar      EQU $d165
; ハナダの こうかんの 話の 家（CERULEAN_TRADE_SPEECH_HOUSE）
DEF ST_CH_ATTR         EQU $5d7d
DEF ST_CH_SRC_BANK     EQU $28
DEF ST_CH_START        EQU $6efe
DEF ST_CH_EVENTS       EQU $6f70
DEF ST_CH_OBJCOUNT     EQU $6f7f      ; 人の 数（4）
DEF ST_CH_END          EQU $6fb4
DEF ST_CH_X            EQU 6
DEF ST_CH_Y            EQU 3
; 24ばんどうろ（ROUTE_24）
DEF ST_R24_ATTR        EQU $56f9
DEF ST_R24_SRC_BANK    EQU $35
DEF ST_R24_START       EQU $779c
DEF ST_R24_EVENTS      EQU $79e5
DEF ST_R24_OBJCOUNT    EQU $79ea      ; 人の 数（1）
DEF ST_R24_END         EQU $79f8
DEF ST_R24_X           EQU 9
DEF ST_R24_Y           EQU 1
; クチバシティ（VERMILION_CITY）
DEF ST_VC_ATTR         EQU $55f1
DEF ST_VC_SRC_BANK     EQU $35
DEF ST_VC_START        EQU $6df6
DEF ST_VC_EVENTS       EQU $7109
DEF ST_VC_OBJCOUNT     EQU $7168      ; 人の 数（6）
DEF ST_VC_END          EQU $71b7
DEF ST_VC_X            EQU 19
DEF ST_VC_Y            EQU 15
; ジュンサーの 絵
DEF ST_SPRITE_JENNY    EQU $58        ; SPRITE_OLD_LINK_RECEPTIONIST（金では 使われて いない）
DEF ST_OWSPRITES       EQU $47b0      ; OverworldSprites（バンク$05。6バイトずつ）
DEF ST_VERMILION_SPRITES EQU $46df    ; VermilionGroupSprites（バンク$05。9番めが SPRITE_BIKER）
ENDC
IF !DEF(ST_OWSPRITES_BANK)
DEF ST_OWSPRITES_BANK  EQU $05
ENDC

; 足した イベントの 表・ジュンサーの 絵の 場所（クリスタルは src/starters_crystal.asm で きめる）
IF !DEF(ST_CH_NEWEV)
DEF ST_CH_NEWEV        EQU $7c00      ; ST_BANK
DEF ST_R24_NEWEV       EQU $7d00      ; ST_BANK
DEF ST_VC_NEWEV        EQU $7c00      ; ST_BANK_VER
DEF ST_JENNY_ADDR      EQU $6000      ; ST_BANK
DEF STARTER_CH_COUNT   EQU 4          ; もとの 人の 数
DEF STARTER_R24_COUNT  EQU 1
DEF STARTER_VC_COUNT   EQU 6
ENDC

DEF STARTER_BULBASAUR  EQU 4
DEF STARTER_CHARMANDER EQU 5
DEF STARTER_SQUIRTLE   EQU 6

;---------------------------------------------------------------- マップの 写し
MACRO starter_map ; 名前, 写す バンク, イベントの 表の 場所
SECTION "starters \1 attr", ROMX[ST_\1_ATTR + 6], BANK[ST_ATTR_BANK]
	db \2
	dw ST_\1_START
	dw Starter\1_Events
SECTION "starters \1 copy", ROMX[ST_\1_START], BANK[\2]
	INCBIN "base.gbc", ST_\1_SRC_BANK * $4000 + ST_\1_START - $4000, ST_\1_END - ST_\1_START
SECTION "starters \1 events", ROMX[\3], BANK[\2]
Starter\1_Events:
	INCBIN "base.gbc", ST_\1_SRC_BANK * $4000 + ST_\1_EVENTS - $4000, ST_\1_OBJCOUNT - ST_\1_EVENTS
	db STARTER_\1_COUNT + 1
	INCBIN "base.gbc", ST_\1_SRC_BANK * $4000 + ST_\1_OBJCOUNT + 1 - $4000, ST_\1_END - ST_\1_OBJCOUNT - 1
ENDM
	starter_map CH,  ST_BANK, ST_CH_NEWEV
	db SPRITE_LASS, ST_CH_Y + 4, ST_CH_X + 4, SPRITEMOVEDATA_STANDING_DOWN, 0, -1, -1
	db PAL_NPC_BLUE << 4 | OBJECTTYPE_SCRIPT, 0
	dw StarterCH_Stub, -1
StarterCH_Stub:
	farsjump StarterBulbasaurScript
	starter_map R24, ST_BANK, ST_R24_NEWEV
	db SPRITE_COOLTRAINER_M, ST_R24_Y + 4, ST_R24_X + 4, SPRITEMOVEDATA_STANDING_DOWN, 0, -1, -1
	db PAL_NPC_BLUE << 4 | OBJECTTYPE_SCRIPT, 0
	dw StarterR24_Stub, -1
StarterR24_Stub:
	farsjump StarterCharmanderScript
	starter_map VC,  ST_BANK_VER, ST_VC_NEWEV
	db ST_SPRITE_JENNY, ST_VC_Y + 4, ST_VC_X + 4, SPRITEMOVEDATA_STANDING_DOWN, 0, -1, -1
	db PAL_NPC_BLUE << 4 | OBJECTTYPE_SCRIPT, 0
	dw StarterVC_Stub, -1
StarterVC_Stub:
	farsjump StarterSquirtleScript

;---------------------------------------------------------------- ジュンサーの 絵
SECTION "starters jenny header", ROMX[ST_OWSPRITES + (ST_SPRITE_JENNY - 1) * 6], BANK[ST_OWSPRITES_BANK]
	dw StarterJennyGFX
IF !DEF(ST_JENNY_SPRITETYPE)
DEF ST_JENNY_SPRITETYPE EQU 1                  ; WALKING_SPRITE（金銀）
ENDC
	db 12 * 16, BANK(StarterJennyGFX), ST_JENNY_SPRITETYPE, 1      ; 12タイル（＋歩く 12タイル）・PAL_OW_BLUE
IF DEF(ST_VERMILION_SPRITES)
SECTION "starters vermilion sprites", ROMX[ST_VERMILION_SPRITES + 8], BANK[$05]
	db ST_SPRITE_JENNY                            ; SPRITE_BIKER の かわり
ENDC                                              ; （クリスタルは もとから クチバの 表に $58 が ある）
SECTION "starters jenny gfx", ROMX[ST_JENNY_ADDR], BANK[ST_BANK]
StarterJennyGFX:
	INCLUDE "src/starters_jenny.inc"

;---------------------------------------------------------------- 本体
SECTION "starters", ROMX[ST_ADDR], BANK[ST_BANK]
; callasm：wScriptVar = 1（もう もらった）。c = ビット
Starter_Check:
	call Starter_Mask
	ld a, [wStarterFlags]
	and b
	ld a, 0
	jr z, .set
	inc a
.set
	ld [ST_wScriptVar], a
	ret
Starter_Set:
	call Starter_Mask
	ld a, [wStarterFlags]
	or b
	ld [wStarterFlags], a
	ret
Starter_Mask:
	ld b, 1
	ld a, c
	and a
	ret z
.loop
	sla b
	dec a
	jr nz, .loop
	ret

; フシギダネ（ハナダの 家の 女の人）
StarterBulbasaurScript:
	faceplayer
	opentext
	callasm .check
	iftrue .after
	writetext StarterText_Bulbasaur1
	writetext StarterText_Bulbasaur2
	yesorno
	iffalse .no
	writetext StarterText_Bulbasaur3
	promptbutton
	writetext StarterText_GotBulbasaur
	playsound SFX_ITEM
	waitsfx
	givepoke BULBASAUR, 10
	ifequal 2, .done                  ; 2 = ボックスも いっぱい
	callasm .set
.done
	closetext
	end
.no
	writetext StarterText_Bulbasaur5
	waitbutton
	closetext
	end
.after
	writetext StarterText_Bulbasaur4
	waitbutton
	closetext
	end
.check
	ld c, STARTER_BULBASAUR
	jp Starter_Check
.set
	ld c, STARTER_BULBASAUR
	jp Starter_Set

; ヒトカゲ（24ばんどうろの 男の人）
StarterCharmanderScript:
	faceplayer
	opentext
	callasm .check
	iftrue .after
	writetext StarterText_Charmander1
	yesorno
	iffalse .no
	writetext StarterText_Charmander2
	promptbutton
	writetext StarterText_GotCharmander
	playsound SFX_ITEM
	waitsfx
	givepoke CHARMANDER, 10
	ifequal 2, .done                  ; 2 = ボックスも いっぱい
	callasm .set
.done
	closetext
	end
.no
	writetext StarterText_Charmander3
	waitbutton
	closetext
	end
.after
	writetext StarterText_Charmander4
	waitbutton
	closetext
	end
.check
	ld c, STARTER_CHARMANDER
	jp Starter_Check
.set
	ld c, STARTER_CHARMANDER
	jp Starter_Set

; ゼニガメ（クチバの ジュンサー。オレンジバッジ）
StarterSquirtleScript:
	faceplayer
	opentext
	callasm .check
	iftrue .after
	callasm .badge
	iffalse .nobadge
	writetext StarterText_Squirtle2
	yesorno
	iffalse .no
	writetext StarterText_Squirtle3
	promptbutton
	writetext StarterText_GotSquirtle
	playsound SFX_ITEM
	waitsfx
	givepoke SQUIRTLE, 10
	ifequal 2, .done                  ; 2 = ボックスも いっぱい
	callasm .set
.done
	closetext
	end
.nobadge
	writetext StarterText_Squirtle1
	waitbutton
	closetext
	end
.no
	writetext StarterText_Squirtle4
	waitbutton
	closetext
	end
.after
	writetext StarterText_Squirtle5
	waitbutton
	closetext
	end
.check
	ld c, STARTER_SQUIRTLE
	jp Starter_Check
.set
	ld c, STARTER_SQUIRTLE
	jp Starter_Set
.badge
	ld a, [ST_wKantoBadges]
	and 1 << 2                        ; オレンジバッジ（THUNDERBADGE）
	ld a, 0
	jr z, .badge_set
	inc a
.badge_set
	ld [ST_wScriptVar], a
	ret

; <PLAYER>は ○○を てにいれた！（ピカチュウ版の ポケモンを もらった ときの 文と 同じ。音も 同じ どうぐの 音）
StarterText_GotBulbasaur:
	db $00, $52, "は", $4f, "フシギダネを　てにいれた！", $57
StarterText_GotCharmander:
	db $00, $52, "は", $4f, "ヒトカゲを　てにいれた！", $57
StarterText_GotSquirtle:
	db $00, $52, "は", $4f, "ゼニガメを　てにいれた！", $57

INCLUDE "src/starters_texts.inc"
