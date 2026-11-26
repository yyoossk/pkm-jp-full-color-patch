; ポケモンセンターの 回復（クリスタル 日本版。金 Ver.1.6.0 の src/pcheal.asm から）
;
; 1. 回復の あと（「いいえ」で ことわった とき・ポケルスの とき も）、主人公が 下を むく。
;    A ボタンを 連打して いても、もう一度 ジョーイさんに 話しかけて「いらっしゃいませ」から くりかえさない。
; 2. せっていの「かいふく」（src/clockopt.asm の 項目 8。16行目）が「はやい」なら、
;    回復の アニメ（ボールを 機械に のせる・曲・ジョーイさんが 横を むく）を はぶいて、すぐ 回復する（回復の 音だけ 鳴らす）。
;    しるしは wOptions2（$cfc5）の ビット3（レポートに 書かれる。ビット0 メニューせつめい、1・2 電話の 回数）。
;
; しくみ（元の PokecenterNurseScript（バンク$2f）の 3か所を farsjump に）
;   ・$2f:$40f8「pause 20 / special StubbedTrainerRankings_Healings / turnobject LAST_TALKED, LEFT / pause 10 /
;       special HealParty / playmusic MUSIC_NONE / setval HEALMACHINE_POKECENTER / special HealMachineAnim / pause 30 /
;       special RestartMapMusic / turnobject LAST_TALKED, DOWN / pause 10」（$4117 の checkphonecall まで）
;       → PcHeal_Heal（ふつうは 元と 同じ 動き、はやいは HealParty と 音）→ $4117 に もどる。
;   ・$2f:$4137 .done の「pause 10 / waitbutton / closetext / end」（ことわった ときも ここを 通る）
;       → PcHeal_End（同じ ことを して、さいごに turnobject PLAYER, DOWN）。
;   ・$2f:$414f .pokerus_done の「setflag ENGINE_CAUGHT_POKERUS / specialphonecall SPECIALCALL_POKERUS / end」
;       （ポケルスの 2つの 文〔ふつう・ポケモンコミュニケーションセンター〕の waitbutton / closetext の あと）
;       → PcHeal_EndPokerus（同じ ことを して 下を むく）。
;   special の 番号（クリスタル 日本版）：HealParty $1b・HealMachineAnim $3e・RestartMapMusic $3d・
;     StubbedTrainerRankings_Healings $9d（元の ならびを そのまま 入れる）。
;   本体は 空いて いる バンク$7c（$7c:$4000〜）。

INCLUDE "src/safari/crystal_includes.asm"   ; pokecrystal の 定数・マクロ（スクリプトの 命令の 番号は 英語版 金銀）
INCLUDE "src/charmap_jp.inc"

IF !DEF(PH_SCRIPT_BANK)
DEF PH_SCRIPT_BANK     EQU $2f
DEF PH_HEAL            EQU $40f8
DEF PH_HEAL_RET        EQU $4117
DEF PH_END             EQU $4137
DEF PH_END_PKRS        EQU $414f
DEF PH_SP_HEALPARTY    EQU $1b
DEF PH_SP_HEALANIM     EQU $3e
DEF PH_SP_RESTARTMUSIC EQU $3d
DEF PH_SP_STUB_HEALS   EQU $9d
DEF PH_wOptions2       EQU $cfc5
DEF PH_wScriptVar      EQU $c2dd
DEF PH_BANK            EQU $7c
DEF PH_ADDR            EQU $4000
ENDC
DEF PH_FAST_BIT EQU 3

SECTION "pcheal hook heal", ROMX[PH_HEAL], BANK[PH_SCRIPT_BANK]
	db farsjump_command, PH_BANK
	dw PcHeal_Heal
SECTION "pcheal hook end", ROMX[PH_END], BANK[PH_SCRIPT_BANK]
	db farsjump_command, PH_BANK
	dw PcHeal_End
SECTION "pcheal hook pokerus", ROMX[PH_END_PKRS], BANK[PH_SCRIPT_BANK]
	db farsjump_command, PH_BANK
	dw PcHeal_EndPokerus

SECTION "pcheal", ROMX[PH_ADDR], BANK[PH_BANK]
PcHeal_Heal:
	callasm PcHeal_IsFast
	iftrue .fast
	pause 20
	db special_command
	dw PH_SP_STUB_HEALS
	turnobject LAST_TALKED, LEFT
	pause 10
	db special_command
	dw PH_SP_HEALPARTY
	playmusic MUSIC_NONE
	setval HEALMACHINE_POKECENTER
	db special_command
	dw PH_SP_HEALANIM
	pause 30
	db special_command
	dw PH_SP_RESTARTMUSIC
	turnobject LAST_TALKED, DOWN
	pause 10
	sjump .back
.fast
	db special_command
	dw PH_SP_STUB_HEALS
	db special_command
	dw PH_SP_HEALPARTY
	playsound SFX_FULL_HEAL
	waitsfx
.back
	db farsjump_command, PH_SCRIPT_BANK
	dw PH_HEAL_RET

PcHeal_End:
	pause 10
	waitbutton
	closetext
	turnobject PLAYER, DOWN
	end

PcHeal_EndPokerus:
	; 元の「setflag ENGINE_CAUGHT_POKERUS / specialphonecall SPECIALCALL_POKERUS」（6バイト）を そのまま
	INCBIN "base.gbc", PH_SCRIPT_BANK * $4000 + PH_END_PKRS - $4000, 6
	turnobject PLAYER, DOWN
	end

; wScriptVar ＝ 1：はやい かいふく
PcHeal_IsFast:
	ld a, [PH_wOptions2]
	and 1 << PH_FAST_BIT
	jr z, .set
	ld a, 1
.set
	ld [PH_wScriptVar], a
	ret
