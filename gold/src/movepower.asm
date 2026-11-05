; 戦闘で わざを えらぶ とき、わざの 威力と 命中も 出す（金 日本版）
;
; ・わざを えらぶ 画面の 右下の わく（元は PP・「わざタイプ」・／タイプ）を つぎの ように する：
;       　　　　15／30      ← PP（元の まま）
;       ドラゴン　×1／2     ← わざの タイプ・相手への 効き目（「わざタイプ」・「／」は けす）
;       いりょく　　 40
;       めいちゅう　100     ← 命中（％）
;   タイプを 上の 行に したのは、日本版は 濁点・半濁点を 1行 上に かくため。いちばん 下の 行に タイプを かくと、
;   その 上の 行の 命中の 数と かさなって「ドラゴン」「エスパー」の 濁点が きえて いた（「トラコン」「エスハー」）。
;   14行めの タイプの 濁点は 13行めの x 10〜13（PP の 左。いつも 空いて いる）に 出る。
;   威力が 0・1 の わざ（へんかわざ・ちきゅうなげ など）は「ー」。
;   命中は 0〜255 を ％に（×100÷255 を 四捨五入。255 → 100、229 → 90、76 → 30 など）。
;   効き目は 相手の タイプ（2つ）への ばいりつ：×4・×2・×1・×1／2・×1／4・×0。
;   野生・トレーナー どちらの 戦闘でも 出す。威力が 0・1 の わざには 出さない。
;   （めざめるパワーは わざの データの タイプ（ノーマル）で 計算する。みやぶる は 考えない）
;
; しくみ
;   ・MoveInfoBox の さいご（predef PrintMoveType / ret。9バイト）を 新しい バンクへの farcall に して、
;     14〜16行めの わくの 中を けして から、タイプ（hlcoord 10, 14）・威力・命中・効き目を かく。
;     （「つかえない！」（かなしばり）の ときは ここを 通らないので 元の まま）
;   ・威力・命中は UpdateMoveData で 入る wPlayerMoveStruct の MOVE_POWER・MOVE_ACC。
;   ・効き目は wPlayerMoveStruct の MOVE_TYPE と wEnemyMonType1・2 で、TypeMatchups（バンク$0d）を さいごまで 見る
;     （CheckTypeMatchup と 同じ。1つの 行は タイプ1 か タイプ2 の どちらかに 1回だけ）。タイプの 右（hlcoord 15, 14）に かく
;     （「×1／2」は 4ます なので、PP の 左だと「15／30」と つながって 見える）。
;
; 銀・クリスタルに 入れるとき：下の DEF を その ROM の 値に する
;   （クリスタルの MoveInfoBox は わくの 場所・文字の 場所が 同じか 確かめる。TypeMatchups の 場所も その ROM の もの）

INCLUDE "src/charmap_jp.inc"

IF !DEF(MP_HOOK)
DEF MP_HOOK            EQU $65e4      ; バンク$0f MoveInfoBox の ld hl, $c4ef / ld a, PRINTMOVETYPE / call Predef / ret
DEF MP_HOOK_BANK       EQU $0f
DEF MP_PREDEF_PRINTMOVETYPE EQU $2a
DEF MP_Predef          EQU $2e05
DEF MP_PlaceString     EQU $0f46
DEF MP_PrintNum        EQU $31f9
DEF MP_wPlayerMoveStruct EQU $caef    ; MOVE_ANIM（+2 威力・+4 命中）
DEF MP_wStringBuffer1  EQU $cf87
DEF MP_wEnemyMonType1  EQU $d0ff
DEF MP_wEnemyMonType2  EQU $d100
DEF MP_TypeMatchups    EQU $4cfd      ; バンク$0d（こうげき・ぼうぎょ・ばいりつ（0／5／20）。$fe くぎり・$ff おわり）
DEF MP_TYPES_BANK      EQU $0d
DEF MP_GetFarByte      EQU $30e4
DEF MP_COORD           EQU $c3a0      ; hlcoord 0, 0
DEF MP_BANK            EQU $45
DEF MP_ADDR            EQU $6400
ENDC
DEF MP_TYPE_COORD      EQU MP_COORD + 14 * 20 + 10   ; タイプの 名前（14行め の 左）

SECTION "movepower hook", ROMX[MP_HOOK], BANK[MP_HOOK_BANK]
	ld a, BANK(MovePower_Draw)
	ld hl, MovePower_Draw
	rst $08
	ret

SECTION "movepower", ROMX[MP_ADDR], BANK[MP_BANK]
MovePower_Draw:
	; 14〜16行めの 右の わく（x 10〜18）を けす（「わざタイプ」・その 濁点・「／タイプ」）
	; b = わざの タイプ（呼ぶ 前に 入って いる）は とって おく
	push bc
	ld hl, MP_COORD + 14 * 20 + 10
	ld b, 3
