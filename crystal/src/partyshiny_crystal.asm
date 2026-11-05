; 手持ちの色ちがいの星 … クリスタル（日本版）用の 値（本体は src/partyshiny.asm）
; PlacePartyNicknames（$14:$409b）は 金と 同じ 形（名前 hlcoord 3, 1 から 2行 ごと、さいごに「やめる」）。
; 「：Ｌ」は x 8 なので ★は 金と 同じ hlcoord 8, 0（2行 ごと）。
; タイル $5e：戦闘では けいけんちの バー（$55〜$5d）の つぎで 使われて いない（3ぴきの 戦闘の 画面で 確かめた）。
DEF PS_HOOK            EQU $40c1      ; .end の ld de, .CancelString / call PlaceString / ret
DEF PS_HOOK_BANK       EQU $14
DEF PS_PlaceString     EQU $1057
DEF PS_wPartyCount     EQU $dc9d
DEF PS_wPartySpecies   EQU $dc9e
DEF PS_wPartyMon1DVs   EQU $dcba      ; wPartyMon1（$dca5）＋ $15
DEF PS_MONLEN          EQU $30
DEF PS_EGG             EQU $fd
DEF PS_TILE            EQU $5e
DEF PS_VRAM            EQU $9000 + PS_TILE * 16
DEF PS_COORD           EQU $c4a0 + 8      ; hlcoord 8, 0
DEF PS_BANK            EQU $76
DEF PS_ADDR            EQU $6c00

DEF PS_FOLLOW_MARK EQU 1               ; 連れ歩きの ★も かく（follow_crystal.asm の Fw_PartyMark）
INCLUDE "src/partyshiny.asm"
