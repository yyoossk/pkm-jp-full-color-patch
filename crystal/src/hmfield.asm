; ひでんわざを フィールドで「話しかけて」使うときは、ポケモンが覚えていなくても使える
; （金・銀・クリスタル 共通。アドレスは下の「ROM ごとにちがう所」だけ変える）
;
; 対象：いあいぎり（木）・なみのり（水）・かいりき（岩）・うずしお・たきのぼり
;   ・バッジがないと使えないのは今までどおり（バッジの確認は CheckPartyMove の外でしている）。
;   ・覚えているポケモンがいれば、今までどおりそのポケモンが使う。
;   ・だれも覚えていなければ、手持ちの いちばん前の（タマゴでない）ポケモンが使う。
;   ・ずつき（木をゆらす）・いわくだき（岩をくだく）も、そのわざマシンを もらったあと（イベントフラグ）なら、
;     覚えているポケモンがいなくても いちばん前のポケモンが使う。もらう前は 今までどおり覚えていないと使えない。
;     （わざマシン02 ずつき = ウバメのもりの人、わざマシン08 いわくだき = 36ばんどうろの人。わざマシンは使うとなくなるので、
;       リュックの中ではなく「もらった」フラグで決める）
;   ・そらをとぶ・フラッシュ は手持ちのメニューから使うわざなので、変わらない。
;
; しくみ
;   フィールドのわざの確認（TrySurfOW・TryCutOW・TryStrengthOW・TryWhirlpoolOW・TryWaterfallOW
;   ・TryHeadbuttOW・HasRockSmash）は、ぜんぶ CheckPartyMove（d = わざ）を呼んでいる。
;   CheckPartyMove の頭を「新しい CheckPartyMove を farcall する」に書きかえる（8バイト。残りは使われなくなる）。
;   farcall（rst $08）は呼んだ先のフラグ（キャリー）をそのまま返すので、呼ぶ側はそのままでよい。
;   キャリーなし = 使える（wCurPartyMon = 使うポケモン）、キャリーあり = 使えない。

;---------------------------------------------------------------------
; ROM ごとにちがう所（金 日本版 後期版の値）
;   tools/hmfield_find.py ROM で、金・銀・クリスタルのどれでも、この5つを出せる。
;   HMFIELD_BANK・HMFIELD_ADDR は空いている所を選ぶ（新しい処理は約70バイト）。
;---------------------------------------------------------------------
IF !DEF(HMFIELD_CheckPartyMove)
DEF HMFIELD_CheckPartyMove      EQU $47b6   ; バンク3 の CheckPartyMove
DEF HMFIELD_CheckPartyMove_BANK EQU $03
DEF HMFIELD_wCurPartyMon        EQU $cfff
DEF HMFIELD_wPartySpecies       EQU $d9e9
DEF HMFIELD_wPartyMon1Moves     EQU $d9f2
DEF HMFIELD_AddNTimes           EQU $315f   ; ホーム
DEF HMFIELD_BANK                EQU $3f     ; 新しい処理を置くバンク
DEF HMFIELD_ADDR                EQU $7e00   ;              アドレス
ENDC

; ずつき・いわくだき の わざマシンを もらったフラグ（金 日本版。銀も同じ番号のはず。クリスタルは
;   pret/pokecrystal の EVENT_GOT_TM02_HEADBUTT・EVENT_GOT_TM08_ROCK_SMASH と wEventFlags で確かめる）
;   HMFIELD_TM_EVENTS EQU 0 を先に書くと、ずつき・いわくだき は今までどおり（覚えていないと使えない）。
IF !DEF(HMFIELD_TM_EVENTS)
DEF HMFIELD_TM_EVENTS          EQU 1
ENDC
IF HMFIELD_TM_EVENTS && !DEF(HMFIELD_wEventFlags)
DEF HMFIELD_wEventFlags        EQU $d7aa
DEF HMFIELD_EVENT_TM02         EQU $5f    ; EVENT_GOT_TM02_HEADBUTT（ウバメのもりの人の verbosegiveitem TM_HEADBUTT のあとの setevent $5f）
DEF HMFIELD_EVENT_TM08         EQU $4b    ; EVENT_GOT_TM08_ROCK_SMASH
ENDC

