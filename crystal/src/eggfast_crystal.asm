; タマゴが うまれるまでの 歩数を 半分に … クリスタル（日本版）用の 値（本体は src/eggfast.asm）
DEF EF_HOOK      EQU $6b9f      ; バンク$25 CountStep の「ld a, [wStepCount]（fa 39 dc）/ cp $80 / jr nz」の cp $80
DEF EF_HOOK_BANK EQU $25

INCLUDE "src/eggfast.asm"
