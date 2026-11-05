DEF RM_BROCK_MAPBANK EQU $26
DEF RM_BROCK_PATCH   EQU $7a99 ; checkflag の所（6バイト）
DEF RM_BROCK_AFTER   EQU $7a9f ; 初めて戦うとき
DEF RM_BROCK_DONE    EQU $7ac5 ; 勝ったあと（.FightDone）
DEF RM_BROCK_CLASS   EQU $11
DEF RM_BROCK_OPEN    EQU 1 ; 1 = 先に faceplayer・opentext 済み
DEF RM_MISTY_MAPBANK EQU $1c
DEF RM_MISTY_PATCH   EQU $5e30 ; checkflag の所（6バイト）
DEF RM_MISTY_AFTER   EQU $5e36 ; 初めて戦うとき
DEF RM_MISTY_DONE    EQU $5e5c ; 勝ったあと（.FightDone）
DEF RM_MISTY_CLASS   EQU $12
DEF RM_MISTY_OPEN    EQU 1 ; 1 = 先に faceplayer・opentext 済み
DEF RM_SURGE_MAPBANK EQU $1d
DEF RM_SURGE_PATCH   EQU $5fa5 ; checkflag の所（6バイト）
DEF RM_SURGE_AFTER   EQU $5fab ; 初めて戦うとき
DEF RM_SURGE_DONE    EQU $5fd7 ; 勝ったあと（.FightDone）
DEF RM_SURGE_CLASS   EQU $13
DEF RM_SURGE_OPEN    EQU 1 ; 1 = 先に faceplayer・opentext 済み
DEF RM_ERIKA_MAPBANK EQU $1a
DEF RM_ERIKA_PATCH   EQU $76d5 ; checkflag の所（6バイト）
DEF RM_ERIKA_AFTER   EQU $76db ; 初めて戦うとき
DEF RM_ERIKA_DONE    EQU $7704 ; 勝ったあと（.FightDone）
DEF RM_ERIKA_CLASS   EQU $15
DEF RM_ERIKA_OPEN    EQU 1 ; 1 = 先に faceplayer・opentext 済み
DEF RM_JANINE_MAPBANK EQU $1e
DEF RM_JANINE_PATCH   EQU $58b5 ; checkflag の所（6バイト）
DEF RM_JANINE_AFTER   EQU $58bb ; 初めて戦うとき
DEF RM_JANINE_DONE    EQU $58fc ; 勝ったあと（.FightDone）
DEF RM_JANINE_CLASS   EQU $1a
DEF RM_JANINE_OPEN    EQU 0 ; 1 = 先に faceplayer・opentext 済み
DEF RM_JANINE_DONE2   EQU $58fe ; .FightDone の faceplayer・opentext のあと
DEF RM_SABRINA_MAPBANK EQU $16
DEF RM_SABRINA_PATCH   EQU $6ca1 ; checkflag の所（6バイト）
DEF RM_SABRINA_AFTER   EQU $6ca7 ; 初めて戦うとき
DEF RM_SABRINA_DONE    EQU $6cd6 ; 勝ったあと（.FightDone）
DEF RM_SABRINA_CLASS   EQU $23
DEF RM_SABRINA_OPEN    EQU 1 ; 1 = 先に faceplayer・opentext 済み
DEF RM_BLAINE_MAPBANK EQU $27
DEF RM_BLAINE_PATCH   EQU $7d4c ; checkflag の所（6バイト）
DEF RM_BLAINE_AFTER   EQU $7d52 ; 初めて戦うとき
DEF RM_BLAINE_DONE    EQU $7d7a ; 勝ったあと（.FightDone）
DEF RM_BLAINE_CLASS   EQU $2e
DEF RM_BLAINE_OPEN    EQU 1 ; 1 = 先に faceplayer・opentext 済み
DEF RM_BLUE_MAPBANK EQU $1e
DEF RM_BLUE_PATCH   EQU $6980 ; checkflag の所（6バイト）
DEF RM_BLUE_AFTER   EQU $6986 ; 初めて戦うとき
DEF RM_BLUE_DONE    EQU $69a9 ; 勝ったあと（.FightDone）
DEF RM_BLUE_CLASS   EQU $40
DEF RM_BLUE_OPEN    EQU 1 ; 1 = 先に faceplayer・opentext 済み
DEF RM_KANTO_BADGE0 EQU $23 ; グレーバッジ（カントーのバッジ 8つは このあとに つづく）
DEF RM_PARTY_BANK  EQU $0e
DEF RM_TrainerGroups EQU $59ba
DEF RM_BROCK_PARTY1 EQU $5d39 ; 1回目の手持ち（36バイト、元のデータをそのまま使う）
DEF RM_BROCK_PARTY1_LEN EQU 36
DEF RM_BROCK_NAME_LEN EQU 4 ; 名前（@まで）
DEF RM_BROCK_PARTY1_OFS EQU $39d39 ; ROM の中の位置
DEF RM_MISTY_PARTY1 EQU $5d5d ; 1回目の手持ち（30バイト、元のデータをそのまま使う）
DEF RM_MISTY_PARTY1_LEN EQU 30
DEF RM_MISTY_NAME_LEN EQU 4 ; 名前（@まで）
DEF RM_MISTY_PARTY1_OFS EQU $39d5d ; ROM の中の位置
DEF RM_SURGE_PARTY1 EQU $5d7b ; 1回目の手持ち（36バイト、元のデータをそのまま使う）
DEF RM_SURGE_PARTY1_LEN EQU 36
DEF RM_SURGE_NAME_LEN EQU 4 ; 名前（@まで）
DEF RM_SURGE_PARTY1_OFS EQU $39d7b ; ROM の中の位置
DEF RM_ERIKA_PARTY1 EQU $5dd9 ; 1回目の手持ち（30バイト、元のデータをそのまま使う）
DEF RM_ERIKA_PARTY1_LEN EQU 30
DEF RM_ERIKA_NAME_LEN EQU 4 ; 名前（@まで）
DEF RM_ERIKA_PARTY1_OFS EQU $39dd9 ; ROM の中の位置
DEF RM_JANINE_PARTY1 EQU $6165 ; 1回目の手持ち（36バイト、元のデータをそのまま使う）
DEF RM_JANINE_PARTY1_LEN EQU 36
DEF RM_JANINE_NAME_LEN EQU 4 ; 名前（@まで）
DEF RM_JANINE_PARTY1_OFS EQU $3a165 ; ROM の中の位置
DEF RM_SABRINA_PARTY1 EQU $66d8 ; 1回目の手持ち（24バイト、元のデータをそのまま使う）
DEF RM_SABRINA_PARTY1_LEN EQU 24
DEF RM_SABRINA_NAME_LEN EQU 4 ; 名前（@まで）
DEF RM_SABRINA_PARTY1_OFS EQU $3a6d8 ; ROM の中の位置
DEF RM_BLAINE_PARTY1 EQU $6eba ; 1回目の手持ち（24バイト、元のデータをそのまま使う）
DEF RM_BLAINE_PARTY1_LEN EQU 24
DEF RM_BLAINE_NAME_LEN EQU 4 ; 名前（@まで）
DEF RM_BLAINE_PARTY1_OFS EQU $3aeba ; ROM の中の位置
DEF RM_BLUE_PARTY1 EQU $7669 ; 1回目の手持ち（43バイト、元のデータをそのまま使う）
DEF RM_BLUE_PARTY1_LEN EQU 43
DEF RM_BLUE_NAME_LEN EQU 5 ; 名前（@まで）
DEF RM_BLUE_PARTY1_OFS EQU $3b669 ; ROM の中の位置
DEF RM_PARTY_FREE  EQU $7710 ; ここから 2288 バイト空いている
DEF RM_PrintWinLoss_Call EQU $3704
DEF RM_GetMapScriptsBank EQU $2c29
DEF RM_wScriptBank EQU $d42a
DEF RM_ReadTrainerParty_Class EQU $57ab ; ld a, [wOtherTrainerClass]（RM_PARTY_FAR）
DEF RM_wOtherTrainerClass EQU $d260
DEF RM_ReadTrainerParty_Done EQU $57ee ; .done（jp ComputeTrainerReward）
DEF RM_TrainerType4_OFS EQU $398bb ; 元の TrainerType4（ROM の中の位置）
DEF RM_TrainerType4_LEN EQU 126
