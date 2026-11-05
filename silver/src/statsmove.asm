; 「つよさをみる」の わざのページ（2ページ目・緑）で、わざを並べかえる（日本版 銀。金のキットの statsmove.asm と同じ。アドレスは金と同じ）
;
; つかいかた（手持ちのポケモンの「つよさをみる」で、わざが出ているページ）
;   SELECT … 並べかえを始める（いちばん上のわざに ▶）
;   上下   … ▶ を動かす
;   A      … 動かすわざを選ぶ（▷ が残る）→ もういちど A で、▶ のわざと 入れかえる（わざと PP がいっしょに動く）
;            同じわざで A を押すと 選ぶのをやめる
;   B・SELECT … 選んでいれば 選ぶのをやめる。選んでいなければ 並べかえをおわる（ページは そのまま）
; ・手持ちのポケモンだけ（ボックス・相手のポケモン・タマゴは できない）。わざが 1つしかないときも できない。
; ・戦闘中は できない（戦っているポケモンのわざと ずれないように。手持ちメニューの「つかえるわざ」も戦闘中は出ない）。
; ・カーソルは わざの名前の左の 枠の線の上に出す（日本版の このページは 左の枠のすぐ右から わざの名前が始まるため）。
;
; しくみ
;   StatsScreen_LoadPage.joypad_action の「and PAD_CTRL_PAD | PAD_A | PAD_B / jr z, .joypad_loop」（4バイト）を
;   バンク$14 の空きの StatsMove_Hook へ。SELECT で 緑のページなら 新しいバンクの StatsMove_Main を farcall する。
;   入れかえたら 手持ちのデータ（わざ・PP）を入れかえ、wTempMon にもうつして LoadGreenPage で ページを書き直す。

DEF SM_BANK            EQU $3f      ; 新しい処理（ひでんわざ・ぶんぷの釣り と同じバンクの空き）
DEF SM_ADDR            EQU $6e00
DEF SM_HOOK            EQU $4d06    ; $14: StatsScreen_LoadPage.joypad_action
DEF SM_JOYPAD_LOOP     EQU $4ce2    ; $14: StatsScreen_LoadPage.joypad_loop
DEF SM_HOOK_FREE       EQU $7fe2    ; バンク$14 の空き（$7fe2〜$7fff）
DEF LoadGreenPage      EQU $501a    ; $14
DEF GREEN_PAGE         EQU 2
DEF DelayFrame         EQU $032e
DEF GetJoypad          EQU $0934
DEF PlayClickSFX       EQU $1e1d
DEF PlaySFX            EQU $3d45
DEF WaitSFX            EQU $3d77
DEF SFX_SWITCH_POKEMON EQU $20
DEF hJoyPressed        EQU $ffa9
DEF wMonType           EQU $ce53    ; 0 = 手持ち
DEF wBattleMode        EQU $d108
DEF wCurPartyMon       EQU $cfff
DEF wTempMonMoves      EQU $d007
DEF wTempMonPP         EQU wTempMonMoves + 21
DEF wPartyMon1Moves    EQU $d9f2
DEF wPartyMon1PP       EQU wPartyMon1Moves + 21
DEF PARTYMON_LENGTH    EQU $30
DEF wTilemap           EQU $c3a0
DEF SCREEN_WIDTH       EQU 20
DEF SM_COL             EQU 8        ; 枠の線（わざの名前の左）
DEF SM_ROW             EQU 6        ; 1つ目のわざの行（3行ずつ）
DEF SM_BORDER          EQU $7c      ; 枠の線（たて）
DEF TILE_CURSOR        EQU $ed      ; ▶
DEF TILE_HOLLOW        EQU $ec      ; ▷
; 作業用の WRAM（使われていない $de37〜。$de38〜$de3a はバグ修正、$de40〜 は 60fps）
; 銀は $de3c を 手持ちの見た目（wIconSpecies）で使っているので、$de3b・$de3d・$de3e を使う
DEF wSMCursor          EQU $de3b
DEF wSMSelected        EQU $de3d    ; $ff = 選んでいない
DEF wSMCount           EQU $de3e

;---------------------------------------------------------------------
SECTION "statsmove hook", ROMX[SM_HOOK], BANK[$14]
	call StatsMove_Hook
	nop

SECTION "statsmove hook body", ROMX[SM_HOOK_FREE], BANK[$14]
; a = 押したボタン（元の and $f3 / jr z, .joypad_loop の代わり。0 でなければ そのまま続ける）
StatsMove_Hook:
	bit 2, a                     ; SELECT
	jr nz, .select
