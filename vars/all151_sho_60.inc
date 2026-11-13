; all151_sho_60 用の場所の表（Ver.2.32 の中で、変更を当てる場所）
DEF Bankswitch EQU $3596
DEF HAS_KIT_HUD EQU 1
DEF HAS_PLACE_SIGN EQU 1
DEF Predef EQU $3DFC
DEF DelayFrames EQU $36E0
DEF JoypadLowSensitivity EQU $37D8
DEF GetItemName EQU $2F86
DEF PrintNumber EQU $3BEC
DEF HAS_FOLLOW EQU 0           ; 連れ歩き（金銀グラフィックの完全版・151匹そろう版）
DEF HandleMenuInput_ EQU $3A69
DEF PlaceUnfilledArrowMenuCursor EQU $3B79
DEF RemovePokemonStub EQU $38C6
DEF DisplayTextID EQU $289E
DEF FwTalkHookAddr EQU $3F89
DEF PrintText EQU $3BD6
DEF YesNoChoice EQU $35AC
DEF GiveItem EQU $3DBD
DEF HAS_MOVE_RELEARN EQU 1     ; わざを思い出させてくれる人がいる
DEF ListMenuGetNameAddr EQU $2CAF ; リストメニューで A：「ld a, 1 / ld [$D094], a / call GetName」
DEF GetName EQU $3712
DEF HAS_TM_MART EQU 1          ; 殿堂入りのあと、わざマシンの店で一回切りのわざマシンも売る
DEF HAS_CHANGEBOX_FIX EQU 1     ; STARTボタンの「パソコン」でボックスをかえたあとのフリーズの直し
DEF RestoreMapTextPointer EQU $3E94
DEF SetMapTextPointer EQU $3E9E
DEF TextPredefs EQU $3EB1
DEF ChangeBoxRedrawBank EQU $09  ; ChangeBox の最後に jp していた所
DEF ChangeBoxRedraw EQU $6FBE
DEF HAS_PC_ITEM_DESC EQU 1      ; パソコンの「どうぐを ひきだす」で道具の説明を出す
DEF HandleMenuInputW EQU $3A65  ; HandleMenuInput（入口）
