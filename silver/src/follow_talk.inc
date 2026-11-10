; 連れ歩きに 話しかけた とき（follow.asm から INCLUDE。銀）
;   鳴いて → 気持ちの アイコン → 会話。会話は 表（follow_talk_data.inc）を 上から 見て、さいしょに 合った 行の 文
;   （2つ 以上 あれば ランダム）。いちばん 下の「ふつう」で、たまに（1/32）どうぐ（きんのたま）を 見つける。
;   ピカチュウ方式は 銀には 入って いなかったので、ピカチュウは 表情の 絵（follow_pika.inc）。

DEF FW_LAST_TALKED     EQU $fe
DEF FW_PlayMonCry      EQU $395d
DEF FW_MapTextbox      EQU $2770
DEF FW_GetWorldMapLocation EQU $2d44
DEF FW_GetFarByte      EQU $30e4
DEF FW_BASEDATA_BANK   EQU $14
DEF FW_BASEDATA        EQU $5aa9
DEF FW_PartyMonNicknames EQU $db34
DEF wPartyMonNicknames EQU $cf87       ; 連れ歩く ポケモンの なまえを 写す 所（wStringBuffer1。会話の 文の 〈なまえ〉）
DEF wMapGroup          EQU $d9c6
DEF wMapNumber         EQU $d9c7
DEF wScriptPos         EQU $d153
DEF FW_NUGGET          EQU $24
; 調べる 間の 一時（セーブの 使われていない 所 $d770〜$d77e）
DEF wFwT               EQU $d770
DEF wFwT_Species       EQU wFwT + 0
DEF wFwT_Type1         EQU wFwT + 1
DEF wFwT_Type2         EQU wFwT + 2
DEF wFwT_Landmark      EQU wFwT + 3
DEF wFwT_Group         EQU wFwT + 4
DEF wFwT_Number        EQU wFwT + 5
DEF wFwT_Status        EQU wFwT + 6
DEF wFwT_Text          EQU wFwT + 7   ; 2バイト

; スクリプトの 命令（日本版の 番号。銀も クリスタル日本版と 同じ 番号だった。ScriptCommandTable $25:$6be4）
MACRO fws_faceplayer
	db $6a
ENDM
MACRO fws_callasm
	db $0e
	db BANK(\1)
	dw \1
ENDM
MACRO fws_showemote ; アイコン, 時間
	db $74, \1, FW_LAST_TALKED, \2
ENDM
MACRO fws_opentext
	db $47
ENDM
MACRO fws_writetext
	db $4c
	dw \1
ENDM
MACRO fws_yesorno
	db $4e
ENDM
MACRO fws_iffalse
	db $08
	dw \1
ENDM
MACRO fws_sjump
	db $03
	dw \1
ENDM
MACRO fws_verbosegiveitem ; どうぐ, 数
	db $9d, \1, \2
ENDM
MACRO fws_waitbutton
	db $53
ENDM
MACRO fws_closetext
	db $49
ENDM
MACRO fws_end
	db $90
ENDM

FollowerTalkScript:
	fws_faceplayer
	fws_callasm Fw_Pick               ; 鳴いて、会話を えらび、アイコンの スクリプトへ とぶ
	fws_end

FwEmoteScripts:
	dw FwEmoteScript0, FwEmoteScript1, FwEmoteScript2, FwEmoteScript3
	dw FwEmoteScript4, FwEmoteScript5, FwEmoteScript6
FOR N, 7
FwEmoteScript{d:N}:
	fws_showemote N, 15
	fws_sjump FwTalkCommon
ENDR
FwTalkCommon:
	fws_opentext
	fws_callasm Fw_PrintChosen
	fws_waitbutton
	fws_closetext
	fws_end

FwItemScript:
	fws_showemote 0, 15               ; ！
	fws_opentext
	fws_writetext FwText_Found
	fws_yesorno
	fws_iffalse FwItemScript_Done
	fws_verbosegiveitem FW_NUGGET, 1
FwItemScript_Done:
	fws_closetext
	fws_end

FwText_Found:
	db $01
	dw wPartyMonNicknames
	db $00, "は", $4f, "なにか　みつけた　ようだ", $51, "ひろいますか？", $57

Fw_Cry:
	call Fw_Species
	cp FW_EGG
	ret z
	jp FW_PlayMonCry

; 連れ歩く ポケモンの 状態（a）・なつき度（a）
Fw_Status:
	push hl
	push de
	call Fw_MonAddr
	ld de, $20
	add hl, de
	ld a, [hl]
	pop de
	pop hl
	ret
Fw_Happy:
	push hl
	push de
	call Fw_MonAddr
	ld de, $1b
	add hl, de
	ld a, [hl]
	pop de
	pop hl
	ret

; 会話を えらぶ（callasm）
Fw_Pick:
	; なまえを 写す（文の 〈なまえ〉）
	call Fw_Index
	jr nc, .idx
	xor a
.idx
	ld l, a
	ld h, 0
	ld e, l
	ld d, h
	add hl, hl
	add hl, de
	add hl, hl                        ; × 6
	ld de, FW_PartyMonNicknames
	add hl, de
	ld de, wPartyMonNicknames
	ld c, 6
