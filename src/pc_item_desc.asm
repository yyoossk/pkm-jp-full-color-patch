; パソコンの「どうぐを ひきだす」（と「どうぐを すてる」）のリストでも、カーソルのある道具の説明を
; 下のわくに出す（フレンドリィショップで買うときの説明と同じしくみ・同じ文）。「やめる」では何も出さない。
; （赤のキット「パソコンの道具の説明文」から。青は作りがちがうので、青の場所に合わせた）
;
; 青のしくみ：リストメニューは入力のたびに 00:0037 から 13:5B3F を farcall する。
;   13:5B3F  ld a, [wListMenuID] / cp PRICEDITEMLISTMENU / jr z, .mart / call HandleMenuInput / ld e, a / ret
;   .mart（13:5B4B）上下も見るキーにして、farcall MartPrintDescription（0C:4578）、HandleMenuInput、スクロールのあと始末
;   0C:45C1 が BagPrintItemDescription（a = 道具。わざマシン・ひでんマシンは「〜を おぼえさせる」）
; 直し：
;   1. 13:5B3F を jp KitPCDescCheck にする。ショップか、パソコンの道具のリスト（wListMenuID = ITEMLISTMENU で
;      wListPointer = wNumBoxItems）なら .mart へ、ちがえば元のとおり。
;   2. .mart の farcall MartPrintDescription（ld b, $0C / ld hl, $4578）を KitPCDesc にする。ショップなら
;      MartPrintDescription へ。パソコンなら、わくを消して、あずけた道具の表（道具・数の 2バイトずつ）から
;      カーソルの道具をとり、0C の入口（ld a, e / jp BagPrintItemDescription）へ farcall する（Bankswitch は de をこわさない）。

IF HAS_PC_ITEM_DESC

DEF wCurrentMenuItem   EQU $CC26
DEF wListScrollOffset  EQU $CC36
DEF wListPointer       EQU $CF72
DEF wListMenuID        EQU $CF7B
DEF wNumBoxItems       EQU $D4B9
DEF wBoxItems          EQU $D4BA
DEF PRICEDITEMLISTMENU EQU 2
DEF ITEMLISTMENU       EQU 3
DEF ListInputHook      EQU $5B3F   ; バンク $13
DEF ListInputMart      EQU $5B4B   ; バンク $13（.mart）
DEF MartDescFarcall    EQU $5B53   ; バンク $13：ld b, $0C / ld hl, MartPrintDescription
DEF MartPrintDescription    EQU $4578  ; バンク $0C
DEF BagPrintItemDescription EQU $45C1  ; バンク $0C

SECTION "パソコンの道具の説明：入力", ROMX[ListInputHook], BANK[$13]
	jp KitPCDescCheck

SECTION "パソコンの道具の説明：説明を出す", ROMX[MartDescFarcall], BANK[$13]
	ld b, BANK(KitPCDesc)
	ld hl, KitPCDesc

SECTION "パソコンの道具の説明：0C の入口", ROMX[$7FF8], BANK[$0C]
KitPCDescStub:
	ld a, e
	jp BagPrintItemDescription

FreeBank13
KitPCDescCheck:
	ld a, [wListMenuID]
	cp PRICEDITEMLISTMENU
	jp z, ListInputMart
	cp ITEMLISTMENU
	jr nz, .normal
	ld a, [wListPointer]
	cp LOW(wNumBoxItems)
	jr nz, .normal
	ld a, [wListPointer + 1]
	cp HIGH(wNumBoxItems)
	jp z, ListInputMart
.normal
	call HandleMenuInputW
	ld e, a
	ret

FreeBankA
KitPCDesc:
	ld a, [wListMenuID]
	cp PRICEDITEMLISTMENU
	jr nz, .pc
	ld b, $0C
	ld hl, MartPrintDescription
	jp Bankswitch
.pc
	hlcoord 1, 13
	lb bc, 4, 18
	call ClearScreenArea
	ld a, [wListScrollOffset]
	ld b, a
	ld a, [wCurrentMenuItem]
	add b
	ld b, a
	ld a, [wNumBoxItems]
	cp b
	ret z                         ; やめる
	ret c
	ld a, b
	add a
	ld e, a
	ld d, 0
	ld hl, wBoxItems
	add hl, de
	ld e, [hl]                    ; 道具
	ld b, $0C
	ld hl, KitPCDescStub
	jp Bankswitch

ENDC
