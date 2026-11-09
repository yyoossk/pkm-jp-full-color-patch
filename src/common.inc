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
