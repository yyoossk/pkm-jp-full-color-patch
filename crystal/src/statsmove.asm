; 「つよさをみる」の わざのページ（2ページ目・緑）で、わざを並べかえる（クリスタル日本版）
;
; つかいかた（手持ちのポケモンの「つよさをみる」で、わざが出ているページ）
;   SELECT … 並べかえを始める（いちばん上のわざに ▶）
;   上下   … ▶ を動かす
;   A      … 動かすわざを選ぶ（▷ が残る）→ もういちど A で、▶ のわざと 入れかえる（わざと PP がいっしょに動く）
;            同じわざで A を押すと 選ぶのをやめる
;   B・SELECT … 選んでいれば 選ぶのをやめる。選んでいなければ 並べかえをおわる（ページは そのまま）
; ・手持ちのポケモンだけ（ボックス・相手のポケモン・タマゴは できない）。わざが 1つしかないときも できない。
; ・戦闘中は できない（戦っているポケモンのわざと ずれないように）。
; ・カーソルは わざの名前の左の 枠の線の上に出す（日本版の このページは 枠のすぐ右から わざの名前が始まるため）。
;
; しくみ（金のキットの statsmove.asm を クリスタルに合わせたもの）
;   MonStatsJoypad.next の「and PAD_CTRL_PAD | PAD_A | PAD_B / jp StatsScreen_JoypadAction」（5バイト）を
;   バンク$13 の空きの StatsMove_Hook へ。SELECT で 緑のページなら 新しいバンクの StatsMove_Main を farcall する。
;   入れかえたら 手持ちのデータ（わざ・PP）を入れかえ、wTempMon にもうつして LoadGreenPage で 書き直す。
;   作業用の値は レジスタとスタックに置く（WRAM は使わない）。

DEF SM_BANK            EQU $70
DEF SM_ADDR            EQU $5c00
DEF SM_HOOK            EQU $5c81    ; $13: MonStatsJoypad.next
DEF SM_HOOK_FREE       EQU $7760    ; バンク$13 の空き
DEF StatsScreen_JoypadAction EQU $5cf4
DEF LoadGreenPage      EQU $5fcc    ; $13
DEF GREEN_PAGE         EQU 2
DEF DelayFrame         EQU $045a
DEF GetJoypad          EQU $0984
DEF PlayClickSFX       EQU $1fcc
DEF PlaySFX            EQU $3bb0
DEF WaitSFX            EQU $3be2
DEF WaitBGMap          EQU $31c2
DEF SFX_SWITCH_POKEMON EQU $20
DEF hJoyPressed        EQU $ffa7
DEF hBGMapMode         EQU $ffd4
DEF wStatsScreenFlags  EQU $cf58
DEF wMonType           EQU $cf53    ; 0 = 手持ち
DEF wBattleMode        EQU $d25e
DEF wCurPartyMon       EQU $d0c9
DEF wTempMonMoves      EQU $d0d0
DEF wTempMonPP         EQU wTempMonMoves + 21
DEF wPartyMon1Moves    EQU $dca7
DEF wPartyMon1PP       EQU wPartyMon1Moves + 21
DEF PARTYMON_LENGTH    EQU $30
DEF wTilemap           EQU $c4a0
DEF SCREEN_WIDTH       EQU 20
DEF SM_COL             EQU 8        ; 枠の線（わざの名前の左）
DEF SM_ROW             EQU 6        ; 1つ目のわざの行（3行ずつ）
DEF TILE_CURSOR        EQU $ed      ; ▶
DEF TILE_HOLLOW        EQU $ec      ; ▷

;---------------------------------------------------------------------
SECTION "statsmove hook", ROMX[SM_HOOK], BANK[$13]
	jp StatsMove_Hook
	nop
	nop

SECTION "statsmove hook body", ROMX[SM_HOOK_FREE], BANK[$13]
; a = 押したボタン
StatsMove_Hook:
	bit 2, a                     ; SELECT
	jr nz, .select
.orig
	and $f3                      ; PAD_CTRL_PAD | PAD_A | PAD_B
	jp StatsScreen_JoypadAction
.select
	ld a, [wStatsScreenFlags]
	and 3
	cp GREEN_PAGE
	ret nz
	ld a, SM_BANK
	ld hl, StatsMove_Main
	rst $08
	ret

