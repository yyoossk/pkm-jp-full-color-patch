; ポケットモンスター 金（日本版）オリジナルのバグ修正
; pret/pokecrystal・pret/pokegold の docs/bugs_and_glitches.md に載っているもののうち、日本版 金 にあるもの。
; アドレスは src/jp_all.inc（英語版のラベル → 日本版のアドレス。J_ラベル / JB_ラベル）を使う。
; 項目の番号は pokecrystal の docs の順番（G1〜G7 は pokegold の docs）。

INCLUDE "bf/pg.inc"

; 追加の処理を置く空き
DEF FREE_0D EQU $7fee   ; バンク$0d $7fee-$7fff
DEF FREE_0F EQU $7f00   ; バンク$0f $7f00-$7fff
DEF FREE_3F EQU $6a00   ; バンク$3f $6a00-

; バグ修正で使う WRAM（日本版 金のゲームデータの後ろの空き。60fps は $de40〜$dee7）
DEF wIsConfusionDamage EQU $de38
DEF wBeatUpAction     EQU $de39

;=====================================================================
; 0. ほろびのうた・まきびしで HP 0 のまま倒れないことがある
;=====================================================================
SECTION "BF0 a", ROMX[J_CheckFaint_PlayerThenEnemy], BANK[JB_CheckFaint_PlayerThenEnemy]
	jp CheckFaint_PlayerThenEnemy_Fix
SECTION "BF0 b", ROMX[J_CheckFaint_EnemyThenPlayer], BANK[JB_CheckFaint_EnemyThenPlayer]
	jp CheckFaint_EnemyThenPlayer_Fix

SECTION "Bank0F free", ROMX[FREE_0F], BANK[$0f]
HasAnyoneFainted:
	call J_HasPlayerFainted
	jp nz, J_HasEnemyFainted
	ret

CheckFaint_PlayerThenEnemy_Fix:
.loop
	call .Function
	ret c
	call HasAnyoneFainted
	ret nz
	jr .loop
.Function:
	call J_HasPlayerFainted
	jp J_CheckFaint_PlayerThenEnemy + 3

CheckFaint_EnemyThenPlayer_Fix:
.loop
	call .Function
	ret c
	call HasAnyoneFainted
	ret nz
	jr .loop
.Function:
	call J_HasEnemyFainted
	jp J_CheckFaint_EnemyThenPlayer + 3

;=====================================================================
; 6. いかりのいでんしの こんらんが 256ターン（または前のポケモンのターン数）続く
;=====================================================================
BerserkGene_SetConfused:
	set SUBSTATUS_CONFUSED, [hl]
	ldh a, [hBattleTurn]
	and a
	ld hl, wPlayerConfuseCount
	jr z, .set
	ld hl, wEnemyConfuseCount
.set
	call J_BattleRandom
	and %11
	add 2
	ld [hl], a
	ld a, BATTLE_VARS_MOVE_ANIM
	ret

;=====================================================================
; 10. かなしばり中で ポイントアップ を使ったわざがあると わるあがき にならないことがある
;=====================================================================
UsableMoves_Disabled_Fix:
	swap a
	and $f
	ld b, a
	ld d, NUM_MOVES + 1
	xor a
.loop
	dec d
	jr z, .done
	ld c, [hl]
	inc hl
	dec b
	jr z, .loop
	or c
	jr .loop
.done
	and PP_MASK
	ret nz
	jp J_MoveSelectionScreen__force_struggle   ; .force_struggle（$64b8）

;=====================================================================
; 11. おいうち で倒れたポケモンが、生き返ったときに前の状態異常のまま
;=====================================================================
PursuitSwitch_Fix:
	ld a, [wCurBattleMon]
	push af
	ld a, [wLastPlayerMon]
	ld [wCurBattleMon], a
	call J_UpdateFaintedPlayerMon
	pop af
	ld [wCurBattleMon], a
	ret

;=====================================================================
; 19. 最大HPが 4 より小さいポケモンと入れかえると止まる
;=====================================================================
SwitchHPPercent_Fix:
	ld hl, wEnemyMonMaxHP
	ld a, [hli]
	ld b, [hl]
	ld c, 100
	and a
	jr z, .shift_done
.shift
	rra
	rr b
	srl c
	and a
	jr nz, .shift
.shift_done
	ld a, c
	ldh [hMultiplier], a
	call J_Multiply
	ld a, b
	ld b, 4
	ldh [hDivisor], a
	jp J_Divide

;=====================================================================
; 31. まひ・やけど で下がる能力が、入れかわって出てきたポケモンにかからない
;=====================================================================
LoadEnemyMon_CopyStats:
	call J_CopyBytes
	jp J_ApplyStatusEffectOnEnemyStats

;=====================================================================
; 32. アイスバッジ で とくぼう が上がらないことがある（BoostStat が a をこわす）
;=====================================================================
BoostStat_KeepA:
	push af
	call J_BoostStat
	pop af
	ret

BF0F_END::

SECTION "BF6", ROMX[$4277], BANK[$0f]   ; HandleBerserkGene の set SUBSTATUS_CONFUSED,[hl] / ld a,BATTLE_VARS_MOVE_ANIM
	call BerserkGene_SetConfused
	nop

;=====================================================================
; 1・3. 太いホネ・でんきだま、リフレクター・ひかりのかべ で こうげき・ぼうぎょが 1024 を超えると回ってしまう
;   TruncateHL_BC が1回しか縮めないのが原因。両方が 255 以下になるまでくり返す
;   （1ビットずつ縮めるので、元より正確になる）
;=====================================================================
SECTION "BF1/3", ROMX[J_TruncateHL_BC], BANK[JB_TruncateHL_BC]
TruncateHL_BC_Fix:
.loop
	ld a, h
	or b
	jr z, .done
	srl b
	rr c
	srl h
	rr l
	jr .loop
.done
	ld a, c
	and a
	jr nz, .c_ok
	inc c
.c_ok
	ld a, l
	and a
	jr nz, .l_ok
	inc l
.l_ok
	ld b, l
	ret
	ASSERT @ <= J_TruncateHL_BC + 32

;=====================================================================
; 2. メタルパウダーで ぼうぎょが上がっていると、かえって大きなダメージを受けることがある
;   縮める前の 16ビットの値で 1.5倍にする
;=====================================================================
SECTION "BF2", ROMX[J_DittoMetalPowder], BANK[JB_DittoMetalPowder]
DittoMetalPowder_Fix:
	push hl
	ld a, MON_SPECIES
	call J_BattlePartyAttr
	ldh a, [hBattleTurn]
	and a
	ld a, [hl]
	jr nz, .got_species
	ld a, [wTempEnemyMonSpecies]
.got_species
	cp DITTO
	jr nz, .done
	push bc
	call J_GetOpponentItem
	ld a, [hl]
	cp METAL_POWDER
	pop bc
	jr nz, .done
	ld h, b
	ld l, c
	srl b
	rr c
	add hl, bc
	ld b, h
	ld c, l
.done
	pop hl
	ret
	ASSERT @ <= J_DittoMetalPowder + 43

