; ポケットモンスター クリスタル（日本版）オリジナルのバグ修正
; 直し方は pret/pokecrystal の docs/bugs_and_glitches.md に合わせた。
; 場所は日本版クリスタルで調べたもの（英語版とはずれている）。

INCLUDE "src/crystal_jp.inc"

; --- このファイルで使うアドレス（日本版）
DEF BattleRandom          EQU $2f71
DEF GetBattleVar          EQU $3990
DEF Multiply              EQU $30e5
DEF GetTilePermission     EQU $1828
DEF hBattleTurn           EQU $ffe4
DEF hMultiplier           EQU $ffb7
DEF hMultiplicand         EQU $ffb4
DEF hProduct              EQU $ffb3
DEF wAttackMissed         EQU $c65b
DEF wEffectFailed         EQU $c701
DEF wPlayerConfuseCount   EQU $c667
DEF wEnemyConfuseCount    EQU $c66f
DEF wBattleType           EQU $d261
DEF wPartyCount           EQU $dc9d
DEF wEnemyMonStatus       EQU $d245
DEF wEnemyMonMaxHP        EQU $d249
DEF wBaseGrowthRate       EQU $d27d

DEF LINK_COLOSSEUM        EQU 3
DEF MAX_STAT_VALUE        EQU 999
DEF PP_MASK               EQU %00111111
DEF BATTLETYPE_TUTORIAL   EQU 3
DEF BATTLE_VARS_SUBSTATUS3_OPP EQU 7
DEF BATTLE_VARS_SUBSTATUS5_OPP EQU 9
DEF BATTLE_VARS_SUBSTATUS5 EQU 4
DEF SUBSTATUS_LOCK_ON     EQU 5
DEF MOON_STONE            EQU $08
DEF MAX_LEVEL             EQU 100

;=====================================================================
; バンク $0D（わざの効果）
;=====================================================================
; 1. ふといホネ・でんきだまで こうげき（とくこう）が 1024 を超えると小さくなる
SECTION "fix thick club", ROMX[$53f1], BANK[$0d]
	jp SpeciesItemBoost_Cap

; 2. 追加効果が100%のわざでも 1/256 で効果が出ない（通信対戦は元のまま）
SECTION "fix effect chance", ROMX[$4ee1], BANK[$0d]
	call EffectChance_Random

; 3. はらだいこ：HP が半分ないのに こうげきが上がる
SECTION "fix belly drum", ROMX[$7c6b], BANK[$0d]
	jp BellyDrum_Fixed

; 4. カウンター・ミラーコート：相手が道具を使ったターンでも成功する
SECTION "fix counter", ROMX[$5850], BANK[$0d]
	call CounterMirrorCoat_Check
SECTION "fix mirror coat", ROMX[$7d23], BANK[$0d]
	call CounterMirrorCoat_Check

; 5. ロックオン・こころのめ のあと、そらをとぶ・あなをほる中の相手に効かないわざがある
SECTION "fix lock-on", ROMX[$7dfb], BANK[$0d]
	jp CheckHiddenOpponent_Fixed

; 6. おんがえし・やつあたり：なつき度によって ダメージが 0 になる
SECTION "fix return", ROMX[$78c2], BANK[$0d]
	jp HappinessPower_Min1
SECTION "fix frustration", ROMX[$7987], BANK[$0d]
	jp HappinessPower_Min1

; 7. へんしん中のポケモンが スケッチで 覚えられないわざを覚える
SECTION "fix sketch", ROMX[$5a89], BANK[$0d]
	ld a, BATTLE_VARS_SUBSTATUS5   ; 相手ではなく自分がへんしん中なら失敗

; 8. 野生のポケモンの テレポートが レベルに関係なく必ず成功する
SECTION "fix teleport", ROMX[$67ea], BANK[$0d]
	jr c, @ + 2 + ($67c6 - $67ec)  ; .failed

