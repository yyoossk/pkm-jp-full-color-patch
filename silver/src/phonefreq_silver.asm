; 電話の回数：銀 日本版（後期版）の値（アドレスは 金と 同じ。置き場所だけ ちがう）
DEF PF_GEAR_BANK        EQU $24
DEF PF_CHECK_HOOK       EQU $4074   ; CheckPhoneCall（call CheckStandingOnEntrance）
DEF PF_JOYPAD_HOOK      EQU $50cf   ; PokegearPhone_Joypad（ld hl, hJoyPressed）
DEF PF_DRAW_HOOK        EQU $4dc3   ; .Phone の call PokegearPhone_UpdateDisplayList
DEF PF_UpdateDisplayList EQU $5241
DEF PF_GEAR_FREE        EQU $7fb0   ; バンク$24 の 空き
DEF PF_CheckStandingOnEntrance EQU $170d
DEF PF_Random           EQU $305e
DEF PF_PlaceString      EQU $0f46
DEF PF_PlaySFX          EQU $3d45
DEF PF_wOptions2        EQU $d1b0
DEF PF_hJoyPressed      EQU $ffa9
DEF PF_hBGMapMode       EQU $ffd6
DEF PF_COORD            EQU $c3a0 + 11 * 20 + 1   ; hlcoord 1, 11（10行めは 4人めの 行なので 濁点の ある 文字は つかわない）
DEF PF_BANK             EQU $47
DEF PF_ADDR             EQU $4400
INCLUDE "src/phonefreq.asm"