; 縮める前にメタルパウダーを計算する（call TruncateHL_BC と call DittoMetalPowder を入れかえ）
SECTION "BF2 p", ROMX[J_PlayerAttackDamage__done], BANK[JB_PlayerAttackDamage__done]
	call J_DittoMetalPowder
	call J_TruncateHL_BC
	ld a, [wBattleMonLevel]
	ld e, a
SECTION "BF2 e", ROMX[J_EnemyAttackDamage__done], BANK[JB_EnemyAttackDamage__done]
	call J_DittoMetalPowder
	call J_TruncateHL_BC
	ld a, [wEnemyMonLevel]
	ld e, a

;=====================================================================
; 4. 追加効果が 100% のわざでも 1/256 で追加効果が出ない
;=====================================================================
SECTION "BF4", ROMX[J_BattleCommand_EffectChance__got_move_chance], BANK[JB_BattleCommand_EffectChance__got_move_chance]
	call EffectChance_Roll        ; call BattleRandom / cp [hl]
	nop

SECTION "Bank0D free", ROMX[FREE_0D], BANK[$0d]
EffectChance_Roll:
	ld a, [hl]
	sub 100 percent
	; 100% のときは乱数を使わない（0 - 255 で必ずキャリー）
	call c, J_BattleRandom
	cp [hl]
	ret

;=====================================================================
; 5. はらだいこ：HP が半分より少なくても こうげきが上がってしまう
;=====================================================================
SECTION "BF5", ROMX[J_BattleCommand_BellyDrum], BANK[JB_BattleCommand_BellyDrum]
	ld a, BANK(BellyDrum_Check)
	ld hl, BellyDrum_Check
	rst $08
	jp nc, J_BattleCommand_BellyDrum__failed
	jr @ + 2 + (23 - 11)          ; 元の push bc / call AnimateCurrentMove へ

SECTION "BF 3F", ROMX[FREE_3F], BANK[$3f]
BellyDrum_Check:
; HP が半分あるかを先に調べてから、こうげきを上げる。キャリー = 成功、bc = 減らす HP
	jfarcall GetHalfMaxHP
	jfarcall CheckUserHasEnoughHP
	ret nc
	push bc
	jfarcall BattleCommand_AttackUp2
	pop bc
	ld a, [wAttackMissed]
	and a
	ret nz
	scf
	ret

;=====================================================================
; 7. こんらんの自分へのダメージに、タイプを強くする道具と だいばくはつ・じばく の効果がかかる
;   こんらんのときは BattleCommand_DamageCalc の .skip_zero_damage_check から入り（だいばくはつの計算をとばす）、
;   wIsConfusionDamage が立っている間は道具の効果をつけない
;=====================================================================
SECTION "BF7 a", ROMX[$4319 + 3], BANK[$0d]   ; CheckEnemyTurn の call HitSelfInConfusion のつぎ
	call ConfusionDamageCalc
SECTION "BF7 b", ROMX[$43be + 3], BANK[$0d]   ; HitConfusion
	call ConfusionDamageCalc
SECTION "BF7 c", ROMX[$579f], BANK[$0d]       ; BattleCommand_DamageCalc の call GetUserItem
	call DamageCalc_GetUserItem

SECTION "BF7 d", ROMX[J_BattleCommand_BellyDrum + 11], BANK[JB_BattleCommand_BellyDrum]   ; はらだいこを直して空いた所（12バイト）
ConfusionDamageCalc:
	ld hl, wIsConfusionDamage
	inc [hl]
	call J_BattleCommand_DamageCalc__skip_zero_damage_check
	ld hl, wIsConfusionDamage
	dec [hl]
	ret
	ASSERT @ <= J_BattleCommand_BellyDrum + 23

SECTION "Bank0D free 2", ROMX[FREE_0D + 8], BANK[$0d]
DamageCalc_GetUserItem:
	ld a, [wIsConfusionDamage]
	and a
	jp z, J_GetUserItem
	ld b, 0                    ; 道具の効果なし
	ret
	ASSERT @ <= $8000

;=====================================================================
; 13〜15・58 ふくろだたき（バンク$0d の空きを作るため、本体をバンク$3f に移す）
;  13. 通信対戦でずれる（cp [hl] → cp c）
;  14. 手持ちが1匹だと、そのあとの効果が出ない
;  15. 失敗しても おうじゃのしるし でひるむ
;  58. まもる・みきり で防がれると みがわり が戻らない
;=====================================================================
SECTION "BF13 stub", ROMX[J_BattleCommand_BeatUp], BANK[JB_BattleCommand_BeatUp]
BattleCommand_BeatUp_Stub:
	ld a, BANK(BeatUp_Main)
	ld hl, BeatUp_Main
	rst $08
	ld a, [wBeatUpAction]
	and a
	ret z
	dec a
	jp z, J_EnemyAttackDamage
	ld b, buildopponentrage_command
	jp J_SkipToBattleCommand

; ふくろだたき を移して空いた所（$55b8〜$56f1）
Bank0D_Free2:
;--- 12. ロックオン・こころのめ でも そらをとぶ・あなをほる 中の相手に当たらないことがある
CheckHiddenOpponent_Fix:
	ld a, BATTLE_VARS_SUBSTATUS5_OPP
	call J_GetBattleVar
	cpl
	and 1 << SUBSTATUS_LOCK_ON
	ret z
	ld a, BATTLE_VARS_SUBSTATUS3_OPP
	call J_GetBattleVar
	and 1 << SUBSTATUS_FLYING | 1 << SUBSTATUS_UNDERGROUND
	ret

;--- 9. カウンター・ミラーコート：相手が道具を使ったときも効いてしまう
Counter_CheckDamage:
	ld hl, wCurDamage
	ld a, [hli]
	or [hl]
	ret nz
	pop hl                     ; カウンター・ミラーコートにはもどらない
	jp J_BattleCommand_EffectChance__failed

;--- 15
BeatUpFailText_Fix:
	ld a, [wBeatUpHitAtLeastOnce]
	and a
	ret nz
	inc a
	ld [wAttackMissed], a
	jp J_PrintButItFailed

;--- 58
FailureText_Fix:
	cp EFFECT_BEAT_UP
	jp nz, J_EndMoveEffect
	jp J_BattleCommand_FailureText + 23 + 15   ; .multihit（call BattleCommand_RaiseSub）

;--- 16. プレゼントのダメージが正しくない（金銀ではすべての対戦）
Present_Stab:
	push bc
	push de
	call J_BattleCommand_Stab
	pop de
	pop bc
	ret

;--- 17. おんがえし・やつあたり がなつき度によってダメージ 0 になる
HappinessPower_Fix:
	and a
	jr nz, .done
	inc a
.done
	ld d, a
	pop bc
	ret
	ASSERT @ <= $56f2

SECTION "BF12", ROMX[J_CheckHiddenOpponent], BANK[JB_CheckHiddenOpponent]
	jp CheckHiddenOpponent_Fix
SECTION "BF9 a", ROMX[$598b], BANK[$0d]   ; BattleCommand_Counter の ld hl,wCurDamage / ld a,[hli] / or [hl] / ret z
	call Counter_CheckDamage
	nop
	nop
	nop
SECTION "BF9 b", ROMX[$7de7], BANK[$0d]   ; BattleCommand_MirrorCoat
	call Counter_CheckDamage
	nop
	nop
	nop
