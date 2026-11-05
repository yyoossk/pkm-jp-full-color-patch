; ルギア・ホウオウの 専用わざ（src/sigmove.asm）を 金 日本版に 入れる
; ・金の バンク$10 は 空きが 6バイトしか ないので、元の ルギア・ホウオウ・セレビィ の表（$7fba〜、つづいて 3つ。
;   うしろに 空き 6バイト）を 書きなおす：新しい ルギア（24）・ホウオウ（24）を $7fba〜 に置き、
;   セレビィの表（20バイト、中身は そのまま）を $7fea に ずらして、セレビィ（251番）の ポインタも かえる。
; ・出てくるレベル：金は うずまきじまの ルギアが 70（checkver の 金の側）→ 40。スズのとうの ホウオウは もともと 40。
DEF SIG_BANK            EQU $10
DEF SIG_PTR_LUGIA       EQU $6b4f
DEF SIG_PTR_HOOH        EQU $6b51
DEF SIG_FREE            EQU $7fba    ; 元の ルギアの表の所（ここから 48バイト）
DEF SIG_LUGIA_WILD_BANK EQU $2d      ; loadwildmon LUGIA, 70（金の側）
DEF SIG_LUGIA_WILD      EQU $452b
DEF SIG_HOOH_WILD_BANK  EQU $29      ; loadwildmon HO_OH, 40（金の側。40 のまま）
DEF SIG_HOOH_WILD       EQU $6e47
INCLUDE "src/sigmove.asm"

SECTION "sigmove celebi ptr", ROMX[SIG_PTR_HOOH + 2], BANK[SIG_BANK]
	dw SigMove_CelebiEvosAttacks
SECTION "sigmove celebi", ROMX[SIG_FREE + 48], BANK[SIG_BANK]
SigMove_CelebiEvosAttacks:           ; 金 日本版の セレビィの表（そのまま）
	db $00, $01, $49, $01, $5d, $01, $69, $01, $d7, $0a, $db, $14, $f6, $1e, $f8, $28, $e2, $32, $c3, $00
