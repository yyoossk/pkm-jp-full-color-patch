; これからの 直しや 追加は ここに 書く（今は 空 ＝ Ver.1.8.0 と 同じ ROM）。
; ・SECTION で バンクと 番地を 決めて 書くと、その 所だけ 土台の ROM の 上に かさなる。
;     SECTION "あたらしい 処理", ROMX[$7158], BANK[$09]   ; 空きは ../空きバンク.txt
;     SECTION "呼ぶ 所", ROMX[$4d02], BANK[$09]            ; 元の 命令を かえる 所
; ・版ごとに 番地が ちがう ときは、INCLUDE EDITION_INC で patches/editions/<版>.inc の 名前を 使う。
;   版の 番号は ED_0〜ED_11（tools/build.py の EDITIONS の じゅん）で、IF DEF(ED_4) などで 分けられる。
; ・処理の 名前と 番地は ../disasm/ の 逆アセンブル（と ../disasm/include/home_names.inc）を 見る。

INCLUDE "charmap.asm"
IF DEF(ED_0) || DEF(ED_4) || DEF(ED_8) || DEF(ED_10)
DEF FOLLOW EQU 1        ; 連れ歩きを 入れる 版（金銀グラフィックの 追加機能の 版）
ENDC   ; 字の 番号（pokegold の 日本語の charmap と 同じ。緑で 「ベ」は 「べ」）

; ===== 直し：Ver.1.8.1 =====
IF !DEF(ED_2) && !DEF(ED_3) && !DEF(ED_6) && !DEF(ED_7)   ; カラー化のみの 版には 当てない

; １．相手の HPバーの 色が 緑の ままに なる 直し
;     DrawEnemyHUDAndHPBar で e（HPバーの ドット数）を 入れた あと、キットの HP数字 処理（37:41a5）が de を こわしていた。
SECTION "相手HUD 呼ぶ所", ROMX[$4fe2], BANK[$0f]
	ld hl, KitEnemyHUDKeepDE
	ld b, $37
	call $3500            ; Bankswitch

SECTION "相手HUD de を まもる", ROMX[$5779], BANK[$37]
KitEnemyHUDKeepDE:
	push de
	call $41a5            ; キットの 相手HP数字
	call KitEnemyHUDFrame
	pop de
	ret

; ２．場所の 名前（看板）の 上に 人などの スプライトが かさなる 直し
;     PrepareOAMData の さいご（使わない OAM を 消す 所）を バンク37へ 移し、
;     看板が 出ている 間（hWY=$70 で のこり時間≠0）は 看板の 行に かかる スプライトを かくす。
DEF hWY_ADDR       EQU $ffb0
DEF hOAMBufOfs     EQU $ff90

SECTION "OAM 消す所 呼ぶ所", ROMX[$45c9], BANK[$01]
	ld hl, KitOAMSignHide
	ld b, $37
	jp $3500              ; Bankswitch（もどると VBlank へ 帰る）

; ４．場所の 名前の 看板を クリスタルと 同じ 見た目・色に し、下から スッと 出入り させる
;     （２の 「看板の 行の スプライトを かくす」 も ここで 看板の 高さに 合わせて 作りなおし）
;   ・枠の タイル 13まい を VRAMバンク1 の $51〜$5D（$9510〜）へ 看板を 出す たびに 読みこむ。
;   ・看板の バッファ（$cd7c、20×4）に クリスタルの PlaceMapNameFrame と 同じ ならびで 枠を 書く。
;   ・名前は ３行めの 真ん中。字は VRAMバンク1 に 「地＝色1・字＝色3」で 読みこむ。
;   ・ウインドウの 属性は ぜんぶ $0F（VRAMバンク1・パレット7）。
;   ・BGパレット7 の 色1・2 を 看板の 色に（元の 色は WRAMバンク7 に とっておき、引っこんだら もどす）。
;   ・VBlank（PrepareOAMData の さいご）で WY を 2ドット ずつ うごかし、看板に かかる スプライトを かくす。
DEF SIGN_T        EQU $50               ; 枠の タイル n は SIGN_T + n
DEF SIGN_C1       EQU 31 | 31 << 5 | 16 << 10   ; うすい 黄色
DEF SIGN_C2       EQU 14 | 9 << 5 | 0 << 10     ; 茶色
DEF wSignBuf      EQU $cd7c
DEF wSignName     EQU $cd68
DEF rSVBK_        EQU $ff70
DEF rVBK_         EQU $ff4f
DEF rWY_          EQU $ff4a
; WRAMバンク7（ほかで 使って いない）
DEF w7Sig         EQU $d000             ; $A5,$5A の しるし
DEF w7Cur         EQU $d002             ; 今の 看板の 高さ（WY）
DEF w7Save        EQU $d003             ; 元の パレット7 色1・色2（4バイト）
; WRAMバンク2（カラー化の パレット）
DEF w2Pal7Src     EQU $d000 + 7 * 8 + 2 ; もとの 色（BG パレット7 色1）
DEF w2Pal7Cur     EQU $d704 + 7 * 8 + 2 ; いまの 色
DEF w2PalDirty    EQU $d784             ; 1 に すると VBlank で BG パレットを 送る