SECTION "BF15", ROMX[J_BattleCommand_BeatUpFailText], BANK[JB_BattleCommand_BeatUpFailText]
	jp BeatUpFailText_Fix
SECTION "BF14", ROMX[$6b3c], BANK[$0d]    ; BattleCommand_EndLoop .only_one_beatup の call BattleCommand_BeatUpFailText / jp EndMoveEffect
	ret
SECTION "BF58", ROMX[$5194], BANK[$0d]    ; BattleCommand_FailureText の jp EndMoveEffect
	jp FailureText_Fix
SECTION "BF16", ROMX[J_BattleCommand_Present], BANK[JB_BattleCommand_Present]
	call Present_Stab
SECTION "BF17 a", ROMX[$79bd], BANK[$0d]  ; BattleCommand_HappinessPower の ld d,a / pop bc / ret
	jp HappinessPower_Fix
SECTION "BF17 b", ROMX[$7a71], BANK[$0d]  ; BattleCommand_FrustrationPower
	jp HappinessPower_Fix

SECTION "BF13 main", ROMX[FREE_3F + $40], BANK[$3f]
; 戻ったあと：wBeatUpAction 0 = そのまま（d e b c を返す）、1 = jp EnemyAttackDamage、2 = 失敗
BeatUp_Main:
	xor a
	ld [wBeatUpAction], a
	ld [wCurDamage], a          ; ResetDamage
	ld [wCurDamage + 1], a
	ldh a, [hBattleTurn]
	and a
	jp nz, .enemy_beats_up

	ld a, [wPlayerSubStatus3]
	bit SUBSTATUS_IN_LOOP, a
	jr nz, .next_mon

	ld c, 20
	call J_DelayFrames
	xor a
	ld [wPlayerRolloutCount], a
	ld [wCurBeatUpPartyMon], a
	ld [wBeatUpHitAtLeastOnce], a
	jr .got_mon

.next_mon
	ld a, [wPlayerRolloutCount]
	ld b, a
	ld a, [wPartyCount]
	sub b
	ld [wCurBeatUpPartyMon], a

.got_mon
	ld a, [wCurBeatUpPartyMon]
	ld hl, wPartyMonNicknames
	call J_GetNickname
	ld a, MON_HP
	call BeatUp_GetMonLocation
	ld a, [hli]
	or [hl]
	jp z, .beatup_fail ; fainted
	ld a, [wCurBeatUpPartyMon]
	ld c, a
	ld a, [wCurBattleMon]
	cp c                        ; 13（元は cp [hl]）
	ld hl, wBattleMonStatus
	jr z, .active_mon
	ld a, MON_STATUS
	call BeatUp_GetMonLocation
.active_mon
	ld a, [hl]
	and a
	jp nz, .beatup_fail

	ld a, $1
	ld [wBeatUpHitAtLeastOnce], a
	ld hl, J_BeatUpAttackText
	call J_StdBattleTextbox

	ld a, [wEnemyMonSpecies]
	ld [wCurSpecies], a
	call J_GetBaseData
	ld a, [wBaseDefense]
	ld c, a

	push bc
	ld a, MON_SPECIES
	call BeatUp_GetMonLocation
	ld a, [hl]
	ld [wCurSpecies], a
	call J_GetBaseData
	ld a, [wBaseAttack]
	pop bc
	ld b, a

	push bc
	ld a, MON_LEVEL
	call BeatUp_GetMonLocation
	ld a, [hl]
	ld e, a
	pop bc

	ld a, [wPlayerMoveStructPower]
	ld d, a
	ret

.enemy_beats_up
	ld a, [wEnemySubStatus3]
	bit SUBSTATUS_IN_LOOP, a
	jr nz, .enemy_next_mon

	xor a
	ld [wEnemyRolloutCount], a
	ld [wCurBeatUpPartyMon], a
	ld [wBeatUpHitAtLeastOnce], a
	jr .enemy_got_mon

.enemy_next_mon
	ld a, [wEnemyRolloutCount]
	ld b, a
	ld a, [wOTPartyCount]
	sub b
	ld [wCurBeatUpPartyMon], a

.enemy_got_mon
	ld a, [wBattleMode]
	dec a
	jr z, .wild

	ld a, [wLinkMode]
	and a
	jr nz, .linked

	ld a, [wCurBeatUpPartyMon]
	ld c, a
	ld b, 0
	ld hl, wOTPartySpecies
	add hl, bc
	ld a, [hl]
	ld [wNamedObjectIndex], a
	call J_GetPokemonName
	jr .got_enemy_nick

.linked
	ld a, [wCurBeatUpPartyMon]
	ld hl, wOTPartyMonNicknames
	ld bc, JP_NAME_LENGTH
	call J_AddNTimes
	ld de, wStringBuffer1
	call J_CopyBytes

.got_enemy_nick
	ld a, MON_HP
	call BeatUp_GetMonLocation
	ld a, [hli]
	or [hl]
	jp z, .beatup_fail

	ld a, [wCurBeatUpPartyMon]
	ld b, a
	ld a, [wCurOTMon]
	cp b
	ld hl, wEnemyMonStatus
	jr z, .active_enemy
	ld a, MON_STATUS
	call BeatUp_GetMonLocation
.active_enemy
	ld a, [hl]
	and a
	jr nz, .beatup_fail

	ld a, $1
	ld [wBeatUpHitAtLeastOnce], a
	jr .finish_beatup

.wild
	ld a, [wEnemyMonSpecies]
	ld [wNamedObjectIndex], a
	call J_GetPokemonName
	ld hl, J_BeatUpAttackText
	call J_StdBattleTextbox
	ld a, 1
	ld [wBeatUpAction], a        ; jp EnemyAttackDamage
	ret

.finish_beatup
	ld hl, J_BeatUpAttackText
	call J_StdBattleTextbox

	ld a, [wBattleMonSpecies]
	ld [wCurSpecies], a
	call J_GetBaseData
	ld a, [wBaseDefense]
	ld c, a

	push bc
	ld a, MON_SPECIES
	call BeatUp_GetMonLocation
	ld a, [hl]
	ld [wCurSpecies], a
	call J_GetBaseData
	ld a, [wBaseAttack]
	pop bc
	ld b, a

	push bc
	ld a, MON_LEVEL
	call BeatUp_GetMonLocation
	ld a, [hl]
	ld e, a
	pop bc

	ld a, [wEnemyMoveStructPower]
	ld d, a
	ret

.beatup_fail
	ld a, 2
	ld [wBeatUpAction], a
	ret

BeatUp_GetMonLocation:
	push bc
	ld c, a
	ld b, 0
	ldh a, [hBattleTurn]
	and a
	ld hl, wPartyMon1Species
	jr z, .got_species
	ld hl, wOTPartyMon1Species
.got_species
	ld a, [wCurBeatUpPartyMon]
	add hl, bc
	call J_GetPartyLocation
	pop bc
	ret

SECTION "BF10", ROMX[$64a3], BANK[$0f]   ; .CheckPlayerHasUsableMoves の .disabled
	jp UsableMoves_Disabled_Fix
SECTION "BF11", ROMX[$5b07], BANK[$0f]   ; PursuitSwitch の ld a,[wLastPlayerMon] … predef SmallFarFlagAction（14バイト）
	call PursuitSwitch_Fix
	jr @ + 2 + 9
