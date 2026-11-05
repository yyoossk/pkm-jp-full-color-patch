; ルギア・ホウオウの専用わざ：銀 日本版（後期版）の値（tools/sigmove_find.py で パッチを入れる前の ROM から調べた値）
; src/sigmove_silver.asm から src/sigmove.asm より前に読みこむ
DEF SIG_BANK           EQU $10
DEF SIG_PTR_LUGIA      EQU $6b4f   ; EvosAttacksPointers の ルギア（249番）
DEF SIG_PTR_HOOH       EQU $6b51   ; ホウオウ（250番）
; バンク$10 は おわりに 6バイトしか空きがない。元の ルギア（$7fba・22バイト）・ホウオウ（$7fd0・22バイト）・
; セレビィ（$7fe6・20バイト）の表と おわりの空き（$7ffa〜$7fff）は つながっているので（$7fba〜$7fff の 70バイト）、
; ルギア・ホウオウの新しい表（24＋24バイト）を $7fba から置き、セレビィの表（そのまま 20バイト）を $7fea に うつす。
DEF SIG_FREE           EQU $7fba
DEF SIG_CELEBI_PTR     EQU $6b53   ; セレビィ（251番）
DEF SIG_CELEBI_NEW     EQU $7fea
; 出てくるときの レベル（スクリプトは checkver で 金と銀に分かれている。銀が通る所）
DEF SIG_LUGIA_WILD_BANK EQU $2d    ; ルギア：銀は 元から 40（$2d:$4536）。同じ 40 を書く
DEF SIG_LUGIA_WILD     EQU $4536
DEF SIG_HOOH_WILD_BANK EQU $29     ; ホウオウ：銀は 70（$29:$6e52）→ 40
DEF SIG_HOOH_WILD      EQU $6e52
