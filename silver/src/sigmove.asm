; ルギア・ホウオウが 専用わざ（エアロブラスト・せいなるほのお）を 覚えられるようにする（金・銀・クリスタル共通）
;
; 元のゲーム：専用わざは レベル1 でしか覚えない。野生のポケモンは「そのレベルまでに覚える わざの 最後の4つ」を持って出るので、
;   レベル40（銀のルギア・金のホウオウ）なら 覚えているが、
;   レベル60（クリスタル）・レベル70（金のルギア・銀のホウオウ）だと 押し出されて 覚えていない。
;   わざを思い出させる人もいないので、あとから覚えることも できなかった。
; 変えたあと：レベルアップで覚える わざの表に「レベル60 で 専用わざ」を足す（レベル1 は そのまま）。
;   ・クリスタルの レベル60、金銀の レベル70 で出てくる ルギア・ホウオウも 専用わざを 覚えている。
;   ・レベル40（銀のルギア・金のホウオウ）は 今までどおり レベル1 の 専用わざを 覚えている。
;   ・すでに つかまえた ルギア・ホウオウも、レベル60 に 上がるとき（60 を こえるときも 1回）に 覚えられる
;     （もう 覚えていれば 何も出ない）。
;   ・出てくるときの レベル：SIG_LUGIA_WILD・SIG_HOOH_WILD（loadwildmon の レベルの バイトの場所）を決めると、
;     そのレベルを SIG_WILD_LEVEL（ふつうは 40。金銀の 元の 低いほうと 同じ）にする（クリスタルは 両方 60 → 40）。
;     レベル40 なら 元の表でも 専用わざを 覚えて出てくる。決めなければ 出てくるレベルは 元のまま。
; しくみ：表が 2バイト ふえるので、ルギアと ホウオウの 表を 同じバンクの 空きに 置きなおし、
;   EvosAttacksPointers の 2つの ポインタを 書きかえる。

;---------------------------------------------------------------------
; ROM ごとにちがう所（ここは クリスタル日本版の値）。tools/sigmove_find.py で調べられる
;---------------------------------------------------------------------
IF !DEF(SIG_BANK)
DEF SIG_BANK           EQU $10     ; EvosAttacks のバンク
DEF SIG_PTR_LUGIA      EQU $6943   ; EvosAttacksPointers の ルギア（249番）の所
DEF SIG_PTR_HOOH       EQU $6945   ; EvosAttacksPointers の ホウオウ（250番）の所
DEF SIG_FREE           EQU $7e40   ; 同じバンクの空き（48バイト）
DEF SIG_LUGIA_WILD_BANK EQU $1c    ; うずまきじまの ルギア：loadwildmon LUGIA, 60 の レベルの所
DEF SIG_LUGIA_WILD     EQU $4ad4
DEF SIG_HOOH_WILD_BANK EQU $1a     ; スズのとうの ホウオウ：loadwildmon HO_OH, 60 の レベルの所
DEF SIG_HOOH_WILD      EQU $5f62
ENDC
IF !DEF(SIG_WILD_LEVEL)
DEF SIG_WILD_LEVEL     EQU 40      ; 出てくるときの レベル
ENDC
IF !DEF(SIG_LEVEL)
DEF SIG_LEVEL          EQU 60      ; もういちど 専用わざを 覚える レベル
ENDC

; わざの番号（金・銀・クリスタル 共通）
DEF AEROBLAST    EQU $b1
DEF SACRED_FIRE  EQU $dd
DEF SAFEGUARD    EQU $db
DEF GUST         EQU $10
DEF RECOVER      EQU $69
DEF HYDRO_PUMP   EQU $38
DEF FIRE_BLAST   EQU $7e
DEF RAIN_DANCE   EQU $f0
DEF SUNNY_DAY    EQU $f1
DEF SWIFT        EQU $81
DEF WHIRLWIND    EQU $12
DEF ANCIENTPOWER EQU $f6
DEF FUTURE_SIGHT EQU $f8

SECTION "sigmove lugia ptr", ROMX[SIG_PTR_LUGIA], BANK[SIG_BANK]
	dw SigMove_LugiaEvosAttacks
	dw SigMove_HoOhEvosAttacks

IF DEF(SIG_LUGIA_WILD)
SECTION "sigmove lugia level", ROMX[SIG_LUGIA_WILD], BANK[SIG_LUGIA_WILD_BANK]
	db SIG_WILD_LEVEL
ENDC
IF DEF(SIG_HOOH_WILD)
SECTION "sigmove hooh level", ROMX[SIG_HOOH_WILD], BANK[SIG_HOOH_WILD_BANK]
	db SIG_WILD_LEVEL
ENDC

SECTION "sigmove lists", ROMX[SIG_FREE], BANK[SIG_BANK]
SigMove_LugiaEvosAttacks:
	db 0                         ; 進化しない
	db 1, AEROBLAST
	db 11, SAFEGUARD
	db 22, GUST
	db 33, RECOVER
	db 44, HYDRO_PUMP
	db 55, RAIN_DANCE
	db SIG_LEVEL, AEROBLAST      ; 足した所
	db 66, SWIFT
	db 77, WHIRLWIND
	db 88, ANCIENTPOWER
	db 99, FUTURE_SIGHT
	db 0

SigMove_HoOhEvosAttacks:
	db 0
	db 1, SACRED_FIRE
	db 11, SAFEGUARD
	db 22, GUST
	db 33, RECOVER
	db 44, FIRE_BLAST
	db 55, SUNNY_DAY
	db SIG_LEVEL, SACRED_FIRE    ; 足した所
	db 66, SWIFT
	db 77, WHIRLWIND
	db 88, ANCIENTPOWER
	db 99, FUTURE_SIGHT
	db 0
