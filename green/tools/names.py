# 分かって いる 処理の 名前（12種類 とも 同じ 番地のもの）。
# ここに 足すと、つぎの 逆アセンブルから その 名前で 出る（組み上がる ROM は かわらない）。

# ホームバンク（$0000-$3fff）
HOME_NAMES = {
    0x01bb: 'CopyData',
    0x0374: 'ClearScreenArea',
    0x03d2: 'TextBoxBorder',
    0x0405: 'PlaceString',
    0x0a8e: 'DelayFrame',
    0x0e1a: 'UpdateSprites',
    0x0ec7: 'TextScriptEnd',
    0x15ff: 'DisplayListMenuID',
    0x1870: 'PrintListMenuEntries',
    0x19e5: 'GetItemName',
    0x2eb5: 'PrintBCDNumber',
    0x33bd: 'IsItemInBag',
    0x34d0: 'HasEnoughMoney',
    0x34db: 'HasEnoughCoins',
    0x3500: 'Bankswitch',
    0x3516: 'YesNoChoice',
    0x3641: 'SaveScreenTilesToBuffer1',
    0x364d: 'LoadScreenTilesFromBuffer1',
    0x3661: 'DelayFrames',
    0x3668: 'PlaySoundWaitForCurrent',
    0x3759: 'JoypadLowSensitivity',
    0x39e8: 'HandleMenuInput',
    0x3aa6: 'PlaceMenuCursor',
    0x3b59: 'PrintText',
    0x3ce7: 'Delay3',
    0x3cff: 'RunPaletteCommand',
}

# ほかの バンクの 処理（バンク, 番地）
BANK_NAMES = {
    (0x1c, 0x6cfe): 'DisplayChangeBoxMenu',
    (0x1c, 0x6e12): 'GetMonCountsForAllBoxes',
    (0x12, 0x5db6): 'GameCornerDrawCoinBox',
}