SECTION "bank 0d fixes", ROMX[$7f40], BANK[$0d]
SpeciesItemBoost_Cap:
	sla l
	rl h
	ld a, HIGH(MAX_STAT_VALUE)
	cp h
	jr c, .cap
	ret nz
	ld a, LOW(MAX_STAT_VALUE)
	cp l
	ret nc
.cap
	ld hl, MAX_STAT_VALUE
	ret

EffectChance_Random:
	ld a, [wLinkMode]
	cp LINK_COLOSSEUM
	jp z, BattleRandom
	ld a, [hl]
	sub $ff                     ; 100%
	ret nc                       ; 100% なら a = 0 で必ず成功
	jp BattleRandom

BellyDrum_Fixed:
	ld a, $0f
	ld hl, $4c9a                 ; GetHalfMaxHP
	rst $08
	ld a, $0f
	ld hl, $4cd9                 ; CheckUserHasEnoughHP
	rst $08
	jp nc, $7ca0                 ; .failed
	push bc
	call $61c8                   ; BattleCommand_AttackUp2
	pop bc
	ld a, [wAttackMissed]
	and a
	jp nz, $7ca0
	jp $7c82

CounterMirrorCoat_Check:
	ld a, [hli]
	or [hl]
	ret nz
	pop af                       ; わざの処理からぬける
	ld a, 1
	ld [wEffectFailed], a
	and a
	ret

CheckHiddenOpponent_Fixed:
	ld a, BATTLE_VARS_SUBSTATUS5_OPP
	call GetBattleVar
	cpl
	and 1 << SUBSTATUS_LOCK_ON
	ret z
	ld a, BATTLE_VARS_SUBSTATUS3_OPP
	call GetBattleVar
	and $60                      ; SUBSTATUS_FLYING | SUBSTATUS_UNDERGROUND
	ret

HappinessPower_Min1:
	and a
	jr nz, .ok
	inc a
.ok
	ld d, a
	pop bc
	ret

;=====================================================================
; バンク $0F（バトルの中心）
;=====================================================================
; 9. ほろびのうた・まきびしで HP が 0 になっても ひんしにならないことがある
SECTION "fix faint 1", ROMX[$423b], BANK[$0f]
	jp CheckFaint_PlayerThenEnemy_Fixed
SECTION "fix faint 2", ROMX[$425b], BANK[$0f]
	jp CheckFaint_EnemyThenPlayer_Fixed

; 10. はかいのいでんし の こんらんが 256ターン（前のポケモンの残り）続く
SECTION "fix berserk gene", ROMX[$42bf], BANK[$0f]
	call BerserkGene_Confuse
	nop

; 11. かなしばり中で ポイントアップを使ったわざだと わるあがきにならないことがある
SECTION "fix struggle", ROMX[$67c1], BANK[$0f]
	jp UsableMoves_Fixed
; 上の jp で $67c1〜$67c3 を かえたので、PP が ぜんぶ 0 の ときの「jr .force_struggle」（$67ac → $67c3）が
; jp の まん中に とんで、「もう だせる わざが ない」の 文が こわれて いた（ld hl の 上の バイトが のこらない）。
; ここでは a ＝ 0（and PP_MASK の あと）なので、$67c1 の jp に とばせば UsableMoves_Fixed が そのまま わるあがき に する
SECTION "fix struggle jr", ROMX[$67ac], BANK[$0f]
	db $18, $67c1 - ($67ac + 2)       ; jr $67c1

; 12. 最大HP が 3 以下のポケモンと入れかえると止まる
SECTION "fix hp percent 1", ROMX[$72be], BANK[$0f]
	call EnemyHPPercent_Fixed
	jr @ + 2 + 15
SECTION "fix hp percent 2", ROMX[$7359], BANK[$0f]
	call EnemyHPPercent_Fixed
	jr @ + 2 + 15

; 13. 入れかえて出てきた相手に まひ・やけどの 能力ダウンがかからない
SECTION "fix load enemy mon", ROMX[$6b43], BANK[$0f]
	jp LoadEnemyMon_Tail

