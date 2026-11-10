; カントーのジムリーダー 再戦（金・銀・クリスタル 日本版 共通の本体）
;
; ・カントーのバッジを 8つ ぜんぶ持っているとき、ジムリーダーに話しかけると
;   「もう いちど しょうぶ する？」と聞かれ、「はい」なら 強い手持ち（Lv66〜74）で戦える。何度でも戦える。
; ・「いいえ」や、まだ 8つ そろっていないときは 元のゲームと同じ（勝ったあとのセリフ・わざマシンなど）。
; ・初めて戦うときは 元のゲームと まったく同じ。
;
; しくみ
;   1. ジムリーダーの話しかけの「checkflag バッジ / iftrue .FightDone」（6バイト）を
;      「farsjump 新しいスクリプト」に書きかえる。
;   2. ジムリーダー 8人の トレーナーのデータ（グループ）を空き場所に移し、
;      1回目（元のデータそのまま）のあとに 2回目（再戦用）を足す → loadtrainer 人, 2 で戦える。
;      （トレーナーのバンクに空きがない 日本版 金銀は RM_PARTY_FAR：再戦用の手持ちを新しいバンクから読む。下の 2 を見る）
;   3. 戦闘で負けたときのセリフ（winlosstext）は ふつうは マップのスクリプトのバンクから読むので、
;      スクリプトが 新しいバンクで動いているときは そのバンクから読むようにする（PrintWinLossText）。
;
; このファイルの前に INCLUDE するもの
;   rematch_<版>.inc（tools/rematch_find.py で作る）・rematch_parties.inc・charmap_jp.inc
;   DEF BASEROM（元の ROM のファイル名）
;   DEF RM_SCRIPT_BANK / RM_SCRIPT_ADDR（新しいスクリプトを置く空き場所）
;   DEF RM_BANK0_FREE（ROM0 の空き 10バイト）

; ---- スクリプトの命令（日本版。金銀クリスタルで同じ番号のものだけ使う）
DEF SC_SCALL        EQU $00
DEF SC_FARSJUMP     EQU $04
DEF SC_IFFALSE      EQU $08
DEF SC_CHECKFLAG    EQU $34
DEF SC_CHECKEVENT   EQU $31
DEF SC_OPENTEXT     EQU $47
DEF SC_CLOSETEXT    EQU $49
DEF SC_WRITETEXT    EQU $4c
DEF SC_YESORNO      EQU $4e
IF !DEF(SC_WAITBUTTON)
DEF SC_WAITBUTTON   EQU $53   ; クリスタル日本版（英語版 $54）
DEF SC_LOADTRAINER  EQU $5d   ; 〃（英語版 $5e）
DEF SC_STARTBATTLE  EQU $5e
DEF SC_RELOADMAPAFTERBATTLE EQU $5f
DEF SC_WINLOSSTEXT  EQU $63
DEF SC_FACEPLAYER   EQU $6a
DEF SC_END          EQU $90
ENDC

DEF ENGINE_BOULDERBADGE EQU RM_KANTO_BADGE0   ; カントーのバッジ 8つ（rematch_find.py が探した番号）

; ---- 1. 話しかけのスクリプトを書きかえる
MACRO rm_patch ; 名前
SECTION "rematch patch \1", ROMX[RM_\1_PATCH], BANK[RM_\1_MAPBANK]
	db SC_FARSJUMP, BANK(Rematch_\1)
	dw Rematch_\1
ENDM
	rm_patch BROCK
	rm_patch MISTY
	rm_patch SURGE
	rm_patch ERIKA
	rm_patch JANINE
	rm_patch SABRINA
	rm_patch BLAINE
	rm_patch BLUE

; ---- 2. トレーナーのデータ
IF DEF(RM_PARTY_FAR)
; トレーナーのバンクに空きがない版（日本版 金・銀）：
;   再戦用の手持ちを 新しいバンク（RM_SCRIPT_BANK）に置き、ReadTrainerParty の頭で
;   「新しいスクリプト（wScriptBank = RM_SCRIPT_BANK）から呼ばれた ジムリーダー」なら そこから読む。
;   loadtrainer は 人, 1（名前・お金・個体値は 1回目と同じ所から読まれる）。
;   手持ちを読む処理は 元の TrainerType4（どうぐ・わざつき）を そのまま写して使う
;   （ホームの処理と WRAM しか使わず、とび先は相対なので どのバンクでも動く）。
;   このファイルの前に決めるもの（rematch_find.py が探す）：
;     RM_ReadTrainerParty_Class（ld a, [wOtherTrainerClass] の所）・RM_ReadTrainerParty_Done（.done）
;     RM_TrainerType4_OFS / RM_TrainerType4_LEN・RM_wOtherTrainerClass
;   と、トレーナーのバンクの空き RM_PARTY_HOOK_FREE（23バイト）、新しいバンクの中の置き場所 RM_PARTY_FAR_ADDR（約520バイト）
DEF RM_TRAINER_ID EQU 1
SECTION "rematch party hook", ROMX[RM_ReadTrainerParty_Class], BANK[RM_PARTY_BANK]
	call Rematch_CheckParty      ; ld a, [wOtherTrainerClass] の代わり

