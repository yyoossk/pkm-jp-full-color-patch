; セレビィと伝説の鳥：銀 日本版（後期版）の値（ウバメの ほこら・3つの マップの 場所・人の 数・空きは 銀の バイトで 確かめて 金と 同じ。置き場所だけ ちがう）
DEF LG_BANK            EQU $49        ; 新しい バンク（写す 所 $44b2・$45ad・$6ecf と 本体 $6000）
DEF LG_ADDR            EQU $6000
DEF LG_wEventFlags     EQU $d7aa
DEF LG_EVENT_BEAT_E4   EQU $0044      ; EVENT_BEAT_ELITE_FOUR（日本版の 番号）
DEF wLegendFlags       EQU $d7a1      ; wEventFlags の 前の 空き（レポートに 書かれる。$d7a0 は ガンテツ）
DEF LG_wScriptVar      EQU $d165
DEF LG_wMapObjects     EQU $d438      ; 16バイトずつ（日本版は 1人めが 2番）
; ウバメのもり
DEF LG_ILEX_BANK       EQU $28
DEF LG_ILEX_SHRINE_PTR EQU $60d3      ; ほこらの bg_event の スクリプトの 場所（dw）
DEF LG_ILEX_FREE       EQU $7ffb      ; バンク$28 の 空き（4バイト 使う）
DEF LG_ILEX_SHRINE_TEXT EQU $608d     ; 元の ほこらの 文（バンク$28）
; うずまきじま 地下2階（WHIRL_ISLAND_B2F）
DEF LG_WI_ATTR         EQU $5ae9
DEF LG_WI_SRC_BANK     EQU $2d
DEF LG_WI_START        EQU $44b2      ; MapScripts（scene 0・callback 0）
DEF LG_WI_EVENTS       EQU $44ba
DEF LG_WI_END          EQU $44fb
DEF LG_WI_SLOT         EQU 5          ; 人（どうぐ）3つ の つぎ
; イワヤマトンネル 地下1階（ROCK_TUNNEL_B1F）
DEF LG_RT_ATTR         EQU $5c51
DEF LG_RT_SRC_BANK     EQU $2f
DEF LG_RT_START        EQU $6ecf      ; MapScripts（scene 0・callback 0）
DEF LG_RT_EVENTS       EQU $6eda
DEF LG_RT_END          EQU $6f20
DEF LG_RT_SLOT         EQU 5
; シロガネやま 2（SILVER_CAVE_ROOM_2）
DEF LG_SC_ATTR         EQU $5b0d
DEF LG_SC_SRC_BANK     EQU $2d
DEF LG_SC_START        EQU $45ad
DEF LG_SC_EVENTS       EQU $45b2
DEF LG_SC_END          EQU $45d1
DEF LG_SC_SLOT         EQU 2
DEF LG_ATTR_BANK       EQU $25
DEF LG_AddSpriteGFX    EQU $41c7      ; バンク$05（and a / ret z / ld c, a の つぎから 呼ぶ：c = 絵）
DEF LG_LoadUsedSpritesGFX EQU $41f8
DEF LG_SPRITE_BANK     EQU $05
INCLUDE "src/legends.asm"
