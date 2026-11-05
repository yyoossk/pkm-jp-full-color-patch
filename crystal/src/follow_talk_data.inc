; tools/follow_talk_gen.py で 作る（手で 書きかえない）。会話の もとは 連れ歩きキットの 会話文案.md
; 表：種類（0 = どれでも）、タイプ（$ff = どれでも）、ランドマーク（$ff）、マップ（グループ・番号。0, 0 = どれでも）、
;     状態（0 = どれでも）、イベントフラグ（$ffff = 見ない。立って いる とき だけ）、アイコン、文の 表
FollowerTalkTable:
	db 0, $ff, $ff, $00, $00, $07
	dw $ffff
	db 6
	dw FwTexts_0
	db 0, $ff, $ff, $00, $00, $08
	dw $ffff
	db 3
	dw FwTexts_1
	db 0, $ff, $ff, $00, $00, $10
	dw $ffff
	db 0
	dw FwTexts_2
	db 0, $ff, $ff, $00, $00, $20
	dw $ffff
	db 0
	dw FwTexts_3
	db 0, $ff, $ff, $00, $00, $40
	dw $ffff
	db 5
	dw FwTexts_4
	db 253, $ff, $ff, $00, $00, $00
	dw $ffff
	db 1
	dw FwTexts_5
	db 152, $ff, $02, $00, $00, $00
	dw $ffff
	db 2
	dw FwTexts_6
	db 158, $ff, $04, $00, $00, $00
	dw $ffff
	db 2
	dw FwTexts_7
	db 155, $ff, $05, $00, $00, $00
	dw $ffff
	db 2
	dw FwTexts_8
	db 0, $19, $2c, $00, $00, $00
	dw $ffff
	db 2
	dw FwTexts_9
	db 69, $ff, $07, $00, $00, $00
	dw $ffff
	db 2
	dw FwTexts_10
	db 201, $ff, $09, $00, $00, $00
	dw $ffff
	db 1
	dw FwTexts_11
	db 0, $14, $0c, $00, $00, $00
	dw $ffff
	db 2
	dw FwTexts_12
	db 79, $ff, $0d, $00, $00, $00
	dw $002b
	db 2
	dw FwTexts_13
	db 80, $ff, $0d, $00, $00, $00
	dw $002b
	db 2
	dw FwTexts_13
	db 79, $ff, $0d, $00, $00, $00
	dw $ffff
	db 3
	dw FwTexts_14
	db 80, $ff, $0d, $00, $00, $00
	dw $ffff
	db 3
	dw FwTexts_14
	db 0, $14, $0d, $00, $00, $00
	dw $ffff
	db 3
	dw FwTexts_15
	db 0, $15, $0d, $00, $00, $00
	dw $ffff
	db 2
	dw FwTexts_16
	db 83, $ff, $0e, $00, $00, $00
	dw $ffff
	db 2
	dw FwTexts_13
	db 251, $ff, $0e, $00, $00, $00
	dw $ffff
	db 4
	dw FwTexts_17
	db 214, $ff, $0e, $00, $00, $00
	dw $ffff
	db 2
	dw FwTexts_18
	db 214, $ff, $32, $00, $00, $00
	dw $ffff
	db 2
	dw FwTexts_18
	db 185, $ff, $14, $00, $00, $00
	dw $ffff
	db 1
	dw FwTexts_19
	db 35, $ff, $10, $0b, $03, $00
	dw $ffff
	db 2
	dw FwTexts_20
	db 0, $17, $11, $00, $00, $00
	dw $ffff
	db 5
	dw FwTexts_21
	db 0, $08, $11, $00, $00, $00
	dw $ffff
	db 1
	dw FwTexts_22
	db 0, $07, $13, $00, $00, $00
	dw $ffff
	db 2
	dw FwTexts_23
	db 172, $ff, $16, $04, $05, $00
	dw $ffff
	db 2
	dw FwTexts_24
	db 182, $ff, $16, $04, $05, $00
	dw $ffff
	db 2
	dw FwTexts_25
	db 243, $ff, $18, $00, $00, $00
	dw $ffff
	db 0
	dw FwTexts_26
	db 244, $ff, $18, $00, $00, $00
	dw $ffff
	db 0
	dw FwTexts_26
	db 245, $ff, $18, $00, $00, $00
	dw $ffff
	db 0
	dw FwTexts_26
	db 250, $ff, $18, $00, $00, $00
	dw $ffff
	db 0
	dw FwTexts_27
	db 250, $ff, $17, $00, $00, $00
	dw $ffff
	db 0
	dw FwTexts_28
	db 128, $ff, $1a, $00, $00, $00
	dw $ffff
	db 0
	dw FwTexts_29
	db 241, $ff, $1a, $00, $00, $00
	dw $ffff
	db 2
	dw FwTexts_30
	db 181, $ff, $1c, $00, $00, $00
	dw $ffff
	db 2
	dw FwTexts_31
	db 98, $ff, $21, $00, $00, $00
	dw $ffff
	db 2
	dw FwTexts_32
	db 60, $ff, $1e, $00, $00, $00
	dw $ffff
	db 2
	dw FwTexts_33
	db 60, $ff, $1f, $00, $00, $00
	dw $ffff
	db 2
	dw FwTexts_33
	db 249, $ff, $1f, $00, $00, $00
	dw $ffff
	db 0
	dw FwTexts_34
	db 0, $15, $1f, $00, $00, $00
	dw $ffff
	db 2
	dw FwTexts_35
	db 0, $05, $22, $00, $00, $00
	dw $ffff
	db 2
	dw FwTexts_36
	db 129, $ff, $26, $00, $00, $00
	dw $ffff
	db 2
	dw FwTexts_37
	db 130, $ff, $26, $00, $00, $00
	dw $ffff
	db 2
	dw FwTexts_13
	db 101, $ff, $24, $03, $31, $00
	dw $ffff
	db 0
	dw FwTexts_38
	db 101, $ff, $24, $03, $32, $00
	dw $ffff
	db 0
	dw FwTexts_38
	db 101, $ff, $24, $03, $33, $00
	dw $ffff
	db 0
	dw FwTexts_38
	db 0, $19, $28, $00, $00, $00
	dw $ffff
	db 2
	dw FwTexts_39
	db 0, $16, $28, $00, $00, $00
	dw $ffff
	db 3
	dw FwTexts_40
	db 0, $19, $24, $02, $02, $00
	dw $ffff
	db 2
	dw FwTexts_39
	db 0, $16, $24, $02, $02, $00
	dw $ffff
	db 3
	dw FwTexts_40
	db 0, $1a, $2a, $00, $00, $00
	dw $ffff
	db 0
	dw FwTexts_41
	db 154, $ff, $58, $00, $00, $00
	dw $ffff
	db 0
	dw FwTexts_42
	db 157, $ff, $58, $00, $00, $00
	dw $ffff
	db 0
	dw FwTexts_43
	db 160, $ff, $58, $00, $00, $00
	dw $ffff
	db 0
	dw FwTexts_44
	db 1, $ff, $30, $00, $00, $00
	dw $ffff
	db 2
	dw FwTexts_45
	db 4, $ff, $32, $00, $00, $00
	dw $ffff
	db 2
	dw FwTexts_46
	db 172, $ff, $32, $00, $00, $00
	dw $ffff
	db 4
	dw FwTexts_47
	db 172, $ff, $44, $00, $00, $00
	dw $ffff
	db 4
	dw FwTexts_47
	db 25, $ff, $32, $00, $00, $00
	dw $ffff
	db 4
	dw FwTexts_47
	db 25, $ff, $44, $00, $00, $00
	dw $ffff
	db 4
	dw FwTexts_47
	db 26, $ff, $32, $00, $00, $00
	dw $ffff
	db 4
	dw FwTexts_47
	db 26, $ff, $44, $00, $00, $00
	dw $ffff
	db 4
	dw FwTexts_47
	db 7, $ff, $34, $00, $00, $00
	dw $ffff
	db 3
	dw FwTexts_48
	db 173, $ff, $35, $00, $00, $00
	dw $ffff
	db 2
	dw FwTexts_49
	db 35, $ff, $35, $00, $00, $00
	dw $ffff
	db 2
	dw FwTexts_49
	db 36, $ff, $35, $00, $00, $00
	dw $ffff
	db 2
	dw FwTexts_49
	db 95, $ff, $42, $00, $00, $00
	dw $ffff
	db 2
	dw FwTexts_50
	db 208, $ff, $42, $00, $00, $00
	dw $ffff
	db 2
	dw FwTexts_50
	db 0, $05, $42, $00, $00, $00
	dw $ffff
	db 2
	dw FwTexts_51
	db 50, $ff, $3e, $00, $00, $00
	dw $ffff
	db 2
	dw FwTexts_52
	db 51, $ff, $3e, $00, $00, $00
	dw $ffff
	db 2
	dw FwTexts_52
	db 0, $18, $48, $19, $08, $00
	dw $ffff
	db 1
	dw FwTexts_53
	db 137, $ff, $47, $00, $00, $00
	dw $ffff
	db 1
	dw FwTexts_54
	db 132, $ff, $4d, $00, $00, $00
	dw $ffff
	db 1
	dw FwTexts_55
	db 0, $02, $50, $00, $00, $00
	dw $ffff
	db 2
	dw FwTexts_56
	db 0, $08, $45, $00, $00, $00
	dw $ffff
	db 2
	dw FwTexts_57
	db 0, $ff, $ff, $00, $00, $00
	dw $ffff
	db 2
	dw FwTexts_Default
	db $fe ; おわり
