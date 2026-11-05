; むしよけの ききめが きれたとき、リュックに のこりが あれば「○○を つかいますか？」と きく（金 日本版）
;
; ・むしよけ（むしよけスプレー・シルバースプレー・ゴールドスプレー）の ききめが きれると、元の 文
;   「むしよけスプレーの こうかが きれました」の あとに「○○を つかいますか？」→ はい で その場で つかう。
; ・きく ものは さいごに つかった むしよけ（リュックに なければ、むしよけ → シルバー → ゴールド の じゅんで ある もの）。
; ・リュックに ひとつも なければ 元と 同じ（文だけ）。
;
; しくみ
;   ・DoRepelStep の さいごの「ld a, BANK(RepelWoreOffScript) / ld hl, RepelWoreOffScript」の 行き先を RepelAsk_Script に。
;   ・UseRepel（むしよけを つかう 所。バンク$03、17バイト）を 書きなおして、さいごの 所を RepelAsk_Set の farcall に：
;     ききめを 入れる・つかった むしよけを wRepelAskLast に おぼえる・元の UseItemText（○○を つかった・へらす）。
;
; 銀・クリスタルに 入れるとき：下の DEF を その ROM の 値に する

INCLUDE "includes.asm"
INCLUDE "src/charmap_jp.inc"

IF !DEF(RA_HOOK)
DEF RA_HOOK            EQU $6b14   ; DoRepelStep の ld a, BANK(RepelWoreOffScript)（5バイト）
DEF RA_HOOK_BANK       EQU $25
DEF RA_WOREOFF_TEXT    EQU $7a79   ; RepelWoreOffScript の 文（RepelWoreOffText）
DEF RA_WOREOFF_BANK    EQU $04
DEF RA_USEREPEL        EQU $787c   ; UseRepel（ld a, [wRepelEffect] から 17バイト）
DEF RA_USEREPEL_BANK   EQU $03
DEF RA_STILL_TEXT      EQU $788d   ; RepelUsedEarlierIsStillInEffectText
DEF RA_USEITEMTEXT     EQU $7c49   ; UseItemText（バンク$03）
DEF RA_PrintText       EQU $0f30
DEF RA_CheckItem       EQU $304b
DEF RA_TossItem        EQU $3025
DEF RA_wRepelEffect    EQU $d9b1
DEF RA_wCurItem        EQU $cffc
DEF RA_wNumItems       EQU $d5aa
DEF RA_wItemQuantityChange EQU $d003
DEF RA_wScriptVar      EQU $d165
DEF RA_wStringBuffer3  EQU $cf9d
DEF wRepelAskLast      EQU $def2   ; 使われていない WRAM（autobox の $def0・$def1 の 次）：さいごに つかった むしよけ
DEF wRepelAskItem      EQU $def3   ; 〃 きいている むしよけ（yesorno で wScriptVar が かわるため）
DEF RA_BANK            EQU $43
DEF RA_ADDR            EQU $7c80
ENDC

SECTION "repelask hook", ROMX[RA_HOOK], BANK[RA_HOOK_BANK]
	ld a, BANK(RepelAsk_Script)
	ld hl, RepelAsk_Script

SECTION "repelask userepel", ROMX[RA_USEREPEL], BANK[RA_USEREPEL_BANK]
; b = ききめ（100・200・250）
	ld a, [RA_wRepelEffect]
	and a
	ld hl, RA_STILL_TEXT
	jp nz, RA_PrintText
	ld a, BANK(RepelAsk_Set)
	ld hl, RepelAsk_Set
	rst $08
	ret

SECTION "repelask", ROMX[RA_ADDR], BANK[RA_BANK]
RepelAsk_Set:
	ld a, b
	ld [RA_wRepelEffect], a
	ld a, [RA_wCurItem]
	ld [wRepelAskLast], a
	ld a, RA_USEREPEL_BANK
	ld hl, RA_USEITEMTEXT
	rst $08
	ret

RepelAsk_Script:
	opentext
	db farwritetext_command, RA_WOREOFF_BANK
	dw RA_WOREOFF_TEXT
	callasm RepelAsk_Find
	iffalse .end
	promptbutton
	getitemname STRING_BUFFER_3, USE_SCRIPT_VAR
	writetext RepelAsk_AskText
	yesorno
	iffalse .no
	callasm RepelAsk_Use
	writetext RepelAsk_UsedText
	playsound SFX_FULL_HEAL
	waitsfx
.end
	waitbutton
.no
	closetext
	end

; wScriptVar = つかう むしよけ（0 = リュックに ない）
RepelAsk_Find:
	ld a, [wRepelAskLast]
	call .check
	ret c
	ld a, REPEL
	call .check
	ret c
	ld a, SUPER_REPEL
	call .check
	ret c
	ld a, MAX_REPEL
	call .check
	ret c
	xor a
	ld [RA_wScriptVar], a
	ret
; a = 道具 → キャリー：リュックに ある（wScriptVar = a）
.check
	cp REPEL
	jr z, .ok
	cp SUPER_REPEL
	jr z, .ok
	cp MAX_REPEL
	jr z, .ok
	and a
	ret
.ok
	ld [RA_wCurItem], a
	ld [RA_wScriptVar], a
	ld [wRepelAskItem], a
	ld hl, RA_wNumItems
	jp RA_CheckItem

; wScriptVar の むしよけを つかう（ききめを 入れて 1こ へらす）
RepelAsk_Use:
	ld a, [wRepelAskItem]
	ld [RA_wCurItem], a
	ld [wRepelAskLast], a
	ld b, 100
	cp REPEL
	jr z, .set
	ld b, 200
	cp SUPER_REPEL
	jr z, .set
	ld b, 250
.set
	ld a, b
	ld [RA_wRepelEffect], a
	ld a, 1
	ld [RA_wItemQuantityChange], a
	ld hl, RA_wNumItems
	jp RA_TossItem

RepelAsk_AskText: ; ○○を つかいますか？
	db $01                           ; text_ram
	dw RA_wStringBuffer3
	db $00, "を", $4f, "つかいますか？", $57
RepelAsk_UsedText: ; （主人公）は ○○を つかった！
	db $00, $52, "は", $4f, $50
	db $01                           ; text_ram
	dw RA_wStringBuffer3
	db $00, "を　つかった！", $57
