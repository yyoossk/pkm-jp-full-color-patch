; かかってくる 電話の 回数を ポケギアの 電話の 画面で えらぶ（ふつう／すくない／なし。金 日本版）
;
; ・ポケギアの 電話の 画面の 下に「ちゃくしん・ふつう　セレクト　かえる」。
;   SELECT で ふつう → すこし → なし → ふつう。
;   （前は「でんわ・すくない　セレクトで　かえる」だったが、濁点が 上の 行（10行め）に かかれ、
;     4人めの 行の カーソル（で の 濁点）・しょくぎょう（6文字め）と かさなって いたので、濁点の ない ことばに した）
; ・ふつう：元のまま。すくない：かかってくる 回数が 4分の1。なし：かかってこない。
; ・とまらないのは、とりたてて かかってくる 大事な 電話（ウツギ博士 など。CheckSpecialPhoneCall）だけ。
;   えらべるのは 自分から かかってくる ふつうの 電話（再戦・ポケモンじまん・どうぐ など。CheckPhoneCall）。
; ・せっていは wOptions2 の ビット 1・2（使われていない。レポートに 書かれる）。
;
; しくみ
;   ・CheckPhoneCall の 頭の「call CheckStandingOnEntrance」を PhoneFreq_Check に：
;     なし → z（電話なし）、すくない → 4分の3 は z、ほかは 元の CheckStandingOnEntrance。
;   ・PokegearPhone_Joypad の 頭の「ld hl, hJoyPressed」を PhoneFreq_Select に：SELECT なら 切りかえて もどる。
;   ・電話の 画面を かく 所（Pokegear_UpdateTilemap .Phone の さいごの call PokegearPhone_UpdateDisplayList）の あとに 文字を かく。
;
; 銀・クリスタルに 入れるとき：下の DEF を その ROM の 値に する

INCLUDE "src/charmap_jp.inc"

IF !DEF(PF_CHECK_HOOK)
DEF PF_GEAR_BANK        EQU $24
DEF PF_CHECK_HOOK       EQU $4074   ; CheckPhoneCall（call CheckStandingOnEntrance）
DEF PF_JOYPAD_HOOK      EQU $50cf   ; PokegearPhone_Joypad（ld hl, hJoyPressed）
DEF PF_DRAW_HOOK        EQU $4dc3   ; .Phone の call PokegearPhone_UpdateDisplayList
DEF PF_UpdateDisplayList EQU $5241
DEF PF_GEAR_FREE        EQU $7fb0   ; バンク$24 の 空き
DEF PF_CheckStandingOnEntrance EQU $170d
DEF PF_Random           EQU $305e
DEF PF_PlaceString      EQU $0f46
DEF PF_PlaySFX          EQU $3d45
DEF PF_wOptions2        EQU $d1b0
DEF PF_hJoyPressed      EQU $ffa9
DEF PF_hBGMapMode       EQU $ffd6
DEF PF_COORD            EQU $c3a0 + 11 * 20 + 1   ; hlcoord 1, 11（10行めは 4人めの 行なので 濁点の ある 文字は つかわない）
DEF PF_BANK             EQU $42
DEF PF_ADDR             EQU $5b00
ENDC
DEF PF_SFX              EQU $08     ; SFX_READ_TEXT_2

SECTION "phonefreq check hook", ROMX[PF_CHECK_HOOK], BANK[PF_GEAR_BANK]
	call PhoneFreq_Check
SECTION "phonefreq joypad hook", ROMX[PF_JOYPAD_HOOK], BANK[PF_GEAR_BANK]
	call PhoneFreq_Select
SECTION "phonefreq draw hook", ROMX[PF_DRAW_HOOK], BANK[PF_GEAR_BANK]
	call PhoneFreq_Draw

SECTION "phonefreq gear", ROMX[PF_GEAR_FREE], BANK[PF_GEAR_BANK]
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
	ld hl, PF_hJoyPressed
	ld a, [hl]
	and 1 << 2                          ; SELECT
	ret z
	pop af                              ; PokegearPhone_Joypad から もどる
	ld a, BANK(PhoneFreq_Toggle)
	ld hl, PhoneFreq_Toggle
	rst $08
	ret

PhoneFreq_Draw:
	call PF_UpdateDisplayList
	ld a, BANK(PhoneFreq_Show)
	ld hl, PhoneFreq_Show
	rst $08
	ret

SECTION "phonefreq", ROMX[PF_ADDR], BANK[PF_BANK]
PhoneFreq_Toggle:
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
	; fallthrough
PhoneFreq_Show:
	; 濁点の ない ことばだけを つかう（濁点は 上の 行（10行め）に かかれ、4人めの 行の 名前・カーソル と かさなるため）
	ld hl, PF_COORD
	ld de, .label
	call PF_PlaceString
	ld hl, PF_COORD + 10
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
	ld hl, PF_COORD + 6
	call PF_PlaceString
	ld a, 1
	ldh [PF_hBGMapMode], a
	ret
.label   db "ちゃくしん・@"
.help    db "セレクト　かえる@"
.strings dw .normal, .less, .none
.normal  db "ふつう@"
.less    db "すこし@"
.none    db "なし　@"