SECTION "rematch party check", ROMX[RM_PARTY_HOOK_FREE], BANK[RM_PARTY_BANK]
Rematch_CheckParty:
IF !DEF(RM_LEAGUE)
	ld a, [RM_wScriptBank]
	cp RM_SCRIPT_BANK
	jr nz, .no
ENDC                             ; RM_LEAGUE：四天王なども 見るので いつも 呼ぶ（新しいスクリプトかは 呼んだ先で 見る）
	ld a, BANK(Rematch_ReadParty)
	ld hl, Rematch_ReadParty
	rst $08                      ; キャリー = 再戦用の手持ちを読んだ
	jr nc, .no
	pop hl                       ; ReadTrainerParty には もどらない
	jp RM_ReadTrainerParty_Done  ; .done（ComputeTrainerReward）
.no
	ld a, [RM_wOtherTrainerClass]
	ret

SECTION "rematch party far", ROMX[RM_PARTY_FAR_ADDR], BANK[RM_SCRIPT_BANK]
Rematch_ReadParty:
IF DEF(RM_LEAGUE)
	call League_ReadParty        ; 16この バッジの あとの 四天王・ワタル・ライバル（src/league.asm）
	ret c
	ld a, [RM_wScriptBank]
	cp RM_SCRIPT_BANK
	jr z, .script
	and a                        ; キャリーなし
	ret
.script
ENDC
	ld a, [RM_wOtherTrainerClass]
	ld c, a
	ld hl, .table
.loop
	ld a, [hli]
	and a
	ret z                        ; ジムリーダーではない（キャリーなし）
	cp c
	jr z, .found
	inc hl
	inc hl
	jr .loop
.found
	ld a, [hli]
	ld d, [hl]
	ld e, a
	call Rematch_TrainerType4
	scf
	ret
.table
	db RM_BROCK_CLASS
	dw RematchParty_BROCK
	db RM_MISTY_CLASS
	dw RematchParty_MISTY
	db RM_SURGE_CLASS
	dw RematchParty_SURGE
	db RM_ERIKA_CLASS
	dw RematchParty_ERIKA
	db RM_JANINE_CLASS
	dw RematchParty_JANINE
	db RM_SABRINA_CLASS
	dw RematchParty_SABRINA
	db RM_BLAINE_CLASS
	dw RematchParty_BLAINE
	db RM_BLUE_CLASS
	dw RematchParty_BLUE
IF DEF(RM_JOHTO)
	db RMJ_FALKNER_CLASS
	dw RematchParty_FALKNER
	db RMJ_BUGSY_CLASS
	dw RematchParty_BUGSY
	db RMJ_WHITNEY_CLASS
	dw RematchParty_WHITNEY
	db RMJ_MORTY_CLASS
	dw RematchParty_MORTY
	db RMJ_CHUCK_CLASS
	dw RematchParty_CHUCK
	db RMJ_JASMINE_CLASS
	dw RematchParty_JASMINE
	db RMJ_PRYCE_CLASS
	dw RematchParty_PRYCE
	db RMJ_CLAIR_CLASS
	dw RematchParty_CLAIR
ENDC
	db 0

Rematch_TrainerType4:            ; 元の TrainerType4 そのまま（de = 手持ちのデータ）
	INCBIN BASEROM, RM_TrainerType4_OFS, RM_TrainerType4_LEN

MACRO rm_farparty ; 名前
RematchParty_\1:
	RM_PARTY2_\1
ENDM
	rm_farparty BROCK
	rm_farparty MISTY
	rm_farparty SURGE
	rm_farparty ERIKA
	rm_farparty JANINE
	rm_farparty SABRINA
	rm_farparty BLAINE
	rm_farparty BLUE

