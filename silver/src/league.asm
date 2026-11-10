; 16この バッジを ぜんぶ あつめた あとは、四天王・ワタル・ライバルの 手持ちを 強くする（金・銀・クリスタル 共通）
;
; ・ジョウトと カントーの バッジ 16こ（wJohtoBadges・wKantoBadges が どちらも $ff）が そろって いる とき、
;   イツキ・キョウ・シバ・カリン・ワタル と ライバル（オツキミやま・セキエイこうげん）の 手持ちを
;   6ぴき・レベル 70 前後・強い わざ・持ち物 つきの 手持ち（src/league_parties.inc）に かえる。
;   バッジが そろう 前は 元の まま。名前・お金の 計算・AI は 元の まま（お金は 最後の ポケモンの レベルで ふえる）。
;
; しくみ
;   ・ジムリーダー 再戦（src/rematch.asm の 2。RM_PARTY_FAR）と 同じ 所（ReadTrainerParty の ld a, [wOtherTrainerClass]）で 見る。
;     RM_LEAGUE を DEF して rematch.asm を INCLUDE すると、Rematch_ReadParty の 頭で League_ReadParty を 呼ぶ。
;     キャリー ＝ この ファイルの 手持ちを 読んだ（Rematch_TrainerType4 ＝ 元の TrainerType4 の 写し で 読む）。
;   ・表は「クラス, 番号（0 ＝ どの 番号でも）, 手持ち」。ライバルは 番号 1〜3（オツキミやま）・4〜6（セキエイこうげん）。
;
; このファイルの 前に 決める もの
;   LG_wJohtoBadges・LG_wKantoBadges・LG_wOtherTrainerID（wOtherTrainerClass ＋ 2）・LG_PARTY_ADDR（RM_SCRIPT_BANK の 中、約 560 バイト）
;   クラスの 番号（金・銀・クリスタル 共通）：WILL $0b・BRUNO $0d・KAREN $0e・KOGA $0f・CHAMPION $10・RIVAL2 $2a

INCLUDE "src/league_parties.inc"

DEF LG_WILL     EQU $0b
DEF LG_BRUNO    EQU $0d
DEF LG_KAREN    EQU $0e
DEF LG_KOGA     EQU $0f
DEF LG_CHAMPION EQU $10
DEF LG_RIVAL2   EQU $2a

SECTION "league parties", ROMX[LG_PARTY_ADDR], BANK[RM_SCRIPT_BANK]
League_ReadParty:
	ld a, [LG_wJohtoBadges]
	ld b, a
	ld a, [LG_wKantoBadges]
	and b
	inc a
	jr nz, .no                   ; 16こ そろって いない
	ld a, [RM_wOtherTrainerClass]
	ld c, a
	ld a, [LG_wOtherTrainerID]
	ld b, a
	ld hl, .table
.loop
	ld a, [hli]
	and a
	jr z, .no
	cp c
	jr nz, .next
	ld a, [hl]
	and a
	jr z, .found                 ; 0 ＝ どの 番号でも
	cp b
	jr z, .found
.next
	inc hl
	inc hl
	inc hl
	jr .loop
.found
	inc hl
	ld a, [hli]
	ld d, [hl]
	ld e, a
	call Rematch_TrainerType4
	scf
	ret
.no
	and a                        ; キャリーなし
	ret

.table
	db LG_WILL,     0
	dw LeagueParty_WILL
	db LG_KOGA,     0
	dw LeagueParty_KOGA
	db LG_BRUNO,    0
	dw LeagueParty_BRUNO
	db LG_KAREN,    0
	dw LeagueParty_KAREN
	db LG_CHAMPION, 0
	dw LeagueParty_LANCE
	db LG_RIVAL2,   1
	dw LeagueParty_RIVAL_1
	db LG_RIVAL2,   2
	dw LeagueParty_RIVAL_2
	db LG_RIVAL2,   3
	dw LeagueParty_RIVAL_3
	db LG_RIVAL2,   4
	dw LeagueParty_RIVAL_4
	db LG_RIVAL2,   5
	dw LeagueParty_RIVAL_5
	db LG_RIVAL2,   6
	dw LeagueParty_RIVAL_6
	db 0

MACRO lg_party ; 名前
LeagueParty_\1:
	LG_PARTY_\1
ENDM
	lg_party WILL
	lg_party KOGA
	lg_party BRUNO
	lg_party KAREN
	lg_party LANCE
	lg_party RIVAL_1
	lg_party RIVAL_2
	lg_party RIVAL_3
	lg_party RIVAL_4
	lg_party RIVAL_5
	lg_party RIVAL_6
