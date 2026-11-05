; つりでかならずかかる … クリスタル（日本版）用の 値（本体は src/fishbite.asm）
; Fish.Fish（$24:$698d）：call Random / cp [hl] / jr nc, .no_bite（30 1f）
DEF FB_ADDR            EQU $6991
DEF FB_BANK            EQU $24

INCLUDE "src/fishbite.asm"
