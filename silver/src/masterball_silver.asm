; マスターボールを売る：銀 日本版（後期版）の値（src/masterball.asm より前に読みこむ）
; GetMart（22バイト）・Marts・店の数・MartIndigoPlateau（品ぞろえも 同じ）・EVENT_GOT_MASTER_BALL_FROM_ELM（$007c）は 金と同じ。
; ItemAttributes だけ ちがう（銀は $01:$6b58。金は $6b93）。
DEF MB_GETMART      EQU $5d9e
DEF MB_GETMART_BANK EQU $05
DEF MB_MARTS        EQU $65ea
DEF MB_NUM_MARTS    EQU $22
DEF MB_MART_INDIGO  EQU $6746
DEF MB_ITEMATTR     EQU $6b58
DEF MB_ITEMATTR_BANK EQU $01
DEF MB_EVENT_BYTE   EQU $d7aa + $7c / 8
DEF MB_EVENT_BIT    EQU $7c % 8
DEF MB_BANK         EQU $46      ; 銀：$43 は 再戦・とけい・ボールの絵。$46:$4000〜 は ボックスの自動切りかえ
DEF MB_ADDR         EQU $4200
DEF MB_MART_CELADON_3F EQU $670f   ; MartCeladon3F（わざマシンの 店。src/tmshop_silver.asm）。金と 同じ
INCLUDE "src/masterball.asm"
