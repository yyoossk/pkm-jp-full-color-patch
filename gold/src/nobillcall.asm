; ボックスが いっぱいに なった ときの マサキからの 電話を かけて こない ように する（金 日本版）
;
; ・元は、つかまえた ポケモンを パソコンに 送って ボックスが いっぱい（30匹）に なると、wBattleResult の
;   ビット7（BATTLERESULT_BOX_FULL）を 立て、戦闘の あとに マサキから 電話（Script_SpecialBillCall）が かかる。
; ・ボックスが いっぱいに なったら 自動で 次の ボックスに 切りかえる（src/autobox.asm）ので、この 電話は いらない。
; しくみ
;   PokeBallEffect .SendToPC の「ld hl, wBattleResult / set BATTLERESULT_BOX_FULL, [hl]」の set（cb fe）を
;   nop 2つ に（しるしを 立てない ので 電話も かからない）。
;
; 銀・クリスタルに 入れるとき：NB_HOOK・NB_HOOK_BANK を その ROM の「set 7, [hl]」（cb fe）の 場所に する。
;   さがしかた：「ld a, [sBoxCount] / cp MONS_PER_BOX / jr nz」（fa 10 ad fe 1e 20 05）の つぎの
;   「ld hl, wBattleResult」（21 xx xx）の あとの cb fe。

IF !DEF(NB_HOOK)
DEF NB_HOOK      EQU $6ec5      ; バンク$03 PokeBallEffect .SendToPC
DEF NB_HOOK_BANK EQU $03
ENDC

SECTION "nobillcall", ROMX[NB_HOOK], BANK[NB_HOOK_BANK]
	nop
	nop