IF DEF(RM_JOHTO)
SECTION "rematch johto parties", ROMX[RMJ_PARTY_ADDR], BANK[RM_SCRIPT_BANK]
	rm_farparty FALKNER
	rm_farparty BUGSY
	rm_farparty WHITNEY
	rm_farparty MORTY
	rm_farparty CHUCK
	rm_farparty JASMINE
	rm_farparty PRYCE
	rm_farparty CLAIR
ENDC

ELSE
DEF RM_TRAINER_ID EQU 2
MACRO rm_grouptr ; 名前
SECTION "rematch group ptr \1", ROMX[RM_TrainerGroups + (RM_\1_CLASS - 1) * 2], BANK[RM_PARTY_BANK]
	dw RematchGroup_\1
ENDM
	rm_grouptr BROCK
	rm_grouptr MISTY
	rm_grouptr SURGE
	rm_grouptr ERIKA
	rm_grouptr JANINE
	rm_grouptr SABRINA
	rm_grouptr BLAINE
	rm_grouptr BLUE

MACRO rm_group ; 名前
RematchGroup_\1:
	INCBIN BASEROM, RM_\1_PARTY1_OFS, RM_\1_PARTY1_LEN    ; 1回目（元のまま）
	INCBIN BASEROM, RM_\1_PARTY1_OFS, RM_\1_NAME_LEN      ; 2回目：名前（同じ）
	db 3                                                  ; TRAINERTYPE_ITEM_MOVES
	RM_PARTY2_\1
ENDM
SECTION "rematch groups", ROMX[RM_PARTY_FREE], BANK[RM_PARTY_BANK]
	rm_group BROCK
	rm_group MISTY
	rm_group SURGE
	rm_group ERIKA
	rm_group JANINE
	rm_group SABRINA
	rm_group BLAINE
	rm_group BLUE

ENDC

; ---- 3. 負けたときのセリフのバンク
SECTION "rematch winloss call", ROM0[RM_PrintWinLoss_Call]
	call Rematch_WinLossTextBank

SECTION "rematch winloss bank", ROM0[RM_BANK0_FREE]
Rematch_WinLossTextBank:
	ld a, [RM_wScriptBank]
	cp RM_SCRIPT_BANK
	ret z
	jp RM_GetMapScriptsBank

; ---- 新しいスクリプト
MACRO rm_script ; 名前, 先に faceplayer・opentext がいるか(0/1)
Rematch_\1:
	db SC_CHECKFLAG
	dw ENGINE_BOULDERBADGE + (\1_BADGE)
	db SC_IFFALSE
	dw .first\@
	db SC_SCALL
	dw Rematch_HasAllKantoBadges
	db SC_IFFALSE
	dw .done\@
IF RM_\1_OPEN == 0
	db SC_FACEPLAYER
	db SC_OPENTEXT
ENDC
	db SC_WRITETEXT
	dw RematchText_\1_Ask
	db SC_YESORNO
	db SC_IFFALSE
	dw .no\@
	db SC_CLOSETEXT
	db SC_WINLOSSTEXT
	dw RematchText_\1_Win, 0
	db SC_LOADTRAINER, RM_\1_CLASS, RM_TRAINER_ID
	db SC_STARTBATTLE
	db SC_RELOADMAPAFTERBATTLE
	db SC_OPENTEXT
	db SC_WRITETEXT
	dw RematchText_\1_After
	db SC_WAITBUTTON
	db SC_CLOSETEXT
	db SC_END
.first\@  ; まだ勝っていない：元のゲームの 初めての戦い
	db SC_FARSJUMP, RM_\1_MAPBANK
	dw RM_\1_AFTER
.done\@   ; バッジが そろっていない：元のゲームの 勝ったあと
	db SC_FARSJUMP, RM_\1_MAPBANK
	dw RM_\1_DONE
.no\@     ; 「いいえ」：元のゲームの 勝ったあと（もう 話しはじめているので、faceplayer・opentext はとばす）
	db SC_FARSJUMP, RM_\1_MAPBANK
IF RM_\1_OPEN == 0
	dw RM_\1_DONE2
ELSE
	dw RM_\1_DONE
ENDC
ENDM

DEF BROCK_BADGE   EQU 0
DEF MISTY_BADGE   EQU 1
DEF SURGE_BADGE   EQU 2
DEF ERIKA_BADGE   EQU 3
DEF JANINE_BADGE  EQU 4
DEF SABRINA_BADGE EQU 5
DEF BLAINE_BADGE  EQU 6
DEF BLUE_BADGE    EQU 7

