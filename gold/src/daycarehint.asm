; そだてやの おじいさんが ２ひきの なかの よさと タマゴの ようすを おしえる（金 日本版）
;
; ・そだてやの 中の おじいさんに はなしかけた とき、おばあさんにも あずけて いて（２ひき）タマゴが まだ なければ、
;   ひきとるか きく 前に：
;     「２ひきは とっても なかが いい ようじゃ」など なかの よさ（４だんかい）と、
;     「タマゴが そろそろ みつかるかも しれんぞ」／「タマゴは まだまだ じゃな」を いう。
;   いっしょに あそばない ２ひき なら「タマゴは できそうに ないわい」。
; ・なかの よさは タマゴが できる みこみ（31%・16%・12%・4%）の ４だんかい と 同じ（CheckBreedmonCompatibility）。
; ・「そろそろ」は つぎに タマゴを しらべる まで 40ぽ いない（wStepsToEgg）。
;
; しくみ
;   ・DayCareMan .AskWithdrawMon の 頭の「farcall GetBreedMon1LevelGrowth」（7バイト）を 新しい バンクの
;     DayCareHint への farcall に。DayCareHint は 話を して から GetBreedMon1LevelGrowth を 呼ぶ（b・d を そのまま かえす）。
;
; 銀・クリスタルに 入れるとき：下の DEF を その ROM の 値に する
;   DH_HOOK  DayCareMan .AskWithdrawMon（farcall GetBreedMon1LevelGrowth）
;   DH_GetBreedMon1LevelGrowth・DH_CheckBreedmonCompatibility・DH_PrintText・WRAM
;   （クリスタルは DayCareMan の 作りが 同じか 確かめる）

INCLUDE "src/charmap_jp.inc"

IF !DEF(DH_HOOK)
DEF DH_HOOK          EQU $6d06       ; バンク$05 DayCareMan .AskWithdrawMon
DEF DH_HOOK_BANK     EQU $05
DEF DH_GetBreedMon1LevelGrowth EQU $696e
DEF DH_GetBreedMon1LevelGrowth_BANK EQU $03
DEF DH_CheckBreedmonCompatibility EQU $78e9
DEF DH_CheckBreedmonCompatibility_BANK EQU $05
DEF DH_PrintText     EQU $0f30
DEF DH_wDayCareMan   EQU $dbd4
DEF DH_wDayCareLady  EQU $dc01
DEF DH_wStepsToEgg   EQU $dc02
DEF DH_wBreedingCompatibility EQU $d143
DEF DH_BANK          EQU $45
DEF DH_ADDR          EQU $6200
; あずけた ポケモンの 今の レベル（DH_LEVEL）
DEF DH_LEVEL EQU 1
DEF DH_LADY_HOOK     EQU $6d5a       ; DayCareLady .AskWithdrawMon（ld a, $03 / ld hl, $6989 / rst $08）
DEF DH_GetBreedMon2LevelGrowth EQU $6989
DEF DH_wBreedMon1Nickname EQU $dbd5
DEF DH_wBreedMon2Nickname EQU $dc04
DEF DH_wLevelTemp    EQU $cf99       ; wStringBuffer2 ＋ 7
DEF DH_LEVEL_ADDR    EQU $6380
ENDC
DEF DH_SOON          EQU 40

SECTION "daycarehint hook", ROMX[DH_HOOK], BANK[DH_HOOK_BANK]
	ld a, BANK(DayCareHint)
	ld hl, DayCareHint
	rst $08

SECTION "daycarehint", ROMX[DH_ADDR], BANK[DH_BANK]
DayCareHint:
IF DEF(DH_LEVEL)
	ld a, DH_GetBreedMon1LevelGrowth_BANK
	ld hl, DH_GetBreedMon1LevelGrowth
	rst $08                          ; e ＝ 今の レベル、d ＝ ふえた レベル
	push de
	push bc
	ld hl, DayCareLevel_Man
	call DayCareLevel_Print
	call .Talk
	pop bc
	pop de
	ret
