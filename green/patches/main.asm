; これからの 直しや 追加は ここに 書く（今は 空 ＝ Ver.1.8.0 と 同じ ROM）。
; ・SECTION で バンクと 番地を 決めて 書くと、その 所だけ 土台の ROM の 上に かさなる。
;     SECTION "あたらしい 処理", ROMX[$7158], BANK[$09]   ; 空きは ../空きバンク.txt
;     SECTION "呼ぶ 所", ROMX[$4d02], BANK[$09]            ; 元の 命令を かえる 所
; ・版ごとに 番地が ちがう ときは、INCLUDE EDITION_INC で patches/editions/<版>.inc の 名前を 使う。
;   版の 番号は ED_0〜ED_11（tools/build.py の EDITIONS の じゅん）で、IF DEF(ED_4) などで 分けられる。
; ・処理の 名前と 番地は ../disasm/ の 逆アセンブル（と ../disasm/include/home_names.inc）を 見る。

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
DEF wKitSignTimer  EQU $d6a4
DEF KIT_SIGN_WY    EQU $70

SECTION "OAM 消す所 呼ぶ所", ROMX[$45c9], BANK[$01]
	ld hl, KitOAMSignHide
	ld b, $37
	jp $3500              ; Bankswitch（もどると VBlank へ 帰る）

SECTION "看板の 行の スプライトを かくす", ROMX[$5790], BANK[$37]
KitOAMSignHide:
	ldh a, [hWY_ADDR]
	cp KIT_SIGN_WY
	jr nz, .clear
	ld a, [wKitSignTimer]
	and a
	jr z, .clear
	ldh a, [hOAMBufOfs]
	ld c, a               ; c = 使っている OAM の おわり
	ld hl, $c300          ; wShadowOAM
	ld de, 4
.hide
	ld a, l
	cp c
	jr nc, .clear
	ld a, [hl]
	cp KIT_SIGN_WY + 16 - 7
	jr c, .next
	ld [hl], $a0          ; 画面の 外へ
.next
	add hl, de
	jr .hide
.clear                    ; ここから 元の 「使わない OAM を 消す」 処理
	ldh a, [hOAMBufOfs]
	ld l, a
	ld h, $c3
	ld de, 4
	ld b, $a0
	ld a, [$d6b5]         ; wMovementFlags
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

ENDC
