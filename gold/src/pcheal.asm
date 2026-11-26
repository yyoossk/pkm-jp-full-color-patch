; ポケモンセンターの 回復（金 日本版）
;
; 1. 回復の あと（ことわった ときも）、主人公が 下を むく。
;    A ボタンを 連打して いても、もう一度 ジョーイさんに 話しかけて「ようこそ」から くりかえさない。
; 2. せっていの「かいふく」（src/clockopt_gold.asm の 8つめ。いちばん下の 行）が「はやい」なら、
;    回復の アニメ（ボールを 機械に のせる・曲）を はぶいて、すぐ 回復する（回復の 音だけ 鳴らす）。
;    しるしは wOptions2（$d1b0）の ビット3（レポートに 書かれる。ビット0 メニューせつめい、1・2 電話の 回数）。
;
; しくみ（元の PokecenterNurseScript（バンク$36:$408a）の 3か所を farsjump に）
;   ・$40bc「pause 20 / turnobject LAST_TALKED, LEFT / … / turnobject LAST_TALKED, DOWN / pause 10」（$40d8 まで）
;       → PcHeal_Heal（ふつうは 元と 同じ 動き、はやいは HealParty と 音）→ $40d8（checkphonecall）に もどる。
;   ・$40f8「pause 10 / waitbutton / closetext / end」（ふつうの おわり）
;       → PcHeal_End（同じ ことを して、さいごに turnobject PLAYER, DOWN）。
;   ・$4100「waitbutton / closetext / setflag ENGINE_CAUGHT_POKERUS / specialphonecall SPECIALCALL_POKERUS / end」
;       （ポケルスの とき）→ PcHeal_EndPokerus（同じ ことを して 下を むく）。
;
; 銀・クリスタルに 入れるとき：下の DEF を その ROM の 値に する。
;   PH_SCRIPT_BANK  PokecenterNurseScript の バンク
;   PH_HEAL         「pause 20 / turnobject LAST_TALKED, LEFT」（8a 14 75 fe 02）の 場所
;   PH_HEAL_RET     その あとの「turnobject LAST_TALKED, DOWN / pause 10」の つぎ（checkphonecall ＝ 9c）
;   PH_END          .done の「turnobject LAST_TALKED, DOWN / pause 10 / waitbutton / closetext / end」の pause 10（8a 0a 53 49 90）
;   PH_END_PKRS     .pokerus の「waitbutton / closetext / setflag」（53 49 36）
;   PH_SP_*         special の 番号（HealParty・HealMachineAnim・RestartMapMusic）
;   ※ クリスタルは ジョーイさんの スクリプトが ちがう（ポケモンセンター2F の 話・ポケルスの 文 など）。
;     「回復の アニメの 所」と「おわりの waitbutton / closetext / end」を さがして 同じ ように する。

INCLUDE "includes.asm"
INCLUDE "src/charmap_jp.inc"

IF !DEF(PH_SCRIPT_BANK)
DEF PH_SCRIPT_BANK     EQU $36
DEF PH_HEAL            EQU $40bc
DEF PH_HEAL_RET        EQU $40d8
DEF PH_END             EQU $40f8
DEF PH_END_PKRS        EQU $4100
DEF PH_SP_HEALPARTY    EQU $1b
DEF PH_SP_HEALANIM     EQU $3d
DEF PH_SP_RESTARTMUSIC EQU $3c
DEF PH_wOptions2       EQU $d1b0
DEF PH_wScriptVar      EQU $d165
DEF PH_BANK            EQU $4b
DEF PH_ADDR            EQU $4400
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
	waitbutton
	closetext
	setflag ENGINE_CAUGHT_POKERUS
	specialphonecall SPECIALCALL_POKERUS
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
