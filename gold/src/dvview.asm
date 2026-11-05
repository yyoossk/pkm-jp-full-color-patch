; つよさの 画面で、SELECT を おすと 個体値を 出す（金 日本版）
;
; ・「つよさを みる」の 3ページめ（青・こうげき〜すばやさ）で SELECT を おすと、のうりょくの 数の かわりに
;   個体値（0〜15）を 出す。わくの 上の 線に「こたいち」、その 上の 空いた 行に「たいりょく」（HP の 個体値）も 出す。
;   もう いちど SELECT で きそポイント（努力値。0〜65535）、もう いちど で 元に もどる
;   （のうりょく → 個体値 → きそポイント → のうりょく。ほかの ポケモン・ほかの ページに いっても、もどす まで その まま）。
;   きそポイントの ときは わくの 上の 線に「きそポイント」、その 上の 上（4行め）に「たいりょく」（HP の きそポイント）。
;   たいりょくの 数は x 15〜19（わくの 中の 5つは x 14〜18）。x 14 からだと 5けたの とき「たいりょく65535」と くっついて いた。
;   （5行めは「ポ」の 半濁点の 行）
;   とくこう・とくぼう は どちらも「とくしゅ」の 個体値・きそポイント（金銀は 1つ）。
;   たいりょく ＝ こうげき・ぼうぎょ・すばやさ・とくしゅ の 個体値の いちばん 下の ビットを 8・4・2・1 に ならべた 数。
; ・2ページめ（わざ）の SELECT は 今までどおり わざの ならびかえ（17）。
;
; しくみ
;   ・StatsScreen_LoadPage .joypad_loop の「call GetJoypad」を バンク$14 の 空き（7バイト）の DV_Stub に。
;     DV_Stub は 新しい バンクの DV_Joypad を farcall。DV_Joypad は GetJoypad を 呼んで、青の ページで SELECT なら
;     きりかえて LoadBluePage で かきなおす（bc ＝ b 1・c ページ は そのまま）。
;   ・LoadBluePage の「farcall LoadStatsScreenPals」を DV_Draw に（LoadStatsScreenPals を 呼んで から、個体値の とき は 上書き）。
;   ・きりかえの 印（0・1・2）は 使われていない WRAM（$deff）。きそポイントは wTempMon の 11バイトめから（$d010。大きい ほうが 先）。
;
; 銀・クリスタルに 入れるとき：下の DEF を その ROM の 値に する
;   （銀は 金と 同じ 作り。クリスタルは 個体値の ページの 作りが 同じか 確かめる）

INCLUDE "src/charmap_jp.inc"

IF !DEF(DV_JOY_HOOK)
DEF DV_JOY_HOOK        EQU $4ce2      ; バンク$14 StatsScreen_LoadPage .joypad_loop の call GetJoypad
DEF DV_HOOK_BANK       EQU $14
DEF DV_STUB            EQU $7fd1      ; バンク$14 の 空き（7バイト）
DEF DV_BLUE_HOOK       EQU $50d8      ; LoadBluePage の farcall LoadStatsScreenPals
DEF DV_LoadBluePage    EQU $50ae
DEF DV_Pals_BANK       EQU $02
DEF DV_Pals            EQU $5241
DEF DV_GetJoypad       EQU $0934
DEF DV_PlaceString     EQU $0f46
DEF DV_PrintNum        EQU $31f9
DEF DV_hJoyPressed     EQU $ffa9
DEF DV_wTempMonDVs     EQU $d01a
DEF DV_wTempMonStatExp EQU $d010      ; HP・こうげき・ぼうぎょ・すばやさ・とくしゅ（2バイトずつ）
DEF DV_wBuffer         EQU $cf87      ; wStringBuffer1（1バイト）
DEF DV_COORD           EQU $c3a0      ; hlcoord 0, 0
DEF wDVShow            EQU $deff
DEF DV_BANK            EQU $45
DEF DV_ADDR            EQU $7300
DEF DV_ADDR2           EQU $7700      ; きそポイント（あとから 足した ぶん）
ENDC
DEF BLUE_PAGE          EQU 3

SECTION "dvview joypad hook", ROMX[DV_JOY_HOOK], BANK[DV_HOOK_BANK]
	call DV_Stub
SECTION "dvview stub", ROMX[DV_STUB], BANK[DV_HOOK_BANK]
DV_Stub:
	ld a, BANK(DV_Joypad)
	ld hl, DV_Joypad
	rst $08
	ret
SECTION "dvview blue hook", ROMX[DV_BLUE_HOOK], BANK[DV_HOOK_BANK]
	ld a, BANK(DV_Draw)
	ld hl, DV_Draw
	rst $08

