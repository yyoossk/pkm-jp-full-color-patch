; かかってくる 電話の 回数を ポケギアの 電話の 画面で えらぶ（ふつう／すくない／なし）… クリスタル（日本版）用
; 金銀の src/phonefreq.asm と 同じ ことを する。クリスタルは バンク$24（ポケギア）に 空きが ほとんど ないので、
; 使われていない 所（LoadPokegearRadioChannelPointer $24:$5806・12バイト、$24:$6da7〜 16バイト）に 小さな 入口だけ 置き、
; 処理は バンク$76 で する。文字は 電話の 一覧の 下の 行（11行目。濁点は 10行目）。
; 一覧を かきなおす たび（PokegearPhone_UpdateDisplayList の さいごの call PokegearPhone_UpdateCursor）に 文字も かきなおす
; （一覧を かきなおす とき 3〜11行目が 消えるため）。
INCLUDE "src/charmap_jp.inc"

DEF PF_GEAR_BANK        EQU $24
DEF PF_CHECK_HOOK       EQU $4074   ; CheckPhoneCall の call CheckStandingOnEntrance
DEF PF_JOYPAD_HOOK      EQU $510c   ; PokegearPhone_Joypad の ld hl, hJoyPressed
DEF PF_DRAW_HOOK        EQU $52c0   ; PokegearPhone_UpdateDisplayList の さいごの call PokegearPhone_UpdateCursor
DEF PF_UpdateCursor     EQU $525d
DEF PF_GEAR_FREE1       EQU $6da7   ; 使われていない AnimateSlotReelIcons の のこり（16バイト）
DEF PF_GEAR_FREE2       EQU $5806   ; 使われていない LoadPokegearRadioChannelPointer（12バイト）
DEF PF_CheckStandingOnEntrance EQU $188e
DEF PF_Random           EQU $2f5e
DEF PF_PlaceString      EQU $1057
DEF PF_PlaySFX          EQU $3bb0
DEF PF_wOptions2        EQU $cfc5   ; ビット 0 は メニューせつめい。ビット 1・2 は 使われていない
DEF PF_hJoyPressed      EQU $ffa7
DEF PF_hBGMapMode       EQU $ffd4
DEF PF_COORD            EQU $c4a0 + 11 * 20 + 1   ; hlcoord 1, 11
DEF PF_BANK             EQU $76
DEF PF_ADDR             EQU $4500
DEF PF_SFX              EQU $08     ; SFX_READ_TEXT_2

SECTION "phonefreq check hook", ROMX[PF_CHECK_HOOK], BANK[PF_GEAR_BANK]
	call PhoneFreq_CheckGear
SECTION "phonefreq joypad hook", ROMX[PF_JOYPAD_HOOK], BANK[PF_GEAR_BANK]
	call PhoneFreq_SelectGear
SECTION "phonefreq draw hook", ROMX[PF_DRAW_HOOK], BANK[PF_GEAR_BANK]
	call PhoneFreq_DrawGear

SECTION "phonefreq gear 1", ROMX[PF_GEAR_FREE1], BANK[PF_GEAR_BANK]
PhoneFreq_CheckGear:                    ; z = 電話を かけない（FarCall は フラグを のこす）
	ld a, BANK(PhoneFreq_Check)
	ld hl, PhoneFreq_Check
	rst $08
	ret
PhoneFreq_DrawGear:
	ld a, BANK(PhoneFreq_Draw)
	ld hl, PhoneFreq_Draw
	rst $08
	ret

SECTION "phonefreq gear 2", ROMX[PF_GEAR_FREE2], BANK[PF_GEAR_BANK]
PhoneFreq_SelectGear:
	ld a, BANK(PhoneFreq_Select)
	ld hl, PhoneFreq_Select
	rst $08                             ; キャリー = SELECT で 切りかえた
	ld hl, PF_hJoyPressed               ; 元の 命令
	ret nc
	pop af                              ; PokegearPhone_Joypad から もどる
	ret

SECTION "phonefreq", ROMX[PF_ADDR], BANK[PF_BANK]
; z = 電話を かけない
PhoneFreq_Check:
	ld a, [PF_wOptions2]
	and %110
	jp z, PF_CheckStandingOnEntrance   ; ふつう
	cp %100
	ret z                               ; なし
	call PF_Random                      ; すくない
	and %11
	jp z, PF_CheckStandingOnEntrance
	xor a
	ret

PhoneFreq_Select:
	ldh a, [PF_hJoyPressed]
	and 1 << 2                          ; SELECT
	ret z                               ; キャリー なし
	ld a, [PF_wOptions2]
	ld b, a
	and %110
	add %010
	cp %110
	jr c, .ok
	xor a
.ok
	ld c, a
	ld a, b
	and %11111001
	or c
	ld [PF_wOptions2], a
	ld de, PF_SFX
	call PF_PlaySFX
	call PhoneFreq_Show
	scf
	ret

PhoneFreq_Draw:
	ld a, PF_GEAR_BANK                  ; 元の call PokegearPhone_UpdateCursor
	ld hl, PF_UpdateCursor
	rst $08
	; fallthrough
PhoneFreq_Show:
	ld hl, PF_COORD
	ld de, .label
	call PF_PlaceString
	ld hl, PF_COORD + 9
	ld de, .help
	call PF_PlaceString
	ld a, [PF_wOptions2]
	and %110                            ; 0・2・4 → 表の 場所
	ld e, a
	ld d, 0
	ld hl, .strings
	add hl, de
	ld e, [hl]
	inc hl
	ld d, [hl]
	ld hl, PF_COORD + 4
	call PF_PlaceString
	ld a, 1
	ldh [PF_hBGMapMode], a
	ret
.label   db "でんわ・@"
.help    db "セレクトで　かえる@"
.strings dw .normal, .less, .none
.normal  db "ふつう　@"
.less    db "すくない@"
.none    db "なし　　@"
