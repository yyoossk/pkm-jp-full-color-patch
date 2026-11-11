; セキエイこうげん（ポケモンリーグ）の ショップで マスターボールを 売る（金 日本版）
; ウツギ博士から マスターボールを もらった あと（EVENT_GOT_MASTER_BALL_FROM_ELM）だけ 並ぶ。値段は 10000円。
;
; しくみ
;   ・ItemAttributes の MASTER_BALL の 値段（0円）を 10000円 に。
;   ・GetMart（バンク$05）を 書きなおして、表から 店の 場所（de）を 読んだ あと MasterBallMart（下の バンク）を farcall。
;     MasterBallMart：セキエイの 店（MartIndigoPlateau）で 博士から もらって いれば、マスターボールを 足した 表
;     （このバンク）に かえる（b = 表の バンク。LoadMartPointer が b の バンクから 読む）。
;     元の GetMart の「店の 番号が NUM_MARTS 以上なら DefaultMart」は 使われていないので、0 番の 店に した（場所が たりないため）。
;
; 銀・クリスタルに 入れるとき：下の DEF を その ROM の 値に する
;   MB_GETMART      GetMart の 場所（バンク MB_GETMART_BANK）。元の 中身と 同じ 並び（22バイト）か 確かめる
;   MB_MARTS        Marts の 表、MB_NUM_MARTS 店の 数（GetMart の cp の 値）
;   MB_MART_INDIGO  MartIndigoPlateau（元の 表：7こ ULTRA_BALL・MAX_REPEL・HYPER_POTION・MAX_POTION・FULL_RESTORE・REVIVE・FULL_HEAL）
;   MB_ITEMATTR     ItemAttributes（MASTER_BALL は 1番め。値段は 先頭の 2バイト）
;   MB_EVENT_BYTE・MB_EVENT_BIT  EVENT_GOT_MASTER_BALL_FROM_ELM の wEventFlags の バイトと ビット
;                                （金は イベント $007c → wEventFlags（$d7aa）+ 15 の ビット 4。
;                                  ProfElmScript の「checkevent ○○ / iftrue / checkflag ENGINE_RISINGBADGE」の ○○）
;   MB_BANK・MB_ADDR  処理と 表を 置く 空き（約 40バイト）

INCLUDE "includes.asm"

IF !DEF(MB_GETMART)
DEF MB_GETMART      EQU $5d9e
DEF MB_GETMART_BANK EQU $05
DEF MB_MARTS        EQU $65ea
DEF MB_NUM_MARTS    EQU $22
DEF MB_MART_INDIGO  EQU $6746
DEF MB_ITEMATTR     EQU $6b93
DEF MB_ITEMATTR_BANK EQU $01
DEF MB_EVENT_BYTE   EQU $d7aa + $7c / 8
DEF MB_EVENT_BIT    EQU $7c % 8
DEF MB_BANK         EQU $43
DEF MB_ADDR         EQU $7c00
DEF MB_MART_CELADON_3F EQU $670f   ; MartCeladon3F（わざマシンの 店。src/tmshop.asm）
ENDC
DEF MB_PRICE EQU 10000

SECTION "masterball price", ROMX[MB_ITEMATTR], BANK[MB_ITEMATTR_BANK]
	dw MB_PRICE

SECTION "masterball getmart", ROMX[MB_GETMART], BANK[MB_GETMART_BANK]
MasterBallGetMart: ; e = 店の 番号 → b = 表の バンク、de = 表
	ld a, e
	cp MB_NUM_MARTS
	jr c, .ok
	ld e, 0
.ok
	ld hl, MB_MARTS
	add hl, de
	add hl, de
	ld e, [hl]
	inc hl
	ld d, [hl]
	ld a, BANK(MasterBallMart)
	ld hl, MasterBallMart
	rst $08
	ret

SECTION "masterball mart", ROMX[MB_ADDR], BANK[MB_BANK]
MasterBallMart:
	ld b, MB_GETMART_BANK
IF DEF(MB_MART_CELADON_3F)
	; タマムシデパート 3F：メニューで えらんだ わざマシンの 表に（src/tmshop.asm の TmShopMart）
	ld a, e
	cp LOW(MB_MART_CELADON_3F)
	jr nz, .not_tm
	ld a, d
	cp HIGH(MB_MART_CELADON_3F)
	jr nz, .not_tm
	ld a, BANK(TmShopMart)
	ld hl, TmShopMart
	rst $08
	ret
.not_tm
ENDC
IF DEF(MB_ED251)
	ld a, e
	cp LOW(MB_MART_GOLDENROD_4F)
	jr nz, .not4f
	ld a, d
	cp HIGH(MB_MART_GOLDENROD_4F)
	jr nz, .not4f
	ld b, BANK(EdMartGoldenrod4F)
	ld de, EdMartGoldenrod4F
	ret
.not4f
ENDC
	ld a, e
	cp LOW(MB_MART_INDIGO)
	ret nz
	ld a, d
	cp HIGH(MB_MART_INDIGO)
	ret nz
	ld a, [MB_EVENT_BYTE]
	bit MB_EVENT_BIT, a
	ret z
	ld b, BANK(MasterBallMartIndigo)
	ld de, MasterBallMartIndigo
	ret

IF DEF(MB_ED251)
DEF MB_MART_GOLDENROD_4F EQU $6675   ; 元の 表「05 1b 1c 1d 1f 1a ff」
EdMartGoldenrod4F:
	db 12
	db PROTEIN, IRON, CARBOS, CALCIUM, HP_UP
	db FIRE_STONE, WATER_STONE, THUNDERSTONE, LEAF_STONE, MOON_STONE, SUN_STONE, KINGS_ROCK
	db -1
ENDC

MasterBallMartIndigo:
	db 8
	db MASTER_BALL
	db ULTRA_BALL, MAX_REPEL, HYPER_POTION, MAX_POTION, FULL_RESTORE, REVIVE, FULL_HEAL
	db -1
