; せっていに「とけい」（あさ・ひる・よる）を足す（金 日本版。クリスタル追加機能キットの src/clockopt.asm をもとにした）
;
; ・せっていの「ウインドウ」の下に「とけい」を出す。
;   あさ（4:00）→ ひる（10:00）→ よる（18:00）に 時計を合わせる（曜日はそのまま。分・秒は 0）。
; ・ゲームを始める前（タイトルの「せっていを かえる」。wMapGroup = 0）は「ーー」を出して変えられない。
; ・今までの項目を 1行ずつ上げ（2〜14行目 → 1〜13行目）、「とけい」を 15行目に出す。
; ・「おわり」は なくす（B・START で とじる。元から B・START で とじられる）。
; ・「とけい」の行：「とけい ▶ひる  ▶せってい」。左右で「ひる」か「せってい」を選ぶ。
;   「ひる」で A … 左右で あさ（4:00）・ひる（10:00）・よる（18:00）を切りかえる（▷ になる。A・B で おわる）。
;   「せってい」で A を押すと、時計を合わせなおす画面（曜日・時・分。元の RestartClock の
;   「じゅうじキーで あわせてください」から。「とけいが くるっている かも」の文は出さない）に入る。
;   ゲームを始める前は 右の文を出さず、A でも何もしない。
;
; クリスタルとちがう所
; ・日本版 金の せってい（バンク$39）は 空きが おわりの 23バイトしかない（クリスタルは $7e40 に置いた）。
;   そこで 新しい処理は 新しいバンク（OPT_FAR_BANK）に置き、バンク$39 には 小さな入口だけを置く：
;     - GetOptionPointer の頭を「OptionsDispatch」へ：項目 0〜6 は 元のまま、7（とけい）は 新しいバンクへ。
;       （表を 9つにする代わり。表をバンク$39 に置く空きがないため）
;     - Options_UpdateCursorPosition（29バイト）を「新しいバンクのカーソルの処理を farcall」にし、
;       あまった所に「開いたときの処理」の入口を置く（元のカーソルの処理は 新しいほうで ぜんぶする）。
; ・金銀の せってい は クリスタルと同じ 8項目（はなしの はやさ〜ウインドウ・おわり）。元の おわり（7）の代わりに とけい（7）を置く。

INCLUDE "src/charmap_jp.inc"

DEF OPT_BANK          EQU $39
DEF OPT_FAR_BANK      EQU $42        ; 新しいバンク（ジムリーダー再戦と同じ。$42:$5800〜）
DEF OPT_FAR_ADDR      EQU $5800
DEF OPT_BANK39_FREE   EQU $7fe9      ; バンク$39 の空き（$7fe2〜$7fe8 はバグ修正）
DEF wJumptableIndex   EQU $ce57
DEF hJoyPressed       EQU $ffa9
DEF wMapGroup         EQU $d9c6      ; 0 = まだゲームを始めていない
DEF wStringBuffer2    EQU $cf92
DEF wTimeOfDay        EQU $d149
DEF UpdateTime        EQU $0467
DEF InitTime          EQU $0537
DEF GetWeekday        EQU $351b
DEF PlaceString       EQU $0f46
DEF AddNTimes         EQU $315f
DEF UpdateFrame       EQU $4ea9      ; バンク$39
DEF GetOptionPointer  EQU $4c60      ; ld a, [wJumptableIndex] / ld e, a / … / jp hl
DEF Options_UpdateCursorPosition EQU $4ef3
DEF TILE_CURSOR       EQU $ed
DEF TILE_HOLLOW       EQU $ec
DEF B_BUTTON          EQU 2
DEF JoyTextDelay      EQU $09fd
DEF wClockSub         EQU $de37     ; とけいの行で選んでいる所（0 = あさ・ひる・よる、1 = せってい）。使われていない WRAM
DEF wTilemap          EQU $c3a0
DEF SCREEN_WIDTH      EQU 20
DEF OPT_CLOCK         EQU 7
DEF CLOCK_ROW         EQU 15
DEF CLOCK_VALUE_COL   EQU 6        ; あさ・ひる・よる（「とけい」の右）
DEF CLOCK_SET_COL     EQU 11       ; 「せってい」（カーソルの右）
DEF RestartClock_Bank EQU $08
DEF RestartClock_SetFromPad EQU $4027   ; RestartClock の「ld hl, wOptions」から（はじめの PrintText をとばす）
DEF WaitBGMap         EQU $33ae
DEF DelayFrame        EQU $032e
DEF GetJoypad         EQU $0934
DEF hJoyDown          EQU $ffaa
DEF A_BUTTON          EQU 1

; ---- 項目を選ぶ所：7・8 は 新しいバンクへ
SECTION "opt dispatch hook", ROMX[GetOptionPointer], BANK[OPT_BANK]
	jp OptionsDispatch           ; ld a, [wJumptableIndex] の代わり