.clear_row
	ld c, 9
	ld a, $7f
.clear
	ld [hli], a
	dec c
	jr nz, .clear
	ld de, 20 - 9
	add hl, de
	dec b
	jr nz, .clear_row
	pop bc
	; タイプ（14行め の 左。濁点は 13行め の x 10〜13 ＝ PP の 左で 空いて いる）
	ld hl, MP_TYPE_COORD
	ld a, MP_PREDEF_PRINTMOVETYPE
	call MP_Predef
	; いりょく（15行め）
	ld hl, MP_COORD + 15 * 20 + 10
	ld de, .PowerLabel
	call MP_PlaceString
	ld a, [MP_wPlayerMoveStruct + 2]
	cp 2
	jr nc, .power
	ld a, $e3                         ; ー
	ld [MP_COORD + 15 * 20 + 18], a
	jr .acc
.power
	ld [MP_wStringBuffer1], a
	ld hl, MP_COORD + 15 * 20 + 16
	ld de, MP_wStringBuffer1
	ld bc, $0103                      ; 1バイト・3けた
	call MP_PrintNum
.acc
	; めいちゅう（16行め。×100÷255 を 四捨五入）
	ld hl, MP_COORD + 16 * 20 + 10
	ld de, .AccLabel
	call MP_PlaceString
	ld a, [MP_wPlayerMoveStruct + 4]
	ld l, a
	ld h, 0
	ld d, h
	ld e, l
	add hl, hl                        ; ×100 = ×64 + ×32 + ×4
	add hl, hl
	push hl                           ; ×4
	add hl, hl
	add hl, hl
	add hl, hl
	push hl                           ; ×32
	add hl, hl                        ; ×64
	pop de
	add hl, de
	pop de
	add hl, de
	ld de, 127
	add hl, de
	ld c, 0                           ; ÷255
	ld de, -255
.div
	ld a, h
	and a
	jr nz, .sub
	ld a, l
	cp 255
	jr c, .divdone
.sub
	add hl, de
	inc c
	jr .div
.divdone
	ld a, c
	ld [MP_wStringBuffer1], a
	ld hl, MP_COORD + 16 * 20 + 16
	ld de, MP_wStringBuffer1
	ld bc, $0103                      ; 1バイト・3けた
	call MP_PrintNum
	; 効き目（タイプの 左。威力が 0・1 の わざは 出さない）
	ld a, [MP_wPlayerMoveStruct + 2]
	cp 2
	ret c
	ld a, [MP_wPlayerMoveStruct + 3]
	ld d, a                           ; わざの タイプ
	ld a, [MP_wEnemyMonType1]
	ld b, a
	ld a, [MP_wEnemyMonType2]
	ld c, a
	ld e, 4                           ; ×1 ＝ 4（1／4 きざみ）
	ld hl, MP_TypeMatchups
.mloop
	call .Far
	cp $ff
	jr z, .mdone
	cp $fe                            ; みやぶる の くぎり
	jr z, .mloop
	cp d
	jr nz, .skip2
	call .Far
	cp b
	jr z, .match
	cp c
	jr z, .match
	inc hl
	jr .mloop
.skip2
	inc hl
	inc hl
	jr .mloop
.match
	call .Far
	and a
	jr nz, .not0
	ld e, a                           ; ×0
	jr .mloop
.not0
	cp 10
	jr nc, .double
	srl e                             ; ×1／2
	jr .mloop
.double
	sla e                             ; ×2
	jr .mloop
.mdone
	ld hl, .Eff0
	ld a, e
	and a
	jr z, .put
	ld hl, .Eff14
	dec a
	jr z, .put
	ld hl, .Eff12
	dec a
	jr z, .put
	ld hl, .Eff1
	cp 4 - 2
	jr z, .put
	ld hl, .Eff2
	cp 8 - 2
	jr z, .put
	ld hl, .Eff4
.put
	ld d, h
	ld e, l
	ld hl, MP_COORD + 14 * 20 + 15
	jp MP_PlaceString

.Far
	ld a, MP_TYPES_BANK
	call MP_GetFarByte
	inc hl
	ret

.Eff0  db $f1, $f6, "@"                 ; ×0
.Eff14 db $f1, $f7, $f3, $fa, "@"       ; ×1／4
.Eff12 db $f1, $f7, $f3, $f8, "@"       ; ×1／2
.Eff1  db $f1, $f7, "@"                 ; ×1
.Eff2  db $f1, $f8, "@"                 ; ×2
.Eff4  db $f1, $fa, "@"                 ; ×4

.PowerLabel db "いりょく@"
.AccLabel   db "めいちゅう@"