SECTION "rematch scripts", ROMX[RM_SCRIPT_ADDR], BANK[RM_SCRIPT_BANK]
	rm_script BROCK
	rm_script MISTY
	rm_script SURGE
	rm_script ERIKA
	rm_script JANINE
	rm_script SABRINA
	rm_script BLAINE
	rm_script BLUE

; カントーのバッジが 8つ そろっていれば スクリプトの答え = TRUE
Rematch_HasAllKantoBadges:
FOR I, 8
	db SC_CHECKFLAG
	dw ENGINE_BOULDERBADGE + I
	db SC_IFFALSE
	dw .no
ENDR
.no
	db SC_END

; ---- セリフ
RematchText_BROCK_Ask:
	db 0, "タケシ『おう　また　きたな！<LINE>カントーの　バッジを<CONT>ぜんぶ　あつめた　きみと<CONT>ほんきで　たたかいたい！<PARA>もういちど<LINE>しょうぶ　するか？<DONE>"
RematchText_BROCK_Win:
	db 0, "タケシ『まいった！<LINE>きみの　つよさは<CONT>ほんものだ！<DONE>"
RematchText_BROCK_After:
	db 0, "タケシ『いわの　ように<LINE>かたい　いしで<CONT>また　きたえなおすよ！<DONE>"

RematchText_MISTY_Ask:
	db 0, "カスミ『あら　また　きたの？<LINE>ちょうど　いいわ！<PARA>きたえなおした<LINE>みずポケモンで<CONT>あいて　してあげる！<PARA>しょうぶ　する？<DONE>"
RematchText_MISTY_Win:
	db 0, "カスミ『もう！<LINE>また　まけちゃった！<DONE>"
RematchText_MISTY_After:
	db 0, "カスミ『つぎは　ぜったい<LINE>まけないんだから！<DONE>"

RematchText_SURGE_Ask:
	db 0, "マチス『ヘイ！　ユー！<LINE>また　ビリビリ　しびれる<CONT>バトルが　したいのか？<DONE>"
RematchText_SURGE_Win:
	db 0, "マチス『オー！<LINE>グレイト！<CONT>ユー　つよいね！<DONE>"
RematchText_SURGE_After:
	db 0, "マチス『また　いつでも<LINE>カモーン！<DONE>"

RematchText_ERIKA_Ask:
	db 0, "エリカ『まあ　ようこそ<LINE>いらっしゃいました<PARA>いまの　わたくしの<LINE>くさポケモンたちと<CONT>しょうぶ　なさいますか？<DONE>"
RematchText_ERIKA_Win:
	db 0, "エリカ『まあ⋯<LINE>おみごとですわ<DONE>"
RematchText_ERIKA_After:
	db 0, "エリカ『また　いつでも<LINE>おこし　くださいね<DONE>"

RematchText_JANINE_Ask:
	db 0, "アンズ『また　きたのね！<LINE>しゅぎょうの　せいかを<CONT>みせて　あげる！<PARA>しょうぶ　する？<DONE>"
RematchText_JANINE_Win:
	db 0, "アンズ『うう⋯<LINE>まだまだ　しゅぎょうが<CONT>たりないわ<DONE>"
RematchText_JANINE_After:
	db 0, "アンズ『つぎは　まけない<LINE>からね！<DONE>"

RematchText_SABRINA_Ask:
	db 0, "ナツメ『あなたが　また<LINE>くることは　わかっていた<PARA>わたしの　みた　みらいを<LINE>かえられるか⋯<CONT>ためして　みる？<DONE>"
RematchText_SABRINA_Win:
	db 0, "ナツメ『この　みらいは<LINE>みえなかった⋯<DONE>"
RematchText_SABRINA_After:
	db 0, "ナツメ『あなたの　ちからは<LINE>わたしの　よちを<CONT>こえているわね<DONE>"

RematchText_BLAINE_Ask:
	db 0, "カツラ『うおーっす！<LINE>また　きたな！<PARA>パワーアップした<LINE>ほのおで　あいてしよう！<CONT>しょうぶ　するか？<DONE>"
RematchText_BLAINE_Win:
	db 0, "カツラ『あちちっ！<LINE>やけどしたのは<CONT>わしの　ほうじゃ！<DONE>"
RematchText_BLAINE_After:
	db 0, "カツラ『また　いつでも<LINE>あつい　しょうぶを<CONT>しようぞ！<DONE>"

RematchText_BLUE_Ask:
	db 0, "グリーン『よう！<LINE>また　きたのか<PARA>おれの　ほんきの<LINE>パーティと<CONT>しょうぶ　するか？<DONE>"