SECTION "opt dispatch", ROMX[OPT_BANK39_FREE], BANK[OPT_BANK]
OptionsDispatch:
	ld a, [wJumptableIndex]
	cp OPT_CLOCK
	jp c, GetOptionPointer + 3   ; 0〜6：元のまま（ld e, a から）
	ld a, OPT_FAR_BANK
	ld hl, Options_HighItems
	rst $08                      ; キャリー = せっていを閉じる
	ret

; ---- 上下の移動：いちばん下 = 7（とけい。おわり は なくした）
SECTION "opt down max", ROMX[$4ed1 + 1], BANK[OPT_BANK]   ; OptionsControl .DownPressed の cp OPT_CANCEL
	db OPT_CLOCK
SECTION "opt up wrap", ROMX[$4eee + 1], BANK[OPT_BANK]    ; .UpPressed の ld [hl], NUM_OPTIONS
	db OPT_CLOCK + 1

; ---- カーソル：新しいバンクで消して置く。あまった所に 開いたときの入口
SECTION "opt cursor", ROMX[Options_UpdateCursorPosition], BANK[OPT_BANK]
	ld a, OPT_FAR_BANK
	ld hl, Options_CursorNew
	rst $08
	ret
Options_InitClockEntry:
	ld a, OPT_FAR_BANK
	ld hl, Options_InitClock
	rst $08
	ret

; ---- 今までの項目を 1行上げる（文字を置く場所 - 20）
MACRO opt_up ; ld hl, nn の場所, nn
SECTION "opt up \@", ROMX[\1 + 1], BANK[OPT_BANK]
	dw \2 - SCREEN_WIDTH
ENDM
	opt_up $4bc3, $c3c9   ; 項目の名前（StringOptions）
	opt_up $4bcc, $c4c3   ; ウインドウの「タイプ」
	opt_up $4cb3, $c3d3   ; はなしの はやさ
	opt_up $4d17, $c3e7   ; せんとうアニメ（濁点の行を消す所）
	opt_up $4d1e, $c3fb   ; せんとうアニメ
	opt_up $4d5f, $c423   ; しあいの ルール
	opt_up $4da8, $c44b   ; サウンド
	opt_up $4de9, $c473   ; プリントの こさ
	opt_up $4e77, $c49b   ; メニューせつめい
	opt_up $4eac, $c4c7   ; ウインドウの番号
; 「タイプ<NEXT>おわり」の「おわり」は 出さない
SECTION "opt owari", ROMX[$4c58 + 3], BANK[OPT_BANK]
	db "@"

; ---- 開いたときに「とけい」も出す（call UpdateFrame の所）
SECTION "opt init", ROMX[$4bea], BANK[OPT_BANK]
	call Options_InitClockEntry

;---------------------------------------------------------------------
SECTION "opt new", ROMX[OPT_FAR_ADDR], BANK[OPT_FAR_BANK]
; 項目 7（とけい）。キャリー = せっていを閉じる
Options_HighItems:
	ld a, [wJumptableIndex]
	cp OPT_CLOCK
	jr z, Options_Clock
; （おわり は なくしたので ここには来ない）
	ldh a, [hJoyPressed]
	and A_BUTTON
	jr nz, .exit
	and a
	ret
.exit
	scf
	ret

Options_CursorNew:
; 元と同じに カーソルの列（10列目）を 1〜16行目まで消す
	ld hl, wTilemap + 1 * SCREEN_WIDTH + 10
	ld de, SCREEN_WIDTH
	ld c, 16
.clear
	ld [hl], $7f                 ; 空白
	add hl, de
	dec c
	jr nz, .clear
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
	ld a, [wClockSub]
	and a
	jr nz, .put
	ld hl, wTilemap + CLOCK_ROW * SCREEN_WIDTH + CLOCK_VALUE_COL - 1
.put
	ld [hl], TILE_CURSOR
	ret

Options_InitClock:
	xor a
	ld [wClockSub], a            ; ひらいたときは「あさ・ひる・よる」の側
	ld a, OPT_BANK
	ld hl, UpdateFrame
	rst $08                      ; 元の call UpdateFrame
	ld hl, wTilemap + CLOCK_ROW * SCREEN_WIDTH + 1
	ld de, .label
	call PlaceString
	ld a, [wMapGroup]
	and a
	jp z, Options_ClockShow      ; ゲームを始める前は 右の文を出さない
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
	ld a, [wClockSub]
	and a
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
	ld [wClockSub], a
	jr Options_ClockShow

; 時計を合わせなおす画面（元の RestartClock の まん中から。画面は おわったら 元にもどる）
.setclock
	ld a, RestartClock_Bank
	ld hl, RestartClock_SetFromPad
	rst $08
	call WaitBGMap
	call .release
	jr Options_ClockShow

; 押しているボタンを はなすまで待つ（もういちど 入らないように）
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
