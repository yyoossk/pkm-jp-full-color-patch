; 手持ちの道具の名前：銀 日本版（後期版）の値（アドレスは 金と 同じ。LoadMenuHeader $1b59・ROM0 の 空き DummyEndPredef $2dd2 も 同じ。置き場所だけ ちがう）
DEF PI_HOOK            EQU $52ed      ; バンク$23 AnimSeq_PartyMon の ld a, [wMenuCursorY]
DEF PI_HOOK_BANK       EQU $23
DEF PI_STUB            EQU $7f80      ; バンク$23 の 空き
DEF PI_GetItemName     EQU $360a
DEF PI_PlaceString     EQU $0f46
DEF PI_w2DMenuCursorInitY EQU $cf0c
DEF PI_w2DMenuCursorInitX EQU $cf0d
DEF PI_w2DMenuNumCols  EQU $cf0f
DEF PI_wMenuCursorY    EQU $cf14
DEF PI_wPartyCount     EQU $d9e8
DEF PI_wPartySpecies   EQU $d9e9
DEF PI_wPartyMon1Item  EQU $d9f1
DEF PI_MONLEN          EQU $30
DEF PI_EGG             EQU $fd
DEF PI_wNamedObjectIndex EQU $d143
DEF PI_wStringBuffer1  EQU $cf87
DEF PI_COORD           EQU $c3a0 + 13 * 20 + 6   ; hlcoord 6, 13
DEF wPILast            EQU $d7a2
DEF PI_MENU_HOOK       EQU $1b59      ; ROM0 LoadMenuHeader の call CopyMenuHeader
DEF PI_CopyMenuHeader  EQU $1b60
DEF PI_ROM0_FREE       EQU $2dd2      ; ROM0 の 空き（DummyEndPredef。どこからも 呼ばれない nop 16こ）
DEF PI_TEXT_HOOK       EQU $4436      ; バンク$14 PlacePartyMenuText の おわり（cd 46 0f の あとの f1 ea ab d1 c9）
DEF PI_TEXT_BANK       EQU $14
DEF PI_TEXT_STUB_ROM0  EQU $3a93      ; ROM0 GetDexNumber（どこからも 呼ばれない。バンク$14 には 空きが ない）
DEF PI_wOptions        EQU $d1ab
DEF PI_BANK            EQU $48
DEF PI_ADDR            EQU $7300
INCLUDE "src/partyitem.asm"
