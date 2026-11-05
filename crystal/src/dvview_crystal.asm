; 個体値 … クリスタル（日本版）用（金銀の src/dvview.asm と 同じ ことを する）
; クリスタルの 3ページめ（青）は わくの 上の 線 6行め、こうげき〜すばやさ 8・10・12・14・16行め（金と 同じ）。数は x 15〜17（金は 16〜18）。
; SELECT の たびに のうりょく → 個体値 → きそポイント（0〜65535）→ のうりょく。
; きそポイントの 数は 5けた で x 14〜18（わくの 中の いちばん 右まで）。「たいりょく」は 4行め（5行めは「ポ」の 半濁点）。
; ちがう 所：
;   ・ボタンは StatsScreen_GetJoypad（$13:$5ccc）の「call GetJoypad」を DV_Stub（バンク$13 の 空き $7780）に して 見る。
;     青の ページで SELECT なら きりかえて、wJumptableIndex（$cf57）を LoadPage（4）に して ページを かきなおす
;     （ページを かえる ときと 同じ）。SELECT は けして おく（2ページめの わざの ならびかえ（statsmove）には 元のまま とどく）。
;   ・LoadBluePage（$13:$6040）の さいごの「ld hl, $c549 / ld bc, 6 / ld a, $28 / call Predef」（$13:$604d。11バイト。
;     predef PrintTempMonStats）を DV_Draw への farcall（＋ nop 5つ）に。
;   ・きりかえの 印は WRAM バンク2 の $dfcb（バンク1 に 空きが ない）。
INCLUDE "src/charmap_jp.inc"

DEF DV_JOY_HOOK        EQU $5ccc
DEF DV_HOOK_BANK       EQU $13
DEF DV_STUB            EQU $7780
DEF DV_BLUE_HOOK       EQU $604d
DEF DV_GetJoypad       EQU $0984
DEF DV_Predef          EQU $2d55
DEF DV_PlaceString     EQU $1057
DEF DV_PrintNum        EQU $3164
DEF DV_hJoyPressed     EQU $ffa7
DEF DV_wStatsScreenFlags EQU $cf58    ; 下の 2ビット ＝ ページ（1 ピンク・2 みどり・3 あお）
DEF DV_wJumptableIndex EQU $cf57
DEF DV_wTempMonDVs     EQU $d0e3
DEF DV_wTempMonStatExp EQU $d0d9      ; wTempMon（$d0ce）の 11バイトめから（HP・こうげき・ぼうぎょ・すばやさ・とくしゅ。大きい ほうが 先）
DEF DV_wBuffer         EQU $d05b
DEF DV_COORD           EQU $c4a0
DEF wDVShow            EQU $dfcb      ; WRAM バンク2（$dfc9・$dfca は 前の ボール）
DEF DV_BANK            EQU $76
DEF DV_ADDR            EQU $6e00
DEF DV_ADDR2           EQU $7100      ; きそポイント（あとから 足した ぶん）
DEF BLUE_PAGE          EQU 3

MACRO dv_load
	ld a, 2
	ldh [$ff70], a
	ld a, [wDVShow]
	push af
	ld a, 1
	ldh [$ff70], a
	pop af
ENDM

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
	REPT 5
	nop
	ENDR

SECTION "dvview", ROMX[DV_ADDR], BANK[DV_BANK]
DV_Joypad:
	call DV_GetJoypad
	ldh a, [DV_hJoyPressed]
	bit 2, a                          ; SELECT
	ret z
	ld a, [DV_wStatsScreenFlags]
	and 3
	cp BLUE_PAGE
	ret nz
	xor a
	ldh [DV_hJoyPressed], a           ; SELECT は ここで つかう
	ld a, 2
	ldh [$ff70], a
	ld a, [wDVShow]                   ; 0 のうりょく → 1 個体値 → 2 きそポイント → 0
	inc a
	cp 3
	jr c, .set
	xor a
.set
	ld [wDVShow], a
	ld a, 1
	ldh [$ff70], a
	ld a, [DV_wJumptableIndex]        ; ページを かきなおす（LoadPage）
	and $80
	or 4
	ld [DV_wJumptableIndex], a
	ret

DV_Draw:
	ld hl, DV_COORD + 8 * 20 + 9      ; 元の 命令（hlcoord 9, 8 / ld bc, 6 / predef PrintTempMonStats）
	ld bc, 6
	ld a, $28
	call DV_Predef
	dv_load
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
	ld hl, DV_COORD + 5 * 20 + 16
	call .Put
	; こうげき・ぼうぎょ・とくこう・とくぼう・すばやさ（8・10・12・14・16 行め）
	ld a, b
	swap a
	ld hl, DV_COORD + 8 * 20 + 15
	call .Put3
	ld a, b
	ld hl, DV_COORD + 10 * 20 + 15
	call .Put3
	ld a, c
	ld hl, DV_COORD + 12 * 20 + 15
	call .Put3
	ld a, c
	ld hl, DV_COORD + 14 * 20 + 15
	call .Put3
	ld a, c
	swap a
	ld hl, DV_COORD + 16 * 20 + 15
	; fallthrough
.Put3
	ld [hl], $7f
	inc hl
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
DV_DrawStatExp:
	ld hl, DV_COORD + 6 * 20 + 10
	ld de, .Label
	call DV_PlaceString
	ld hl, DV_COORD + 4 * 20 + 9
	ld de, DV_Draw.HPLabel
	call DV_PlaceString
	ld hl, DV_COORD + 4 * 20 + 15     ; 5けたでも「たいりょく」と くっつかないよう 1つ 右（x15〜19）
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
