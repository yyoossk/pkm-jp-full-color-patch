; 殿堂入りしたあとは、タマムシデパート 2かいの わざマシンの店員が、一回しか手に入らない わざマシンも売る
;   元から売っている 9本（01・02・05・07・09・17・32・33・37）に、ジムリーダーにもらう・道に落ちているなどで
;   一回しか手に入らない 38本を足して、わざマシンの番号の順にならべる（47本）。
;   ゲームコーナーの景品（15・23・50。青は 14:7C02、151匹そろう版は 14:7BF3）は、コインでなんどでも手に入るので入れない。
;   値段は元のゲームの わざマシンの値段のまま。
;   殿堂入りしたか：殿堂入りの記録の数（wNumHoFTeams $D521）が 0 でない。
;
; 店のリストは LoadItemList（$29E4）が wItemList（$CF62。14こまで）に写してから出すので、47本は入らない。
; 「かう」のリストを出す所（バンク1 $6C52：ld hl, wItemList / wListPointer に入れる。11バイト）を、
; バンクを切りかえて TMMartList を呼ぶ形にかえる。TMMartList が wListPointer に入れる。
; この店員で殿堂入りのあとなら、てきのパーティの所（wEnemyPartyCount $D81B〜。たたかいの間だけ使う）に
; 長いリストを作って、そこを指す。
; （ピカチュウのキット「わざマシンの店」から。ピカチュウはホームの rst のあきから呼んでいたが、
;   青はここに 11バイトあるので、そのまま Bankswitch で呼ぶ）

IF HAS_TM_MART

DEF wItemList        EQU $CF62
DEF wListPointer     EQU $CF72
DEF wItemListPointer EQU $D0ED ; LoadItemList が 上・下 の順に入れる（リストの「数」の所）
DEF wNumHoFTeams     EQU $D521
DEF wEnemyPartyCount EQU $D81B ; 1 + 47 + 1 = 49バイト
DEF TMMartClerkList  EQU $2417 ; タマムシデパート 2かいの わざマシンの店員のリスト（$2416 の $FE の次）
DEF TM01 EQU $C9

SECTION "わざマシンの店 かうリスト", ROMX[$6C52], BANK[$01]
	ld b, BANK(TMMartList)
	ld hl, TMMartList
	call Bankswitch
	ds 3, 0 ; nop（元の 11バイトの残り）
	assert @ == $6C5D

FreeBankA
TMMartList:
	ld hl, wItemListPointer
	ld a, [hli]
	cp HIGH(TMMartClerkList)
	jr nz, .normal
	ld a, [hl]
	cp LOW(TMMartClerkList)
	jr nz, .normal
	ld a, [wNumHoFTeams]
	and a
	jr z, .normal
	ld hl, TMMartAllTMs
	ld de, wEnemyPartyCount
.copy
	ld a, [hli]
	ld [de], a
	inc de
	inc a
	jr nz, .copy
	ld hl, wEnemyPartyCount
	jr .set
.normal
	ld hl, wItemList
.set
	ld a, l
	ld [wListPointer], a
	ld a, h
	ld [wListPointer + 1], a
	ret

TMMartAllTMs:
	db .end - .items - 1
.items
FOR N, 1, 50
	IF N != 15 && N != 23
		db TM01 + N - 1
	ENDC
ENDR
	db -1
.end
	assert .end - .items - 1 == 47

ENDC
