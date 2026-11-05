; せっていに「とけい」（あさ・ひる・よる／時計の設定）を足す（クリスタル日本版）
;
; ・「おわり」は なくす（B・START で とじる。元から B・START で とじられる）。
; ・今までの項目を 1行ずつ上げ（2〜14行目 → 1〜13行目。1行目の「はなしの はやさ」には濁点がない）、
;   15行目に「とけい　▶ひる　 せってい」を出す（とけい 1列目、あさ・ひる・よる 6列目、せってい 11列目）。
; ・とけいの行では 左右で「ひる」か「せってい」を選ぶ（ひらいたときは「ひる」の側）。
;   「ひる」で A … ▷ になり、左右で あさ（4:00）・ひる（10:00）・よる（18:00）に 時計を合わせる
;     （曜日はそのまま。分・秒は 0）。A・B で ▶ にもどる（この B では とじない）。
;   「せってい」で A … 元の RestartClock の「ld hl, wOptions」の所から（「くるっているかも」の文をとばす）
;     曜日・時・分を合わせる画面。おわったら WaitBGMap して、ボタンを はなすまで待つ。
; ・いちばん下の項目は とけい（7）。上下は とけい ⇔ いちばん上 で回りこむ。
; ・ゲームを始める前（タイトルのメニューの せってい。wMapGroup = 0）は「とけい　▶ーー」だけで、左右・A は効かない。
; ・とけいの行で 選んでいる所（wClockSub）は、WRAM バンク1 に 使われていない所がないので、
;   60fps・手持ちの見た目・ずかんの絵の色と同じ WRAM バンク2 の空き（$dfc2）に置き、読み書きのときに バンクを切りかえる。

INCLUDE "src/charmap_jp.inc"

DEF OPT_BANK          EQU $39
DEF wJumptableIndex   EQU $cf57
DEF hJoyPressed       EQU $ffa7
DEF wMapGroup         EQU $dc7b      ; 0 = まだゲームを始めていない
DEF wStringBuffer2    EQU $d066
DEF wTimeOfDay        EQU $d29a
DEF UpdateTime        EQU $05a7
DEF InitTime          EQU $0677
DEF GetWeekday        EQU $3342
DEF PlaceString       EQU $1057
DEF AddNTimes         EQU $30ca
DEF UpdateFrame       EQU $44d3
DEF OPT_POINTERS      EQU $4299      ; 元の表（8つ）
DEF TILE_CURSOR       EQU $ed
DEF wTilemap          EQU $c4a0
DEF SCREEN_WIDTH      EQU 20
DEF OPT_CLOCK         EQU 7
DEF CLOCK_ROW         EQU 15

DEF TILE_HOLLOW       EQU $ec
DEF CLOCK_VALUE_COL   EQU 6          ; あさ・ひる・よる
DEF CLOCK_SET_COL     EQU 11         ; せってい
DEF A_BUTTON          EQU 1
DEF B_BUTTON          EQU 2
DEF RestartClock_Bank EQU $08
DEF RestartClock_SetFromPad EQU $4027   ; RestartClock の「ld hl, wOptions」から（はじめの PrintText をとばす）
DEF JoyTextDelay      EQU $0a4d
DEF GetJoypad         EQU $0984
DEF DelayFrame        EQU $045a
DEF WaitBGMap         EQU $31c2
DEF hJoyDown          EQU $ffa8
DEF rSVBK             EQU $ff70
DEF CLOCKSUB_WRAMBANK EQU 2
DEF wClockSub         EQU $dfc2      ; WRAM バンク2（0 = あさ・ひる・よる、1 = せってい）

; ---- 表を 8つに（7 = とけい。おわり は なくす）
SECTION "opt pointers ptr", ROMX[$4290 + 1], BANK[OPT_BANK]
	dw OptionPointersNew

; ---- 上下の移動：いちばん下 = 7（とけい）
SECTION "opt down max", ROMX[$44fb + 1], BANK[OPT_BANK]
	db OPT_CLOCK
