; 電話帳の再戦の印：銀 日本版（後期版）の値（アドレス・再戦の イベントの 番号は 金と 同じ。置き場所だけ ちがう）
DEF PM_HOOK            EQU $5283      ; バンク$24 PokegearPhone_UpdateDisplayList の call PokegearPhone_UpdateCursor
DEF PM_HOOK_BANK       EQU $24
DEF PM_UpdateCursor    EQU $5220
DEF PM_STUB            EQU $7fe8      ; バンク$24 の 空き（10バイト）
DEF PM_PlaceString     EQU $0f46
DEF PM_wPhoneList      EQU $d98c
DEF PM_wScroll         EQU $c5d2      ; wPokegearPhoneScrollPosition
DEF PM_wEventFlags     EQU $d7aa
DEF PM_ROW0            EQU $c3a0 + 4 * 20 + 18   ; hlcoord 18, 4（1行め の 印）
DEF PM_ROWS            EQU 4
DEF PM_BANK            EQU $48
DEF PM_ADDR            EQU $5c00
INCLUDE "src/phonemark.asm"