SECTION "看板 枠を 書く 呼ぶ所", ROMX[$46b7], BANK[$37]
	call KitSignFrame
	ds 6, 0
SECTION "看板 名前を 置く 呼ぶ所", ROMX[$46d0], BANK[$37]
	call KitSignName
	ds 6, 0
SECTION "看板 出す 呼ぶ所", ROMX[$46d9], BANK[$37]
	call KitSignStart
SECTION "看板 字形 呼ぶ所", ROMX[$4744], BANK[$37]
	call nc, KitSignGlyph
SECTION "看板 属性", ROMX[$474d], BANK[$37]
	ld c, $0f            ; どの マスも VRAMバンク1・パレット7
	nop
	nop

SECTION "看板 クリスタル風", ROMX[$5800], BANK[$37]
KitSignFrame:
	ld hl, wSignBuf
	ld a, SIGN_T + 1
	ld [hli], a
	ld b, 4
.top
	ld a, SIGN_T + 3
	ld [hli], a
	ld [hli], a
	ld a, SIGN_T + 2
	ld [hli], a
	ld [hli], a
	dec b
	jr nz, .top
	ld a, SIGN_T + 3
	ld [hli], a
	ld [hli], a
	ld a, SIGN_T + 4
	ld [hli], a
	ld a, SIGN_T + 5
	ld [hli], a
	call .mid
	ld a, SIGN_T + 11
	ld [hli], a
	ld a, SIGN_T + 6
	ld [hli], a
	call .mid
	ld a, SIGN_T + 12
	ld [hli], a
	ld a, SIGN_T + 7
	ld [hli], a
	ld b, 4
.bot
	ld a, SIGN_T + 9
	ld [hli], a
	ld [hli], a
	ld a, SIGN_T + 8
	ld [hli], a
	ld [hli], a
	dec b
	jr nz, .bot
	ld a, SIGN_T + 9
	ld [hli], a
	ld [hli], a
	ld [hl], SIGN_T + 10
	ret
.mid
	ld a, SIGN_T + 13
	ld b, 18
.m
	ld [hli], a
	dec b
	jr nz, .m
	ret

; 名前を ３行めの 真ん中に 置く（左はし ＝ (20 − 文字数) ÷ 2）
KitSignName:
	ld hl, wSignName
	ld b, 0
.count
	ld a, [hli]
	cp $50
	jr z, .done
	inc b
	ld a, b
	cp 16
	jr c, .count
.done
	ld a, 20
	sub b
	srl a
	ld e, a
	ld d, 0
	ld hl, wSignBuf + 2 * 20
	add hl, de
	ld de, wSignName
	jp $0405             ; PlaceString

; 看板を 出す ときに 枠の タイルと パレットを 用意してから、キットの ウインドウ書きへ
KitSignStart:
	ld hl, SignFrameGfx
	ld de, $9510
	ld c, 13 * 16 / 2
.gfx
	di
	ld a, 1
	ldh [rVBK_], a
	call $47be           ; VRAM に 書ける まで まつ
	ld a, [hli]
	ld [de], a
	inc de
	ld a, [hli]
	ld [de], a
	inc de
	xor a
	ldh [rVBK_], a
	ei
	dec c
	jr nz, .gfx
; パレット（WRAMバンクを かえて いる あいだは call / push / pop を しない）
	di
	ldh a, [rSVBK_]
	ld e, a
	ld a, 2
	ldh [rSVBK_], a
	ld hl, w2Pal7Src
	ld a, [hli]
	ld b, a
	ld a, [hli]
	ld c, a
	ld a, [hli]
	ld d, a
	ld h, [hl]
	ld a, b
	cp LOW(SIGN_C1)
	jr nz, .save
	ld a, c
	cp HIGH(SIGN_C1)
	jr nz, .save
	ld a, d
	cp LOW(SIGN_C2)
	jr nz, .save
	ld a, h
	cp HIGH(SIGN_C2)
	jr z, .set           ; もう 看板の 色（元の 色は とってある）