SECTION "opt up wrap", ROMX[$4518 + 1], BANK[OPT_BANK]
	db OPT_CLOCK + 1

; ---- カーソルの場所（元の 10列目を消す処理のあと）
SECTION "opt cursor", ROMX[$452b], BANK[OPT_BANK]
	jp Options_CursorNew

; ---- 今までの項目を 1行上げる（文字を置く場所 - 20）
MACRO opt_up ; ld hl, nn の場所
SECTION "opt up \@", ROMX[\1 + 1], BANK[OPT_BANK]
	dw \2 - SCREEN_WIDTH
ENDM
	opt_up $41e4, $c4c9   ; 項目の名前
	opt_up $41ed, $c5c3   ; ウインドウの「タイプ」
	opt_up $42dd, $c4d3   ; はなしの はやさ
	opt_up $4341, $c4e7   ; せんとうアニメ（濁点の行を消す所）
	opt_up $4348, $c4fb   ; せんとうアニメ
	opt_up $4389, $c523   ; しあいの ルール
	opt_up $43d2, $c54b   ; サウンド
	opt_up $4413, $c573   ; プリントの こさ
	opt_up $44a1, $c59b   ; メニューせつめい
	opt_up $44d6, $c5c7   ; ウインドウの番号
; 「タイプ<NEXT>おわり」の「おわり」は 出さない
SECTION "opt owari", ROMX[$4282 + 3], BANK[OPT_BANK]
	db "@"

; ---- 開いたときに「とけい」も出す
SECTION "opt init", ROMX[$420b], BANK[OPT_BANK]
	call Options_InitClock

SECTION "opt new", ROMX[$7e40], BANK[OPT_BANK]
OptionPointersNew:
	INCBIN "base.gbc", OPT_BANK * $4000 + OPT_POINTERS - $4000, 7 * 2   ; はなしのはやさ〜ウインドウ
	dw Options_Clock

; wClockSub を a に読む／a を書く（WRAM バンク2）
GetClockSub:
	push bc
	ldh a, [rSVBK]
	ld b, a
	ld a, CLOCKSUB_WRAMBANK
	ldh [rSVBK], a
	ld a, [wClockSub]
	ld c, a
	ld a, b
	ldh [rSVBK], a
	ld a, c
	pop bc
	and a
	ret
SetClockSub:
	push bc
	ld c, a
	ldh a, [rSVBK]
	ld b, a
	ld a, CLOCKSUB_WRAMBANK
	ldh [rSVBK], a
	ld a, c
	ld [wClockSub], a
	ld a, b
	ldh [rSVBK], a
	pop bc
	ret

; 元の処理が 10列目（1〜16行目）を消したあと
Options_CursorNew:
	ld hl, wTilemap + CLOCK_ROW * SCREEN_WIDTH + CLOCK_VALUE_COL - 1
	ld [hl], $7f                 ; とけいの行の 左のカーソル
	ld a, [wJumptableIndex]
	cp OPT_CLOCK
	jr nc, .bottom
	ld hl, wTilemap + 1 * SCREEN_WIDTH + 10
	ld bc, 2 * SCREEN_WIDTH
	call AddNTimes
	ld [hl], TILE_CURSOR
	ret
.bottom
	ld hl, wTilemap + CLOCK_ROW * SCREEN_WIDTH + 10
	call GetClockSub
	jr nz, .put
	ld hl, wTilemap + CLOCK_ROW * SCREEN_WIDTH + CLOCK_VALUE_COL - 1
.put
	ld [hl], TILE_CURSOR
	ret