RematchText_BLUE_Win:
	db 0, "グリーン『ちっ⋯<LINE>やっぱり　つよいな<DONE>"
RematchText_BLUE_After:
	db 0, "グリーン『おまえと　たたかうと<LINE>あいつを　おもいだすぜ<DONE>"

; =====================================================================
; ジョウトの ジムリーダー 再戦（RM_JOHTO を 決めた ときだけ。日本版 金・銀。トレーナーのバンクに 空きが ない 版 ＝ RM_PARTY_FAR 用）
;   ・殿堂入りの あと（EVENT_BEAT_ELITE_FOUR）、ジムリーダーに 話しかけると「もう いちど しょうぶ する？」と きかれ、
;     「はい」なら 強い 手持ち（Lv52〜58）で 戦える。何度でも 戦える。
;   ・「いいえ」・殿堂入り まえ・初めて 戦う ときは 元の ゲームと 同じ。
;   ・話しかけの「checkevent EVENT_BEAT_○○ / iftrue .FightDone」（イブキは「checkflag ライジングバッジ / iftrue .AlreadyGotBadge」）を
;     farsjump に かえる。手持ちは カントーと 同じ しくみ（上の 2）で 新しい バンクから 読む。
;   このファイルの前に 決めるもの（rematch_johto_<版>.inc）：
;     RMJ_<名前>_MAPBANK / _PATCH（6バイトの 所）/ _CMD（SC_CHECKEVENT か SC_CHECKFLAG）/ _ID（イベント・フラグの 番号）/
;     _DONE（勝った あと）/ _DONE_NO（「いいえ」の とき。もう 話しはじめて いるので opentext を とばした 所）/ _OPEN（0 ＝ opentext が まだ）/ _CLASS
;     RMJ_EVENT_BEAT_ELITE_FOUR・RMJ_SCRIPT_ADDR（新しい スクリプト）・RMJ_PARTY_ADDR（手持ち）
IF DEF(RM_JOHTO)
MACRO rmj_patch ; 名前
SECTION "rematch johto patch \1", ROMX[RMJ_\1_PATCH], BANK[RMJ_\1_MAPBANK]
	db SC_FARSJUMP, BANK(RematchJ_\1)
	dw RematchJ_\1
ENDM
	rmj_patch FALKNER
	rmj_patch BUGSY
	rmj_patch WHITNEY
	rmj_patch MORTY
	rmj_patch CHUCK
	rmj_patch JASMINE
	rmj_patch PRYCE
	rmj_patch CLAIR

MACRO rmj_script ; 名前
RematchJ_\1:
	db RMJ_\1_CMD
	dw RMJ_\1_ID
	db SC_IFFALSE
	dw .first\@
	db SC_CHECKEVENT
	dw RMJ_EVENT_BEAT_ELITE_FOUR
	db SC_IFFALSE
	dw .done\@
IF RMJ_\1_OPEN == 0
	db SC_OPENTEXT
ENDC
	db SC_WRITETEXT
	dw RematchText_\1_Ask
	db SC_YESORNO
	db SC_IFFALSE
	dw .no\@
	db SC_CLOSETEXT
	db SC_WINLOSSTEXT
	dw RematchText_\1_Win, 0
	db SC_LOADTRAINER, RMJ_\1_CLASS, RM_TRAINER_ID
	db SC_STARTBATTLE
	db SC_RELOADMAPAFTERBATTLE
	db SC_OPENTEXT
	db SC_WRITETEXT
	dw RematchText_\1_After
	db SC_WAITBUTTON
	db SC_CLOSETEXT
	db SC_END
.first\@  ; まだ 勝って いない（イブキは バッジが まだ）：元の ゲームの つづき
	db SC_FARSJUMP, RMJ_\1_MAPBANK
	dw RMJ_\1_PATCH + 6
.done\@   ; 殿堂入り まえ：元の ゲームの 勝った あと
	db SC_FARSJUMP, RMJ_\1_MAPBANK
	dw RMJ_\1_DONE
.no\@     ; 「いいえ」：元の ゲームの 勝った あと
	db SC_FARSJUMP, RMJ_\1_MAPBANK
	dw RMJ_\1_DONE_NO
ENDM

SECTION "rematch johto scripts", ROMX[RMJ_SCRIPT_ADDR], BANK[RM_SCRIPT_BANK]
	rmj_script FALKNER
	rmj_script BUGSY
	rmj_script WHITNEY
	rmj_script MORTY
	rmj_script CHUCK
	rmj_script JASMINE
	rmj_script PRYCE
	rmj_script CLAIR

