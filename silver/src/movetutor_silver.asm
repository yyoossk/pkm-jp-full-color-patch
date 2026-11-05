; 技教えの人：銀 日本版（後期版）。src/movetutor.asm（金）から 作った もの。
; 銀の コガネの スクリプト・イベントの 場所（$34:$4000〜$44ee・callback $4003・人の 数 $4437）・殿堂入り イベント $0044・
; special DisplayCoinCaseBalance $4e・wDailyFlags2 ビット6 は 金と 同じ（銀の バイトで 確かめた）。ちがうのは LearnMove と 置き場所だけ。
; 技教えの 人（クリスタルの コガネシティの 人と 同じ。金 日本版）
;
; ・殿堂入りの あと、コインケースを もっていれば、水よう日・土よう日に コガネシティ（12, 22。ゲームコーナーの 前）に 出る。
; ・コイン 4000まいで かえんほうしゃ・10まんボルト・れいとうビーム の どれかを 1回 おしえる（その日は もう 出ない）。
; ・おぼえられる ポケモンは クリスタルと 同じ（src/movetutor_compat.inc。tools/movetutor_gen.py で pokecrystal から 作る）。
;
; しくみ
;   ・コガネシティの スクリプトと イベントの 表（バンク$34 $4000〜$44ee）を この バンクの 同じ 場所に 写し、
;     マップの 見出しの スクリプトの バンクを この バンクに する（バンク$34 には 人を 足す 空きが ないため）。
;     写した 所の うち、マップに 入った ときの callback の 場所と、人の 数・人（さいごに 技教えの 人）だけ かえる。
;   ・callback：元の 中身（setflag ×2）の あと、出る 日なら EVENT_MOVETUTOR_HIDDEN を 消す、ちがえば たてる。
;   ・おしえる：手もちを えらぶ（SelectMonFromParty）→ おぼえられるか（表）→ もう おぼえて いないか（KnowsMove）→
;     メニューの 画面で LearnMove（わざを おもいださせる 人と 同じ）。
;
; 銀・クリスタルに 入れるとき（クリスタルは もとから あるので いらない）：下の DEF を その ROM の 値に する

INCLUDE "includes.asm"
INCLUDE "src/jp_all_silver.inc"
INCLUDE "src/charmap_jp.inc"

IF !DEF(MT_ATTR)
DEF MT_ATTR             EQU $4ec5   ; GoldenrodCity_MapAttributes（バンク$25）
DEF MT_ATTR_BANK        EQU $25
DEF MT_SRC_BANK         EQU $34     ; コガネの スクリプト・イベントの バンク
DEF MT_SRC_START        EQU $4000   ; GoldenrodCity_MapScripts
DEF MT_SRC_CALLBACK     EQU $4003   ; callback の 場所（dw）
DEF MT_SRC_OBJCOUNT     EQU $4437   ; 人の 数（14）
DEF MT_SRC_END          EQU $44ee   ; イベントの 表の おわり
DEF MT_CALLBACK_ORIG    EQU $4005   ; 元の callback（setflag $0045 / setflag $0015 / endcallback）
DEF MT_EVENT_BEAT_E4    EQU $0044   ; EVENT_BEAT_ELITE_FOUR（日本版の 番号）
DEF EVENT_MOVETUTOR_HIDDEN EQU $07fd ; 使われていない イベントフラグ（サファリの $7f0〜$7fc の 次）
DEF MT_SPECIAL_COINS    EQU $4e     ; special DisplayCoinCaseBalance（日本版の 番号）
DEF MT_wDailyFlags2     EQU $d92f
DEF MT_wEventFlags      EQU $d7aa
DEF MT_DAILY_BIT        EQU 6       ; wDailyFlags2 の 使われていない ビット（その日 もう おしえた）
DEF MT_EVOSATTACKS_DUMMY EQU 0
DEF MT_LEARNMOVE        EQU $67ae   ; 銀（金は $67e9）
DEF MT_LEARNMOVE_BANK   EQU $01
DEF MT_KNOWSMOVE        EQU $7f70
DEF MT_KNOWSMOVE_BANK   EQU $03
DEF MT_SELECTMON        EQU $4000
DEF MT_SELECTMON_BANK   EQU $14
DEF MT_BANK             EQU $48
DEF MT_ADDR             EQU $5000
ENDC
; コガネの 人は 14人で いっぱい（日本版は 14人まで）なので、殿堂入りの あとは ずっと 出ない
; ロケット団の 見はり（8人め。EVENT_GOLDENROD_CITY_ROCKET_SCOUT：ラジオとうを とりもどすと ずっと 消える）の
; 人の 表（wMapObjects）を、マップに 入った ときに 技教えの 人に 書きかえる。
DEF MT_SLOT EQU 9                   ; wMapObjects の 何番め（日本版は 1人めが 2番）
DEF MT_wMapObjects EQU $d438
DEF MT_OBJ EQU MT_SLOT              ; disappear の 番号

SECTION "movetutor attributes", ROMX[MT_ATTR + 6], BANK[MT_ATTR_BANK]
	db MT_BANK