Options_InitClock:
	xor a
	call SetClockSub             ; ひらいたときは「あさ・ひる・よる」の側
	call UpdateFrame             ; 元の call UpdateFrame
	ld hl, wTilemap + CLOCK_ROW * SCREEN_WIDTH + 1
	ld de, .label
	call PlaceString
	ld a, [wMapGroup]
	and a
	jp z, Options_ClockShow      ; ゲームを始める前は「せってい」を出さない
	ld hl, wTilemap + CLOCK_ROW * SCREEN_WIDTH + CLOCK_SET_COL
	ld de, .set
	call PlaceString
	jp Options_ClockShow
.label
	db "とけい@"
.set
	db "せってい@"

Options_Clock:
	ld a, [wMapGroup]
	and a
	jp z, Options_ClockShow      ; ゲームを始める前は 何もしない
	ldh a, [hJoyPressed]
	bit 5, a                     ; ひだり：あさ・ひる・よる を選ぶ
	jr nz, .pick_value
	bit 4, a                     ; みぎ：せってい を選ぶ
	jr nz, .pick_set
	bit 0, a                     ; A
	jp z, Options_ClockShow
	call GetClockSub
	jp nz, .setclock
; あさ・ひる・よる で A：左右で切りかえる（A・B で おわる）
	ld hl, wTilemap + CLOCK_ROW * SCREEN_WIDTH + CLOCK_VALUE_COL - 1
	ld [hl], TILE_HOLLOW         ; 切りかえ中は ▷
	call .release
.edit
	call DelayFrame
	call JoyTextDelay
	ldh a, [hJoyPressed]
	and A_BUTTON | B_BUTTON
	jr nz, .edit_done
	ldh a, [hJoyPressed]
	bit 5, a
	jr nz, .left
	bit 4, a
	jr z, .edit
	call .now
	inc a
	cp 3
	jr c, .set
	xor a
	jr .set
.left
	call .now
	dec a
	cp 3
	jr c, .set
	ld a, 2
.set
	ld e, a
	ld d, 0
	ld hl, .hours
	add hl, de
	ld a, [hl]
	push af
	call UpdateTime
	call GetWeekday
	ld [wStringBuffer2], a       ; 曜日はそのまま
	pop af
	ld [wStringBuffer2 + 1], a   ; 時
	xor a
	ld [wStringBuffer2 + 2], a   ; 分
	ld [wStringBuffer2 + 3], a   ; 秒
	call InitTime
	call Options_ClockShow
	jr .edit
.edit_done
	call .release
	jr Options_ClockShow

.pick_value
	xor a
	jr .pick
.pick_set
	ld a, 1
.pick
	call SetClockSub
	jr Options_ClockShow

; 時計を合わせなおす画面（元の RestartClock の まん中から。おわりに ExitMenu で 画面がもどる）
.setclock
	ld a, RestartClock_Bank
	ld hl, RestartClock_SetFromPad
	rst $08
	call WaitBGMap
	call .release
	jr Options_ClockShow

; 押しているボタンを はなすまで待つ
.release
	call DelayFrame
	call GetJoypad
	ldh a, [hJoyDown]
	and a
	jr nz, .release
	ret

; a = 今の時間帯（0 あさ・1 ひる・2 よる）
.now
	call UpdateTime
	ld a, [wTimeOfDay]
	cp 3
	ret c
	ld a, 2
	ret

.hours
	db 4, 10, 18

Options_ClockShow:
	ld a, [wMapGroup]
	and a
	ld a, 3                      ; ーー
	jr z, .got
	call UpdateTime
	ld a, [wTimeOfDay]
	cp 3
	jr c, .got
	ld a, 2
.got
	ld e, a
	ld d, 0
	ld hl, .strings
	add hl, de
	add hl, de
	ld a, [hli]
	ld d, [hl]
	ld e, a
	ld hl, wTilemap + CLOCK_ROW * SCREEN_WIDTH + CLOCK_VALUE_COL
	call PlaceString
	and a
	ret
.strings
	dw .morn, .day, .nite, .none
.morn
	db "あさ@"
.day
	db "ひる@"
.nite
	db "よる@"
.none
	db "ーー@"
