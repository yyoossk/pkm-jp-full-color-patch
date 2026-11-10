; むしとり大会で つかまえた ポケモンを、にがす かわりに パソコンへ おくれる（金 日本版。クリスタルの contestpc_crystal.asm から）
;   元の ゲームは 大会の ポケモンは 1匹だけで、2匹めを つかまえると「いれかえる？」と きかれ、えらばなかった ほうは にがす。
;   ・「はい」（入れかえる）→ 前の ポケモンを「○○を パソコンに おくりますか？」→ はい なら パソコンへ。
;   ・「いいえ」（入れかえない）→ つかまえた ポケモンを「○○を パソコンに おくりますか？」→ はい なら パソコンへ。
;   ・いいえ なら 元の ゲームと 同じ（にがす）。
;   ・いまの ボックスが いっぱい（30匹）なら、次の あいて いる ボックスへ おくる（「○○を ボックス２に おくりました！」）。
;     ぜんぶ いっぱいの ときは「ボックスが いっぱいなので…」で にがす。
; しくみ
;   ・BugContest_SetCaughtContestMon（$03:$6a4d）の「lb bc, 14, 12 / call PlaceYesNoBox / ret c」（$03:$6a62。7バイト）を
;     farcall ContestPC_YesNo / ret c に。
;   ・パソコンへ おくるのは 大会の おわりに 手持ちが いっぱいの ときと 同じ 処理（CheckPartyFullAfterContest .TryAddToBox
;     $31:$7cb1）を まねて 書いた。金銀には つかまえた 場所の データが ないので、そこは しない。
;     ニックネームは きかない（戦いの 中で 名前の 画面を ひらくと もどった あと フィールドの 画面に なるため）。
;   ・入れかえない ときは、前の ポケモン（wContestMon $dc5d・48バイト）を wOTPartyMon6（$ddbe。野生の 戦いでは 使わない）に
;     よけて、つかまえた ポケモンを .generatestats（$03:$6a7c）で wContestMon に 作り、おくって から 前の ポケモンを もどす。
;     （金銀は 初代ゲームボーイでも 動くので、クリスタルの ように WRAM バンク2 は 使わない）
;   ・アドレスは 日本版 金の ROM（tools では なく TryAddToBox・BugContest_SetCaughtContestMon の 中の 値から）。
;     銀は 同じ 探し方で しらべる（下の DEF）。
INCLUDE "src/charmap_jp.inc"

IF !DEF(CP_HOOK)
DEF CP_HOOK            EQU $6a62
DEF CP_HOOK_BANK       EQU $03
DEF CP_GENSTATS        EQU $6a7c      ; BugContest_SetCaughtContestMon.generatestats
DEF CP_InsertPokemonIntoBox EQU $59a7
DEF CP_InsertPokemonIntoBox_BANK EQU $14
DEF CP_CopyBytes       EQU $30d6
DEF CP_wCurPartyMon    EQU $cfff
DEF CP_wBufferMon      EQU $cf2d
DEF CP_wBufferMonOT    EQU $cf27
DEF CP_wPlayerName     EQU $d1b5
DEF CP_sBoxMonNicknames EQU $b1a4
DEF CP_PlaceYesNoBox   EQU $1bf1
DEF CP_PrintText       EQU $0f30
DEF CP_GetPokemonName  EQU $35e0
DEF CP_GetBaseData     EQU $39dd
DEF CP_OpenSRAM        EQU $309d
DEF CP_CloseSRAM       EQU $30ad
DEF CP_sBoxCount       EQU $ad10
DEF CP_wContestMon     EQU $dc5d      ; 48バイト
DEF CP_wTempEnemyMonSpecies EQU $d0df
DEF CP_wNamedObjectIndex EQU $d143
DEF CP_wCurPartySpecies EQU $cffe
DEF CP_wCurSpecies     EQU $ce54
DEF CP_wStringBuffer1  EQU $cf87
DEF CP_wCurBox         EQU $d8af
DEF CP_sBox            EQU $ad10      ; SRAM バンク1（いまの ボックス）
DEF CP_BOX_SIZE        EQU $54a
DEF CP_wStringBuffer2  EQU $cf92      ; 写す 間：[4] ＝ 元の SRAM バンク・[5] ＝ 先の SRAM バンク。文：[0] ＝ ボックスの 数字・[1] ＝ "@"
DEF CP_SAVE            EQU $ddbe      ; wOTPartyMon6（48バイト。野生の 戦いでは 使わない）
DEF CP_BANK            EQU $45
DEF CP_ADDR            EQU $7c00
ENDC

