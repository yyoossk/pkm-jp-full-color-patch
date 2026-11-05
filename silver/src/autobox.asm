; ボックスが いっぱいに なったら 自動で 次の ボックスに 切りかえる（ピカチュウ版フルカラーと 同じ。金 日本版）
;
; ・フィールドで いまの ボックスが いっぱい（30匹）なら、次の あいている ボックスに 切りかえて レポートを 書く。
;   「ポケモン ボックス１が いっぱいに なりました！ ／ ポケモン ボックス２に じどうで きりかえました！ ／
;     ボックスを きりかえたので レポートを かきました！」（ピカチュウ版の 文）
;   ぜんぶ いっぱいなら「ポケモン ボックスが ぜんぶ いっぱいです！ パソコンで ボックスを せいり してください」（1回だけ）。
; ・次の ボックスは いまの 次から じゅんに さがす（9 の 次は 1）。
; ・まだ 1回も レポートを 書いていないとき・ちがう 人の レポートが あるときは しない（ボックスの データが ないため）。
; しくみ
;   CheckTimeEvents（フィールドで 毎回）の .do_daily の さいごの farcall CheckPhoneCall を AutoBox_Check に かえる。
;   電話が かかってこなければ、いまの ボックスの 数を 見て、いっぱいなら スクリプト（CallScript）を 始める。
;   切りかえは パソコンの「ボックスを かえる」と 同じ（SaveBox → wCurBox → LoadBox → _SaveGameData）。

INCLUDE "includes.asm"
INCLUDE "src/jp_all.inc"

;---------------------------------------------------------------------
; ROM ごとに ちがう所（金 日本版）
;---------------------------------------------------------------------
IF !DEF(AUTOBOX_HOOK)
DEF AUTOBOX_HOOK        EQU $6890    ; CheckTimeEvents.do_daily の farcall CheckPhoneCall（6バイト）
DEF AUTOBOX_HOOK_BANK   EQU $25
DEF AUTOBOX_BANK        EQU $42      ; 処理・文章を 置く 空き
DEF AUTOBOX_ADDR        EQU $7000
DEF wAutoBoxDone        EQU $def0    ; 使われていない WRAM（1 = この いっぱいは もう 知らせた）
DEF wAutoBoxNew         EQU $def1    ; 〃 切りかえる ボックス（0〜）
DEF AUTOBOX_NUM_BOXES   EQU 9        ; 日本版
DEF AUTOBOX_MONS_PER_BOX EQU 30      ; 日本版
DEF AUTOBOX_SBOX_BANK   EQU 1        ; いまの ボックス（sBoxCount）
DEF AUTOBOX_SBOXCOUNT   EQU $ad10
ENDC
IF !DEF(AUTOBOX_BOXES)
; ボックス 1〜9 の 場所（GetBoxCount.BoxBankAddresses と 同じ。SRAM の バンク, アドレス）
MACRO AUTOBOX_BOXES
	db $2
	dw $a000
	db $2
	dw $a54a
	db $2
	dw $aa94
	db $2
	dw $afde
	db $2
	dw $b528
	db $2
	dw $ba72
	db $3
	dw $a000
	db $3
	dw $a54a
	db $3
	dw $aa94
ENDM
ENDC

MACRO jfarcall ; 日本版の 名前（J_ / JB_）で farcall
	ld a, JB_\1
	ld hl, J_\1
	rst $08
ENDM

SECTION "autobox hook", ROMX[AUTOBOX_HOOK], BANK[AUTOBOX_HOOK_BANK]
	ld a, BANK(AutoBox_Check)
	ld hl, AutoBox_Check

SECTION "autobox", ROMX[AUTOBOX_ADDR], BANK[AUTOBOX_BANK]
; キャリー = スクリプトを 始めた（元の CheckPhoneCall と 同じ）
AutoBox_Check:
	jfarcall CheckPhoneCall
	ret c
	ld a, [wSavedAtLeastOnce]
	and a
	ret z                            ; まだ レポートが ない（キャリーなし）
	ld a, [wCurBox]
	call AutoBox_Count
	cp AUTOBOX_MONS_PER_BOX
	jr c, .notfull
	ld a, [wAutoBoxDone]
	and a
	ret nz                           ; もう 知らせた
	jfarcall CompareLoadedAndSavedPlayerID
	ret nz                           ; ちがう 人の レポート
	ld a, 1
	ld [wAutoBoxDone], a
	ld a, BANK(AutoBox_Script)
	ld hl, AutoBox_Script
	call J_CallScript
	scf
	ret
