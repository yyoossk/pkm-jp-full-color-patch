DEF RM_BROCK_MAPBANK EQU $34
DEF RM_BROCK_PATCH   EQU $7b0e ; checkflag の所（6バイト）
DEF RM_BROCK_AFTER   EQU $7b14 ; 初めて戦うとき
DEF RM_BROCK_DONE    EQU $7b3a ; 勝ったあと（.FightDone）
DEF RM_BROCK_CLASS   EQU $11
DEF RM_BROCK_OPEN    EQU 1 ; 1 = 先に faceplayer・opentext 済み
DEF RM_MISTY_MAPBANK EQU $28
DEF RM_MISTY_PATCH   EQU $70cd ; checkflag の所（6バイト）
DEF RM_MISTY_AFTER   EQU $70d3 ; 初めて戦うとき
DEF RM_MISTY_DONE    EQU $70f9 ; 勝ったあと（.FightDone）
DEF RM_MISTY_CLASS   EQU $12
DEF RM_MISTY_OPEN    EQU 1 ; 1 = 先に faceplayer・opentext 済み
DEF RM_SURGE_MAPBANK EQU $2c
DEF RM_SURGE_PATCH   EQU $6186 ; checkflag の所（6バイト）
DEF RM_SURGE_AFTER   EQU $618c ; 初めて戦うとき
DEF RM_SURGE_DONE    EQU $61b8 ; 勝ったあと（.FightDone）
DEF RM_SURGE_CLASS   EQU $13
DEF RM_SURGE_OPEN    EQU 1 ; 1 = 先に faceplayer・opentext 済み
DEF RM_ERIKA_MAPBANK EQU $27
DEF RM_ERIKA_PATCH   EQU $7743 ; checkflag の所（6バイト）
DEF RM_ERIKA_AFTER   EQU $7749 ; 初めて戦うとき
DEF RM_ERIKA_DONE    EQU $7772 ; 勝ったあと（.FightDone）
DEF RM_ERIKA_CLASS   EQU $15
DEF RM_ERIKA_OPEN    EQU 1 ; 1 = 先に faceplayer・opentext 済み
DEF RM_JANINE_MAPBANK EQU $2d
DEF RM_JANINE_PATCH   EQU $5de2 ; checkflag の所（6バイト）
DEF RM_JANINE_AFTER   EQU $5de8 ; 初めて戦うとき
DEF RM_JANINE_DONE    EQU $5e29 ; 勝ったあと（.FightDone）
DEF RM_JANINE_CLASS   EQU $1a
DEF RM_JANINE_OPEN    EQU 0 ; 1 = 先に faceplayer・opentext 済み
DEF RM_JANINE_DONE2   EQU $5e2b ; .FightDone の faceplayer・opentext のあと
DEF RM_SABRINA_MAPBANK EQU $29
DEF RM_SABRINA_PATCH   EQU $6f07 ; checkflag の所（6バイト）
DEF RM_SABRINA_AFTER   EQU $6f0d ; 初めて戦うとき
DEF RM_SABRINA_DONE    EQU $6f3c ; 勝ったあと（.FightDone）
DEF RM_SABRINA_CLASS   EQU $23
DEF RM_SABRINA_OPEN    EQU 1 ; 1 = 先に faceplayer・opentext 済み
DEF RM_BLAINE_MAPBANK EQU $35
DEF RM_BLAINE_PATCH   EQU $7dbd ; checkflag の所（6バイト）
DEF RM_BLAINE_AFTER   EQU $7dc3 ; 初めて戦うとき
DEF RM_BLAINE_DONE    EQU $7deb ; 勝ったあと（.FightDone）
DEF RM_BLAINE_CLASS   EQU $2e
DEF RM_BLAINE_OPEN    EQU 1 ; 1 = 先に faceplayer・opentext 済み
DEF RM_BLUE_MAPBANK EQU $26
DEF RM_BLUE_PATCH   EQU $7453 ; checkflag の所（6バイト）
DEF RM_BLUE_AFTER   EQU $7459 ; 初めて戦うとき
DEF RM_BLUE_DONE    EQU $747c ; 勝ったあと（.FightDone）
DEF RM_BLUE_CLASS   EQU $40
DEF RM_BLUE_OPEN    EQU 1 ; 1 = 先に faceplayer・opentext 済み
DEF RM_KANTO_BADGE0 EQU $22 ; グレーバッジ（カントーのバッジ 8つは このあとに つづく）
DEF RM_PARTY_BANK  EQU $0e
DEF RM_TrainerGroups EQU $595c
DEF RM_BROCK_PARTY1 EQU $5cd9 ; 1回目の手持ち（36バイト、元のデータをそのまま使う）
DEF RM_BROCK_PARTY1_LEN EQU 36
DEF RM_BROCK_NAME_LEN EQU 4 ; 名前（@まで）
DEF RM_BROCK_PARTY1_OFS EQU $39cd9 ; ROM の中の位置
DEF RM_MISTY_PARTY1 EQU $5cfd ; 1回目の手持ち（30バイト、元のデータをそのまま使う）
DEF RM_MISTY_PARTY1_LEN EQU 30
DEF RM_MISTY_NAME_LEN EQU 4 ; 名前（@まで）
DEF RM_MISTY_PARTY1_OFS EQU $39cfd ; ROM の中の位置
DEF RM_SURGE_PARTY1 EQU $5d1b ; 1回目の手持ち（36バイト、元のデータをそのまま使う）
DEF RM_SURGE_PARTY1_LEN EQU 36
DEF RM_SURGE_NAME_LEN EQU 4 ; 名前（@まで）
DEF RM_SURGE_PARTY1_OFS EQU $39d1b ; ROM の中の位置
DEF RM_ERIKA_PARTY1 EQU $5d79 ; 1回目の手持ち（30バイト、元のデータをそのまま使う）
DEF RM_ERIKA_PARTY1_LEN EQU 30
DEF RM_ERIKA_NAME_LEN EQU 4 ; 名前（@まで）
DEF RM_ERIKA_PARTY1_OFS EQU $39d79 ; ROM の中の位置
DEF RM_JANINE_PARTY1 EQU $604f ; 1回目の手持ち（36バイト、元のデータをそのまま使う）
DEF RM_JANINE_PARTY1_LEN EQU 36
DEF RM_JANINE_NAME_LEN EQU 4 ; 名前（@まで）
DEF RM_JANINE_PARTY1_OFS EQU $3a04f ; ROM の中の位置
DEF RM_SABRINA_PARTY1 EQU $6571 ; 1回目の手持ち（24バイト、元のデータをそのまま使う）
DEF RM_SABRINA_PARTY1_LEN EQU 24
DEF RM_SABRINA_NAME_LEN EQU 4 ; 名前（@まで）
DEF RM_SABRINA_PARTY1_OFS EQU $3a571 ; ROM の中の位置
DEF RM_BLAINE_PARTY1 EQU $6c50 ; 1回目の手持ち（24バイト、元のデータをそのまま使う）
DEF RM_BLAINE_PARTY1_LEN EQU 24
DEF RM_BLAINE_NAME_LEN EQU 4 ; 名前（@まで）
DEF RM_BLAINE_PARTY1_OFS EQU $3ac50 ; ROM の中の位置
DEF RM_BLUE_PARTY1 EQU $72de ; 1回目の手持ち（43バイト、元のデータをそのまま使う）
DEF RM_BLUE_PARTY1_LEN EQU 43
DEF RM_BLUE_NAME_LEN EQU 5 ; 名前（@まで）
DEF RM_BLUE_PARTY1_OFS EQU $3b2de ; ROM の中の位置
DEF RM_PARTY_FREE  EQU $7fd6 ; ここから 42 バイト空いている
DEF RM_PrintWinLoss_Call EQU $38db
DEF RM_GetMapScriptsBank EQU $2cec
DEF RM_wScriptBank EQU $d152
DEF RM_ReadTrainerParty_Class EQU $5764 ; ld a, [wOtherTrainerClass]（RM_PARTY_FAR）
DEF RM_wOtherTrainerClass EQU $d10a
DEF RM_ReadTrainerParty_Done EQU $57a7 ; .done（jp ComputeTrainerReward）
DEF RM_TrainerType4_OFS EQU $39874 ; 元の TrainerType4（ROM の中の位置）
DEF RM_TrainerType4_LEN EQU 126