.nick
	ld a, [hli]
	ld [de], a
	inc de
	dec c
	jr nz, .nick
	call Fw_Species
	cp FW_PIKACHU
	jr nz, .notpika
	call Fw_PikaChoose                ; 鳴き声は 絵と いっしょに
	jp .jump
.notpika
	call Fw_Cry
	; しらべる ものを 集める
	call Fw_Species
	ld [wFwT_Species], a
	ld a, $ff
	ld [wFwT_Type1], a
	ld [wFwT_Type2], a
	call Fw_Species
	cp FW_EGG
	jr z, .notype
	dec a
	ld l, a
	ld h, 0
	add hl, hl
	add hl, hl
	add hl, hl
	add hl, hl
	add hl, hl                        ; × 32
	ld de, FW_BASEDATA + 7
	add hl, de
	push hl
	ld a, FW_BASEDATA_BANK
	call FW_GetFarByte
	ld [wFwT_Type1], a
	pop hl
	inc hl
	ld a, FW_BASEDATA_BANK
	call FW_GetFarByte
	ld [wFwT_Type2], a
.notype
	ld a, [wMapGroup]
	ld [wFwT_Group], a
	ld b, a
	ld a, [wMapNumber]
	ld [wFwT_Number], a
	ld c, a
	call FW_GetWorldMapLocation
	ld [wFwT_Landmark], a
	call Fw_Status
	ld [wFwT_Status], a
	call Fw_Species
	cp FW_EGG
	jr nz, .scan
	xor a
	ld [wFwT_Status], a               ; タマゴは 状態を 見ない

.scan
	ld hl, FollowerTalkTable
.row
	ld a, [hl]
	cp $fe
	jp z, .default
	push hl
	; 種類
	and a
	jr z, .ok_species
	ld b, a
	ld a, [wFwT_Species]
	cp b
	jr nz, .next
.ok_species
	inc hl
	; タイプ
	ld a, [hl]
	cp $ff
	jr z, .ok_type
	ld b, a
	ld a, [wFwT_Type1]
	cp b
	jr z, .ok_type
	ld a, [wFwT_Type2]
	cp b
	jr nz, .next
.ok_type
	inc hl
	; ランドマーク
	ld a, [hl]
	cp $ff
	jr z, .ok_landmark
	ld b, a
	ld a, [wFwT_Landmark]
	cp b
	jr nz, .next
.ok_landmark
	inc hl
	; マップ
	ld a, [hli]
	ld b, a
	ld a, [hl]
	ld c, a
	or b
	jr z, .ok_map
	ld a, [wFwT_Group]
	cp b
	jr nz, .next
	ld a, [wFwT_Number]
	cp c
	jr nz, .next
.ok_map
	inc hl
	; 状態
	ld a, [hl]
	and a
	jr z, .ok_status
	ld b, a
	ld a, [wFwT_Status]
	and b
	jr z, .next
.ok_status
	inc hl
	; イベントフラグ
	ld a, [hli]
	ld e, a
	ld a, [hl]
	ld d, a
	and e
	inc a
	jr z, .ok_event                   ; $ffff
	push hl
	ld b, 2                           ; CHECK_FLAG
	call FW_EventFlagAction
	pop hl
	ld a, c
	and a
	jr z, .next
.ok_event
	inc hl
	pop de                            ; 行の はじめ（すてる）
	jr .match
.next
	pop hl
	ld de, FW_TALK_ROW
	add hl, de
	jr .row

.match
	; hl = アイコン
	ld a, [hli]
	push af
	ld a, [hli]
	ld h, [hl]
	ld l, a                           ; hl = 文の 表
	; いちばん 下の「ふつう」なら たまに どうぐ
	push hl
	ld de, FwTexts_Default
	ld a, l
	cp e
	jr nz, .choose
	ld a, h
	cp d
	jr nz, .choose
	call FW_Random
	cp 8
	jr nc, .choose
	pop hl
	pop af
	ld hl, FwItemScript
	jr .jump
.choose
	pop hl
	ld a, [hli]                       ; 文の 数
	ld c, a
	push hl
	call FW_Random
	pop hl
.mod
	cp c
	jr c, .got
	sub c
	jr .mod
.got
	add a
	ld e, a
	ld d, 0
	add hl, de
	ld a, [hli]
	ld [wFwT_Text], a
	ld a, [hl]
	ld [wFwT_Text + 1], a
	pop af
	add a
	ld e, a
	ld d, 0
	ld hl, FwEmoteScripts
	add hl, de
	ld a, [hli]
	ld h, [hl]
	ld l, a
.jump
	ld a, l
	ld [wScriptPos], a
	ld a, h
	ld [wScriptPos + 1], a
	ret
.default
	; ここには 来ない（表の さいごは かならず 合う）
	ld hl, FwEmoteScript2
	jr .jump

Fw_PrintChosen:
	ld a, [wFwT_Text]
	ld l, a
	ld a, [wFwT_Text + 1]
	ld h, a
	ld b, FW_BANK
	jp FW_MapTextbox

INCLUDE "src/follow_talk_data.inc"
INCLUDE "src/follow_pika.inc"
INCLUDE "src/follow_pika_data.inc"