DEF FW_TALK_ROW EQU 11

FwTexts_0:
	db 1
	dw FwTexts_0_0
FwTexts_1:
	db 1
	dw FwTexts_1_0
FwTexts_2:
	db 1
	dw FwTexts_2_0
FwTexts_3:
	db 1
	dw FwTexts_3_0
FwTexts_4:
	db 1
	dw FwTexts_4_0
FwTexts_5:
	db 1
	dw FwTexts_5_0
FwTexts_6:
	db 2
	dw FwTexts_6_0
	dw FwTexts_6_1
FwTexts_7:
	db 2
	dw FwTexts_7_0
	dw FwTexts_7_1
FwTexts_8:
	db 2
	dw FwTexts_8_0
	dw FwTexts_8_1
FwTexts_9:
	db 1
	dw FwTexts_9_0
FwTexts_10:
	db 2
	dw FwTexts_10_0
	dw FwTexts_10_1
FwTexts_11:
	db 5
	dw FwTexts_11_0
	dw FwTexts_11_1
	dw FwTexts_11_2
	dw FwTexts_11_3
	dw FwTexts_11_4
FwTexts_12:
	db 1
	dw FwTexts_12_0
FwTexts_13:
	db 1
	dw FwTexts_13_0
FwTexts_14:
	db 1
	dw FwTexts_14_0
