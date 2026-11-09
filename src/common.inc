; 全版共通の決まりごと
; 全版で空いているバンク: $24 $25 $35 $36 $37 $38 $39 $3A $3B $3C $3D
DEF FREE_BANK_A EQU $24
DEF FREE_BANK_B EQU $25

; 版を見分ける記号: ED_FULL / ED_COLOR / ED_ALL151, GFX_KIN / GFX_SHO, FPS60

; ハードと、全版で同じ場所
DEF rSVBK EQU $FF70
DEF hWY EQU $FFB0
DEF hOAMBufferOffset EQU $FF90
DEF wShadowOAM EQU $C300
DEF wPlayerHPBarColor EQU $CF17
DEF wEnemyHPBarColor EQU $CF18
DEF wMovementFlags EQU $D6B5      ; bit 6: 段差・つりのとき OAM の最後の4つを消さない
DEF wPlaceSignTimer EQU $D6A5     ; 場所の名前の看板ののこり時間（キット）
DEF PLACE_SIGN_WY EQU $70         ; 看板を出しているときのウインドウの位置

; 戦闘 HUD のキット処理（バンク $13）
DEF KitPlayerHUDNumbers EQU $5506
DEF KitEnemyHUDNumbers EQU $4800
DEF KIT_BANK EQU $13

; 空いているバンクに置く処理は、SECTION の代わりに「FreeBankA」と書く。
; 改良のファイルは1つずつ別にアセンブルされ、リンクのときに順につながって置かれる。
MACRO FreeBankA
	SECTION FRAGMENT "空きバンクA", ROMX, BANK[FREE_BANK_A]
ENDM

; 画面のタイルの表（20x18）
DEF wTileMap EQU $C3A0
MACRO coord ; coord 名前, x, y
	DEF \1 EQU wTileMap + (\3) * 20 + (\2)
ENDM
; 戦闘画面の BG 属性の表（カラー化、WRAM バンク 2、20x18）
DEF W2_BattleAttrMap EQU $D200
DEF KitBattleAttrHook EQU $54FA   ; 戦闘の属性の表のあとによぶキット（バンク $13）
; ほかのファイルからよぶ処理のラベルは「::」で書く

; バンク $13（キットのバンク）の空き $7800〜。キットの処理を直接 call したいときに使う
MACRO FreeBank13
	SECTION FRAGMENT "空きバンク13", ROMX, BANK[$13]
ENDM

; よく使う形
DEF SCREEN_WIDTH EQU 20
MACRO hlcoord ; hlcoord x, y
	ld hl, wTileMap + (\2) * SCREEN_WIDTH + (\1)
ENDM
MACRO ldcoord_a ; ldcoord_a x, y
	ld [wTileMap + (\2) * SCREEN_WIDTH + (\1)], a
ENDM
MACRO lb ; lb r16, hi, lo
	ld \1, LOW(\2) << 8 | LOW(\3)
ENDM
MACRO predef ; predef 番号（Predef は版ごと）
	ld a, \1
	call Predef
ENDM

; バンク0 の処理（どの版も同じ番地のもの）
DEF ClearScreenArea EQU $1902
DEF FarCopyData EQU $174C     ; a = バンク、hl → de に bc バイト（$CEE4 をこわす）
DEF hJoy5 EQU $FFB5
DEF PAD_A EQU 1
DEF PAD_B EQU 2
DEF B_PAD_B EQU 1
DEF LEFT_ALIGN EQU 1 << 6

; WRAM（どの版も同じ）
DEF wCurSpecies EQU $D092
DEF wMonHeader EQU $D095
DEF wMonHBaseHP EQU wMonHeader + 1
DEF wMonHBaseAttack EQU wMonHeader + 2
DEF wMonHBaseDefense EQU wMonHeader + 3
DEF wMonHBaseSpeed EQU wMonHeader + 4
DEF wMonHBaseSpecial EQU wMonHeader + 5
DEF wNamedObjectIndex EQU $D0E3   ; wPokedexNum と同じ所
DEF wNameBuffer EQU $CD68

; ROM のデータ
DEF EvosMovesPointerTable EQU $715F   ; バンク $0E
DEF BANK_EvosMovesPointerTable EQU $0E
DEF EVOLVE_LEVEL EQU 1
DEF EVOLVE_ITEM EQU 2
DEF EVOLVE_TRADE EQU 3

; predef の番号
DEF PRINT_MON_TYPE EQU $4B
MACRO next ; 文字列の次の行
	db "<NEXT>", \#
ENDM
DEF PlaceString EQU $1993