.save
	ld a, 7
	ldh [rSVBK_], a
	ld a, b
	ld [w7Save], a
	ld a, c
	ld [w7Save + 1], a
	ld a, d
	ld [w7Save + 2], a
	ld a, h
	ld [w7Save + 3], a
	ld a, 2
	ldh [rSVBK_], a
.set
	ld hl, w2Pal7Src
	ld a, LOW(SIGN_C1)
	ld [hli], a
	ld a, HIGH(SIGN_C1)
	ld [hli], a
	ld a, LOW(SIGN_C2)
	ld [hli], a
	ld [hl], HIGH(SIGN_C2)
	ld hl, w2Pal7Cur
	ld a, LOW(SIGN_C1)
	ld [hli], a
	ld a, HIGH(SIGN_C1)
	ld [hli], a
	ld a, LOW(SIGN_C2)
	ld [hli], a
	ld [hl], HIGH(SIGN_C2)
	ld a, 1
	ld [w2PalDirty], a
	ld a, e
	ldh [rSVBK_], a
	ei
	jp $4733             ; キットの ウインドウ書き

; 名前の 字形を VRAMバンク1 に 「地＝色1・字＝色3」で 読みこむ（キットの 37:477f の かわり）
;   字形は 字と 同じ 番号（$8800〜）では なく、看板の バッファの 何番め（0〜79）を タイルの 番号に して
;   VRAMバンク1 の $9000〜$94FF（フィールドでは あいて いる）に おき、b を その 番号に かえて もどる
;   （呼ぶ 所は push hl / push bc / push de の あとで call する ので、sp + 6 が バッファの 次の 字）
KitSignGlyph:
	ld hl, sp + 6
	ld a, [hl]
	sub LOW(wSignBuf) + 1
	push af               ; タイルの 番号
	push bc
	ld a, b
	sub $80
	ld l, a
	ld h, 0
	add hl, hl
	add hl, hl
	add hl, hl
	ld bc, $4b19
	add hl, bc
	ld de, $cee4
	ld bc, 8
	ld a, $04
	call $028c           ; FarCopyData
	ld hl, sp + 3        ; push af の a
	ld l, [hl]
	ld h, 0
	add hl, hl
	add hl, hl
	add hl, hl
	add hl, hl
	ld bc, $9000
	add hl, bc
	ld d, h
	ld e, l
	ld hl, $cee4
	ld c, 8
.row
	ld a, [hli]
	ld b, a
	di
	ld a, 1
	ldh [rVBK_], a
	call $47be
	ld a, $ff
	ld [de], a
	inc de
	ld a, b
	ld [de], a
	inc de
	xor a
	ldh [rVBK_], a
	ei
	dec c
	jr nz, .row
	pop bc
	pop af
	ld b, a              ; 窓に 書く タイルの 番号
	ret

; VBlank：看板の 出入りと、看板に かかる スプライトを かくす。そのあと 元の 「使わない OAM を 消す」
;   hWY = $70 … 上へ 2ドット、hWY = $90 … 下へ 2ドット、それ 以外 … すぐ やめる
KitOAMSignHide:
IF DEF(FOLLOW)
	call FwFrame          ; 連れ歩きを OAM に 足す（看板の 下に かくす 前に）
ENDC
	di                    ; ここは DelayFrame の 中（割りこみ あり）。WRAMバンクを かえる あいだ 止める
	ldh a, [rSVBK_]
	ld e, a
	ld a, 7
	ldh [rSVBK_], a
	ld a, [w7Sig]
	cp $a5
	jr nz, .init
	ld a, [w7Sig + 1]
	cp $5a
	jr nz, .init
	ld a, [w7Cur]
	ld b, a
	jr .got
.init
	ld a, $a5
	ld [w7Sig], a
	ld a, $5a
	ld [w7Sig + 1], a
	ld a, $90
	ld [w7Cur], a
	ld b, a
.got
	ld a, 2              ; c = 1 なら パレット7 が 看板の 色の まま
	ldh [rSVBK_], a
	ld c, 0
	ld a, [w2Pal7Src]
	cp LOW(SIGN_C1)
	jr nz, .gotPal
	ld a, [w2Pal7Src + 1]
	cp HIGH(SIGN_C1)
	jr nz, .gotPal
	ld a, [w2Pal7Src + 2]
	cp LOW(SIGN_C2)
	jr nz, .gotPal
	ld a, [w2Pal7Src + 3]
	cp HIGH(SIGN_C2)
	jr nz, .gotPal
	inc c
