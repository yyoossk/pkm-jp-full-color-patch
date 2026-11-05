; ガンテツが ぼんぐりの ボールを まとめて 作る（金 日本版）
;
; ・ガンテツに ぼんぐりを わたすと、えらんだ 色の ぼんぐりを リュックに ある だけ ぜんぶ わたす。
; ・次の日に、わたした 数だけ ボールを くれる（たとえば あかぼんぐり 5こ → レベルボール 5こ）。
; ・リュックが いっぱいで 受けとれない ときは 元と 同じく あとで もう一度。
;
; しくみ
;   ・SelectApricornForKurt（special）を 新しい バンクの Kurt_Select への farcall に：
;     元と 同じく ぼんぐりを えらばせて、リュックの その ぼんぐりの 数を wKurtCount に 入れ、ぜんぶ へらす。
;   ・Script_giveitem の「ld [wItemQuantityChange], a」を Kurt_GiveQty の call に：
;     ガンテツの 家の 中で wKurtCount が 0 で なければ、その 数を わたす。
;     （ガンテツの 家で もらえる どうぐは ガンテツの ボールだけ。さいしょの ルアーボールは wKurtCount が 0 なので 1こ）
;   ・wKurtCount は レポートに 書かれる 所の 使われていない バイト（wEventFlags の すぐ前の 空き）。
;     まえの レポートで ぼんぐりを わたした まま だと 0 なので 1こ（元と 同じ）。
;
; 銀・クリスタルに 入れるとき：下の DEF を その ROM の 値に する
;   KB_SELECT        SelectApricornForKurt（8バイト 以上。中身は ぜんぶ Kurt_Select が する）
;   KB_Kurt_SelectApricorn・KB_TossItem・KB_wScriptVar も その ROM の 値に
;   KB_GIVEITEM      Script_giveitem の 2つめの「call GetScriptByte」の つぎの「ld [wItemQuantityChange], a」
;   KB_GIVE_FREE     KB_GIVEITEM と 同じ バンクの 空き（約 25バイト）
;   KB_MAP_GROUP・KB_MAP_NUMBER  KURTS_HOUSE（クリスタルは 同じ 作りか 確かめる）
;   wKurtCount       レポートに 書かれる 使われていない 1バイト

INCLUDE "includes.asm"

IF !DEF(KB_SELECT)
DEF KB_SELECT        EQU $45d1        ; バンク$03 SelectApricornForKurt（28バイト）
DEF KB_SELECT_BANK   EQU $03
DEF KB_GIVEITEM      EQU $763f + 16   ; バンク$25 Script_giveitem の ld [wItemQuantityChange], a
DEF KB_GIVE_BANK     EQU $25
DEF KB_GIVE_FREE     EQU $7fc0        ; バンク$25 の 空き
DEF KB_MAP_GROUP     EQU 8            ; KURTS_HOUSE
DEF KB_MAP_NUMBER    EQU 4
DEF KB_Kurt_SelectApricorn EQU $4ba1
DEF KB_Kurt_SelectApricorn_BANK EQU $09
DEF KB_TossItem      EQU $3025
DEF KB_wScriptVar    EQU $d165
DEF KB_wCurItem      EQU $cffc
DEF KB_wItemQuantityChange EQU $d003
DEF KB_wNumItems     EQU $d5aa
DEF KB_wMapGroup     EQU $d9c6
DEF KB_wMapNumber    EQU $d9c7
DEF wKurtCount       EQU $d7a0        ; wEventFlags（$d7aa）の 前の 空き（レポートに 書かれる）
DEF KB_BANK          EQU $45
DEF KB_ADDR          EQU $6000
ENDC

SECTION "kurtbulk select hook", ROMX[KB_SELECT], BANK[KB_SELECT_BANK]
	ld a, BANK(Kurt_Select)
	ld hl, Kurt_Select
	rst $08
	ret

SECTION "kurtbulk give hook", ROMX[KB_GIVEITEM], BANK[KB_GIVE_BANK]
	call Kurt_GiveQty

SECTION "kurtbulk give", ROMX[KB_GIVE_FREE], BANK[KB_GIVE_BANK]
Kurt_GiveQty:
	ld [KB_wItemQuantityChange], a
	ld a, [KB_wMapGroup]
	cp KB_MAP_GROUP
	ret nz
	ld a, [KB_wMapNumber]
	cp KB_MAP_NUMBER
	ret nz
	ld a, [wKurtCount]
	and a
	ret z
	ld [KB_wItemQuantityChange], a
	ret

SECTION "kurtbulk", ROMX[KB_ADDR], BANK[KB_BANK]
Kurt_Select:
	ld a, KB_Kurt_SelectApricorn_BANK
	ld hl, KB_Kurt_SelectApricorn
	rst $08
	ld a, c
	ld [KB_wScriptVar], a
	and a
	ret z
	ld [KB_wCurItem], a
	ld b, a
	ld hl, KB_wNumItems + 1
.loop
	ld a, [hli]
	cp -1
	jr z, .one
	cp b
	jr z, .found
	inc hl
	jr .loop
.found
	ld a, [hl]
	and a
	jr nz, .set
.one
	ld a, 1
.set
	ld [KB_wItemQuantityChange], a
	ld [wKurtCount], a
	ld hl, KB_wNumItems
	jp KB_TossItem
