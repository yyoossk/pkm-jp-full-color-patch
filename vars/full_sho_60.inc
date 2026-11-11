; full_sho_60 用の場所の表（Ver.2.32 の中で、変更を当てる場所）
DEF Bankswitch EQU $3595        ; バンクを切りかえて hl を呼ぶ処理
DEF HAS_KIT_HUD EQU 1           ; 戦闘の HUD にキットの呼び出しがある
DEF HAS_PLACE_SIGN EQU 1        ; 場所の名前の看板がある
DEF Predef EQU $3DFB
DEF DelayFrames EQU $36DF
DEF JoypadLowSensitivity EQU $37D7
DEF GetItemName EQU $2F85
DEF PrintNumber EQU $3BEB
DEF HAS_FOLLOW EQU 0           ; 連れ歩き（金銀グラフィックの完全版・151匹そろう版）
DEF HandleMenuInput_ EQU $3A68
DEF PlaceUnfilledArrowMenuCursor EQU $3B78
DEF RemovePokemonStub EQU $38C5
DEF DisplayTextID EQU $289D
DEF FwTalkHookAddr EQU $3F88
DEF PrintText EQU $3BD5
DEF YesNoChoice EQU $35AB
DEF GiveItem EQU $3DBC
DEF HAS_MOVE_RELEARN EQU 1     ; わざを思い出させてくれる人がいる
DEF ListMenuGetNameAddr EQU $2CAE ; リストメニューで A：「ld a, 1 / ld [$D094], a / call GetName」
DEF GetName EQU $3711
DEF HAS_TM_MART EQU 1          ; 殿堂入りのあと、わざマシンの店で一回切りのわざマシンも売る