SECTION "dvview", ROMX[DV_ADDR], BANK[DV_BANK]
DV_Joypad:
	call DV_GetJoypad
	ldh a, [DV_hJoyPressed]
	bit 2, a                          ; SELECT
	ret z
	ld a, c
	cp BLUE_PAGE
	ret nz
	ld a, [wDVShow]                   ; 0 のうりょく → 1 個体値 → 2 きそポイント → 0
	inc a
	cp 3
	jr c, .set
	xor a
.set
	ld [wDVShow], a
	push bc
	ld a, DV_HOOK_BANK
	ld hl, DV_LoadBluePage
	rst $08
	pop bc
	ret

DV_Draw:
	ld a, DV_Pals_BANK
	ld hl, DV_Pals
	rst $08
	ld a, [wDVShow]
	and a
	ret z
	cp 2
	jp z, DV_DrawStatExp
	; わくの 上に「こたいち」・その 上に たいりょく
	ld hl, DV_COORD + 6 * 20 + 10
	ld de, .Label
	call DV_PlaceString
	ld hl, DV_COORD + 5 * 20 + 9
	ld de, .HPLabel
	call DV_PlaceString
	ld a, [DV_wTempMonDVs]
	ld b, a
	ld a, [DV_wTempMonDVs + 1]
	ld c, a
	; たいりょく（HP）
	xor a
	bit 4, b
	jr z, .hp1
	or 8
.hp1
	bit 0, b
	jr z, .hp2
	or 4
.hp2
	bit 4, c
	jr z, .hp3
	or 2
.hp3
	bit 0, c
	jr z, .hp4
	or 1
.hp4
	ld hl, DV_COORD + 5 * 20 + 17
	call .Put
	; こうげき・ぼうぎょ・とくこう・とくぼう・すばやさ（8・10・12・14・16 行め）
	ld a, b
	swap a
	ld hl, DV_COORD + 8 * 20 + 16
	call .Put3
	ld a, b
	ld hl, DV_COORD + 10 * 20 + 16
	call .Put3
	ld a, c
	ld hl, DV_COORD + 12 * 20 + 16
	call .Put3
	ld a, c
	ld hl, DV_COORD + 14 * 20 + 16
	call .Put3
	ld a, c
	swap a
	ld hl, DV_COORD + 16 * 20 + 16
	; fallthrough

; a の 下 4ビット を hl に 3けた（右よせ）で
.Put3
	ld [hl], $7f
	inc hl
; a の 下 4ビット を hl に 2けた（右よせ）で
.Put
	ld [hl], $7f
	inc hl
	ld [hl], $7f
	dec hl
	and $0f
	ld [DV_wBuffer], a
	push bc
	ld de, DV_wBuffer
	ld bc, $0102
	call DV_PrintNum
	pop bc
	ret

.Label   db "　こたいち　@"
.HPLabel db "たいりょく@"

SECTION "dvview statexp", ROMX[DV_ADDR2], BANK[DV_BANK]
; きそポイント（努力値。0〜65535）
; わくの 上の 線に「きそポイント」（半濁点は 5行め）、4行めに たいりょく、わくの 中の 数を 5けたに
DV_DrawStatExp:
	ld hl, DV_COORD + 6 * 20 + 10
	ld de, .Label
	call DV_PlaceString
	ld hl, DV_COORD + 4 * 20 + 9
	ld de, DV_Draw.HPLabel
	call DV_PlaceString
	ld hl, DV_COORD + 4 * 20 + 15     ; 1つ 右（x 15〜19）：5けたの とき「たいりょく65535」と くっつかない ように
	ld de, DV_wTempMonStatExp         ; HP
	call .Put5
	ld hl, DV_COORD + 8 * 20 + 14
	ld de, DV_wTempMonStatExp + 2     ; こうげき
	call .Put5
	ld hl, DV_COORD + 10 * 20 + 14
	ld de, DV_wTempMonStatExp + 4     ; ぼうぎょ
	call .Put5
	ld hl, DV_COORD + 12 * 20 + 14
	ld de, DV_wTempMonStatExp + 8     ; とくしゅ（とくこう）
	call .Put5
	ld hl, DV_COORD + 14 * 20 + 14
	ld de, DV_wTempMonStatExp + 8     ; とくしゅ（とくぼう）
	call .Put5
	ld hl, DV_COORD + 16 * 20 + 14
	ld de, DV_wTempMonStatExp + 6     ; すばやさ
	; fallthrough

; [de]（2バイト・大きい ほうが 先）を hl から 5けた（右よせ）で
.Put5
	push hl
	ld a, $7f
	ld [hli], a
	ld [hli], a
	ld [hli], a
	ld [hli], a
	ld [hl], a
	pop hl
	ld bc, $0205
	jp DV_PrintNum

.Label db "　きそポイント　@"