.notfull
	xor a
	ld [wAutoBoxDone], a
	ret

; a = ボックス（0〜）→ a = その ボックスの ポケモンの 数（GetBoxCount と 同じ 読み方。farcall では a が もどらないので 自分で 読む）
AutoBox_Count:
	ld c, a
	ld a, [wCurBox]
	cp c
	jr z, .active
	ld b, 0
	ld hl, AutoBox_BoxAddresses
	add hl, bc
	add hl, bc
	add hl, bc
	ld a, [hli]
	call J_OpenSRAM
	ld a, [hli]
	ld h, [hl]
	ld l, a
	ld a, [hl]
	jp J_CloseSRAM
.active
	ld a, AUTOBOX_SBOX_BANK
	call J_OpenSRAM
	ld a, [AUTOBOX_SBOXCOUNT]
	jp J_CloseSRAM

AutoBox_Script:
	callasm AutoBox_Find
	iffalse .allfull
	playsound SFX_SAVE
	waitsfx
	callasm AutoBox_Switch
	opentext
	writetext AutoBox_SwitchedText
	closetext
	end
.allfull
	opentext
	writetext AutoBox_AllFullText
	closetext
	end

; wScriptVar = 1：あいている ボックスが ある（wAutoBoxNew、文の 番号を wStringBuffer1 に）/ 0：ぜんぶ いっぱい
AutoBox_Find:
	ld a, [wCurBox]
	ld c, a
	ld b, AUTOBOX_NUM_BOXES - 1
.loop
	inc c
	ld a, c
	cp AUTOBOX_NUM_BOXES
	jr c, .ok
	ld c, 0
.ok
	push bc
	ld a, c
	call AutoBox_Count
	pop bc
	cp AUTOBOX_MONS_PER_BOX
	jr c, .found
	dec b
	jr nz, .loop
	xor a
	ld [wScriptVar], a
	ret
.found
	ld a, c
	ld [wAutoBoxNew], a
	ld hl, wStringBuffer1
	ld a, [wCurBox]
	add $f7                          ; 「１」〜
	ld [hli], a
	ld a, $50                        ; 「@」
	ld [hli], a
	ld a, c
	add $f7
	ld [hli], a
	ld [hl], $50
	ld a, 1
	ld [wScriptVar], a
	ret

; パソコンの「ボックスを かえる」と 同じ（たずねないで 書く）
AutoBox_Switch:
	jfarcall PauseGameLogic
	jfarcall SaveBox
	ld a, [wAutoBoxNew]
	ld [wCurBox], a
	jfarcall LoadBox
	jfarcall _SaveGameData
	jfarcall ResumeGameLogic
	ret

; ピカチュウ版の 文（名前の 所だけ wStringBuffer1 に した）
AutoBox_BoxAddresses:
	AUTOBOX_BOXES

AutoBox_SwitchedText: ; ポケモン ボックス１が いっぱいに なりました！ ポケモン ボックス２に じどうで きりかえました！ ボックスを きりかえたので レポートを かきました！
	db $00, $54, $7f, $1c, $ac, $87, $8c, $50
	db $01
	dw wStringBuffer1
	db $00, $26, $4f, $b2, $df, $44, $b2, $c6, $7f, $c5, $d8, $cf, $bc, $c0, $e7, $51, $54, $7f, $1c, $ac, $87, $8c, $50
	db $01
	dw wStringBuffer1 + 2
	db $00, $c6, $4f, $2c, $34, $b3, $33, $7f, $b7, $d8, $b6, $b4, $cf, $bc, $c0, $e7, $51, $1c, $ac, $87, $8c, $dd, $7f
	db $b7, $d8, $b6, $b4, $c0, $c9, $33, $4f, $a7, $43, $e3, $93, $dd, $7f, $b6, $b7, $cf, $bc, $c0, $e7, $58
AutoBox_AllFullText: ; ポケモン ボックスが ぜんぶ いっぱいです！ パソコンで ボックスを せいり してください
	db $00, $54, $7f, $1c, $ac, $87, $8c, $26, $4f, $2e, $de, $3c, $7f, $b2, $df, $44, $b2, $33, $bd, $e7, $51, $40, $8e
	db $89, $ab, $33, $7f, $1c, $ac, $87, $8c, $dd, $4f, $be, $b2, $d8, $7f, $bc, $c3, $b8, $30, $bb, $b2, $58
