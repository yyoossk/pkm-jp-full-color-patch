; むしとり大会で つかまえた ポケモンを、にがす かわりに パソコンへ おくれる（金銀 日本版。値は src/contestpc_silver.asm など）
; （クリスタル追加機能キットの src/contestpc_crystal.asm を 金銀に した もの）
;   元の ゲームは 大会の ポケモンは 1匹だけで、2匹めを つかまえると「ポケモンを いれかえる？」と きかれ、えらばなかった ほうは にがす。
;   ・「はい」（入れかえる）→ 前の ポケモンを「○○を パソコンに おくりますか？」→ はい なら パソコンへ。
;   ・「いいえ」（入れかえない）→ つかまえた ポケモンを「○○を パソコンに おくりますか？」→ はい なら パソコンへ。
;   ・いいえ なら 元の ゲームと 同じ（にがす）。ボックスが いっぱい（30匹）の ときは「ボックスが いっぱいなので…」で にがす。
; しくみ
;   ・BugContest_SetCaughtContestMon の「lb bc, 14, 12 / call PlaceYesNoBox / ret c」（7バイト）を farcall ContestPC_YesNo / ret c に
;     （farcall は キャリーを かえす）。
;   ・パソコンへ おくるのは 大会の おわりに 手持ちが いっぱいの ときと 同じ 処理（CheckPartyFullAfterContest .TryAddToBox：
;     wContestMon → wBufferMon（32バイト）、wPlayerName → wBufferMonOT、farcall InsertPokemonIntoBox、名前 → sBoxMonNicknames）を まねる。
;     金銀は つかまえた 場所・時間を おぼえないので、クリスタルの SetBoxMonCaughtData・つかまえた 場所 は ない。
;     ニックネームは きかない（戦いの 中で 名前の 画面を ひらくと もどった あと フィールドの 画面に なるため）。
;   ・入れかえない ときは、前の ポケモン（wContestMon・48バイト）を 使われていない WRAM（CP_SAVE）に よけて、
;     つかまえた ポケモンを .generatestats で wContestMon に 作り、おくって から 前の ポケモンを もどす
;     （金銀は WRAM の バンクを 切りかえないので CopyBytes で よい）。
INCLUDE "src/charmap_jp.inc"

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
	ld hl, CP_wContestMon             ; 前の ポケモンを よける
	ld de, CP_SAVE
	ld bc, 48
	call CP_CopyBytes
	ld a, CP_HOOK_BANK
	ld hl, CP_GENSTATS
	rst $08                           ; つかまえた ポケモンを wContestMon に
	call ContestPC_Send
	ld hl, CP_SAVE                    ; 前の ポケモンを もどす
	ld de, CP_wContestMon
	ld bc, 48
	call CP_CopyBytes
.ret_c
	scf
	ret

; a ＝ 種類。「○○を パソコンに おくりますか？」キャリー ＝ いいえ
ContestPC_Ask:
	ld [CP_wNamedObjectIndex], a
	call CP_GetPokemonName
	ld hl, ContestPC_AskText
	call CP_PrintText
	ld bc, $0e0c                      ; 「いれかえる？」と 同じ 場所（右下）
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
	call CP_CloseSRAM
	ld hl, ContestPC_SentText
	jp CP_PrintText
.full
	ld hl, ContestPC_FullText
	jp CP_PrintText

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