FwTexts_15:
	db 1
	dw FwTexts_15_0
FwTexts_16:
	db 1
	dw FwTexts_16_0
FwTexts_17:
	db 2
	dw FwTexts_17_0
	dw FwTexts_17_1
FwTexts_18:
	db 1
	dw FwTexts_18_0
FwTexts_19:
	db 1
	dw FwTexts_19_0
FwTexts_20:
	db 1
	dw FwTexts_20_0
FwTexts_21:
	db 1
	dw FwTexts_21_0
FwTexts_22:
	db 1
	dw FwTexts_22_0
FwTexts_23:
	db 1
	dw FwTexts_23_0
FwTexts_24:
	db 1
	dw FwTexts_24_0
FwTexts_25:
	db 1
	dw FwTexts_25_0
FwTexts_26:
	db 1
	dw FwTexts_26_0
FwTexts_27:
	db 1
	dw FwTexts_27_0
FwTexts_28:
	db 1
	dw FwTexts_28_0
FwTexts_29:
	db 1
	dw FwTexts_29_0
FwTexts_30:
	db 1
	dw FwTexts_30_0
FwTexts_31:
	db 1
	dw FwTexts_31_0
FwTexts_32:
	db 1
	dw FwTexts_32_0
FwTexts_33:
	db 1
	dw FwTexts_33_0
