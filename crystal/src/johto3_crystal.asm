; ジョウトの 御三家を 3びき とも もらえる … クリスタル（日本版）用（251匹そろう版 src/edition251_crystal.asm の その 部分だけ）
;  ・ウツギ はかせの けんきゅうじょで 1ぴき えらぶと、のこりの 2ひきも もらえる（えらんだ ポケモンだけ きのみを もつ）。
;    ライバルの ポケモンは えらんだ 1ぴき（EVENT_GOT_〜_FROM_ELM）で きまるので 元の まま。
;  ・まえの セーブデータ（もう 1ぴき もらった あと）では、ウツギ はかせに はなしかけると のこりの 2ひきを くれる。
;  ・しるしは wEdFlags（$d837。wTimeOfDayPal の あとの 使われていない バイト。レポートに 書かれる）の ビット4〜6
;    （251匹そろう版と 同じ。251匹そろう版と いっしょには 組まない ― 同じ 物が edition251 に 入って いる）。
INCLUDE "src/safari/crystal_includes.asm"   ; pokecrystal の 定数・マクロ（スクリプトの 命令の 番号は 英語版 金銀）
INCLUDE "src/charmap_jp.inc"

DEF ED_BANK            EQU $6e        ; あいている バンク（$4000〜 けんきゅうじょ、$6e00〜 ウツギ はかせ）
DEF ED_wEventFlags     EQU $da65
DEF ED_wScriptVar      EQU $c2dd
DEF wEdFlags           EQU $d837

; ---- ごさんけ 3びき ---------------------------------------------------------
; ElmsLab の givepoke（5バイト）を farscall（4バイト）＋ waitsfx に かえる
MACRO ed_starter_hook
SECTION "johto3 starter hook \1", ROMX[\1], BANK[$1b]
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

SECTION "johto3 starters", ROMX[$4000], BANK[ED_BANK]
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

; ---- まえの セーブデータ：ウツギ はかせが のこりの 2ひきを くれる ----------------
; EVENT_GOT_A_POKEMON_FROM_ELM（$1a）の あと、えらんで いない（EVENT_GOT_〜_FROM_ELM $1b・$1c・$1d が ない）で
; まだ もらって いない（wEdFlags ビット 4 ヒノアラシ・5 ワニノコ・6 チコリータ）ポケモンを くれる。
; 新しく はじめた ときは けんきゅうじょで 3びき もらった とき ビット 4〜6 を ぜんぶ たてる。
; ウツギ はかせ（ElmsLab の 1人め）の スクリプトの 場所（$1b:$7302。元は $61f5）を $1b:$7ff8 の farsjump EdElmScript に。
DEF ED_ELM0 EQU 4
SECTION "johto3 elm ptr", ROMX[$7302], BANK[$1b]
	dw $7ff8
SECTION "johto3 elm stub", ROMX[$7ff8], BANK[$1b]
	farsjump EdElmScript

SECTION "johto3 elm", ROMX[$6e00], BANK[ED_BANK]
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
	db $4b, $1b
	dw $68ba                         ; 「〜を もらった！」
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
	db farsjump_command, $1b          ; 元の ウツギ はかせの スクリプト
	dw $61f5
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