.gotPal
	ld a, e
	ldh [rSVBK_], a
	ld d, 0              ; d = 1 なら パレットを もどす
	ldh a, [hWY_ADDR]
	cp $70
	jr nz, .notUp
	ld a, b
	sub 2
	cp $70
	jr nc, .up
	ld a, $70
.up
	ld b, a
	jr .setWY
.notUp
	cp $90
	jr nz, .other
	ld a, b
	cp $90
	jp nc, .clear        ; 出ていない
	dec c                ; 戦闘や マップの 読みなおしで 色が かわって いたら、うごかさず すぐ やめる
	jr nz, .quit
	add 2
	ld b, a
	cp $90
	jr c, .setWY
	ld b, $90            ; 引っこみ おわり
	inc d
	jr .store
.other
	ld a, b
	cp $90
	jp nc, .clear
.quit
	ld b, $90            ; 窓を ほかで 使うので すぐ やめる
	inc d
	jr .store
.setWY
	ld a, b
	ldh [rWY_], a
.store
	ld a, 7
	ldh [rSVBK_], a
	ld a, b
	ld [w7Cur], a
	ld a, e
	ldh [rSVBK_], a
	ld a, b
	cp $90
	jr nc, .restore
	add 16 - 8 + 1       ; これ より 下に かかる スプライトを かくす
	ld c, a
	ldh a, [hOAMBufOfs]
	ld e, a
	ld hl, $c300         ; wShadowOAM
.hide
	ld a, l
	cp e
	jr nc, .restore
	ld a, [hl]
	cp c
	jr c, .next
	ld [hl], $a0
.next
	ld a, l
	add 4
	ld l, a
	jr .hide
.restore
	ld a, d
	and a
	jr z, .clear
	ldh a, [rSVBK_]
	ld e, a
	ld a, 7
	ldh [rSVBK_], a
	ld a, [w7Save]
	ld b, a
	ld a, [w7Save + 1]
	ld c, a
	ld a, [w7Save + 2]
	ld d, a
	ld a, [w7Save + 3]
	ld h, a
	ld a, 2
	ldh [rSVBK_], a
	ld a, [w2Pal7Src]    ; マップが かわって 色が 読みなおされて いたら もどさない
	cp LOW(SIGN_C1)
	jr nz, .noRestore
	ld a, [w2Pal7Src + 1]
	cp HIGH(SIGN_C1)
	jr nz, .noRestore
	ld a, [w2Pal7Src + 2]
	cp LOW(SIGN_C2)
	jr nz, .noRestore
	ld a, [w2Pal7Src + 3]
	cp HIGH(SIGN_C2)
	jr nz, .noRestore
	ld a, b
	ld [w2Pal7Src], a
	ld [w2Pal7Cur], a
	ld a, c
	ld [w2Pal7Src + 1], a
	ld [w2Pal7Cur + 1], a
	ld a, d
	ld [w2Pal7Src + 2], a
	ld [w2Pal7Cur + 2], a
	ld a, h
	ld [w2Pal7Src + 3], a
	ld [w2Pal7Cur + 3], a
	ld a, 1
	ld [w2PalDirty], a
.noRestore
	ld a, e
	ldh [rSVBK_], a
.clear                   ; ここから 元の 「使わない OAM を 消す」 処理
	ei
	ldh a, [hOAMBufOfs]
	ld l, a
	ld h, $c3
	ld de, 4
	ld b, $a0
	ld a, [$d6b5]        ; wMovementFlags
	bit 6, a
	ld a, $a0
	jr z, .loop
	ld a, $90
.loop
	cp l
	ret z
	ld [hl], b
	add hl, de
	jr .loop

