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
;   ・いまの ボックスが いっぱい（30匹）なら、次の あいて いる ボックス（いまの 次から じゅんに。9 の 次は 1）に おくる
;     （「○○を ボックス２に おくりました！」。大会の 間は レポートを 書けないので ボックスは 切りかえない。大会の あと
;     フィールドで いつもの 自動切りかえ（autobox）が 動く）。戦いの 中なので SaveBox・LoadBox（wBoxPartialData ＝ 戦いの
;     データと 同じ 所を 使う）は 使わず、SRAM から SRAM へ 1バイトずつ 写す：いまの ボックス（sBox）→ その ボックスの 場所、
;     おくる ボックス → sBox、sBox に 入れる、sBox → おくる ボックスの 場所、いまの ボックスの 場所 → sBox（1つ ＝ $54a バイト）。
;     ぜんぶ いっぱいなら 今までどおり「ボックスが いっぱいなので…」。
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

; wContestMon を ボックスへ（いまの ボックスが いっぱいなら 次の あいて いる ボックスへ）
ContestPC_Send:
	ld a, 1                           ; BANK(sBoxCount)
	call CP_OpenSRAM
	ld a, [CP_sBoxCount]
	cp 30
	call CP_CloseSRAM
	jr c, .here
	call ContestPC_FindBox            ; a ＝ おくる ボックス
	jr c, .full
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
	jp CP_CloseSRAM

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
;   戦いの 中なので SaveBox・LoadBox（wBoxPartialData ＝ 戦いの データと 同じ 所）は 使わない
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

; ボックス 1〜9 の 場所（GetBoxCount.BoxBankAddresses と 同じ。SRAM の バンク, 場所）
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