ELSE
	call .Talk
	ld a, DH_GetBreedMon1LevelGrowth_BANK
	ld hl, DH_GetBreedMon1LevelGrowth
	rst $08
	ret
ENDC

.Talk
	ld a, [DH_wDayCareLady]
	bit 0, a                         ; DAYCARELADY_HAS_MON_F
	ret z
	ld a, [DH_wDayCareMan]
	bit 6, a                         ; DAYCAREMAN_HAS_EGG_F
	ret nz
	ld a, DH_CheckBreedmonCompatibility_BANK
	ld hl, DH_CheckBreedmonCompatibility
	rst $08
	ld a, [DH_wBreedingCompatibility]
	and a
	jr z, .never
	inc a
	jr z, .never
	dec a
	ld hl, .Best
	cp 230
	jr nc, .print
	ld hl, .Good
	cp 170
	jr nc, .print
	ld hl, .Ok
	cp 110
	jr nc, .print
	ld hl, .Bad
.print
	call DH_PrintText
	ld hl, .Later
	ld a, [DH_wStepsToEgg]
	cp DH_SOON + 1
	jr nc, .last
	ld hl, .Soon
	jr .last
.never
	ld hl, .Never
.last
	jp DH_PrintText

.Never
	db $00, $f8, "ひきは　いっしょに", $4f
	db "あそぼうと　せんのう", $51
	db "タマゴは　できそうに　ないわい", $58
.Best
	db $00, $f8, "ひきは　とっても", $4f
	db "なかが　いい　ようじゃ", $58
.Good
	db $00, $f8, "ひきは　なかが　いい　ようじゃ", $58
.Ok
	db $00, $f8, "ひきは　まあまあ", $4f
	db "なかが　いい　ようじゃ", $58
.Bad
	db $00, $f8, "ひきは　あまり", $4f
	db "なかが　よくない　ようじゃ", $58
.Soon
	db $00, "タマゴが　そろそろ", $4f
	db "みつかるかも　しれんぞ", $58
.Later
	db $00, "タマゴは　まだまだ　じゃな", $58

IF DEF(DH_LEVEL)
; あずけた ポケモンの 今の レベルも おしえる（おじいさん・おばあさん）
;   DH_LADY_HOOK（DayCareLady .AskWithdrawMon の farcall GetBreedMon2LevelGrowth）も DayCareLevel_Lady への farcall に。
;   DH_wBreedMon1Nickname・DH_wBreedMon2Nickname・DH_GetBreedMon2LevelGrowth・DH_wLevelTemp（1バイト）を 決める
SECTION "daycarehint lady hook", ROMX[DH_LADY_HOOK], BANK[DH_HOOK_BANK]
	ld a, BANK(DayCareLevel_Lady)
	ld hl, DayCareLevel_Lady
	rst $08

SECTION "daycarehint level", ROMX[DH_LEVEL_ADDR], BANK[DH_BANK]
DayCareLevel_Lady:
	ld a, DH_GetBreedMon1LevelGrowth_BANK
	ld hl, DH_GetBreedMon2LevelGrowth
	rst $08
	push de
	push bc
	ld hl, DayCareLevel_LadyText
	call DayCareLevel_Print
	pop bc
	pop de
	ret

DayCareLevel_Print:                  ; e ＝ レベル、hl ＝ 文
	ld a, e
	ld [DH_wLevelTemp], a
	jp DH_PrintText

DayCareLevel_Man:
	db $01
	dw DH_wBreedMon1Nickname
	db $00, "は　いま", $4f
	db "レべル", $50
	db $09
	dw DH_wLevelTemp
	db $13
	db $00, "　じゃ", $58
DayCareLevel_LadyText:
	db $01
	dw DH_wBreedMon2Nickname
	db $00, "は　いま", $4f
	db "レべル", $50
	db $09
	dw DH_wLevelTemp
	db $13
	db $00, "　よ", $58
ENDC