; 14. グレイシャバッジで とくぼうが上がらないことがある
SECTION "fix glacier badge", ROMX[$6d7e], BANK[$0f]
	call c, BoostStat_KeepA

SECTION "bank 0f fixes", ROMX[$7f40], BANK[$0f]
HasAnyoneFainted:
	call $470f                   ; HasPlayerFainted
	jp nz, $470a                 ; HasEnemyFainted
	ret

CheckFaint_PlayerThenEnemy_Fixed:
.loop
	call .function
	ret c
	call HasAnyoneFainted
	ret nz
	jr .loop
.function
	call $470f
	jp $423e

CheckFaint_EnemyThenPlayer_Fixed:
.loop
	call .function
	ret c
	call HasAnyoneFainted
	ret nz
	jr .loop
.function
	call $470a
	jp $425e

BerserkGene_Confuse:
	set 7, [hl]                  ; SUBSTATUS_CONFUSED
	ldh a, [hBattleTurn]
	and a
	ld hl, wPlayerConfuseCount
	jr z, .got
	ld hl, wEnemyConfuseCount
.got
	call BattleRandom
	and %11
	add 2
	ld [hl], a                   ; 2〜5ターン
	ld a, $0c                    ; BATTLE_VARS_MOVE_ANIM
	ret

UsableMoves_Fixed:
	and PP_MASK
	ret nz
	ld hl, $4b2e                 ; BattleText_MonHasNoMovesLeft
	jp $67c6

EnemyHPPercent_Fixed:
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
	jp Multiply

LoadEnemyMon_Tail:
	call CopyBytes
	jp $6c42                     ; ApplyStatusEffectOnEnemyStats

BoostStat_KeepA:
	push af
	call $6d8e                   ; BoostStat
	pop af
	ret

;=====================================================================
; バンク $03（道具・フィールド）
;=====================================================================
; 15. へんしん中のポケモンを捕まえると メタモンになる
SECTION "fix transform catch", ROMX[$6cc6], BANK[$03]
	db $6cdd - $6cc7             ; jr nz, .load_data

; 16. つりの名人（ボールの使い方を見せる人）：手持ちとボックスがいっぱいだと止まる
SECTION "fix tutorial", ROMX[$6b5f], BANK[$03]
	call CatchTutorial_PartyCount

; 17. どく・まひ・やけど で 捕まえやすくならない
SECTION "fix status catch", ROMX[$6c17], BANK[$03]
	call CatchStatusBonus
	jr @ + 2 + ($6c27 - $6c1c)

; 18. 最大HP が 342 以上のポケモンの 捕まえやすさの計算がおかしい
SECTION "fix catch hp", ROMX[$6bf0], BANK[$03]
	call CatchHPFix
	nop
	nop
	nop

; 19. ムーンボールが効かない
SECTION "fix moon ball 1", ROMX[$6f6f], BANK[$03]
	inc hl
	nop
	nop
SECTION "fix moon ball 2", ROMX[$6f78], BANK[$03]
	cp MOON_STONE

; 20. ラブラブボールが 同じ性別のときに効く
SECTION "fix love ball", ROMX[$6fcb], BANK[$03]
	ret z

; 21. スピードボールが 3匹にしか効かない
SECTION "fix fast ball", ROMX[$6ff1], BANK[$03]
	jr nz, @ + 2 + ($6fe6 - $6ff3)

; 22. ポケモンの上で つりができる
SECTION "fix fishing", ROMX[$51db], BANK[$03]
	call Fish_CheckWaterAndNPC
	jr nc, @ + 2 + ($51e5 - $51e0)
	nop
	nop

; 23. 育て屋から引き取ると けいけんちが減ることがある
SECTION "fix day-care", ROMX[$6055], BANK[$03]
	jp RetrieveBreedmon_Exp

SECTION "bank 03 fixes", ROMX[$7f30], BANK[$03]
CatchTutorial_PartyCount:
	ld a, [wBattleType]
	cp BATTLETYPE_TUTORIAL
	ld a, 0
	ret z
	ld a, [wPartyCount]
	ret