; クリスタルの 場所の 名前の 看板の 枠（pokecrystal gfx/frames/map_entry_sign.png の タイル1〜13）
SignFrameGfx:
	db $ff, $ff, $e0, $ff, $cf, $f0, $9f, $e0, $91, $ee, $97, $ee, $97, $ee, $9f, $e0 ; 1
	db $ff, $ff, $00, $ff, $aa, $55, $ff, $00, $ff, $00, $ff, $00, $ff, $00, $ff, $00 ; 2
	db $ff, $ff, $00, $ff, $ff, $00, $ff, $00, $ff, $00, $ff, $00, $ff, $00, $ff, $00 ; 3
	db $ff, $ff, $07, $ff, $f3, $0f, $f9, $07, $89, $77, $e9, $77, $e9, $77, $f9, $07 ; 4
	db $cf, $f0, $e1, $fe, $cf, $f0, $cf, $f0, $cf, $f0, $cf, $f0, $e0, $ff, $cf, $f0 ; 5
	db $9f, $e0, $9f, $e0, $9f, $e0, $9f, $e0, $cf, $f0, $e1, $fe, $cf, $f0, $9f, $e0 ; 6
	db $91, $ee, $97, $ee, $97, $ee, $8f, $f0, $80, $ff, $c0, $ff, $e0, $ff, $ff, $ff ; 7
	db $ff, $00, $ff, $00, $ff, $00, $ff, $00, $aa, $55, $00, $ff, $00, $ff, $ff, $ff ; 8
	db $ff, $00, $ff, $00, $ff, $00, $ff, $00, $00, $ff, $00, $ff, $aa, $ff, $ff, $ff ; 9
	db $89, $77, $e9, $77, $e9, $77, $f1, $0f, $81, $7f, $03, $ff, $07, $ff, $ff, $ff ; 10
	db $f3, $0f, $87, $7f, $f3, $0f, $f3, $0f, $f3, $0f, $f3, $0f, $07, $ff, $f3, $0f ; 11
	db $f9, $07, $f9, $07, $f9, $07, $f9, $07, $f3, $0f, $87, $7f, $f3, $0f, $f9, $07 ; 12
	db $ff, $00, $ff, $00, $ff, $00, $ff, $00, $ff, $00, $ff, $00, $ff, $00, $ff, $00 ; 13

; ３．相手の HUD の 枠の 線が HP の 数字で とぎれる 直し
;     相手の HUD を ５行に して、枠の 線を １行 下（４行め）へ うつす（自分側と 同じ 形）。
;       ２行め: │HP:バー
;       ３行め: │ のこり／最大     （(1,3) に たて線 $72、(2,3) と (10,3) は 空白）
;       ４行め: └────────◣  （$74 / $76×8 / $78）
SECTION "相手HUD の 枠", ROMX[$57e0], BANK[$37]
KitEnemyHUDFrame:
	ld hl, $c3a0 + 3 * 20 + 1   ; (1,3)
	ld a, $72                   ; (1,2) と 同じ たて線（CGB 用 タイル）
	ld [hli], a
	ld [hl], $7f                ; (2,3)
	ld hl, $c3a0 + 3 * 20 + 10  ; (10,3)
	ld [hl], $7f
	ld hl, $c3a0 + 4 * 20 + 1   ; (1,4)
	ld [hl], $74
	inc hl
	ld a, $76
	ld b, 8
.line
	ld [hli], a
	dec b
	jr nz, .line
	ld [hl], $78
	ret

; 相手の HUD を 消す 所を ５行に（４行めの 線が のこらないように）
SECTION "相手HUD 消す1", ROMX[$4610], BANK[$0f]
	db 5
SECTION "相手HUD 消す2", ROMX[$4b13], BANK[$0f]
	db 5
SECTION "相手HUD 消す3", ROMX[$4f54], BANK[$0f]
	db 5
SECTION "相手HUD 消す4", ROMX[$7310], BANK[$0f]
	db 5
SECTION "相手HUD 消す5", ROMX[$6341], BANK[$01]
	db 5

; 戦闘画面の 色の 割りあて（WRAM2 の 属性の 表 $d200）
;   相手の HUD（パレット3）を 0〜4行めに、自分の ポケモン（パレット0）を 5行め からに。
SECTION "戦闘の 属性 相手HUD 行数", ROMX[$702b], BANK[$1c]
	db 5
SECTION "戦闘の 属性 自分ポケモン", ROMX[$705a], BANK[$1c]
	ld hl, $d200 + 5 * 20
	ld a, $00
	ld b, 7
SECTION "戦闘の 属性 たて線 呼ぶ所", ROMX[$7031], BANK[$1c]
	call KitBattleAttrVLine
SECTION "戦闘の 属性 たて線", ROMX[$7c00], BANK[$1c]
KitBattleAttrVLine:
	call $78b7                  ; 元の 処理（(1,2) を $0b に する など）
	ld a, $0b                   ; (1,3) も (1,2) と 同じ（VRAMバンク1・パレット3）
	ld [$d200 + 3 * 20 + 1], a
	ret

; ５．ずかんの キット（タイプ・進化・種族値）
INCLUDE "dex_types.asm"

IF DEF(FOLLOW)
; ６．連れ歩き（全ポケモン）
INCLUDE "follow.asm"
ENDC

ENDC