FwTexts_34:
	db 1
	dw FwTexts_34_0
FwTexts_35:
	db 1
	dw FwTexts_35_0
FwTexts_36:
	db 1
	dw FwTexts_36_0
FwTexts_37:
	db 1
	dw FwTexts_37_0
FwTexts_38:
	db 1
	dw FwTexts_38_0
FwTexts_39:
	db 3
	dw FwTexts_39_0
	dw FwTexts_39_1
	dw FwTexts_39_2
FwTexts_40:
	db 2
	dw FwTexts_40_0
	dw FwTexts_40_1
FwTexts_41:
	db 5
	dw FwTexts_41_0
	dw FwTexts_41_1
	dw FwTexts_41_2
	dw FwTexts_41_3
	dw FwTexts_41_4
FwTexts_42:
	db 1
	dw FwTexts_42_0
FwTexts_43:
	db 1
	dw FwTexts_43_0
FwTexts_44:
	db 1
	dw FwTexts_44_0
FwTexts_45:
	db 2
	dw FwTexts_45_0
	dw FwTexts_45_1
FwTexts_46:
	db 1
	dw FwTexts_46_0
FwTexts_47:
	db 2
	dw FwTexts_47_0
	dw FwTexts_47_1
FwTexts_48:
	db 1
	dw FwTexts_48_0
FwTexts_49:
	db 2
	dw FwTexts_49_0
	dw FwTexts_49_1
FwTexts_50:
	db 1
	dw FwTexts_50_0
FwTexts_51:
	db 4
	dw FwTexts_51_0
	dw FwTexts_51_1
	dw FwTexts_51_2
	dw FwTexts_51_3
FwTexts_52:
	db 1
	dw FwTexts_52_0
FwTexts_53:
	db 1
	dw FwTexts_53_0
FwTexts_54:
	db 1
	dw FwTexts_54_0
FwTexts_55:
	db 1
	dw FwTexts_55_0
FwTexts_56:
	db 1
	dw FwTexts_56_0
FwTexts_57:
	db 1
	dw FwTexts_57_0
FwTexts_Default:
	db 1
	dw FwTexts_Default_0
FwTexts_0_0: ; 〈〉は/すこし　ねむそうだ
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "すこし　ねむそうだ"
	db $57
FwTexts_1_0: ; 〈〉は/ぐあいが　わるそうだ
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "ぐあいが　わるそうだ"
	db $57
FwTexts_2_0: ; 〈〉は/すこし　いたそうだ
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "すこし　いたそうだ"
	db $57
FwTexts_3_0: ; 〈〉は/こおりづけに　なっている！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "こおりづけに　なっている！"
	db $57
FwTexts_4_0: ; 〈〉は/うごきが　にぶく　なっている
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "うごきが　にぶく　なっている"
	db $57
FwTexts_5_0: ; 〈〉は/ときどき　うごいている……
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "ときどき　うごいている……"
	db $57
FwTexts_6_0: ; 〈〉は/はっぱを　ふりまわしている
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "はっぱを　ふりまわしている"
	db $57
FwTexts_6_1: ; 〈〉は/はっぱを　ぴくぴく　させている
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "はっぱを　ぴくぴく　させている"
	db $57
FwTexts_7_0: ; 〈〉は/あごを　うごかしている
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "あごを　うごかしている"
	db $57
FwTexts_7_1: ; 〈〉は/くちを　ぱくぱく　させている
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "くちを　ぱくぱく　させている"
	db $57
FwTexts_8_0: ; 〈〉は/ひのこを　いくつか　はいた
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "ひのこを　いくつか　はいた"
	db $57
