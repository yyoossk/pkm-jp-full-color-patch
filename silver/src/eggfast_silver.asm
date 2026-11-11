; タマゴの 歩数を 半分：銀 日本版（後期版）の値。CountStep は 金と 同じ 場所（前 fa 83 d9、後ろ 20 08）
DEF EF_HOOK      EQU $6ad2      ; バンク$25 CountStep の cp $80
DEF EF_HOOK_BANK EQU $25
INCLUDE "src/eggfast.asm"
