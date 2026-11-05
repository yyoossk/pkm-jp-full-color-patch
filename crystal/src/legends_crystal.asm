; セレビィと伝説の鳥 … クリスタル（日本版）用の 値（本体は src/legends.asm）
; マップは MapGroupPointers（$25:$4000）→ ヘッダ → MapAttributes を たどって 調べた
INCLUDE "src/safari/crystal_includes.asm"   ; pokecrystal の 定数・マクロ（スクリプトの 命令の 番号は 英語版 金銀）
DEF LG_NO_INCLUDES EQU 1

DEF LG_BANK            EQU $77        ; 新しい バンク（あいている）
DEF LG_ADDR            EQU $6000
DEF LG_wEventFlags     EQU $da65
DEF LG_EVENT_BEAT_E4   EQU $0044      ; EVENT_BEAT_ELITE_FOUR（ProfElmScript $1b:$61f7 の checkevent）
DEF wLegendFlags       EQU $d836      ; wTimeOfDayPal（$d834）の あとの 使われていない 4バイト（レポートに 書かれる）の 2つめ
DEF LG_wScriptVar      EQU $c2dd
DEF LG_wMapObjects     EQU $d711      ; 16バイトずつ（0 は 主人公、1人めが 1番）
DEF LG_wObjectMasks    EQU $d811      ; wMapObjects の あと。1バイトずつ（-1 で かくす）
DEF LG_DISAPPEAR_OFS   EQU 1          ; 日本版の disappear は 番号 − 1 の 人（GetScriptObject $25:$71e1 の dec a）
; ウバメのもり（3-52。スクリプト バンク$19、イベント $64a3）
DEF LG_ILEX_BANK       EQU $19
DEF LG_ILEX_SHRINE_PTR EQU $64ce      ; ほこらの bg_event（5つめ。8, 22）の スクリプトの 場所（dw）
DEF LG_ILEX_FREE       EQU $7ff8      ; バンク$19 の 空き（4バイト 使う）
DEF LG_ILEX_SHRINE_TEXT EQU $6369     ; 元の ほこらの 文（Text_IlexForestShrine。27バイト）
DEF LG_ILEX_ORIG_SCRIPT EQU $6022     ; 元の ほこらの スクリプト（IlexForestShrineScript）
DEF LG_EVENT_FOREST_IS_RESTLESS EQU $00c0
; うずまきじま 地下2階（3-72）
DEF LG_WI_ATTR         EQU $5b10
DEF LG_WI_SRC_BANK     EQU $1c
DEF LG_WI_START        EQU $4a5f      ; MapScripts（scene 0・callback 0）
DEF LG_WI_EVENTS       EQU $4a67
DEF LG_WI_END          EQU $4aa8
DEF LG_WI_SLOT         EQU 4          ; どうぐ 3つ の つぎ
; イワヤマトンネル 地下1階（3-88）
DEF LG_RT_ATTR         EQU $5c84
DEF LG_RT_SRC_BANK     EQU $1f
DEF LG_RT_START        EQU $6e75
DEF LG_RT_EVENTS       EQU $6e80
DEF LG_RT_END          EQU $6ec6
DEF LG_RT_SLOT         EQU 4
; シロガネやま 2（3-75）
DEF LG_SC_ATTR         EQU $5b34
DEF LG_SC_SRC_BANK     EQU $1c
DEF LG_SC_START        EQU $4b5a
DEF LG_SC_EVENTS       EQU $4b65
DEF LG_SC_END          EQU $4bab
DEF LG_SC_SLOT         EQU 4
DEF LG_ATTR_BANK       EQU $25
DEF LG_RefreshSprites  EQU $4159      ; バンク$05（クリスタルの AddSpriteGFX は 作りが ちがうので こちらを 使う）
DEF LG_SPRITE_BANK     EQU $05

INCLUDE "src/legends.asm"
