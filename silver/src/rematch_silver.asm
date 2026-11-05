; カントー・ジョウトの ジムリーダー 再戦（日本版 銀）
INCLUDE "src/charmap_jp.inc"
INCLUDE "src/rematch_silver.inc"      ; tools/rematch_find.py で作ったもの
INCLUDE "src/rematch_parties.inc"
DEF RM_JOHTO EQU 1                    ; ジョウトの ジムリーダーも 再戦（rematch.asm の いちばん 下）
INCLUDE "src/rematch_johto_silver.inc"
INCLUDE "src/rematch_johto_parties.inc"
DEF BASEROM EQUS "\"base.gbc\""
DEF RM_PARTY_FAR EQU 1               ; トレーナーのバンク（$0e）に空きが 少ないので、再戦用の手持ちは 新しいバンクから読む
DEF RM_SCRIPT_BANK EQU $43           ; 新しいバンク（ROM を 2MB にしたので空いている。$40〜$42 は手持ちの見た目）
DEF RM_SCRIPT_ADDR EQU $4000         ; カントーの スクリプト・セリフ
DEF RM_PARTY_FAR_ADDR EQU $4800      ; 再戦用の手持ちと 読む処理（$5000〜$515c は せっていの とけい）
DEF RMJ_SCRIPT_ADDR EQU $5200        ; ジョウトの スクリプト・セリフ
DEF RMJ_PARTY_ADDR EQU $5a00         ; ジョウトの 再戦用の 手持ち（$6000〜 は ボールの 絵）
DEF RM_PARTY_HOOK_FREE EQU $7fe0     ; バンク$0e の空き（バグ修正が $7fc8〜$7fd9 を使っている）
DEF RM_BANK0_FREE  EQU $3f8a         ; ROM0 の空き（$3f8a〜$3f9f。$3fe0〜 は ずかんとパソコンの絵の色の入口）
INCLUDE "src/rematch.asm"
