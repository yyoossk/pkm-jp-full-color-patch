; せっていの「はなしの はやさ」に「さいこう」（文字が 待たずに 一度に 出る）を 足す（金 日本版）
;
; ・はやさ：さいこう ⇔ はやい ⇔ ふつう ⇔ おそい（左右で 切りかえ。はしで 反対の はしへ）。
; ・さいこう は wOptions の 文字の 待ち（下の 3ビット）を 0 に する。PrintLetterDelay は 待ちが 0 なら 待たない。
;
; しくみ
;   ・Options_TextSpeed（バンク$39）の 頭を「新しい バンクの TextSpeedNew を farcall して もどる」に する
;     （バンク$39 には 文字を 足す 空きが ないため）。元の 処理は ぜんぶ TextSpeedNew が する。
;   ・はやさの 文字の 場所は src/clockopt_gold.asm で 1行 上げた 所（TS_COORD）。clockopt を 入れないときは 元の 場所に する。
;
; 銀・クリスタルに 入れるとき：下の DEF を その ROM の 値に する

INCLUDE "src/charmap_jp.inc"

IF !DEF(TS_HOOK)
DEF TS_HOOK          EQU $4c7f     ; Options_TextSpeed（call GetTextSpeed から 7バイト 以上）
DEF TS_HOOK_BANK     EQU $39
DEF TS_COORD         EQU $c3d3 - 20 ; 文字を 置く 場所（元は hlcoord 11, 3 = $c3d3。clockopt で 1行 上）
DEF TS_wOptions      EQU $d1ab
DEF TS_hJoyPressed   EQU $ffa9
DEF TS_PlaceString   EQU $0f46
DEF TS_BANK          EQU $42
DEF TS_ADDR          EQU $5a00
ENDC

SECTION "textspeed hook", ROMX[TS_HOOK], BANK[TS_HOOK_BANK]
	ld a, BANK(TextSpeedNew)
	ld hl, TextSpeedNew
	rst $08
	ret

SECTION "textspeed", ROMX[TS_ADDR], BANK[TS_BANK]
TextSpeedNew:
	; いまの はやさ → c（0 さいこう・1 はやい・2 ふつう・3 おそい）
	ld a, [TS_wOptions]
	and %111
	ld b, a
	ld c, 0
	ld hl, .delays
.find
	ld a, [hli]
	cp b
	jr z, .found
	inc c
	ld a, c
	cp 4
	jr c, .find
	ld c, 2                          ; ほかの 値は ふつう
.found
	ldh a, [TS_hJoyPressed]
	bit 5, a                         ; 左
	jr nz, .left
	bit 4, a                         ; 右
	jr z, .show
	inc c                            ; 右
	ld a, c
	cp 4
	jr c, .save
	ld c, 0
	jr .save
.left
	ld a, c
	and a
	jr nz, .dec
	ld c, 4
.dec
	dec c
.save
	ld b, 0
	ld hl, .delays
	add hl, bc
	ld a, [TS_wOptions]
	and $f8
	or [hl]
	ld [TS_wOptions], a
.show
	ld b, 0
	ld hl, .strings
	add hl, bc
	add hl, bc
	ld e, [hl]
	inc hl
	ld d, [hl]
	ld hl, TS_COORD
	call TS_PlaceString
	and a
	ret

.delays
	db 0, 1, 3, 5                    ; さいこう・はやい（TEXT_DELAY_FAST）・ふつう（MED）・おそい（SLOW）
.strings
	dw .instant, .fast, .mid, .slow
.instant db "さいこう@"
.fast    db "はやい　@"
.mid     db "ふつう　@"
.slow    db "おそい　@"