.mask
	and $f3                      ; PAD_CTRL_PAD | PAD_A | PAD_B
	ret nz
.loop
	add sp, 2                    ; もどり先をすてて
	jp SM_JOYPAD_LOOP            ; ボタン待ちにもどる
.select
	ld a, c
	cp GREEN_PAGE
	jr nz, .loop
	push bc
	ld a, SM_BANK
	ld hl, StatsMove_Main
	rst $08
	pop bc
	jr .loop

;---------------------------------------------------------------------
SECTION "statsmove main", ROMX[SM_ADDR], BANK[SM_BANK]
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
	ld [wSMCount], a
	xor a
	ld [wSMCursor], a
	dec a
	ld [wSMSelected], a
	call PlayClickSFX

.loop
	call StatsMove_Draw
	call DelayFrame
	call GetJoypad
	ldh a, [hJoyPressed]
	bit 6, a                     ; 上
	jr nz, .up
	bit 7, a                     ; 下
	jr nz, .down
	bit 0, a                     ; A
	jr nz, .a
	and %00000110                ; B・SELECT
	jr z, .loop
	ld a, [wSMSelected]
	cp $ff
	jp z, .exit
	ld a, $ff
	ld [wSMSelected], a
	jr .loop

.up
	ld a, [wSMCursor]
	and a
	jr z, .loop
	dec a
	ld [wSMCursor], a
	jr .loop

.down
	ld a, [wSMCount]
	ld b, a
	ld a, [wSMCursor]
	inc a
	cp b
	jr nc, .loop
	ld [wSMCursor], a
	jr .loop

.a
	call PlayClickSFX
	ld a, [wSMSelected]
	cp $ff
	jr nz, .swap
	ld a, [wSMCursor]
	ld [wSMSelected], a
	jr .loop
.swap
	ld b, a
	ld a, [wSMCursor]
	cp b
	jr z, .unselect
	ld c, a
	; 手持ちのデータの わざ と PP を入れかえる（b・c = 番号）
	ld a, [wCurPartyMon]
	ld hl, wPartyMon1Moves
	call .mon_ptr
	push hl
	call .swap_bc
	pop hl
	ld de, wPartyMon1PP - wPartyMon1Moves
	add hl, de
	call .swap_bc
	; wTempMon にもうつす
	ld a, [wCurPartyMon]
	ld hl, wPartyMon1Moves
	call .mon_ptr
	ld de, wTempMonMoves
	call .copy4
	ld a, [wCurPartyMon]
	ld hl, wPartyMon1PP
	call .mon_ptr
	ld de, wTempMonPP
	call .copy4
	ld de, SFX_SWITCH_POKEMON
	call PlaySFX
	call WaitSFX
	; ページを書き直す（b = 1：ポケモンの絵は そのまま、c = 緑のページ）
	ld bc, (1 << 8) | GREEN_PAGE
	ld a, $14
	ld hl, LoadGreenPage
	rst $08
.unselect
	ld a, $ff
	ld [wSMSelected], a
	jp .loop

.exit
	ld a, $ff
	ld [wSMCursor], a            ; カーソルを消す
	call StatsMove_Draw
	ret

; hl = 表の頭、a = 手持ちの番号 → hl = そのポケモンの所
.mon_ptr
	ld de, PARTYMON_LENGTH
.mon_loop
	and a
	ret z
	add hl, de
	dec a
	jr .mon_loop

; [hl+b] と [hl+c] を入れかえる
.swap_bc
	push hl
	ld d, 0
	ld e, b
	add hl, de
	ld a, [hl]
	pop de                       ; de = 表の頭
	push hl                      ; hl = b の所
	ld h, d
	ld l, e
	ld d, 0
	ld e, c
	add hl, de                   ; hl = c の所
	ld e, [hl]
	ld [hl], a
	pop hl
	ld [hl], e
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

; 枠の線の上に ▶（いまの所）・▷（選んだわざ）を出す。wSMCursor = $ff なら 消すだけ
StatsMove_Draw:
	ld hl, wTilemap + SM_ROW * SCREEN_WIDTH + SM_COL
	ld de, 3 * SCREEN_WIDTH
	ld b, 0
.row
	ld a, [wSMCursor]
	cp b
	ld a, TILE_CURSOR
	jr z, .put
	ld a, [wSMSelected]
	cp b
	ld a, TILE_HOLLOW
	jr z, .put
	ld a, SM_BORDER
.put
	ld [hl], a
	add hl, de
	inc b
	ld a, b
	cp 4
	jr c, .row
	ret
