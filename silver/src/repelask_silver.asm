; むしよけをもう一度つかう：銀 日本版（後期版）の値。DoRepelStep・UseRepel・文の 場所は 金と同じ（銀の シンボルで 確かめた）
DEF RA_HOOK            EQU $6b14   ; DoRepelStep の ld a, BANK(RepelWoreOffScript)（5バイト）
DEF RA_HOOK_BANK       EQU $25
DEF RA_WOREOFF_TEXT    EQU $7a79   ; RepelWoreOffScript の 文（RepelWoreOffText）
DEF RA_WOREOFF_BANK    EQU $04
DEF RA_USEREPEL        EQU $787c   ; UseRepel（ld a, [wRepelEffect] から 17バイト）
DEF RA_USEREPEL_BANK   EQU $03
DEF RA_STILL_TEXT      EQU $788d   ; RepelUsedEarlierIsStillInEffectText
DEF RA_USEITEMTEXT     EQU $7c49   ; UseItemText（バンク$03）
DEF RA_PrintText       EQU $0f30
DEF RA_CheckItem       EQU $304b
DEF RA_TossItem        EQU $3025
DEF RA_wRepelEffect    EQU $d9b1
DEF RA_wCurItem        EQU $cffc
DEF RA_wNumItems       EQU $d5aa
DEF RA_wItemQuantityChange EQU $d003
DEF RA_wScriptVar      EQU $d165
DEF RA_wStringBuffer3  EQU $cf9d
DEF wRepelAskLast      EQU $deeb   ; 使われていない WRAM（銀：$dee8 とけい、$dee9・$deea ボックスの自動切りかえ）：さいごに つかった むしよけ
DEF wRepelAskItem      EQU $deec   ; 〃 きいている むしよけ（yesorno で wScriptVar が かわるため）
DEF RA_BANK            EQU $47      ; 銀の 新しい バンク
DEF RA_ADDR            EQU $4000
INCLUDE "src/repelask.asm"