; 金・銀・クリスタル 共通
DEF HMFIELD_HEADBUTT   EQU $1d
DEF HMFIELD_ROCK_SMASH EQU $f9
DEF HMFIELD_EGG       EQU $fd
DEF HMFIELD_MONLEN    EQU $30     ; PARTYMON_STRUCT_LENGTH
DEF HMFIELD_NUM_MOVES EQU 4
DEF HMFIELD_CUT       EQU $0f
DEF HMFIELD_SURF      EQU $39
DEF HMFIELD_STRENGTH  EQU $46
DEF HMFIELD_WATERFALL EQU $7f
DEF HMFIELD_WHIRLPOOL EQU $fa

;---------------------------------------------------------------------
SECTION "hmfield CheckPartyMove", ROMX[HMFIELD_CheckPartyMove], BANK[HMFIELD_CheckPartyMove_BANK]
	ld a, HMFIELD_BANK
	ld hl, HMField_CheckPartyMove
	rst $08
	ret

;---------------------------------------------------------------------
SECTION "hmfield main", ROMX[HMFIELD_ADDR], BANK[HMFIELD_BANK]
; d = わざ → キャリーなし：wCurPartyMon = 使うポケモン / キャリーあり：使えない
HMField_CheckPartyMove:
	xor a
	ld [HMFIELD_wCurPartyMon], a
; まず元と同じ：覚えているポケモンをさがす
	ld e, 0
.loop
	ld c, e
	ld b, 0
	ld hl, HMFIELD_wPartySpecies
	add hl, bc
	ld a, [hl]
	and a
	jr z, .nobody
	cp -1
	jr z, .nobody
	cp HMFIELD_EGG
	jr z, .next
	ld bc, HMFIELD_MONLEN
	ld hl, HMFIELD_wPartyMon1Moves
	ld a, e
	call HMFIELD_AddNTimes
	ld b, HMFIELD_NUM_MOVES
.check
	ld a, [hli]
	cp d
	jr z, .yes
	dec b
	jr nz, .check
.next
	inc e
	jr .loop

; だれも覚えていない：話しかけて使う ひでんわざ なら、いちばん前のポケモン
.nobody
IF HMFIELD_TM_EVENTS
	ld a, d
	ld hl, HMFIELD_wEventFlags + HMFIELD_EVENT_TM02 / 8
	ld b, 1 << (HMFIELD_EVENT_TM02 % 8)
	cp HMFIELD_HEADBUTT
	jr z, .tm
	ld hl, HMFIELD_wEventFlags + HMFIELD_EVENT_TM08 / 8
	ld b, 1 << (HMFIELD_EVENT_TM08 % 8)
	cp HMFIELD_ROCK_SMASH
	jr nz, .not_tm
.tm
	ld a, [hl]
	and b
	jr z, .no                    ; まだ わざマシンを もらっていない
	jr .front
.not_tm
ENDC
	ld hl, .moves
.hm
	ld a, [hli]
	and a
	jr z, .no
	cp d
	jr nz, .hm
.front
	ld e, 0
	ld hl, HMFIELD_wPartySpecies
.first
	ld a, [hli]
	and a
	jr z, .no
	cp -1
	jr z, .no
	cp HMFIELD_EGG
	jr nz, .yes
	inc e
	jr .first

.yes
	ld a, e
	ld [HMFIELD_wCurPartyMon], a
	xor a              ; キャリーなし
	ret
.no
	scf
	ret

.moves
	db HMFIELD_CUT, HMFIELD_SURF, HMFIELD_STRENGTH, HMFIELD_WHIRLPOOL, HMFIELD_WATERFALL, 0
