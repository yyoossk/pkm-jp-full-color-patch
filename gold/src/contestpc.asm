; むしとり大会で つかまえた ポケモンを、にがす かわりに パソコンへ おくれる（金 日本版。クリスタルの contestpc_crystal.asm から）
;   元の ゲームは 大会の ポケモンは 1匹だけで、2匹めを つかまえると「いれかえる？」と きかれ、えらばなかった ほうは にがす。
;   ・「はい」（入れかえる）→ 前の ポケモンを「○○を パソコンに おくりますか？」→ はい なら パソコンへ。
;   ・「いいえ」（入れかえない）→ つかまえた ポケモンを「○○を パソコンに おくりますか？」→ はい なら パソコンへ。
;   ・いいえ なら 元の ゲームと 同じ（にがす）。ボックスが いっぱい（30匹）の ときは「ボックスが いっぱいなので…」で にがす。
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
	call CP_CloseSRAM                 ; （金銀は つかまえた 場所の データが ない）
	ld a, [CP_wCurPartySpecies]
	ld [CP_wNamedObjectIndex], a
	call CP_GetPokemonName
	ld hl, ContestPC_SentText
	jp CP_PrintText
.full
	ld hl, ContestPC_FullText
	jp CP_PrintText

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
ContestPC_FullText: ; ボックスが いっぱいなので パソコンに おくれません！
	db $00, $1c, "ックスが　いっぱいなので", $4f, "パソコンに　おくれません！", $58
