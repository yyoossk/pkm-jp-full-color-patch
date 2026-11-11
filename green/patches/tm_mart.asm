; 殿堂入りしたあとは、タマムシデパート 2かいの わざマシンの店員が、一回しか 手に入らない わざマシンも 売る。
;   元から 売って いる 9本（01・02・05・07・09・17・32・33・37）に、ジムリーダーに もらう・道に 落ちて いる などで
;   一回しか 手に入らない 38本を 足して、わざマシンの 番号の 順に ならべる（47本）。
;   ゲームコーナーの 景品（15・23・50。緑は 14:7c26）は、コインで なんども 手に入るので 入れない。
;   値段は 元の ゲームの わざマシンの 値段の まま。殿堂入りしたか：殿堂入りの 記録の 数（wNumHoFTeams）が 0 でない。
;
; 店の リストは wItemList（$CF62。14こ まで）に 写してから 出すので、47本は 入らない。
; 「かう」の リストを 出す 所（01:6B93 の ld hl, wItemList）を 呼び出しに かえ、この 店員で 殿堂入りの あとなら、
; てきの パーティの データの 所（wEnemyPartyCount〜。たたかいの 間だけ 使う）に 長い リストを 作って、そこを 指す。

DEF wTMMartItemList      EQU $cf62 ; wItemList
DEF wTMMartListPointer   EQU $d0ed ; wItemListPointer（LoadItemList が 上・下 の 順に 入れる）
DEF wTMMartNumHoFTeams   EQU $d521 ; wNumHoFTeams
DEF TM_MART_BUF          EQU $d81b ; wEnemyPartyCount（1 + 47 + 1 = 49バイト）
DEF TM_MART_CLERK_LIST   EQU $0e74 ; わざマシンの 店員の リスト（$0E73 の TX_SCRIPT_MART の 次 = 数の 所）

; ---------------------------------------------------------------- 呼び出し
SECTION "わざマシンの店 呼ぶ所", ROMX[$6b93], BANK[$01]
	call TMMartTrampoline  ; hl = 出す リスト

; ホームの あき（$3F06 の ret の あと。9バイト）
SECTION "わざマシンの店 入り口", ROM0[$3f07]
TMMartTrampoline:
	ld b, $37
	ld hl, TMMartList
	jp $3500               ; Bankswitch（hl は こわさない）
	assert @ <= $3f10

; ---------------------------------------------------------------- 本体
SECTION "わざマシンの店", ROMX[$7f00], BANK[$37]
; 出力：hl = 「かう」の リスト（数・品物…・$FF）
TMMartList:
	ld hl, wTMMartListPointer
	ld a, [hli]
	cp HIGH(TM_MART_CLERK_LIST)
	jr nz, .normal
	ld a, [hl]
	cp LOW(TM_MART_CLERK_LIST)
	jr nz, .normal
	ld a, [wTMMartNumHoFTeams]
	and a
	jr z, .normal
	ld hl, TMMartAllTMs
	ld de, TM_MART_BUF
.copy
	ld a, [hli]
	ld [de], a
	inc de
	inc a
	jr nz, .copy
	ld hl, TM_MART_BUF
	ret
.normal
	ld hl, wTMMartItemList
	ret

; わざマシン n = $C8 + n
TMMartAllTMs:
	db .end - .items - 1
.items
FOR N, 1, 50
	IF N != 15 && N != 23
		db $c8 + N
	ENDC
ENDR
	db -1
.end
	assert .end - .items - 1 == 47
	assert @ <= $8000
