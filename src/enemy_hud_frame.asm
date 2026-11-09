; 相手の HP バーの枠の線が、HP の数字で途切れる不具合を直す
;
; 元の相手の HUD は4行（0:濁点 1:名前 2:│HP:バー 3:└──◣）で、キットの HP の数字を
; 3行めの (3,3)〜(9,3) に書いていたため、枠の線の上に数字がのっていた。
; 自分側と同じ形にするため、相手の HUD を5行にして、枠の線を4行めにうつす。
;   2行め: │HP:バー        （そのまま）
;   3行め: │ 37/ 37        （(1,3) にたて線、(2,3) と (10,3) は空白）
;   4行め: └────────◣  （(1,4) 角 $74、(2,4)〜(9,4) 横線 $76、(10,4) 端 $78）
; (1) 数字を出したあと（src/hpbar_color_fix.asm の KeepDE_EnemyHUD）で 3・4行めを書く
; (2) 相手の HUD を消す4か所を5行にする
; (3) 戦闘画面の属性の表で、(1,3) をたて線と同じ $0B、(1,4)〜(10,4) を HUD の枠と同じ $03 にする

IF HAS_KIT_HUD

	coord EnemyHUD_VLine3, 1, 3
	coord EnemyHUD_Gap3, 2, 3
	coord EnemyHUD_End3, 10, 3
	coord EnemyHUD_Bottom, 1, 4

DEF HUD_VLINE_TILE EQU $72   ; (1,2) と同じたて線（VRAM バンク1 のタイル）
DEF HUD_BLANK_TILE EQU $7F
DEF HUD_CORNER_TILE EQU $74
DEF HUD_HLINE_TILE EQU $76
DEF HUD_END_TILE EQU $78
DEF HUD_VLINE_ATTR EQU $0B   ; (1,2) の属性（VRAM バンク1・パレット3）
DEF HUD_FRAME_ATTR EQU $03   ; HUD の枠の属性（パレット3）

FreeBankA
EnemyHUDFrameFiveRows::
	ld a, HUD_VLINE_TILE
	ld [EnemyHUD_VLine3], a
	ld a, HUD_BLANK_TILE
	ld [EnemyHUD_Gap3], a
	ld [EnemyHUD_End3], a
	ld hl, EnemyHUD_Bottom
	ld a, HUD_CORNER_TILE
	ld [hli], a
	ld a, HUD_HLINE_TILE
	ld c, 8
.line
	ld [hli], a
	dec c
	jr nz, .line
	ld [hl], HUD_END_TILE
	ret

; 戦闘画面の属性の表を作る処理（バンク $1C）の最後で、キットの処理をよぶ所を
; ここに飛ばし、キットの処理のあとで 3・4行めの属性を合わせる。
SECTION "相手HUD 属性の表の呼び出し", ROMX[$6B19], BANK[$1C]
	ld b, BANK(EnemyHUDAttrFiveRows)
	ld hl, EnemyHUDAttrFiveRows
	call Bankswitch

FreeBankA
EnemyHUDAttrFiveRows:
	ld hl, KitBattleAttrHook
	ld b, KIT_BANK
	call Bankswitch            ; 元の処理（WRAM はバンク2 のままもどる）
	ld a, HUD_VLINE_ATTR
	ld [W2_BattleAttrMap + 3 * 20 + 1], a
	ld hl, W2_BattleAttrMap + 4 * 20 + 1
	ld a, HUD_FRAME_ATTR
	ld c, 10
.attr
	ld [hli], a
	dec c
	jr nz, .attr
	ret

; 相手の HUD を消す所（hlcoord 1, 0 / lb bc, 4, xx / call ClearScreenArea）を5行に
SECTION "相手HUD 消す1", ROMX[$460C + 5], BANK[$0F]
	db 5
SECTION "相手HUD 消す2", ROMX[$4B0E + 5], BANK[$0F]
	db 5
SECTION "相手HUD 消す3", ROMX[$4F4E + 5], BANK[$0F]
	db 5
SECTION "相手HUD 消す4", ROMX[$7309 + 5], BANK[$0F]
	db 5

ENDC