SECTION "contestpc hook", ROMX[CP_HOOK], BANK[CP_HOOK_BANK]
	ld a, BANK(ContestPC_YesNo)
	ld hl, ContestPC_YesNo
	rst $08
	ret c

SECTION "contestpc", ROMX[CP_ADDR], BANK[CP_BANK]
; キャリー ＝ 入れかえない（元の ret c）
ContestPC_YesNo:
	ld bc, $0e0c                      ; 元の 命令（lb bc, 14, 12 / call PlaceYesNoBox）
	call CP_PlaceYesNoBox
	jr c, .keep
	; 入れかえる：前の ポケモンを おくるか
	ld a, [CP_wContestMon]
	call ContestPC_Ask
	call nc, ContestPC_Send
	and a
	ret
.keep
	; 入れかえない：つかまえた ポケモンを おくるか
	ld a, [CP_wTempEnemyMonSpecies]
	call ContestPC_Ask
	jr c, .ret_c
	ld a, 2                           ; 前の ポケモンを よける
	call ContestPC_Copy
	ld a, CP_HOOK_BANK
	ld hl, CP_GENSTATS
	rst $08                           ; つかまえた ポケモンを wContestMon に
	call ContestPC_Send
	ld a, 1                           ; 前の ポケモンを もどす
	call ContestPC_Copy
.ret_c
	scf
	ret

; a ＝ 種類。「○○を パソコンに おくりますか？」キャリー ＝ いいえ
ContestPC_Ask:
	ld [CP_wNamedObjectIndex], a
	call CP_GetPokemonName
	ld hl, ContestPC_AskText
	call CP_PrintText
	ld bc, $0e0c                      ; 「入れかえる？」と 同じ 場所（右下）
	jp CP_PlaceYesNoBox

; wContestMon を ボックスへ。いまの ボックスが いっぱい なら、次の あいて いる ボックスへ 直接 おくる
; （大会中は レポートを 書けない ので ボックスは 切りかえない。大会が おわれば いつもの 自動切りかえが 動く）
ContestPC_Send:
	ld a, 1                           ; BANK(sBoxCount)
	call CP_OpenSRAM
	ld a, [CP_sBoxCount]
	cp 30
	call CP_CloseSRAM
	jr c, .here
	call ContestPC_FindBox            ; a ＝ おくる ボックス
	jr c, .full
	; 戦いの 中なので SaveBox・LoadBox は 使わない（wBoxPartialData が 戦いの データと 同じ 所）。SRAM から SRAM へ 写す
	push af
	push af
	ld a, [CP_wCurBox]
	ld e, 1                           ; sBox → いまの ボックスの 場所
	call ContestPC_BoxCopy
	pop af
	push af
	ld e, 0                           ; おくる ボックス → sBox
	call ContestPC_BoxCopy
	call .insert
	pop af
	ld e, 1                           ; sBox → おくる ボックス
	call ContestPC_BoxCopy
	ld a, [CP_wCurBox]
	ld e, 0                           ; いまの ボックス → sBox
	call ContestPC_BoxCopy
	ld a, [CP_wCurPartySpecies]
	ld [CP_wNamedObjectIndex], a
	call CP_GetPokemonName
	pop af
	add $f7                           ; 「１」〜（名前を 作る 処理が wStringBuffer2 を 使うので ここで 書く）
	ld [CP_wStringBuffer2], a
	ld a, $50
	ld [CP_wStringBuffer2 + 1], a
	ld hl, ContestPC_SentBoxText
	jp CP_PrintText
.here
	call .insert
	ld a, [CP_wCurPartySpecies]
	ld [CP_wNamedObjectIndex], a
	call CP_GetPokemonName
	ld hl, ContestPC_SentText
	jp CP_PrintText
.full
	ld hl, ContestPC_FullText
	jp CP_PrintText

; wContestMon を sBox に 入れる
.insert
	ld a, [CP_wContestMon]
	ld [CP_wCurPartySpecies], a
	ld [CP_wCurSpecies], a
	call CP_GetBaseData
	; CheckPartyFullAfterContest.TryAddToBox（$31:$7cb1）と 同じ（ニックネームは きかない：戦いの 中で 名前の 画面を
	; ひらくと、もどった あと フィールドの 画面に なって しまう。名前は ポケモンの 名前の まま）
	xor a
	ld [CP_wCurPartyMon], a
	ld hl, CP_wContestMon
	ld de, CP_wBufferMon
	ld bc, 32                         ; BOXMON_STRUCT_LENGTH
	call CP_CopyBytes
	ld hl, CP_wPlayerName
	ld de, CP_wBufferMonOT
	ld bc, 6
	call CP_CopyBytes
	ld a, CP_InsertPokemonIntoBox_BANK
	ld hl, CP_InsertPokemonIntoBox
	rst $08
	ld a, [CP_wCurPartySpecies]
	ld [CP_wNamedObjectIndex], a
	call CP_GetPokemonName
	ld a, 1                           ; BANK(sBoxMonNicknames)
	call CP_OpenSRAM
	ld hl, CP_wStringBuffer1
	ld de, CP_sBoxMonNicknames
	ld bc, 6
	call CP_CopyBytes
	jp CP_CloseSRAM                   ; （金銀は つかまえた 場所の データが ない）