;---------------------------------------------------------------------
SECTION "statsmove main", ROMX[SM_ADDR], BANK[SM_BANK]
; b = わざの数、d = ▶ の所、e = 選んだわざ（$ff = 選んでいない）
StatsMove_Main:
	ld a, [wMonType]
	and a
	ret nz                       ; 手持ちだけ
	ld a, [wBattleMode]
	and a
	ret nz                       ; 戦闘中はしない
	ld hl, wTempMonMoves
	ld b, 0
.count
	ld a, [hli]
	and a
	jr z, .counted
	inc b
	ld a, b
	cp 4
	jr c, .count
.counted
	ld a, b
	cp 2
	ret c
	ld a, [wTilemap + SM_ROW * SCREEN_WIDTH + SM_COL]
	ld c, a                      ; c = 枠の線のタイル
	ld de, $00ff
	call .sfx_click

.loop
	call StatsMove_Draw
	push bc
	push de
	call WaitBGMap
	call GetJoypad
	pop de
	pop bc
	ldh a, [hJoyPressed]
	bit 6, a                     ; 上
	jr nz, .up
	bit 7, a                     ; 下
	jr nz, .down
	bit 0, a                     ; A
	jr nz, .a
	and %00000110                ; B・SELECT
	jr z, .loop
	ld a, e
	cp $ff
	jr z, .exit
	ld e, $ff
	jr .loop

.up
	ld a, d
	and a
	jr z, .loop
	dec d
	jr .loop

.down
	ld a, d
	inc a
	cp b
	jr nc, .loop
	ld d, a
	jr .loop

.a
	call .sfx_click
	ld a, e
	cp $ff
	jr nz, .swap
	ld e, d
	jr .loop
.swap
	cp d
	jr z, .unselect
	push bc
	push de
	; 手持ちのデータの わざ と PP を入れかえる（d・e = 番号）
	ld hl, wPartyMon1Moves
	call .mon_ptr
	call .swap_de
	ld hl, wPartyMon1PP
	call .mon_ptr
	call .swap_de
	; wTempMon にもうつす
	ld hl, wPartyMon1Moves
	call .mon_ptr
	ld de, wTempMonMoves
	call .copy4
	ld hl, wPartyMon1PP
	call .mon_ptr
	ld de, wTempMonPP
	call .copy4
	ld de, SFX_SWITCH_POKEMON
	call PlaySFX
	call WaitSFX
	; ページを書き直す
	ld a, $13
	ld hl, LoadGreenPage
	rst $08
	pop de
	pop bc
.unselect
	ld e, $ff
	jp .loop

.exit
	ld d, $ff                    ; カーソルを消す（枠の線にもどす）
	call StatsMove_Draw
	call WaitBGMap
	ret

.sfx_click
	push bc
	push de
	call PlayClickSFX
	pop de
	pop bc
	ret

; hl = 表の頭 → hl = [wCurPartyMon] 番目のポケモンの所
.mon_ptr
	ld a, [wCurPartyMon]
	push de
	ld de, PARTYMON_LENGTH
.mon_loop
	and a
	jr z, .mon_done
	add hl, de
	dec a
	jr .mon_loop
.mon_done
	pop de
	ret

; [hl+d] と [hl+e] を入れかえる（hl・de はそのまま）
.swap_de
	push hl
	push bc
	ld b, h
	ld c, l
	ld a, l
	add d
	ld l, a
	ld a, h
	adc 0
	ld h, a                      ; hl = d の所
	push hl
	ld a, c
	add e
	ld c, a
	ld a, b
	adc 0
	ld b, a                      ; bc = e の所
	pop hl
	ld a, [bc]
	push af
	ld a, [hl]
	ld [bc], a
	pop af
	ld [hl], a
	pop bc
	pop hl
	ret

.copy4
	ld b, 4
.copy_loop
	ld a, [hli]
	ld [de], a
	inc de
	dec b
	jr nz, .copy_loop
	ret

; 枠の線の上に ▶（いまの所 d）・▷（選んだわざ e）を出す。c = 枠の線のタイル
StatsMove_Draw:
	push bc
	ld hl, wTilemap + SM_ROW * SCREEN_WIDTH + SM_COL
	ld b, 0
.row
	ld a, d
	cp b
	ld a, TILE_CURSOR
	jr z, .put
	ld a, e
	cp b
	ld a, TILE_HOLLOW
	jr z, .put
	ld a, c
.put
	ld [hl], a
	push de
	ld de, 3 * SCREEN_WIDTH
	add hl, de
	pop de
	inc b
	ld a, b
	cp 4
	jr c, .row
	pop bc
	ret
