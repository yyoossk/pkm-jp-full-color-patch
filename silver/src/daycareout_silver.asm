; そだてやの おじいさん（外）：銀 日本版（後期版）の値。ROUTE_34 の データは 金と 同じ 場所
DEF DO_BANK     EQU $2f
DEF DO_OBJECT   EQU $5949      ; object_event の y（元 $14）、つぎが x（元 $13）
DEF DO_FACING   EQU $52c0      ; ifequal RIGHT（元 03）
DEF DO_MOVE1    EQU $54e4      ; 0a 0a 09 47
DEF DO_MOVE2    EQU $54e8      ; 08 0a 0a 09 09 47
INCLUDE "src/daycareout.asm"