FwTexts_8_1: ; 〈〉は/ひのこを　ひとつ　はいた……
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "ひのこを　ひとつ　はいた……"
	db $57
FwTexts_9_0: ; 〈〉は/さむくなって　ごきげんだ
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "さむくなって　ごきげんだ"
	db $57
FwTexts_10_0: ; 〈〉は/きままに　ゆらゆら　おどった
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "きままに　ゆらゆら　おどった"
	db $57
FwTexts_10_1: ; 〈〉は/ふしぎな　おどりを　おどった
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "ふしぎな　おどりを　おどった"
	db $57
FwTexts_11_0: ; 〈〉から/ふしぎな　おとが　きこえる……
	db $01
	dw wPartyMonNicknames
	db $00
	db "から"
	db $4f
	db "ふしぎな　おとが　きこえる……"
	db $57
FwTexts_11_1: ; 〈〉は……/くるくる　まわりはじめた
	db $01
	dw wPartyMonNicknames
	db $00
	db "は……"
	db $4f
	db "くるくる　まわりはじめた"
	db $57
FwTexts_11_2: ; 〈〉が/うなっている¶まるで　しゃべって/いるみたいだ……
	db $01
	dw wPartyMonNicknames
	db $00
	db "が"
	db $4f
	db "うなっている"
	db $51
	db "まるで　しゃべって"
	db $4f
	db "いるみたいだ……"
	db $57
FwTexts_11_3: ; ポケモンは/うごかない
	db $00
	db "ポケモンは"
	db $4f
	db "うごかない"
	db $57
FwTexts_11_4: ; ポケモンが/なにか　うたっている？
	db $00
	db "ポケモンが"
	db $4f
	db "なにか　うたっている？"
	db $57
FwTexts_12_0: ; ポケモンは/あつくて　ごきげんだ！
	db $00
	db "ポケモンは"
	db $4f
	db "あつくて　ごきげんだ！"
	db $57
FwTexts_13_0: ; 〈〉は/とても　うれしそうだ
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "とても　うれしそうだ"
	db $57
FwTexts_14_0: ; ポケモンは/なんだか　かなしそうだ
	db $00
	db "ポケモンは"
	db $4f
	db "なんだか　かなしそうだ"
	db $57
FwTexts_15_0: ; ポケモンは/じめんの　みずが　いやみたいだ¶〈〉は/ぬれて　ごきげんななめだ……
	db $00
	db "ポケモンは"
	db $4f
	db "じめんの　みずが　いやみたいだ"
	db $51
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "ぬれて　ごきげんななめだ……"
	db $57
FwTexts_16_0: ; 〈〉は/うれしそうに　はねまわっている！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "うれしそうに　はねまわっている！"
	db $57
FwTexts_17_0: ; 〈〉は/たのしそうに　おどった！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "たのしそうに　おどった！"
	db $57
FwTexts_17_1: ; 〈〉は/うつくしく　おどった！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "うつくしく　おどった！"
	db $57
FwTexts_18_0: ; 〈〉は/きに　しがみついている！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "きに　しがみついている！"
	db $57
FwTexts_19_0: ; 〈〉は/ぴくりとも　うごかない……¶きの　まねを/しているようだ！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "ぴくりとも　うごかない……"
	db $51
	db "きの　まねを"
	db $4f
	db "しているようだ！"
	db $57
FwTexts_20_0: ; 〈〉は/ゆびを　ふって　おどっている！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "ゆびを　ふって　おどっている！"
	db $57
FwTexts_21_0: ; 〈〉は/びりびり　きているようだ！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "びりびり　きているようだ！"
	db $57
FwTexts_22_0: ; 〈〉は/なにかを　けいかいしている……
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "なにかを　けいかいしている……"
	db $57
FwTexts_23_0: ; 〈〉は/すこし　こうふん　している
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "すこし　こうふん　している"
	db $57
FwTexts_24_0: ; 〈〉は/まいこはんと　いっしょに　おどった！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "まいこはんと　いっしょに　おどった！"
	db $57
