; カントー・ジョウトの ジムリーダー 再戦（金 日本版）
INCLUDE "src/charmap_jp.inc"
INCLUDE "src/rematch_gold.inc"       ; tools/rematch_find.py で作ったもの（初版・後期版で同じ）
INCLUDE "src/rematch_parties.inc"
DEF RM_JOHTO EQU 1                   ; ジョウトの ジムリーダーも 再戦（rematch.asm の いちばん 下）
INCLUDE "src/rematch_johto_gold.inc"
INCLUDE "src/rematch_johto_parties.inc"
DEF RMJ_SCRIPT_ADDR EQU $4800        ; ジョウトの スクリプト・セリフ（RM_SCRIPT_BANK）
DEF RMJ_PARTY_ADDR EQU $5400         ; ジョウトの 再戦用の 手持ち（RM_SCRIPT_BANK）
DEF BASEROM EQUS "\"base.gbc\""
DEF RM_PARTY_FAR EQU 1               ; トレーナーのバンク（$0e）に空きが 40バイトほどしかないので、
                                     ; 再戦用の手持ちは 新しいバンクから読む（rematch.asm の 2 を見る）
DEF RM_SCRIPT_BANK EQU $42           ; 新しいバンク（2MB にした所。$40・$41 は手持ちのアイコンの絵）
DEF RM_SCRIPT_ADDR EQU $4000
DEF RM_PARTY_FAR_ADDR EQU $5000     ; 再戦用の手持ちと 読む処理（同じバンク）
DEF RM_PARTY_HOOK_FREE EQU $7fe0     ; バンク$0e の空き（バグ修正が $7fc8〜$7fd9 を使っている）
DEF RM_BANK0_FREE  EQU $00f6         ; ROM0 の空き（$00f6〜$00ff。$0068〜$00f5 はほかの機能）
; 16この バッジの あとの 四天王・ワタル・ライバル（src/league.asm。クリスタル追加機能キットの 51）
DEF RM_LEAGUE EQU 1
DEF LG_wJohtoBadges    EQU $d56f
DEF LG_wKantoBadges    EQU $d570
DEF LG_wOtherTrainerID EQU $d10d     ; 金は wOtherTrainerClass $d10a ＋ 3（wBattleType の あとに 1バイト ある）
DEF LG_PARTY_ADDR      EQU $5c00     ; RM_SCRIPT_BANK（$5b69〜$5fff が 空き）
INCLUDE "src/rematch.asm"
INCLUDE "src/league.asm"
