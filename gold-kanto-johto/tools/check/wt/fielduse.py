def field_use(w, item, s=None):
    """フィールドで どうぐの ポケットの item を つかう（START → リュック）"""
    idx = w.item_index(0xD5AA, item)
    if idx is None: return False
    for _ in range(3): w.g.press('B', 4, 20)
    w.settle(); w.g.press('S', 4, 40)
    if s: s('メニュー')
    for _ in range(8):
        if w.rd(0xCF14)[0] == 3: break
        w.g.press('D' if w.rd(0xCF14)[0] < 3 else 'U', 4, 12)
    w.g.press('A', 4, 60)
    for _ in range(5):
        if w.pocket_is('item'): break
        w.g.press('R', 4, 20)
    for _ in range(12): w.g.press('U', 4, 10)
    for _ in range(idx): w.g.press('D', 4, 12)
    if s: s('どうぐ')
    w.g.press('A', 4, 40); w.g.press('A', 4, 60)
    if s: s('つかう')
    for _ in range(6): w.g.press('B', 4, 30)
    return True
