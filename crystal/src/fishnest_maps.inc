; 「ぶんぷをみる」の釣りの場所の表。tools/fishnest_maps.py で作った（pokegold.gbc）

; 釣りができる所（地名, 釣りのグループ）。マップ（グループ.番号）は確かめ用
FishNestMaps:
	db $1b, $01 ; map 1.14
	db $21, $03 ; map 2.5
	db $26, $0c ; map 2.6
	db $13, $01 ; map 3.15
	db $09, $04 ; map 3.22
	db $0a, $03 ; map 3.29
	db $0a, $01 ; map 3.31
	db $0d, $03 ; map 3.32
	db $0e, $04 ; map 3.44
	db $22, $03 ; map 3.49
	db $1e, $0a ; map 3.60
	db $2d, $03 ; map 3.67
	db $2b, $03 ; map 3.70
	db $29, $05 ; map 3.73
	db $5c, $03 ; map 3.74
	db $50, $01 ; map 3.81
	db $16, $04 ; map 4.9
	db $28, $04 ; map 5.10
	db $51, $01 ; map 6.5
	db $52, $02 ; map 6.6
	db $55, $02 ; map 6.7
	db $54, $02 ; map 6.8
	db $36, $01 ; map 7.6
	db $35, $03 ; map 7.12
	db $40, $03 ; map 7.13
	db $42, $03 ; map 7.14
	db $37, $03 ; map 7.15
	db $38, $03 ; map 7.16
	db $36, $03 ; map 7.17
	db $24, $04 ; map 9.5
	db $25, $08 ; map 9.6
	db $08, $0b ; map 10.1
	db $12, $04 ; map 10.2
	db $06, $04 ; map 10.5
	db $0f, $01 ; map 11.1
	db $10, $01 ; map 11.2
	db $3b, $04 ; map 12.1
	db $3c, $02 ; map 12.3
	db $2e, $02 ; map 13.2
	db $1b, $02 ; map 15.1
	db $4a, $0d ; map 17.1
	db $4b, $01 ; map 17.2
	db $4f, $01 ; map 17.4
	db $50, $08 ; map 17.5
	db $49, $0d ; map 18.2
	db $5d, $04 ; map 19.1
	db $2d, $04 ; map 19.2
	db $4d, $01 ; map 21.2
	db $1d, $01 ; map 22.1
	db $1f, $02 ; map 22.2
	db $20, $01 ; map 22.3
	db $56, $04 ; map 23.2
	db $30, $04 ; map 23.3
	db $5a, $02 ; map 24.1
	db $5b, $02 ; map 24.2
	db $01, $02 ; map 24.4
	db $04, $04 ; map 26.1
	db $05, $04 ; map 26.2
	db $03, $01 ; map 26.3
	db 0

; 釣りのグループごとに 釣れるポケモン（ボロ・いい・すごいつりざお、朝昼・夜）
FishNestGroupMons:
	dw .group1
	dw .group2
	dw .group3
	dw .group4
	dw .group5
	dw .group6
	dw .group7
	dw .group8
	dw .group9
	dw .group10
	dw .group11
	dw .group12
	dw .group13
.end_ptrs
.group1
	db $81, $62, $de, $78, $63, 0
.group2
	db $81, $48, $aa, $5a, $49, $ab, 0
.group3
	db $81, $76, $77, 0
.group4
	db $81, $3c, 0
.group5
	db $81, $93, $94, 0
.group6
	db $81, $d3, 0
.group7
	db $81, $df, 0
.group8
	db $81, $82, 0
.group9
	db $81, $93, $94, 0
.group10
	db $81, $62, $74, $63, $75, 0
.group11
	db $81, $48, $d3, 0
.group12
	db $81, $3c, $df, 0
.group13
	db $81, $48, $d3, 0
