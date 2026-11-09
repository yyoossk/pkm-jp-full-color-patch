; 戦闘の HP バーの色が、HP が減っても緑のままになる不具合を直す
;
; HUD を描く処理（バンク $0F）では、DrawHP のあとの e（HP バーのドット数）を
; GetBattleHealthBarColor が見て色を決める。そのあいだに入れたキットの
; HP の数字の処理（farcall）が de をこわしていたので、色がいつも緑になっていた。
; farcall の8バイト（ld hl / ld b / call Bankswitch）の飛び先を、
; de を保存してからキットの処理を呼ぶ小さな処理に変える。

IF HAS_KIT_HUD

SECTION "HPバーの色 自分側の呼び出し", ROMX[$4F13], BANK[$0F]
	ld hl, KeepDE_PlayerHUD
	ld b, BANK(KeepDE_PlayerHUD)
	call Bankswitch

SECTION "HPバーの色 相手側の呼び出し", ROMX[$4FE7], BANK[$0F]
	ld hl, KeepDE_EnemyHUD
	ld b, BANK(KeepDE_EnemyHUD)
	call Bankswitch

FreeBankA
KeepDE_PlayerHUD:
	push de
	ld hl, KitPlayerHUDNumbers
	jr KeepDE_Common
KeepDE_EnemyHUD:
	push de
	ld hl, KitEnemyHUDNumbers
KeepDE_Common:
	ld b, KIT_BANK
	call Bankswitch
	pop de
	ret

ENDC