CatchStatusBonus:
	ld a, [wEnemyMonStatus]
	ld c, 10
	and (1 << 5) | %111          ; こおり・ねむり
	ret nz
	ld a, [wEnemyMonStatus]
	ld c, 5
	and a
	ret nz
	ld c, 0
	ret

CatchHPFix:
	ld a, d
	and a
	jr z, .low
	srl d
	rr e
	srl b
	rr c
.low
	ld a, c
	and a
	ret nz
	ld c, 1
	ret

Fish_CheckWaterAndNPC:
	call GetTilePermission
	cp 1                         ; WATER_TILE
	scf
	ret nz
	ld a, $01
	ld hl, $796f                 ; CheckFacingObject（前にだれかいたら carry）
	rst $08
	ret

RetrieveBreedmon_Exp:
	ld d, MAX_LEVEL
	ld a, $14
	ld hl, $4edd                 ; CalcExpAtLevel
	rst $08
	pop bc
	ld hl, 8 + 2                 ; MON_EXP + 2
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
	jr c, .keep                  ; 今のけいけんちのまま
	ld a, b
	ld [hli], a
	ld a, c
	ld [hli], a
	ld a, d
	ld [hl], a
.keep
	and a
	ret

;=====================================================================
; バンク $14
;=====================================================================
; 24. レベル1 の「やや遅い」成長のポケモンの けいけんちが おかしくなる
SECTION "fix exp lv1", ROMX[$4edd], BANK[$14]
	call CalcExpAtLevel_Lv1

SECTION "bank 14 fixes", ROMX[$79d0], BANK[$14]
CalcExpAtLevel_Lv1:
	ld a, d
	dec a
	jr nz, .formula
	pop hl                       ; CalcExpAtLevel からぬける
	ld hl, hProduct
	ld [hli], a
	ld [hli], a
	ld [hli], a
	ld [hl], a
	ret
.formula
	ld a, [wBaseGrowthRate]
	ret

;=====================================================================
; データ
;=====================================================================
; 25. ドラゴンのウロコ（りゅうのキバではなく）で ドラゴンわざが強くなる
SECTION "fix dragon fang", ROMX[$69fa + 7 * ($90 - 1) + 2], BANK[$01]
	db $40, 10                   ; りゅうのキバ：HELD_DRAGON_BOOST, 10
SECTION "fix dragon scale", ROMX[$69fa + 7 * ($97 - 1) + 2], BANK[$01]
	db 0, 0                      ; ドラゴンのウロコ：効果なし

; 26. ぼうぎょを下げるわざ（とけるようえき・アイアンテール・いわくだき）が みがわりを壊した後でも下げる
SECTION "fix defense down hit", ROMX[$7864 + 17], BANK[$09]
	db $7f, $8d, $ff, $ff        ; defensedown / statdownmessage / endmove

; 27. 攻撃して自分の能力を上げるわざ（はがねのつばさ・メタルクロー・げんしのちから）が
;     相手をたおすと上がらない
SECTION "fix defense up hit", ROMX[$78dd + 15], BANK[$09]
	db $71, $8c, $11, $12, $ff   ; defenseup / statupmessage / checkfaint / buildopponentrage / endmove
SECTION "fix attack up hit", ROMX[$78f1 + 15], BANK[$09]
	db $70, $8c, $11, $12, $ff
SECTION "fix all up hit", ROMX[$7905 + 15], BANK[$09]
	db $a4, $11, $12, $ff

; 28. もらったけいけんちが 5けた（10000以上）だと 正しく出ない
SECTION "fix exp text", ROMX[$714d], BANK[$0f]
	db $25

; 29. かしこいAI：自分がもうどくなのに くろいまなざしを使いたがる
SECTION "fix ai mean look", ROMX[$4e26 + 1], BANK[$0e]
	dw $c660                     ; wPlayerSubStatus5