; ---- コガネの スクリプトと イベントの 写し（同じ 場所）
SECTION "movetutor goldenrod copy", ROMX[MT_SRC_START], BANK[MT_BANK]
	INCBIN "base.gbc", MT_SRC_BANK * $4000 + MT_SRC_START - $4000, MT_SRC_CALLBACK - 1 - MT_SRC_START
	db MAPCALLBACK_OBJECTS              ; 元は MAPCALLBACK_NEWMAP（人を 読んだ あとに 呼ばれるように）
	dw MoveTutor_Callback
	INCBIN "base.gbc", MT_SRC_BANK * $4000 + MT_SRC_CALLBACK + 2 - $4000, MT_SRC_END - MT_SRC_CALLBACK - 2

SECTION "movetutor", ROMX[MT_ADDR], BANK[MT_BANK]
MoveTutor_Callback:
	db setflag_command               ; 元の 中身（setflag $0045 / setflag $0015）
	dw $0045
	db setflag_command
	dw $0015
	callasm MoveTutor_CheckAppear
	iffalse .hide
	callasm MoveTutor_SetObject
	clearevent EVENT_MOVETUTOR_HIDDEN
	endcallback
.hide
	setevent EVENT_MOVETUTOR_HIDDEN
	endcallback

; wScriptVar = 1：出る（殿堂入り・コインケース・水よう日か 土よう日・今日 まだ おしえて いない）
MoveTutor_CheckAppear:
	xor a
	ld [wScriptVar], a
	ld a, [MT_wEventFlags + MT_EVENT_BEAT_E4 / 8]
	bit MT_EVENT_BEAT_E4 % 8, a
	ret z
	ld a, COIN_CASE
	ld [wCurItem], a
	ld hl, wNumItems                 ; CheckItem は wNumItems を わたすと どうぐの 種類で ポケットを えらぶ
                                 ; （金の 元は wNumKeyItems で、たいせつなものの 並びに よっては 見つからなかった）
	call J_CheckItem
	ret nc
	call J_GetWeekday
	cp WEDNESDAY
	jr z, .day
	cp SATURDAY
	ret nz
.day
	ld a, [MT_wDailyFlags2]
	bit MT_DAILY_BIT, a
	ret nz
	ld a, 1
	ld [wScriptVar], a
	ret

MoveTutorScript:
	faceplayer
	opentext
	writetext MoveTutor_AskText
	yesorno
	iffalse .refused
	db special_command
	dw MT_SPECIAL_COINS
	writetext MoveTutor_CostText
	yesorno
	iffalse .refused2
	checkcoins 4000
	ifequal HAVE_LESS, .nocoins
	writetext MoveTutor_WhichText
	loadmenu .MenuHeader
	verticalmenu
	closewindow
	ifequal 1, .ok
	ifequal 2, .ok
	ifequal 3, .ok
	sjump .but
.ok
	callasm MoveTutor_SetMove
	writetext MoveTutor_WhoText
	promptbutton
.choose
	callasm MoveTutor_Teach
	ifequal 0, .but
	ifequal 2, .cannot
	ifequal 3, .choose_again          ; もう おぼえて いる・おぼえなかった
	writetext MoveTutor_DoneText
	promptbutton
	takecoins 4000
	waitsfx
	playsound SFX_TRANSACTION
	db special_command
	dw MT_SPECIAL_COINS
	writetext MoveTutor_ByeText
	waitbutton
	closetext
	callasm MoveTutor_SetToday
	playsound SFX_ENTER_DOOR
	disappear MT_OBJ
	waitsfx
	end
.cannot
	writetext MoveTutor_CannotText
	promptbutton
.choose_again
	writetext MoveTutor_WhoText
	promptbutton
	sjump .choose
.but
	writetext MoveTutor_ButText
	waitbutton
	closetext
	end
.refused
	writetext MoveTutor_RefusedText
	waitbutton
	closetext
	end
.refused2
	writetext MoveTutor_Refused2Text
	waitbutton
	closetext
	end
.nocoins
	writetext MoveTutor_NoCoinsText
	waitbutton
	closetext
	end

.MenuHeader:
	db MENU_BACKUP_TILES
	menu_coords 0, 2, 15, 11
	dw .MenuData
	db 1
.MenuData:
	db STATICMENU_CURSOR
	db 4
	db "かえんほうしゃ@"
	db $f7, $f6, "まん", $1c, "ルト@"     ; 10まんボルト
	db "れいとうビーム@"
	db "やめる@"

; 見はりの 人の 表を 技教えの 人に する（クリスタルと 同じ 場所・見た目・動き）
MoveTutor_SetObject:
	ld hl, MT_wMapObjects + MT_SLOT * 16 + 1
	ld de, .data
	ld c, .end - .data
.copy
	ld a, [de]
	inc de
	ld [hli], a
	dec c
	jr nz, .copy
	ret
