; カントーのジムリーダー 再戦（クリスタル日本版）
INCLUDE "src/charmap_jp.inc"
INCLUDE "src/rematch_crystal.inc"     ; tools/rematch_find.py で作ったもの
INCLUDE "src/rematch_parties.inc"
DEF RM_JOHTO EQU 1                   ; ジョウトの ジムリーダーも 再戦（rematch.asm の いちばん 下）
INCLUDE "src/rematch_johto_crystal.inc"
INCLUDE "src/rematch_johto_parties.inc"
DEF RMJ_SCRIPT_ADDR EQU $7400        ; ジョウトの スクリプト・セリフ（RM_SCRIPT_BANK。$7000〜 は テスト用）
DEF RMJ_PARTY_ADDR EQU $6800         ; ジョウトの 再戦用の 手持ち（RM_SCRIPT_BANK）
DEF BASEROM EQUS "\"base.gbc\""
DEF RM_SCRIPT_BANK EQU $70           ; 新しいバンク（なまえ・わすれる と同じ）
DEF RM_SCRIPT_ADDR EQU $5000
DEF RM_PARTY_FAR EQU 1               ; トレーナーのバンク（$0e）には 空きが あるが、ジョウトの グループを 足す 作りが
                                     ; まだ ないので、再戦用の手持ちは 新しいバンクから読む（rematch.asm の 2 を見る）
DEF RM_PARTY_FAR_ADDR EQU $6100      ; 再戦用の手持ちと 読む処理（同じバンク。$5000〜$603b は カントーの スクリプト）
DEF RM_PARTY_HOOK_FREE EQU $7710     ; バンク$0e の空き（23バイト）
DEF RM_BANK0_FREE  EQU $3fe0         ; 60fps版の VBlank の処理（$3f90〜）のあと
; 16この バッジの あとの 四天王・ワタル・ライバル（src/league.asm）
DEF RM_LEAGUE EQU 1
DEF LG_wJohtoBadges    EQU $d84a
DEF LG_wKantoBadges    EQU $d84b
DEF LG_wOtherTrainerID EQU $d262     ; wOtherTrainerClass $d260 ＋ 2
DEF LG_PARTY_ADDR      EQU $6a00     ; RM_SCRIPT_BANK（$6958〜$73ff が 空き）
INCLUDE "src/rematch.asm"
INCLUDE "src/league.asm"