SECTION "BF19 a", ROMX[$70e5], BANK[$0f] ; SendOutMonText の ld a,25 … call Divide（28バイト）
	call SwitchHPPercent_Fix
	jr @ + 2 + 23
SECTION "BF19 b", ROMX[$7180], BANK[$0f] ; WithdrawMonText
	call SwitchHPPercent_Fix
	jr @ + 2 + 23

;=====================================================================
; 8. さんせい・アイアンテール・いわくだき が みがわり を壊したあとでも ぼうぎょ を下げる
;   （2回目の effectchance をなくす）
;=====================================================================
SECTION "BF8", ROMX[J_DefenseDownHit + 17], BANK[JB_DefenseDownHit]
	db $7f, $8d, $ff, $ff        ; defensedown / statdownmessage / endmove（effectchance を消した）

;=====================================================================
; 20. ダメージを与えて自分の能力を上げるわざで、相手を倒すと能力が上がらない
;=====================================================================
SECTION "BF20 a", ROMX[J_DefenseUpHit + 15], BANK[JB_DefenseUpHit]
	db $71, $8c, $11, $12        ; defenseup / statupmessage / checkfaint / buildopponentrage
SECTION "BF20 b", ROMX[J_AttackUpHit + 15], BANK[JB_AttackUpHit]
	db $70, $8c, $11, $12        ; attackup / statupmessage / checkfaint / buildopponentrage
SECTION "BF20 c", ROMX[J_AllUpHit + 15], BANK[JB_AllUpHit]
	db $a4, $11, $12             ; allstatsup / checkfaint / buildopponentrage

;=====================================================================
; 18. ドラゴンのキバ ではなく りゅうのウロコ が ドラゴンタイプのわざを強くする
;=====================================================================
SECTION "BF18 a", ROMX[$6f7c + 2], BANK[$01]   ; DRAGON_FANG の 持たせた効果
	db HELD_DRAGON_BOOST, 10
SECTION "BF18 b", ROMX[$6fad + 2], BANK[$01]   ; DRAGON_SCALE
	db HELD_NONE, 0

;=====================================================================
; 21. へんしん したポケモンが スケッチ で覚えられないわざを覚える（相手ではなく自分の へんしん を調べる）
;=====================================================================
SECTION "BF21", ROMX[$5bc2], BANK[$0d]   ; BattleCommand_Sketch の ld a, BATTLE_VARS_SUBSTATUS5_OPP
	db BATTLE_VARS_SUBSTATUS5

;=====================================================================
; ボール（バンク$03）
;=====================================================================
DEF FREE_03 EQU $7fa8   ; バンク$03 $7fa8-$7fff

; 22. へんしん したポケモンを捕まえると メタモン になる
SECTION "BF22", ROMX[$6d96], BANK[$03]   ; PokeBallEffect の jr nz, .ditto → jr nz, .load_data
	jr nz, @ + 2 + $16

; 24. つかまえかた の説明で、手持ちとボックスがいっぱいだと止まる
SECTION "BF24", ROMX[$6c30], BANK[$03]   ; ld a,[wPartyCount] / cp PARTY_LENGTH
	call Ball_PartyFullCheck
	nop
	nop

; 25. まひ・やけど・どく が捕まえやすさに効いていない
SECTION "BF25", ROMX[$6cf1], BANK[$03]   ; and a / ld c, 5
	call Ball_StatusCheck

; 30. 最大HP が 342 以上だと捕まえやすさの計算がおかしくなる
SECTION "BF30", ROMX[$6cc1], BANK[$03]   ; ld a,c / and a / jr nz,.okay_1 / ld c,1
	call Ball_HPCheck
	nop
	nop
	nop

; 46. 持たせた道具の HELD_CATCH_CHANCE が効かない
SECTION "BF46", ROMX[$6d00], BANK[$03]   ; ld a, [wBattleMonItem]
	call Ball_GetHeldItem

; 26. ムーンボール が効かない
SECTION "BF26 a", ROMX[$7025], BANK[$03]
	inc hl                      ; inc hl ×3 → ×1
	nop
	nop
SECTION "BF26 b", ROMX[$7025 + 9], BANK[$03]
	cp MOON_STONE
; 27. ラブラブボール が ちがう性別のときに効く
SECTION "BF27", ROMX[$707d + 4], BANK[$03]
	ret z
; 28. スピードボール が3匹にしか効かない
SECTION "BF28", ROMX[$709c + 11], BANK[$03]
	jr nz, @ - 11               ; → .loop

SECTION "Bank03 free", ROMX[FREE_03], BANK[$03]
Ball_PartyFullCheck:
	ld a, [wBattleType]
	cp BATTLETYPE_TUTORIAL
	ld a, 0                     ; 説明のときは手持ちに空きがあることにする
	jr z, .cmp
	ld a, [wPartyCount]
.cmp
	cp PARTY_LENGTH
	ret

Ball_StatusCheck:
	ld a, [wEnemyMonStatus]
	and a
	ld c, 5
	ret

Ball_HPCheck:
	ld a, d
	and a
	jr z, .check_cur_low
	srl d
	rr e
	srl b
	rr c
.check_cur_low
	ld a, c
	and a
	ret nz
	ld c, 1
	ret

Ball_GetHeldItem:
	ld a, [wBattleMonItem]
	ld b, a
	ret
	ASSERT @ <= $8000

SECTION "BF31", ROMX[$69cf], BANK[$0f]   ; LoadEnemyMon の最後 call CopyBytes
	call LoadEnemyMon_CopyStats
SECTION "BF32", ROMX[J_BadgeStatBoosts__CheckBadge + 3], BANK[JB_BadgeStatBoosts__CheckBadge]
	call c, BoostStat_KeepA

;=====================================================================
; AI（バンク$0e・$0b）
;=====================================================================
DEF FREE_0E EQU $7fc8   ; バンク$0e $7fc8-$7fff
DEF FREE_0B EQU $7c70   ; バンク$0b $7c70-$7fff
DEF wEnemyFutureSightCount_JP EQU $cbf0

; 33. かしこいAI が、自分が もうどく のときに くろいまなざし を選びやすくする（相手を調べるはずが自分を調べていた）
SECTION "BF33", ROMX[$4e08], BANK[$0e]   ; AI_Smart_MeanLook の ld a, [wEnemySubStatus5]
	dw wPlayerSubStatus5
; 34. かしこいAI が、2ターン目から テクスチャー2 を選ばなくなる
SECTION "BF34", ROMX[$4d9b], BANK[$0e]   ; AI_Smart_Conversion2 の jr nz, .discourage → jr z
	db $28
; 35. かしこいAI が、ソーラービーム・かえんぐるま・つきのひかり を覚えていても にほんばれ を選びやすくしない
SECTION "BF35", ROMX[$50e9 + 1], BANK[$0e]   ; AI_Smart_SunnyDay の ld hl, SunnyDayMoves
	dw SunnyDayMoves_Fix
; 36. 用心深いAI が、あとから効くわざを選びにくくしないことがある
SECTION "BF36", ROMX[$5421], BANK[$0e]   ; AI_Cautious の call Random / cp 90 percent + 1 / ret nc / inc [hl] / jr .loop
	call AI_Cautious_Roll
	jr nc, J_AI_Cautious__loop
	inc [hl]
	jr J_AI_Cautious__loop