; いまの 次から じゅんに あいて いる ボックスを さがす。a ＝ ボックス（0〜）、キャリー ＝ ぜんぶ いっぱい
ContestPC_FindBox:
	ld a, [CP_wCurBox]
	ld c, a
	ld b, 9 - 1
.loop
	inc c
	ld a, c
	cp 9
	jr c, .ok
	ld c, 0
.ok
	push bc
	call ContestPC_BoxAddr            ; d ＝ バンク、hl ＝ 場所
	ld a, d
	call CP_OpenSRAM
	ld a, [hl]
	call CP_CloseSRAM
	pop bc
	cp 30
	jr c, .found
	dec b
	jr nz, .loop
	scf
	ret
.found
	ld a, c
	and a
	ret

; c ＝ ボックス（0〜）→ d ＝ SRAM バンク、hl ＝ 場所
ContestPC_BoxAddr:
	ld b, 0
	ld hl, ContestPC_Boxes
	add hl, bc
	add hl, bc
	add hl, bc
	ld d, [hl]
	inc hl
	ld a, [hli]
	ld h, [hl]
	ld l, a
	ret

; a ＝ ボックス（0〜）、e ＝ 0：その ボックス → sBox ／ 1：sBox → その ボックス（SRAM から SRAM へ 1バイトずつ）
ContestPC_BoxCopy:
	ld c, a
	ld a, e
	push af
	call ContestPC_BoxAddr
	pop af                            ; a ＝ e
	and a
	jr nz, .tobox
	; その ボックス（d:hl）→ sBox
	ld a, d
	ld [CP_wStringBuffer2 + 4], a
	ld a, 1
	ld [CP_wStringBuffer2 + 5], a
	ld de, CP_sBox
	jr .go
.tobox
	ld a, d
	ld [CP_wStringBuffer2 + 5], a
	ld a, 1
	ld [CP_wStringBuffer2 + 4], a
	ld d, h
	ld e, l
	ld hl, CP_sBox
.go
	ld bc, CP_BOX_SIZE
	ld a, $0a                         ; SRAM を つかえる ように（OpenSRAM と 同じ）
	ld [$0000], a
.copy
	ld a, [CP_wStringBuffer2 + 4]
	ld [$4000], a
	ld a, [hli]
	push af
	ld a, [CP_wStringBuffer2 + 5]
	ld [$4000], a
	pop af
	ld [de], a
	inc de
	dec bc
	ld a, b
	or c
	jr nz, .copy
	jp CP_CloseSRAM

; ボックス 1〜9 の 場所（GetBoxCount.BoxBankAddresses $03:$6953 と 同じ。SRAM の バンク, 場所）
ContestPC_Boxes:
	db $2
	dw $a000
	db $2
	dw $a54a
	db $2
	dw $aa94
	db $2
	dw $afde
	db $2
	dw $b528
	db $2
	dw $ba72
	db $3
	dw $a000
	db $3
	dw $a54a
	db $3
	dw $aa94

; a ＝ 2：wContestMon → よける所、1：よける所 → wContestMon（48バイト）
ContestPC_Copy:
	ld hl, CP_wContestMon
	ld de, CP_SAVE
	cp 2
	jr z, .go
	ld hl, CP_SAVE
	ld de, CP_wContestMon
.go
	ld bc, 48
	jp CP_CopyBytes

ContestPC_AskText: ; ○○を パソコンに おくりますか？
	db $01
	dw CP_wStringBuffer1
	db $00, "を", $4f, "パソコンに　おくりますか？", $57
ContestPC_SentText: ; ○○を パソコンに おくりました！
	db $01
	dw CP_wStringBuffer1
	db $00, "を", $4f, "パソコンに　おくりました！", $58
ContestPC_SentBoxText: ; ○○を ボックス２に おくりました！
	db $01
	dw CP_wStringBuffer1
	db $00, "を", $4f, $1c, "ックス", $50
	db $01
	dw CP_wStringBuffer2
	db $00, "に　おくりました！", $58
ContestPC_FullText: ; ボックスが いっぱいなので パソコンに おくれません！
	db $00, $1c, "ックスが　いっぱいなので", $4f, "パソコンに　おくれません！", $58