FwTexts_25_0: ; 〈〉は/まいこはんより　じょうずに/おどった！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "まいこはんより　じょうずに"
	db $55
	db "おどった！"
	db $57
FwTexts_26_0: ; 〈〉は/おおきな　こえで　ほえた！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "おおきな　こえで　ほえた！"
	db $57
FwTexts_27_0: ; 〈〉の　こえで/とうが　ゆれた！
	db $01
	dw wPartyMonNicknames
	db $00
	db "の　こえで"
	db $4f
	db "とうが　ゆれた！"
	db $57
FwTexts_28_0: ; 〈〉は/そらを　みあげて　さけんでいる！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "そらを　みあげて　さけんでいる！"
	db $57
FwTexts_29_0: ; 〈〉は/とつぜん　ほえた！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "とつぜん　ほえた！"
	db $57
FwTexts_30_0: ; 〈〉は　うれしくて/ころがり　はじめた
	db $01
	dw wPartyMonNicknames
	db $00
	db "は　うれしくて"
	db $4f
	db "ころがり　はじめた"
	db $57
FwTexts_31_0: ; 〈〉は　アカリちゃんと/いっしょに　ひかった！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は　アカリちゃんと"
	db $4f
	db "いっしょに　ひかった！"
	db $57
FwTexts_32_0: ; 〈〉は/よこに　あるいた！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "よこに　あるいた！"
	db $57
FwTexts_33_0: ; 〈〉は/おなかを　ゆらした
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "おなかを　ゆらした"
	db $57
FwTexts_34_0: ; 〈〉は　ながい　からだを/うごかして　おおきく　ほえた！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は　ながい　からだを"
	db $4f
	db "うごかして　おおきく　ほえた！"
	db $57
FwTexts_35_0: ; 〈〉は/ぬれて　うれしそうだ！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "ぬれて　うれしそうだ！"
	db $57
FwTexts_36_0: ; 〈〉は/やまを　みあげている¶のぼるのが/たのしみな　ようだ
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "やまを　みあげている"
	db $51
	db "のぼるのが"
	db $4f
	db "たのしみな　ようだ"
	db $57
FwTexts_37_0: ; 〈〉は/いつもより　はねている！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "いつもより　はねている！"
	db $57
FwTexts_38_0: ; 〈〉は/ふるえている！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "ふるえている！"
	db $57
FwTexts_39_0: ; わっ！　つめたい　かぜが/ふいた！¶でも　うれしそう？
	db $00
	db "わっ！　つめたい　かぜが"
	db $4f
	db "ふいた！"
	db $51
	db "でも　うれしそう？"
	db $57
FwTexts_39_1: ; 〈〉は/さむくて　ごきげんだ！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "さむくて　ごきげんだ！"
	db $57
FwTexts_39_2: ; 〈〉は　さむくて/うれしそうに　よろこんでいる！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は　さむくて"
	db $4f
	db "うれしそうに　よろこんでいる！"
	db $57
FwTexts_40_0: ; 〈〉は/さむくて　ごきげんななめだ……
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "さむくて　ごきげんななめだ……"
	db $57
FwTexts_40_1: ; 〈〉は　さむくて/からだを　ちぢめた……
	db $01
	dw wPartyMonNicknames
	db $00
	db "は　さむくて"
	db $4f
	db "からだを　ちぢめた……"
	db $57
FwTexts_41_0: ; 〈〉は/とつぜん　ほえた！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "とつぜん　ほえた！"
	db $57
FwTexts_41_1: ; 〈〉は/こうふん　している！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "こうふん　している！"
	db $57
FwTexts_41_2: ; 〈〉は/とつぜん　とおぼえした！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "とつぜん　とおぼえした！"
	db $57
FwTexts_41_3: ; 〈〉は/じっと　あなたを　みつめている
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "じっと　あなたを　みつめている"
	db $57
FwTexts_41_4: ; 〈〉は/ちいさく　うなっている
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "ちいさく　うなっている"
	db $57
