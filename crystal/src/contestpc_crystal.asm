; むしとり大会で つかまえた ポケモンを、にがす かわりに パソコンへ おくれる … クリスタル（日本版）
;   元の ゲームは 大会の ポケモンは 1匹だけで、2匹めを つかまえると「入れかえる？」と きかれ、えらばなかった ほうは にがす。
;   ・「はい」（入れかえる）→ 前の ポケモンを「○○を パソコンに おくりますか？」→ はい なら パソコンへ。
;   ・「いいえ」（入れかえない）→ つかまえた ポケモンを「○○を パソコンに おくりますか？」→ はい なら パソコンへ。
;   ・いいえ なら 元の ゲームと 同じ（にがす）。ボックスが いっぱい（30匹）の ときは「ボックスが いっぱいなので…」で にがす。
; しくみ
;   ・BugContest_SetCaughtContestMon（$03:$697c）の「lb bc, 14, 12 / call PlaceYesNoBox / ret c」（$03:$6991。7バイト）を
;     farcall ContestPC_YesNo / ret c に。
;   ・パソコンへ おくるのは 大会の おわりに 手持ちが いっぱいの ときと 同じ 処理（CheckPartyFullAfterContest .TryAddToBox
;     $13:$592c。wContestMon を ボックスに 入れて、つかまえた 場所を しぜんこうえん に する）を まねて 書いた。
;     ニックネームは きかない（戦いの 中で 名前の 画面を ひらくと もどった あと フィールドの 画面に なるため）。
;   ・入れかえない ときは、前の ポケモン（wContestMon $df12・48バイト）を WRAM バンク2 の $dfd0〜$dfff に よけて、
;     つかまえた ポケモンを .generatestats（$03:$69ab）で wContestMon に 作り、おくって から 前の ポケモンを もどす。
INCLUDE "src/charmap_jp.inc"

DEF CP_HOOK            EQU $6991
DEF CP_HOOK_BANK       EQU $03
DEF CP_GENSTATS        EQU $69ab      ; BugContest_SetCaughtContestMon.generatestats
DEF CP_TRYADD_BANK     EQU $13        ; CheckPartyFullAfterContest.TryAddToBox（$13:$592c）を まねる
DEF CP_SetBoxMonCaughtData EQU $5a23
DEF CP_InsertPokemonIntoBox EQU $53b8
DEF CP_InsertPokemonIntoBox_BANK EQU $14
DEF CP_CopyBytes       EQU $2ff2
DEF CP_wCurPartyMon    EQU $d0c9
DEF CP_wCurPartyLevel  EQU $d103
DEF CP_wBufferMon      EQU $d00e
DEF CP_wBufferMonOT    EQU $d008
DEF CP_wPlayerName     EQU $d48e
DEF CP_sBoxMonNicknames EQU $b1a4
DEF CP_sBoxMon1Level   EQU $ad4f
DEF CP_sBoxMon1CaughtLocation EQU $ad4e
DEF CP_PlaceYesNoBox   EQU $1d9d
DEF CP_PrintText       EQU $1041
DEF CP_GetPokemonName  EQU $3407
DEF CP_GetBaseData     EQU $3826
DEF CP_OpenSRAM        EQU $2f9d
DEF CP_CloseSRAM       EQU $2fad
DEF CP_sBoxCount       EQU $ad10
DEF CP_wContestMon     EQU $df12      ; WRAM バンク1（48バイト）
DEF CP_wTempEnemyMonSpecies EQU $d235
DEF CP_wNamedObjectIndex EQU $d296
DEF CP_wCurPartySpecies EQU $d0c8
DEF CP_wCurSpecies     EQU $cf54
DEF CP_wStringBuffer1  EQU $d05b
DEF CP_SAVE            EQU $dfd0      ; WRAM バンク2（$dfd0〜$dfff。$dfc0〜$dfcb は ほかの 機能）
DEF CP_BANK            EQU $76
DEF CP_ADDR            EQU $7600

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

; wContestMon を ボックスへ
ContestPC_Send:
	ld a, 1                           ; BANK(sBoxCount)
	call CP_OpenSRAM
	ld a, [CP_sBoxCount]
	cp 30
	call CP_CloseSRAM
	jr nc, .full
	ld a, [CP_wContestMon]
	ld [CP_wCurPartySpecies], a
	ld [CP_wCurSpecies], a
	call CP_GetBaseData
	; CheckPartyFullAfterContest.TryAddToBox（$13:$592c）と 同じ（ニックネームは きかない：戦いの 中で 名前の 画面を
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
	ld a, [CP_sBoxMon1Level]
	ld [CP_wCurPartyLevel], a
	call CP_CloseSRAM
	ld a, CP_TRYADD_BANK
	ld hl, CP_SetBoxMonCaughtData
	rst $08
	ld a, 1
	call CP_OpenSRAM
	ld hl, CP_sBoxMon1CaughtLocation
	ld a, [hl]
	and $80                           ; CAUGHT_GENDER_MASK
	or $13                            ; LANDMARK_NATIONAL_PARK
	ld [hl], a
	call CP_CloseSRAM
	ld a, [CP_wCurPartySpecies]
	ld [CP_wNamedObjectIndex], a
	call CP_GetPokemonName
	ld hl, ContestPC_SentText
	jp CP_PrintText
.full
	ld hl, ContestPC_FullText
	jp CP_PrintText

; a ＝ 2：wContestMon → よける所、1：よける所 → wContestMon（48バイト。WRAM バンクを 1バイトずつ 切りかえる）
ContestPC_Copy:
	ld hl, CP_wContestMon
	ld de, CP_SAVE
	ld c, 48
	cp 2
	jr z, .loop
	ld hl, CP_SAVE
	ld de, CP_wContestMon
.loop
	push af                           ; a ＝ 読む バンクの 反対（2 ＝ 1 から 読む）
	cp 2
	ld a, 1
	jr z, .rd
	ld a, 2
.rd
	ldh [$ff70], a
	ld b, [hl]
	inc hl
	pop af
	push af
	ldh [$ff70], a                    ; 書く バンク（2 か 1）
	ld a, b
	ld [de], a
	inc de
	pop af
	dec c
	jr nz, .loop
	ld a, 1
	ldh [$ff70], a
	ret

ContestPC_AskText: ; ○○を パソコンに おくりますか？
	db $01
	dw CP_wStringBuffer1
	db $00, "を", $4f, "パソコンに　おくりますか？", $57
ContestPC_SentText: ; ○○を パソコンに おくりました！
	db $01
	dw CP_wStringBuffer1
	db $00, "を", $4f, "パソコンに　おくりました！", $58
ContestPC_FullText: ; ボックスが いっぱいなので パソコンに おくれません！
	db $00, $1c, "ックスが　いっぱいなので", $4f, "パソコンに　おくれません！", $58