.data
	db SPRITE_POKEFAN_M, 22 + 4, 12 + 4, SPRITEMOVEDATA_SPINRANDOM_SLOW, 0, -1, -1
	db PAL_NPC_RED << 4 | OBJECTTYPE_SCRIPT, 0
	dw MoveTutorScript, EVENT_MOVETUTOR_HIDDEN
.end

MoveTutor_SetToday:
	ld hl, MT_wDailyFlags2
	set MT_DAILY_BIT, [hl]
	ret

; wScriptVar（1〜3）→ wPutativeTMHMMove と わざの 名前（wStringBuffer2）
MoveTutor_SetMove:
	ld a, [wScriptVar]
	ld [wMoveTutorWhich], a
	ld c, a
	ld b, 0
	ld hl, MoveTutor_Moves - 1
	add hl, bc
	ld a, [hl]
	ld [wPutativeTMHMMove], a
	ld [wNamedObjectIndex], a
	call J_GetMoveName
	jp J_CopyName1
DEF wMoveTutorWhich EQU wBufferMon + 32  ; えらんだ わざ（1〜3）

MoveTutor_Moves:
	db FLAMETHROWER, THUNDERBOLT, ICE_BEAM

; 手もちを えらんで おしえる。wScriptVar：0 = やめた、1 = おぼえた、2 = おぼえられない、3 = もう おぼえている・やめた
MoveTutor_Teach:
	ld a, [wPutativeTMHMMove]
	push af
	ld a, MT_SELECTMON_BANK
	ld hl, MT_SELECTMON
	rst $08
	pop bc                           ; b = わざ（SelectMonFromParty の あいだに かわらないように）
	ld a, b
	ld [wPutativeTMHMMove], a
	ld a, 0
	jp c, .set
	ld a, [wCurPartyMon]
	ld hl, wPartyMonNicknames
	call J_GetNickname               ; 名前 → wStringBuffer1（文で 使う）
	ld a, [wCurPartySpecies]
	cp EGG
	ld a, 2
	jr z, .set
	; おぼえられるか：表の ビット（図鑑の 番号 - 1）
	ld a, [wMoveTutorWhich]
	dec a
	swap a
	add a                            ; × 32
	ld e, a
	ld d, 0
	ld hl, MoveTutorCompat_FLAMETHROWER
	add hl, de
	ld a, [wCurPartySpecies]
	dec a
	ld c, a
	srl a
	srl a
	srl a
	ld e, a
	add hl, de
	ld a, c
	and 7
	ld b, a
	ld a, [hl]
	inc b
.shift
	dec b
	jr z, .bit
	rrca
	jr .shift
.bit
	and 1
	ld a, 2
	jr z, .set
	; もう おぼえて いる？（元の KnowsMove：おぼえて いれば 文を 出して キャリー）
	ld a, MT_KNOWSMOVE_BANK
	ld hl, MT_KNOWSMOVE
	rst $08
	ld a, 3
	jr c, .set
	; メニューの 画面で おぼえさせる（わざを おもいださせる 人と 同じ）
	call J_FadeToMenu
	call J_ClearBGPalettes
	call J_ClearScreen
	call J_DelayFrame
	ld b, SCGB_MOVE_LIST
	call J_GetSGBLayout
	ld a, MT_LEARNMOVE_BANK
	ld hl, MT_LEARNMOVE
	rst $08
	push bc
	call J_CloseSubmenu
	pop bc
	ld a, b
	and a
	ld a, 3
	jr z, .set
	ld a, 1
.set
	ld [wScriptVar], a
	ret

INCLUDE "src/movetutor_compat.inc"

MoveTutor_AskText:
	db $00, "わしは　ポケモンに", $4f
	db "すごい　わざを　おしえられるぞ", $51
	db "わざを　おしえて　ほしいか？", $57
MoveTutor_CostText:
	db $00, "コイン　", $fa, $f6, $f6, $f6, "まい　だが", $4f
	db "いいか？", $57
MoveTutor_RefusedText:
	db $00, "そうか……", $4f
	db "すごい　わざ　なのに……", $57
MoveTutor_Refused2Text:
	db $00, "そうか　ざんねんじゃ", $4f
	db "いえに　かえって", $55
	db "おかねを　とってこんと……", $57
MoveTutor_WhichText:
	db $00, "ワハハ！", $4f
	db "こうかいは　させんぞ！", $51
	db "どの　わざを　おしえようか？", $57
MoveTutor_WhoText:
	db $00, "どの　ポケモンに", $4f
	db "おしえようか？", $57
MoveTutor_CannotText:
	db $00, "その　ポケモンには", $4f
	db "おしえられんのう", $57
MoveTutor_DoneText:
	db $00, "この　わざの　すごさが", $4f
	db "わかれば　きみも", $55
	db "いちにんまえの　トレーナーじゃ！", $57
MoveTutor_ByeText:
	db $00, "ワハハ！", $4f
	db "さらばじゃ！", $57
MoveTutor_ButText:
	db $00, "そ　そんな……", $57
MoveTutor_NoCoinsText:
	db $00, "……　コインが", $4f
	db "たりんようじゃな……", $57