RematchText_FALKNER_Ask:
	db 0, "ハヤト『また　きたのか！<LINE>とりポケモンも<CONT>あれから　つよく　なった<PARA>もう　いちど<LINE>しょうぶ　するか？<DONE>"
RematchText_FALKNER_Win:
	db 0, "ハヤト『くっ⋯<LINE>また　つばさを<CONT>おられて　しまった<DONE>"
RematchText_FALKNER_After:
	db 0, "ハヤト『ちちに　まけない<LINE>とりつかいに　なるため<CONT>まだまだ　きたえるぞ！<DONE>"

RematchText_BUGSY_Ask:
	db 0, "ツクシ『あっ　きみか！<LINE>むしポケモンの　けんきゅう<CONT>もっと　すすんだんだ<PARA>ためして　みる？<DONE>"
RematchText_BUGSY_Win:
	db 0, "ツクシ『うーん！<LINE>まだ　けんきゅうが<CONT>たりなかったか！<DONE>"
RematchText_BUGSY_After:
	db 0, "ツクシ『むしポケモンの<LINE>ふかさは　まだまだ<CONT>こんな　もんじゃないよ！<DONE>"

RematchText_WHITNEY_Ask:
	db 0, "アカネ『あっ　あんたか！<LINE>こんどは　なかへんで！<PARA>うちの　ほんきと<LINE>しょうぶ　する？<DONE>"
RematchText_WHITNEY_Win:
	db 0, "アカネ『うそやん！<LINE>また　まけたー！<DONE>"
RematchText_WHITNEY_After:
	db 0, "アカネ『ええもん！<LINE>つぎは　ぜったい<CONT>かったるからな！<DONE>"

RematchText_MORTY_Ask:
	db 0, "マツバ『きみが　くることは<LINE>みえていたよ<PARA>いまの　ぼくの<LINE>ゴーストたちと<CONT>しょうぶ　するかい？<DONE>"
RematchText_MORTY_Win:
	db 0, "マツバ『やはり　きみは<LINE>えらばれた　トレーナー<CONT>なのかも　しれない<DONE>"
RematchText_MORTY_After:
	db 0, "マツバ『ぼくも　まだ<LINE>しゅぎょうが　たりないね<DONE>"

RematchText_CHUCK_Ask:
	db 0, "シジマ『うおおーっ！<LINE>また　きたか！<PARA>たきに　うたれて<LINE>きたえなおした　ちからを<CONT>みせて　やろう！<DONE>"
RematchText_CHUCK_Win:
	db 0, "シジマ『ぐおお⋯！<LINE>まいった！<DONE>"
RematchText_CHUCK_After:
	db 0, "シジマ『よし！<LINE>また　たきに<CONT>うたれて　くるぞ！<DONE>"

RematchText_JASMINE_Ask:
	db 0, "ミカン『あ⋯　こんにちは<LINE>はがねの　ように<CONT>つよく　なりました<PARA>しょうぶ　して<LINE>いただけますか？<DONE>"
RematchText_JASMINE_Win:
	db 0, "ミカン『⋯やっぱり<LINE>つよい　です<DONE>"
RematchText_JASMINE_After:
	db 0, "ミカン『また⋯<LINE>きて　くださいね<DONE>"

RematchText_PRYCE_Ask:
	db 0, "ヤナギ『ほう⋯<LINE>また　きたか<PARA>こおりの　ように<LINE>きたえあげた　わしの<CONT>ポケモンと　たたかうか？<DONE>"
RematchText_PRYCE_Win:
	db 0, "ヤナギ『わしも　まだまだ<LINE>じゃな⋯<DONE>"
RematchText_PRYCE_After:
	db 0, "ヤナギ『わかい　もんには<LINE>まだ　まけて<CONT>おれんのじゃがのう<DONE>"

RematchText_CLAIR_Ask:
	db 0, "イブキ『あら　あなた<LINE>また　きたの？<PARA>ドラゴンつかいの<LINE>ほんとうの　ちから<CONT>みせて　あげるわ！<PARA>しょうぶ　する？<DONE>"
RematchText_CLAIR_Win:
	db 0, "イブキ『くっ⋯<LINE>また　まけるなんて<DONE>"
RematchText_CLAIR_After:
	db 0, "イブキ『つぎは　ぜったい<LINE>まけないわよ！<DONE>"
ENDC
