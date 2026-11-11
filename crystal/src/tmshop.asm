; 1回しか もらえない わざマシンを タマムシデパート 3F で 買える（金 日本版）
;
; ・タマムシデパート 3F の 店員に はなしかけると「どの　わざマシンに　しますか？」と きいて、
;   「わざマシン01ー17」「わざマシン18ー35」「わざマシン36ー50」「やめる」を えらぶ。
;   えらんだ はんいの わざマシン（元から 売って いる 5つ ＋ 1回しか もらえない 32こ）の 店に なる。
;   タマムシシティ（カントー）は 殿堂入りの あとに 行ける ので、殿堂入りの あとに 買える。
; ・売らない もの：ほかの 店で 売って いる もの（02 ずつき・08 いわくだき・33・41・48 パンチ）、
;   ゲームコーナーの 景品（14・15・25・29・32・38）、毎週 もらえる 21 やつあたり・27 おんがえし。
; ・値段は 元の 値段（ItemAttributes の まま）。
;
; しくみ
;   ・店員の スクリプト（CeladonDeptStore3FClerkScript）の 頭を この バンクの TmShopScript への farsjump に。
;     TmShopScript は メニューで えらばせて から 元と 同じ「pokemart MARTTYPE_STANDARD, MART_CELADON_3F」を する。
;   ・店の 表：GetMart の フック（src/masterball.asm の MasterBallMart）が、タマムシ 3F の 表の とき
;     TmShopMart を 呼ぶ。TmShopMart は wScriptVar（メニューで えらんだ 1〜3）の 表に かえる（b = バンク、de = 表）。
;     1つの 店は 14こまで（wCurMartItems が 15バイト）なので 3つに わけた。
;
; 銀・クリスタルに 入れるとき：下の DEF を その ROM の 値に する
;   TS_CLERK・TS_CLERK_BANK  CeladonDeptStore3FClerkScript（元：faceplayer / opentext / pokemart 0, MART_CELADON_3F /
;                            closetext / end ＝ 6a 47 93 00 xx 00 49 90）。頭の 4バイトを かえる
;   TS_MART_ID               MART_CELADON_3F の 番号
;   TS_wScriptVar            wScriptVar
;   TS_BANK・TS_ADDR          空き（約 200バイト）
;   src/masterball.asm の MB_MART_CELADON_3F（Marts の 表の MART_CELADON_3F の 場所）も その ROM の 値に

IF !DEF(TS_NO_INCLUDES)          ; クリスタルは src/tmshop_crystal.asm で 先に 読みこむ
INCLUDE "includes.asm"
INCLUDE "src/charmap_jp.inc"
ENDC

IF !DEF(TS_CLERK)
DEF TS_CLERK        EQU $639a      ; バンク$27 CeladonDeptStore3FClerkScript
DEF TS_CLERK_BANK   EQU $27
DEF TS_MART_ID      EQU $19        ; MART_CELADON_3F
DEF TS_wScriptVar   EQU $d165
DEF TS_BANK         EQU $4b
DEF TS_ADDR         EQU $4000
ENDC

SECTION "tmshop clerk", ROMX[TS_CLERK], BANK[TS_CLERK_BANK]
	db farsjump_command, TS_BANK
	dw TmShopScript

SECTION "tmshop", ROMX[TS_ADDR], BANK[TS_BANK]
TmShopScript:
	faceplayer
	opentext
	writetext TmShop_Text
	loadmenu .MenuHeader
	verticalmenu
	closewindow
	ifequal 1, .mart
	ifequal 2, .mart
	ifequal 3, .mart
	closetext
	end
.mart
	pokemart MARTTYPE_STANDARD, TS_MART_ID
	closetext
	end

.MenuHeader:
	db MENU_BACKUP_TILES
	menu_coords 0, 2, 14, 11
	dw .MenuData
	db 1
.MenuData:
	db STATICMENU_CURSOR
	db 4
	db "わざマシン", $f6, $f7, "ー", $f7, $fd, "@"   ; 01ー17
	db "わざマシン", $f7, $fe, "ー", $f9, $fb, "@"   ; 18ー35
	db "わざマシン", $f9, $fc, "ー", $fb, $f6, "@"   ; 36ー50
	db "やめる@"

TmShop_Text:
	db $00, "いらっしゃいませ！", $4f
	db "どの　わざマシンに　しますか？", $57

; GetMart の フック（src/masterball.asm）から 呼ぶ。b・de ＝ 元の 表 → えらんだ はんいの 表
TmShopMart::
	ld a, [TS_wScriptVar]
	dec a
	cp 3
	ret nc
	add a
	ld l, a
	ld h, 0
	ld de, .lists
	add hl, de
	ld e, [hl]
	inc hl
	ld d, [hl]
	ld b, BANK(@)
	ret
.lists
	dw TmShopList1, TmShopList2, TmShopList3

TmShopList1:
	db 13
	db TM_DYNAMICPUNCH, TM_CURSE, TM_ROLLOUT, TM_ROAR, TM_TOXIC, TM_ZAP_CANNON, TM_PSYCH_UP
	db TM_HIDDEN_POWER, TM_SUNNY_DAY, TM_SWEET_SCENT, TM_SNORE, TM_ICY_WIND, TM_PROTECT
	db -1
TmShopList2:
	db 12
	db TM_RAIN_DANCE, TM_GIGA_DRAIN, TM_ENDURE, TM_SOLARBEAM, TM_IRON_TAIL, TM_DRAGONBREATH
	db TM_EARTHQUAKE, TM_DIG, TM_SHADOW_BALL, TM_MUD_SLAP, TM_SWAGGER, TM_SLEEP_TALK
	db -1
TmShopList3:
	db 12
	db TM_SLUDGE_BOMB, TM_SANDSTORM, TM_SWIFT, TM_DEFENSE_CURL, TM_DREAM_EATER, TM_DETECT
	db TM_REST, TM_ATTRACT, TM_THIEF, TM_STEEL_WING, TM_FURY_CUTTER, TM_NIGHTMARE
	db -1