FwTexts_42_0: ; 〈〉は　くびを　ふって/かけごえを　あげた！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は　くびを　ふって"
	db $4f
	db "かけごえを　あげた！"
	db $57
FwTexts_43_0: ; 〈〉は　ほのおを/ふいて　さけんだ！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は　ほのおを"
	db $4f
	db "ふいて　さけんだ！"
	db $57
FwTexts_44_0: ; 〈〉は　うでを/ふりまわして　さけんでいる！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は　うでを"
	db $4f
	db "ふりまわして　さけんでいる！"
	db $57
FwTexts_45_0: ; 〈〉は/つるを　くねくね　させた！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "つるを　くねくね　させた！"
	db $57
FwTexts_45_1: ; 〈〉は/つるを　ぴしっと　ならした！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "つるを　ぴしっと　ならした！"
	db $57
FwTexts_46_0: ; 〈〉は/しっぽの　ほのおを　もやした！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "しっぽの　ほのおを　もやした！"
	db $57
FwTexts_47_0: ; 〈〉は/たのしく　おどった！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "たのしく　おどった！"
	db $57
FwTexts_47_1: ; 〈〉は　うれしくて/おどりだした！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は　うれしくて"
	db $4f
	db "おどりだした！"
	db $57
FwTexts_48_0: ; 〈〉は　ころんで/ちょっと　くやしそうだ！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は　ころんで"
	db $4f
	db "ちょっと　くやしそうだ！"
	db $57
FwTexts_49_0: ; 〈〉は/そらを　みあげている！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "そらを　みあげている！"
	db $57
FwTexts_49_1: ; 〈〉は/とつぜん　おどりだした！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "とつぜん　おどりだした！"
	db $57
FwTexts_50_0: ; 〈〉は　たのしそうに/じめんに　もぐっている！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は　たのしそうに"
	db $4f
	db "じめんに　もぐっている！"
	db $57
FwTexts_51_0: ; 〈〉は　たのしそうに/ころがっている！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は　たのしそうに"
	db $4f
	db "ころがっている！"
	db $57
FwTexts_51_1: ; 〈〉は/いわを　けずりはじめた！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "いわを　けずりはじめた！"
	db $57
FwTexts_51_2: ; 〈〉は　たのしそうに/いわを　ぶつけている！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は　たのしそうに"
	db $4f
	db "いわを　ぶつけている！"
	db $57
FwTexts_51_3: ; 〈〉は　じめんを/たたいて　ならしはじめた！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は　じめんを"
	db $4f
	db "たたいて　ならしはじめた！"
	db $57
FwTexts_52_0: ; 〈〉は　からだを/のばして　くつろいでいる！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は　からだを"
	db $4f
	db "のばして　くつろいでいる！"
	db $57
FwTexts_53_0: ; ……　……　……　……¶〈〉は/だまって　うなずいた！
	db $00
	db "……　……　……　……"
	db $51
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "だまって　うなずいた！"
	db $57
FwTexts_54_0: ; 〈〉は/なにか　つぶやいた……
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "なにか　つぶやいた……"
	db $57
FwTexts_55_0: ; ……おや？　〈〉の/すがたは……/かわらなかった！
	db $00
	db "……おや？　"
	db $01
	dw wPartyMonNicknames
	db $00
	db "の"
	db $4f
	db "すがたは……"
	db $55
	db "かわらなかった！"
	db $57
FwTexts_56_0: ; 〈〉は/ゆうがに　そらを　とんでいる！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "ゆうがに　そらを　とんでいる！"
	db $57
FwTexts_57_0: ; 〈〉は　たのしそうに/ゆらゆら　ゆれている
	db $01
	dw wPartyMonNicknames
	db $00
	db "は　たのしそうに"
	db $4f
	db "ゆらゆら　ゆれている"
	db $57
FwTexts_Default_0: ; 〈〉は/あなたと　いっしょで　うれしそうだ！
	db $01
	dw wPartyMonNicknames
	db $00
	db "は"
	db $4f
	db "あなたと　いっしょで　うれしそうだ！"
	db $57
