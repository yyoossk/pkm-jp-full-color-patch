; 手持ちの道具の名前 … クリスタル（日本版）用の 値（本体は src/partyitem.asm）
; SpriteAnimFunc_PartyMon（$23:$52a2）の ld a, [wMenuCursorY]（fa 9d cf）。
; 手持ちの 画面は 金と 同じ（名前 x 3、やめる x 1。12・13行めの x 6〜18 は あいて いる）。
DEF PI_HOOK            EQU $52a2
DEF PI_HOOK_BANK       EQU $23
DEF PI_STUB            EQU $7fe0      ; バンク$23 の 空き（$7f10〜$7fde は 手持ちの 見た目）
DEF PI_GetItemName     EQU $3431
DEF PI_PlaceString     EQU $1057
DEF PI_w2DMenuCursorInitY EQU $cf95
DEF PI_w2DMenuCursorInitX EQU $cf96
DEF PI_w2DMenuNumCols  EQU $cf98
DEF PI_wMenuCursorY    EQU $cf9d
DEF PI_wPartyCount     EQU $dc9d
DEF PI_wPartySpecies   EQU $dc9e
DEF PI_wPartyMon1Item  EQU $dca6
DEF PI_MONLEN          EQU $30
DEF PI_EGG             EQU $fd
DEF PI_wNamedObjectIndex EQU $d296
DEF PI_wStringBuffer1  EQU $d05b
DEF PI_COORD           EQU $c4a0 + 13 * 20 + 6   ; hlcoord 6, 13
DEF wPILast            EQU $d832      ; wTimeOfDayPal の 前の 使われていない 2バイトの 1つめ（レポートに 書かれる）
DEF PI_MENU_HOOK       EQU $1d00      ; ROM0 LoadMenuHeader の call CopyMenuHeader（クリスタルでは 使わない）
DEF PI_CopyMenuHeader  EQU $1d07      ; CopyMenuHeader（ld de, wMenuHeader / ld bc, $10 / call CopyBytes …）
DEF PI_wMenuHeader     EQU $cf75      ; これを 決めると CopyMenuHeader の 頭を つなぐ（戦闘の 手持ちの メニューも けせる）
DEF PI_ROM0_FREE       EQU $2d15      ; ROM0 の 空き（DummyEndPredef。どこからも 呼ばれない nop 16こ と ret。$2d25 の ret は のこす）
DEF PI_BANK            EQU $76
DEF PI_ADDR            EQU $7400      ; （メニューの 前に けす 処理を 足して $100 を こえたので $7000 から うつした）
DEF PI_TEXT_HOOK       EQU $44c1      ; バンク$14 PlacePartyMenuText の おわり（f1 ea c0 cf c9）
DEF PI_TEXT_BANK       EQU $14
DEF PI_TEXT_STUB       EQU $7a00      ; バンク$14 の 空き（$79d0〜$79e0 は バグ修正）
DEF PI_wOptions        EQU $cfc0

INCLUDE "src/partyitem.asm"