SECTION "Bank0E free", ROMX[FREE_0E], BANK[$0e]
SunnyDayMoves_Fix:
	db FIRE_PUNCH
	db EMBER
	db FLAMETHROWER
	db SOLARBEAM
	db FIRE_SPIN
	db FIRE_BLAST
	db FLAME_WHEEL
	db SACRED_FIRE
	db MORNING_SUN
	db SYNTHESIS
	db MOONLIGHT
	db -1 ; end

AI_Cautious_Roll:
	call J_Random
	cp $e6                      ; 90 percent + 1（日本版の値）
	ret
	ASSERT @ <= $8000

; 37. AI が、ねむり 以外の状態異常でも あくむ を選ばない
SECTION "BF37", ROMX[$5572], BANK[$0b]   ; AI_Redundant.Nightmare の ld a, [wBattleMonStatus] / and a
	call AI_Nightmare_Status
	nop
; 38. AI が、みらいよち をもう使ったかを調べていない
SECTION "BF38", ROMX[$55ce], BANK[$0b]   ; AI_Redundant.FutureSight
	ld a, [wEnemyFutureSightCount_JP]
	and a
	ret

SECTION "Bank0B free", ROMX[FREE_0B], BANK[$0b]
AI_Nightmare_Status:
	ld a, [wBattleMonStatus]
	and SLP_MASK
	ret

; 39. AI が CheckTypeMatchup に a でタイプを渡せると思っているが、関数の中で書きかえられている
SECTION "BF39", ROMX[J_BattleCheckTypeMatchup], BANK[JB_BattleCheckTypeMatchup]
	jp BattleCheckTypeMatchup_Fix
SECTION "BF39 b", ROMX[J_CheckTypeMatchup + 3], BANK[JB_CheckTypeMatchup]   ; push hl/de/bc のつぎの ld a, BATTLE_VARS_MOVE_TYPE / call GetBattleVar
	nop
	nop
	nop
	nop
	nop
SECTION "BF39 c", ROMX[$55b8 + $80], BANK[$0d]   ; ふくろだたき を移して空いた所の続き
BattleCheckTypeMatchup_Fix:
	ld hl, wEnemyMonType1
	ldh a, [hBattleTurn]
	and a
	jr z, .get_type
	ld hl, wBattleMonType1
.get_type
	ld a, BATTLE_VARS_MOVE_TYPE
	call J_GetBattleVar         ; hl・de・bc はそのまま
	jp J_CheckTypeMatchup
	ASSERT @ <= $56f2

; 40〜42. AI が かいふくのくすり・なんでもなおし を使っても、あくむ・こんらん・やけど／まひ の能力ダウンが治らない
SECTION "BF40", ROMX[$44ef], BANK[$0e]    ; AI_HealStatus の ld hl,wEnemySubStatus5 / res SUBSTATUS_TOXIC,[hl] / ret
	jp AI_HealStatus_Tail
SECTION "BF40 b", ROMX[J_AICheckEnemyFractionMaxHP], BANK[JB_AICheckEnemyFractionMaxHP]   ; 使われていない関数の所
AI_HealStatus_Tail:
	ld [wEnemyConfuseCount], a  ; a = 0
	ld hl, wEnemySubStatus3
	res SUBSTATUS_CONFUSED, [hl]
	ld hl, wEnemySubStatus1
	res SUBSTATUS_NIGHTMARE, [hl]
	ld hl, wEnemySubStatus5
	res SUBSTATUS_TOXIC, [hl]
	jfarcall CalcEnemyStats
	ret

; 43. AI が 賞金の値を道具として使うことがある（2つ目からの道具を調べるときに de を戻していない）
SECTION "BF43 a", ROMX[$4132 + 1], BANK[$0e]   ; AI_TryItem の jr .loop → ld de, wEnemyTrainerItem1 へ
	db $ed - 3
SECTION "BF43 b", ROMX[$4143 + 1], BANK[$0e]   ; jr c, .loop
	db $dc - 3

; 44. 野生のポケモンの テレポート が レベルの差に関係なく必ず成功する
SECTION "BF44", ROMX[$68fd], BANK[$0d]   ; .loop_enemy のあとの jr nc, .run_away → jr c, .failed
	jr c, $68d9

; 45. ライバル（2回目のクラス）の個体値が1回目より低い
SECTION "BF45", ROMX[J_TrainerClassDVs + (RIVAL2 - 1) * 2], BANK[JB_TrainerClassDVs]
	dn 13, 13, 13, 13

;=====================================================================
; 47. エンディングを見たあと、戦闘のわざ選びで 上下 を押しっぱなしにすると動き続ける（hInMenu が戻らない）
;=====================================================================
DEF wCreditsSavedInMenu EQU $de3a
SECTION "BF47 a", ROMX[$6b1c], BANK[$21]   ; Credits の ld a, TRUE / ldh [hInMenu], a
	call Credits_SaveInMenu
	nop
SECTION "BF47 b", ROMX[$6b3c], BANK[$21]   ; .exit_credits の call ClearBGPalettes
	call Credits_RestoreInMenu
SECTION "BF home", ROM0[$00e4]             ; ホームの空き $00e4-$00ff
Credits_SaveInMenu:
	ldh a, [hInMenu]
	ld [wCreditsSavedInMenu], a
	ld a, TRUE
	ldh [hInMenu], a
	ret
Credits_RestoreInMenu:
	ld a, [wCreditsSavedInMenu]
	ldh [hInMenu], a
	jp J_ClearBGPalettes
	ASSERT @ <= $0100

;=====================================================================
; 48. LoadMetatiles で 128 番より後のブロックが前に戻ってしまう
;=====================================================================
SECTION "BF48", ROM0[$1faf]                ; add a / ld l, a / ld h, 0 / add hl, hl ×3
	ld l, a
	ld h, 0
	add hl, hl
	add hl, hl
	add hl, hl
	add hl, hl

;=====================================================================
; 49. なみのり で海に入ったとき、すぐ隣のマップにつながっていると新しいマップを読みこまない
;   （ゆっくり歩く動きではなく、自動入力で1歩進める）
;=====================================================================
SECTION "BF49 a", ROMX[$4a31], BANK[$03]   ; UsedSurfScript の applymovement PLAYER, wMovementBuffer
	db $90, $90, $90, $90                  ; end
SECTION "BF49 b", ROMX[J_SurfStartStep], BANK[JB_SurfStartStep]
SurfStartStep_Fix:
	ld a, [wPlayerDirection]
	srl a
	srl a
	maskbits NUM_DIRECTIONS
	ld e, a
	ld d, 0
	ld hl, .movement_data
	add hl, de
	add hl, de
	add hl, de
	ld a, BANK(.movement_data)
	jp J_StartAutoInput
.movement_data
	db PAD_DOWN,  0, -1
	db PAD_UP,    0, -1
	db PAD_LEFT,  0, -1
	db PAD_RIGHT, 0, -1
	ASSERT @ <= J_SurfStartStep + 37

