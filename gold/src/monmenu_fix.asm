; 手持ちの メニューが 2列の とき、カーソルが 何も ない 所に 行かない ように する（5 の 直し。金 日本版）
;
; ・手持ちの ポケモンを えらんだ ときの メニュー（いあいぎり・つよさをみる…）が 9こ 以上で 2列に なり、
;   数が 奇数の ときは、いちばん 下の 行の 右が 空いて いる。元は そこに カーソルが 行けて（A を おしても 何も おきない）、
;   何も ない 所に ▶ が 出て いた。そこに 行こうと したら 同じ 行の 左（もどる）に する。
;
; しくみ
;   ・2DMenu の ループ の「call _2DMenuInterpretJoypad」（バンク$09 $4166）を バンク$09 の 空き（$7fd9）の MonMenuFix_Stub に。
;     ボタンを 読んだ あと、2列の 手持ちの メニュー（w2DMenuNumCols 2・w2DMenuCursorOffsets $27・wMonSubmenuCount が 奇数）で
;     カーソルが いちばん 下の 行の 右なら 左に もどす（▶ は つぎの ループで その 場所に かかれる）。
;
; 銀に 入れるとき：下の DEF を 銀の 値に する（5 は 金銀だけ）

IF !DEF(MF_HOOK)
DEF MF_HOOK            EQU $4166      ; バンク$09 の call _2DMenuInterpretJoypad
DEF MF_BANK9           EQU $09
DEF MF_Interpret       EQU $419c      ; _2DMenuInterpretJoypad
DEF MF_STUB            EQU $7fd9      ; バンク$09 の 空き（12バイト）
DEF MF_w2DMenuNumRows  EQU $cf0e
DEF MF_w2DMenuNumCols  EQU $cf0f
DEF MF_w2DMenuCursorOffsets EQU $cf12
DEF MF_wMenuCursorY    EQU $cf14
DEF MF_wMenuCursorX    EQU $cf15
DEF MF_wMonSubmenuCount EQU $d0c5
DEF MF_BANK            EQU $45
DEF MF_ADDR            EQU $7b00
ENDC

SECTION "monmenufix hook", ROMX[MF_HOOK], BANK[MF_BANK9]
	call MonMenuFix_Stub
SECTION "monmenufix stub", ROMX[MF_STUB], BANK[MF_BANK9]
MonMenuFix_Stub:
	call MF_Interpret
	push af
	ld a, BANK(MonMenuFix)
	ld hl, MonMenuFix
	rst $08
	pop af
	ret

SECTION "monmenufix", ROMX[MF_ADDR], BANK[MF_BANK]
MonMenuFix:
	ld a, [MF_w2DMenuNumCols]
	cp 2
	ret nz
	ld a, [MF_w2DMenuCursorOffsets]
	cp $27                            ; 手持ちの メニューの 2列（$20 | 7）
	ret nz
	ld a, [MF_wMonSubmenuCount]
	bit 0, a
	ret z                             ; 偶数なら 空きは ない
	ld a, [MF_wMenuCursorX]
	cp 2
	ret nz
	ld a, [MF_w2DMenuNumRows]
	ld l, a
	ld a, [MF_wMenuCursorY]
	cp l
	ret nz
	ld a, 1
	ld [MF_wMenuCursorX], a
	ret