;=====================================================================
; 23. レベル1 のポケモン（成長が中くらいに遅いグループ）の経験値がマイナスになって大きな値になる
;=====================================================================
DEF wBaseGrowthRate_JP EQU $d128
SECTION "BF23", ROMX[J_CalcExpAtLevel], BANK[JB_CalcExpAtLevel]
	jp CalcExpAtLevel_Fix
SECTION "Bank14 free", ROMX[$7fb6], BANK[$14]   ; バンク$14 $7fb6-$7fff
CalcExpAtLevel_Fix:
	ld a, d
	dec a
	jr nz, .use_formula
; レベル1 は経験値 0
	ld hl, hProduct
	ld [hli], a
	ld [hli], a
	ld [hli], a
	ld [hl], a
	ret
.use_formula
	ld a, [wBaseGrowthRate_JP]
	jp J_CalcExpAtLevel + 3
	ASSERT @ <= $8000

;=====================================================================
; 50. 泳ぐNPC が 動ける範囲を守らない（すり抜けの印があっても陸に当たるかを調べていた）
;=====================================================================
SECTION "BF50", ROMX[J_CanObjectMoveInDirection], BANK[JB_CanObjectMoveInDirection]
CanObjectMoveInDirection_Fix:
	ld hl, OBJECT_PALETTE
	add hl, bc
	ld a, [hl]
	ld hl, OBJECT_FLAGS1
	add hl, bc
	bit NOCLIP_TILES_F, [hl]
	jr nz, .continue
	push hl
	push bc
	bit SWIMMING_F, a
	jr z, .water
	call J_WillObjectBumpIntoLand
	jr .bumped
.water
	call J_WillObjectBumpIntoWater
.bumped
	pop bc
	pop hl
	ret c
	jr .continue
	ASSERT @ <= J_CanObjectMoveInDirection + 40
	ds J_CanObjectMoveInDirection + 40 - @, 0
.continue

;=====================================================================
; 51. 釣りざおで NPC の上を釣れる / G5. なみのり で NPC の上に乗れる
;=====================================================================
SECTION "BF51", ROMX[$5232], BANK[$03]   ; FishFunction.TryFish の call GetFacingTileCoord … jr z, .facingwater
	ld a, BANK(Fish_CheckFacing)
	ld hl, Fish_CheckFacing
	rst $08
	jr z, $523f               ; .facingwater
	jr $5232 + 10             ; .fail
SECTION "BFG5", ROMX[$49dc], BANK[$03]   ; SurfFunction.TrySurf の call GetFacingTileCoord … ld a, $1 / ret
	ld a, BANK(Surf_CheckFacing)
	ld hl, Surf_CheckFacing
	rst $08
	jr c, $49f4               ; .cannotsurf
	ret                       ; a = 1

;=====================================================================
; 52. 育て屋に預けたポケモンを引き取ると、レベルが上がっていなくても経験値が減ることがある
;=====================================================================
SECTION "BF52", ROMX[$60a8], BANK[$03]   ; RetrieveBreedmon の ld a,[wCurPartyLevel] … ld [hl],a（24バイト）
	pop bc
	ld a, BANK(Breedmon_SetExp)
	ld hl, Breedmon_SetExp
	rst $08
	jr @ + 2 + 24 - 9

SECTION "BF 3F b", ROMX[FREE_3F + $200], BANK[$3f]
Fish_CheckFacing:
; z = 水の方を向いていて、NPC がいない
	call J_GetFacingTileCoord
	call J_GetTilePermission
	cp WATER_TILE
	ret nz
	jfarcall CheckFacingObject
	sbc a                       ; NPC がいない（nc）→ 0（z）
	ret

Surf_CheckFacing:
; キャリー = なみのり できない、c = 1
	call J_GetFacingTileCoord
	call J_GetTilePermission
	cp WATER_TILE
	jr nz, .cannot
	jfarcall CheckDirection
	ret c
	jfarcall CheckFacingObject
	ld c, 1
	ret
.cannot
	scf
	ret

Breedmon_SetExp:
; bc = 預けていたポケモン
	ld d, MAX_LEVEL
	jfarcall CalcExpAtLevel
	ld hl, MON_EXP + 2
	add hl, bc
	ldh a, [hMultiplicand]
	ld b, a
	ldh a, [hMultiplicand + 1]
	ld c, a
	ldh a, [hMultiplicand + 2]
	ld d, a
	ld a, [hld]
	sub d
	ld a, [hld]
	sbc c
	ld a, [hl]
	sbc b
	ret c                       ; 最大レベルの経験値より少ない → そのまま
	ld a, b
	ld [hli], a
	ld a, c
	ld [hli], a
	ld a, d
	ld [hl], a
	ret

;=====================================================================
; 55. アルフの遺跡 の研究所の屋根の色が夜におかしい（洞窟グループの屋根の色を グレン と同じ赤に）
;=====================================================================
SECTION "BF55", ROMX[$794c], BANK[$02]
	RGB 31,10,00, 18,06,00 ; morn/day
	RGB 18,05,09, 17,08,07 ; nite

;=====================================================================
; 56. ヤドンの井戸 のまわりの石の 左下の角 がちがうタイル（johto_modern のブロック $5B）
;=====================================================================
SECTION "BF56 a", ROMX[$6750 + 4], BANK[$06]
	db $47
SECTION "BF56 b", ROMX[$6750 + 6], BANK[$06]
	db $47
SECTION "BF56 c", ROMX[$6750 + 12], BANK[$06]
	db $47

;=====================================================================
; 57. アンノーン のタマゴがかえるとき、ちがう形が出る
;=====================================================================
SECTION "BF57", ROMX[J_GetEggFrontpic + 10], BANK[JB_GetEggFrontpic]   ; ld hl, wBattleMonDVs
	call EggFrontpic_GetDVs
SECTION "Bank05 free", ROMX[$7ff5], BANK[$05]
EggFrontpic_GetDVs:
	ld a, MON_DVS
	jp J_GetPartyParamLocation
	ASSERT @ <= $8000

;=====================================================================
; 59. HP が多いと HPバー の動きが遅い
;=====================================================================
SECTION "BF59", ROMX[$59f0 + 3], BANK[$03]   ; LongAnim_UpdateVariables の pop bc / pop de / pop hl / ld a, e
	ld a, e
	pop bc
	pop de
	pop hl

;=====================================================================
; 60. HP が少ないときの HPバー の動きが1ドットずれる
;=====================================================================
SECTION "BF60", ROMX[$5af9 + 4], BANK[$03]   ; ShortHPBar_CalcPixelFrame の ld a,h / sbc $0 / ld h,a / jr c, .done
	call HPBar_SubHigh
	jr c, @ + 2 + 4             ; .done
	nop
SECTION "Bank03 free 2", ROMX[FREE_03 + $30], BANK[$03]
HPBar_SubHigh:
	ld a, h
	sbc $0
	ld h, a
	ret c
	ret nz
	scf                         ; 0 になったときも終わり
	ret
	ASSERT @ <= $8000

;=====================================================================
; 61. コンテスト以外で パークボール を使うとアニメーションがこわれる
;=====================================================================
SECTION "BF61", ROMX[$6c47 + 4], BANK[$03]   ; ld a, [wCurItem] / cp PARK_BALL
	ld a, [wBattleType]
	cp BATTLETYPE_CONTEST

;=====================================================================
; 62. 戦闘の始まりの画面の動きが、相手のレベルを見ていない
;=====================================================================
SECTION "BF62", ROMX[J_StartTrainerBattle_DetermineWhichAnimation], BANK[JB_StartTrainerBattle_DetermineWhichAnimation]
	call BattleTransition_GetLevels  ; a = 先頭のポケモンのレベル + 3、hl = wCurPartyLevel（相手のレベル）
	ld de, 0
	nop
	nop
	nop
	nop
	nop
	ASSERT @ == J_StartTrainerBattle_DetermineWhichAnimation + 11   ; cp [hl]

SECTION "Bank23 free", ROMX[$7c90], BANK[$23]   ; バンク$23 $7c90-$7fff
BattleTransition_GetLevels:
	ld a, [wOtherTrainerClass]
	and a
	call nz, SetTrainerBattleLevel
	ld b, PARTY_LENGTH
	ld hl, wPartyMon1HP
	ld de, PARTYMON_STRUCT_LENGTH - 1
.loop
	ld a, [hli]
	or [hl]
	jr nz, .okay
	add hl, de
	dec b
	jr nz, .loop
.okay
	ld de, MON_LEVEL - MON_HP - 1
	add hl, de
	ld a, [hl]
	add 3
	ld hl, wCurPartyLevel
	ret

SetTrainerBattleLevel:
; 相手のトレーナーの1匹目のレベル → wCurPartyLevel（トレーナーのデータはバンク$0e）
	ld a, 255
	ld [wCurPartyLevel], a
	ld a, [wLinkMode]
	and a
	ret nz
	ld a, [wOtherTrainerClass]
	dec a
	ld c, a
	ld b, 0
	ld hl, $595c                ; TrainerGroups
	add hl, bc
	add hl, bc
	ld a, $0e
	call J_GetFarWord
	ld a, [wOtherTrainerID]
	ld b, a
.skip_trainer
	dec b
	jr z, .skip_name
.skip_party
	ld a, $0e
	call J_GetFarByte
	inc hl
	cp $ff
	jr nz, .skip_party
	jr .skip_trainer
.skip_name
	ld a, $0e
	call J_GetFarByte
	inc hl
	cp $50                      ; "@"
	jr nz, .skip_name
	inc hl                      ; トレーナーの種類
	ld a, $0e
	call J_GetFarByte
	ld [wCurPartyLevel], a
	ret

;=====================================================================
; 63. トレーナーの NPC の見た目・色が、ほかの同じトレーナーと合っていない（むしとり大会の参加者も）
;   （bf/npc63.inc は tools/npc2.py で、マップのイベントの並びから日本版の位置を出して作った）
;=====================================================================
INCLUDE "bf/npc63.inc"

;=====================================================================
; 65. スロットで コインが出るときの音が とぎれる
;=====================================================================
SECTION "BF65", ROMX[$6e80 + 5], BANK[$24]   ; SlotsAction_PayoutAnim の ret z
	ret nz

;=====================================================================
; 66. ロケット団の幹部・研究員と戦うときに ロケット団の戦闘の曲 にならない
;=====================================================================
SECTION "BF66", ROMX[$7a31], BANK[$11]   ; PlayBattleMusic の cp GRUNTM / jr z / cp GRUNTF / jr z
	call RocketBattleMusic_Check
	jr z, $7a81                 ; .done
	nop
	nop
	nop
SECTION "Bank11 free", ROMX[$7fac], BANK[$11]
RocketBattleMusic_Check:
	cp GRUNTM
	ret z
	cp GRUNTF
	ret z
	cp EXECUTIVEM
	ret z
	cp EXECUTIVEF
	ret z
	cp SCIENTIST
	ret
	ASSERT @ <= $8000

;=====================================================================
; 67. 足もとのタイルが $3E のとき 壁にぶつかる音が出ない
;=====================================================================
SECTION "BF67", ROMX[J_DoPlayerMovement__CheckWarp], BANK[JB_DoPlayerMovement__CheckWarp]
CheckWarp_Fix:
	ld a, [wWalkingDirection]
	cp STANDING
	jr z, $4259                 ; .not_warp
	ld e, a
	ld d, 0
	ld hl, $425b                ; .EdgeWarps
	add hl, de
	ld a, [wPlayerTileCollision]
	cp [hl]
	jr nz, $4259
	ld a, TRUE
	ld [wWalkingIntoEdgeWarp], a
	ld a, [wWalkingDirection]
	ASSERT @ == J_DoPlayerMovement__CheckWarp + 28

;=====================================================================
; 68. 図鑑で エンテイ の鳴き声を聞くと ライコウ・スイクン の鳴き声がおかしくなる（回避策）
;=====================================================================
SECTION "BF68", ROMX[J_DexEntryScreen_MenuActionJumptable__Cry], BANK[JB_DexEntryScreen_MenuActionJumptable__Cry]
	ld a, [wCurPartySpecies]
	call J_PlayMonCry
	ret

;=====================================================================
; 69. 野生のポケモンが逃げたときの にげる音 が正しく鳴らない
;=====================================================================
SECTION "BF69", ROMX[$410c + 4], BANK[$0f]   ; WildFled_EnemyFled_LinkBattleCanceled の call PlaySFX
	dw J_WaitPlaySFX

;=====================================================================
; 70. 5けたの経験値が正しく表示されない
;=====================================================================
SECTION "BF70", ROMX[$6f81 + 3], BANK[$0f]   ; text_decimal wStringBuffer2, 2, 4 → 2, 5
	dn 2, 5

;=====================================================================
; 71. 進化の石を使える／使えない の表示が、進化の3番目までしか見ていない（回避策：6つまで読む）
;   日本版の wStringBuffer1 は 11バイトなので、続く wStringBuffer2 まで使う（ここでは使っていない）
;=====================================================================
SECTION "BF71", ROMX[$427b], BANK[$14]   ; .DetermineCompatibility の ld bc, 10
	dw 19

;=====================================================================
; 72. EVOLVE_STAT の進化（4バイト）があると 進化の石の表示がおかしくなる
;=====================================================================
SECTION "BF72", ROMX[$4283 + 4], BANK[$14]   ; .loop2 の inc hl / inc hl / cp EVOLVE_ITEM
	call EvoStone_SkipEntry
	nop
SECTION "Bank14 free 2", ROMX[$7fd8], BANK[$14]
EvoStone_SkipEntry:
	cp EVOLVE_STAT
	jr nz, .not_four_bytes
	inc hl
.not_four_bytes
	inc hl
	inc hl
	cp EVOLVE_ITEM
	ret
	ASSERT @ <= $8000

;=====================================================================
; 73. 殿堂入り 200回 の「でんどういり マスター」の表示が出ない
;=====================================================================
SECTION "BF73", ROMX[$6854 + 4], BANK[$21]   ; cp HOF_MASTER_COUNT + 1 → cp HOF_MASTER_COUNT
	db HOF_MASTER_COUNT

;=====================================================================
; 75. デイジーの毛づくろい で なつき度が上がらないことがある（0.4%）
;=====================================================================
SECTION "BF75", ROMX[$7f43], BANK[$01]   ; DaisysGrooming の ld hl, HappinessData_DaisysGrooming
	dw HappinessData_DaisysGrooming_Fix
SECTION "Bank01 free", ROMX[$7fa0], BANK[$01]     ; バンク$01 $7fa0-$7fff
HappinessData_DaisysGrooming_Fix:
	db 50 percent, 2, $12        ; HAPPINESS_GROOMING（日本版の値）50%
	db -1,         2, $12        ; 50%

;=====================================================================
; 76. いかりのみずうみ の コイキング が長くならず、ほかの所のほうが長い（jr z → jr nz）
;   ※日本版は長さを mm で持っているので、77（フィート・インチの変換ミス）は日本版にはない
;=====================================================================
SECTION "BF76 a", ROMX[J_LoadEnemyMon__CheckMagikarpArea + 5], BANK[JB_LoadEnemyMon__CheckMagikarpArea]
	db $20                       ; jr nz, .Happiness
SECTION "BF76 b", ROMX[J_LoadEnemyMon__CheckMagikarpArea + 12], BANK[JB_LoadEnemyMon__CheckMagikarpArea]
	db $20

;=====================================================================
; 78. コイキング の長さの計算がまちがうことがある（BCLessThanDE の余計な ret nc）
;=====================================================================
SECTION "BF78", ROMX[J_CalcMagikarpLength__BCLessThanDE + 3], BANK[JB_CalcMagikarpLength__BCLessThanDE]
	nop

;=====================================================================
; 82. ツボツボ を返すときに手持ちがほかにいないと、マニアがちがうことを言う
;=====================================================================
SECTION "BF82", ROMX[$765b], BANK[$2d]   ; ManiaScript.returnshuckie の ifequal SHUCKIE_FAINTED, .default_postevent
	dw $767b                    ; .nothingleft

;=====================================================================
; 84. ScriptCall で wScriptStack があふれて止まることがある
;=====================================================================
SECTION "BF84", ROMX[J_ScriptCall], BANK[JB_ScriptCall]
	jp ScriptCall_Fix
SECTION "Bank25 free", ROMX[$7f20], BANK[$25]   ; 60fps の後ろ
ScriptCall_Fix:
	ld hl, wScriptStackSize
	ld a, [hl]
	cp 5
	ret nc
	push de
	inc [hl]
	ld e, a
	ld d, 0
	ld hl, wScriptStack
	add hl, de
	add hl, de
	add hl, de
	pop de
	ld a, [wScriptBank]
	ld [hli], a
	ld a, [wScriptPos]
	ld [hli], a
	ld a, [wScriptPos + 1]
	ld [hl], a
	ld a, b
	ld [wScriptBank], a
	ld a, e
	ld [wScriptPos], a
	ld a, d
	ld [wScriptPos + 1], a
	ret

;=====================================================================
; 86. ChooseWildEncounter が野生のポケモンの種類を正しく調べていない（レベルを調べていた）
;=====================================================================
SECTION "BF86", ROMX[J_ChooseWildEncounter__ok + 4], BANK[JB_ChooseWildEncounter__ok]
	ld b, [hl]
	ld a, b
	call J_ValidateTempWildMonSpecies
	jr c, @ + 2 + 12            ; .nowildbattle

;=====================================================================
; 87. RandomUnseenWildMon がいつも朝のポケモンを選ぶ
;=====================================================================
SECTION "BF87", ROMX[J_RandomUnseenWildMon__GetGrassmon], BANK[JB_RandomUnseenWildMon__GetGrassmon]
	ld a, [wTimeOfDay]
	ld bc, NUM_GRASSMON * 2
	call J_AddNTimes
	push hl
	ld bc, 5 + 4 * 2
	add hl, bc

;=====================================================================
; 88. TryObjectEvent で 表にない種類のとき、データをプログラムとして動かしてしまう（pop bc を先に）
;=====================================================================
SECTION "BF88", ROMX[$690d + 10], BANK[$25]   ; jr nc, .nope / pop bc → pop bc / jr nc, .nope
	pop bc
	jr nc, @ + 2 + 5            ; .nope（xor a / ret）

;=====================================================================
; 89. ReadObjectEvents が wObjectMasks まで書いてしまう
;=====================================================================
SECTION "BF89", ROM0[$24ca]                   ; ld a, NUM_OBJECTS / sub c
	call ReadObjectEvents_Count
SECTION "BF home 2", ROM0[$3f84]              ; ホームの空き $3f81-$3f9f
ReadObjectEvents_Count:
	ld a, NUM_OBJECTS - 1
	sub c
	ret nc
	xor a                       ; 多すぎるときも .skip へ（z）
	ret
	ASSERT @ <= $3fa0

;=====================================================================
; 91. BattleAnimCmd_ClearObjs が アニメの物を 6⅔個 分しか消さない
;=====================================================================
SECTION "BF91", ROMX[J_BattleAnimCmd_ClearObjs + 4], BANK[JB_BattleAnimCmd_ClearObjs]   ; ld a, $a0
	db NUM_BATTLE_ANIM_STRUCTS * BATTLEANIMSTRUCT_LENGTH

;=====================================================================
; 92. せってい を開いた瞬間に 左右 を押していると、全部の項目が変わる
;=====================================================================
SECTION "BF92", ROMX[$4baf], BANK[$39]        ; _Option の ld hl, hInMenu
	call Option_ClearJoypad
SECTION "Bank39 free", ROMX[$7fe2], BANK[$39]
Option_ClearJoypad:
	call J_ClearJoypad
	ld hl, hInMenu
	ret

;=====================================================================
; ここから pokegold の docs（金銀だけのバグ）
;=====================================================================
; G1. コインケース：日本版は文の作りがちがっていて、このバグは起きない（直すと逆におかしくなるので直さない）

; G2. セーブしていない状態で殿堂入りすると ボックスがこわれることがある
SECTION "BFG2", ROMX[$65e8], BANK[$21]       ; HallOfFame の ld hl, wHallOfFameCount / ld a, [hl] / cp HOF_MASTER_COUNT
	ld a, BANK(HallOfFame_EraseIfNoSave)
	ld hl, HallOfFame_EraseIfNoSave
	rst $08
SECTION "BF 3F G2", ROMX[FREE_3F + $300], BANK[$3f]
HallOfFame_EraseIfNoSave:
	ld a, [wSavedAtLeastOnce]
	and a
	jr nz, .saved
	ld a, $05
	ld hl, $4cdd                ; ErasePreviousSave
	rst $08
.saved
	ld hl, wHallOfFameCount
	ld a, [hl]
	cp HOF_MASTER_COUNT
	ret

; G6. ハナダジム の水で釣りができる
SECTION "BFG6", ROMX[$45e0 + 8], BANK[$25]   ; MapGroup_Cerulean の CeruleanGym の釣りのグループ
	db FISHGROUP_NONE

;=====================================================================
; 54. port タイルセット（港）の ワープのじゅうたんの左側の角のタイル2つ がまちがっている
;   （pokecrystal の docs の直した絵から2タイルを直し、pokegold の lzcompress で圧縮しなおした。元より短いので同じ所に入る）
;=====================================================================
SECTION "BF54", ROMX[$553c], BANK[$07]
	INCBIN "bf/port_fixed.2bpp.lz"
	ASSERT @ <= $553c + 1035
