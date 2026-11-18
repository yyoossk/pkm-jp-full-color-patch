import time
def tleft(w): return w.budget - (time.time() - w.t0)
def grind_r1(w, s):
    """1ばん道路で 先頭を 12 まで（トキワの ポケモンセンターで 回復）"""
    if w.pos()[:2] != (13,1): w.travel((13,1), s)
    while tleft(w) > 15:
        if w.grind((23,9), 12, s, maxb=3): return True
    return False
def to_pewter(w, s):
    w.run_wild = True
    for m in [(23,3),(23,1),(26,83),(26,84),(26,85),(23,1)]:
        if w.pos()[:2] == m: continue
        if not w.travel(m, s):
            if tleft(w) < 10: return False
            w.log.append('とちゅう %s' % (m,)); return False
        if tleft(w) < 10: return False
    w.leave('U', s); w.advance(s)
    return True
def to_forest(w, s):
    w.run_wild = True
    for m in [(23,3),(23,1),(26,83),(26,84)]:
        if w.pos()[:2] == m: continue
        if not w.travel(m, s): return False
    return True
def north(w, s):
    w.run_wild = True
    m = w.pos()[:2]; ok = w.leave('U', s); w.advance(s); return w.pos()[:2] != m
def heal_at(center):
    def f(w, s):
        return w.heal(center, s)
    return f
def grind_to(lv, center, home=None):
    def f(w, s):
        if home and w.pos()[:2] != home: w.travel(home, s)
        while tleft(w) > 15:
            if w.grind(center, lv, s, maxb=3): return True
        return False
    return f
pewter_heal = heal_at((14,6))
grind_forest = grind_to(20, (14,6), (26,84))
def gym(gmap, center, leader):
    def f(w, s):
        w.run_wild = True
        if not w.heal(center, s): return False
        if not w.travel(gmap, s): return False
        w.talk_to(*leader, shot=s); w.advance(s, n=200)
        return w.pos()[:2] == gmap
    return f
brock = gym((14,4), (14,6), (5,1))
def talk_leader(leader):
    def f(w, s):
        w.talk_to(*leader, shot=s); w.advance(s, n=200); return True
    return f
brock2 = talk_leader((5,1))
def cont(w, s):
    w.advance(s, n=300); return True
def go(dest):
    def f(w, s):
        w.run_wild = True
        while tleft(w) > 20:
            if w.pos()[:2] == dest: return True
            if w.party()[0]['hp'] == 0: w.advance(s)
            w.travel(dest, s, tries=1)
            if w.log and w.log[-1].startswith('行けない'): return False
        return w.pos()[:2] == dest
    return f
to_cerulean = go((7,4))
def fossil(w, s):
    w.run_wild = True
    w.talk_to(12, 8, shot=s); w.advance(s, n=200)
    w.talk_to(12, 6, shot=s); w.advance(s, n=60)
    return True
def heal_go(center, dest):
    def f(w, s):
        w.run_wild = True
        if w.party()[0]['hp'] < w.party()[0]['mx']: w.heal(center, s)
        return go(dest)(w, s)
    return f
to_bill = heal_go((7,4), (26,51))
grind_r4 = grind_to(30, (7,4), (7,12))
def bill1(w, s):
    o = w.objs(); w.log.append(str(o))
    w.talk_to(o[0][0], o[0][1], shot=s); w.advance(s, n=100)
    return True
def bill2(w, s):
    c = w.coll(w.pos()[:2])
    w.log.append(' '.join('%02x' % (c(x, y) or 0) for y in range(2, 8) for x in range(0, 8)))
    for (x, y, d) in ((1, 5, 'U'), (0, 5, 'U'), (2, 4, 'L')):
        if (x, y) in w.reach():
            w.goto_safe(x, y); w.face(d); s('pc'); w.g.press('A', 4, 40); w.advance(s, n=100)
            o = [p for p in w.objs()]
            break
    for i in range(10):
        w.g.wait(60); s('wait')
        if w.textbox(): w.advance(s, n=100)
    return True
misty = gym((7,6), (7,4), (5,3))
misty2 = talk_leader((5,3))
def misty3(w, s):
    for _ in range(4): w.g.press('B', 4, 30)
    if not gym((7,6), (7,4), (5,3))(w, s): return False
    _,_,x,y = w.pos()
    if w.pos()[:2] == (7,6): w.talk_to(5, 3, shot=s); w.advance(s, n=300)
    return True
GRASSY = {43, 69, 25, 63, 16, 21, 23, 27, 56, 52}
def catcher(w):
    def want(sp):
        have = {p['sp'] for p in w.party()}
        return len(w.party()) < 6 and sp in GRASSY and sp not in have
    w.want = want
def to_vermilion(w, s):
    catcher(w)
    for _ in range(4): w.g.press('B', 4, 30)
    return go((12,5))(w, s)
def captain(w, s):
    catcher(w)
    if not go((26,47))(w, s): return False
    o = w.objs(); w.log.append(str(o))
    w.talk_to(o[0][0], o[0][1], shot=s); w.advance(s, n=150)
    return True
def catch_grass(w, s):
    w.want = lambda sp: sp in (43, 69) and not any(p['sp'] in (43, 69) for p in w.party()) and len(w.party()) < 6
    for _ in range(4): w.g.press('B', 4, 30)
    if w.pos()[:2] != (7,16) and not go((7,16))(w, s): return False
    while tleft(w) > 20:
        if any(p['sp'] in (43, 69) for p in w.party()): return True
        if w.count_item(5) == 0: w.log.append('ボールが ない'); return False
        w.grind((7,4), 99, s, maxb=1)
    return False
grind_odd = grind_to(24, (7,4), (7,16))
def grind_odd2(w, s):
    while tleft(w) > 15:
        if w.party()[0]["lv"] >= 24: return True
        w.grind((7,4), 24, s, maxb=3, hp_min=0.6)
    return False
def lead_char(w):
    def lf(e, wild):
        for i, p in enumerate(w.party()):
            if p['sp'] in (4, 5, 6) and p['hp'] > 0: return i
        return None
    w.lead_for = lf
def misty4(w, s):
    lead_char(w)
    return misty3(w, s)
def surge(w, s):
    w.can_cut = True; lead_char(w)
    for _ in range(4): w.g.press('B', 4, 30)
    if not gym((12,11), (12,5), (5,2))(w, s): return False
    return True
NOSAFFRON = {(25,2), (26,100), (26,101), (26,102), (26,103)}
NOR11 = {(12,2)}
def to_lavender(w, s):
    w.can_cut = True; lead_char(w); w.avoid = NOSAFFRON | NOR11
    for _ in range(4): w.g.press('B', 4, 30)
    return go((18,5))(w, s)
def to_celadon(w, s):
    w.can_cut = True; lead_char(w); w.avoid = NOSAFFRON
    for _ in range(4): w.g.press('B', 4, 30)
    return go((21,17))(w, s)
def erika(w, s):
    w.can_cut = True; lead_char(w); w.avoid = NOSAFFRON
    for _ in range(4): w.g.press('B', 4, 30)
    if not gym((21,21), (21,17), (5,3))(w, s): return False
    return True
def gamecorner(w, s):
    w.can_cut = True; lead_char(w); w.avoid = NOSAFFRON
    for _ in range(4): w.g.press('B', 4, 30)
    if not go((21,19))(w, s): return False
    w.talk_to(9, 5, shot=s, counter=False); w.advance(s, n=200)
    w.goto_safe(9, 5); w.face('U'); w.g.press('A', 4, 60); s('poster'); w.advance(s, n=60)
    w.g.wait(60); s('after')
    return go((26,21))(w, s)
def hideout_b4(w, s):
    w.can_cut = True; lead_char(w)
    return go((26,24))(w, s)
def liftkey(w, s):
    w.run_wild = True
    if w.has_key(0x88): return True
    w.talk_to(11, 2, shot=s); w.advance(s, n=200)
    w.talk_to(11, 2, shot=s); w.advance(s, n=100)
    for o in w.objs():
        if o[2] == 84 and abs(o[0] - 11) + abs(o[1] - 2) <= 2:
            w.talk_to(o[0], o[1], shot=s, counter=False); w.advance(s, n=60)
    w.log.append('リフトキー %s' % w.has_key(0x88))
    return w.has_key(0x88)
def to_elevator(w, s):
    w.run_wild = True
    return go((26,25))(w, s)
def giovanni(w, s):
    w.run_wild = True; lead_char(w)
    if w.has_key(0x87): return True
    if w.pos()[:2] == (26,25):
        w.settle(); w.goto(1, 2); w.face('U'); w.g.press('A', 8, 60); w.g.wait(40)
        w.g.press('D', 8, 30); w.g.press('D', 8, 30); s('floor'); w.g.press('A', 8, 60); w.advance(s, n=30); w.g.wait(120)
        w.settle(); w.door(2, 1, 'U'); w.g.wait(60); w.settle()
    w.settle()
    for o in [(24,10),(25,10),(25,3)]:
        if o in [(x, y) for x, y, _ in w.objs()]:
            w.talk_to(*o, shot=s); w.advance(s, n=300)
    for x, y, sp in w.objs():
        if sp == 84 and abs(x - 25) + abs(y - 3) <= 2:
            w.talk_to(x, y, shot=s, counter=False); w.advance(s, n=60)
    w.log.append('シルフスコープ %s' % w.has_key(0x87))
    return w.has_key(0x87)
def leave_hideout(w, s):
    if w.pos()[0] != 26 or w.pos()[1] not in (21, 22, 23, 24, 25): return True
    if not go((26,25))(w, s): return False
    w.settle(); w.goto(1, 2); w.face('U'); w.g.press('A', 8, 60); w.g.wait(40)
    for _ in range(4): w.g.press('U', 8, 20)
    w.g.press('A', 8, 60); w.advance(s, n=30); w.g.wait(120)
    w.settle(); w.door(2, 1, 'U'); w.g.wait(60); w.settle()
    return w.pos()[:2] == (26,21)
def has_flute(w): return w.has_key(0x38) or w.count_item(0x38) > 0
def tower(w, s):
    w.can_cut = True; lead_char(w); w.avoid = NOSAFFRON; w.run_wild = True
    if has_flute(w): return True
    for _ in range(4): w.g.press('B', 4, 30)
    if not leave_hideout(w, s): return False
    if not go((26,20))(w, s): return False
    for o in [(10,8),(11,8),(10,3)]:
        if w.pos()[:2] != (26,20): break
        if o in [(x, y) for x, y, _ in w.objs()]:
            w.talk_to(*o, shot=s); w.advance(s, n=300)
    w.settle()
    if w.pos()[:2] == (26,121) and not has_flute(w):
        for o in w.objs():
            if o[2] == 47: w.talk_to(o[0], o[1], shot=s); w.advance(s, n=200)
    w.log.append('ふえ %s' % has_flute(w))
    return has_flute(w)
def to_fuchsia(w, s):
    w.can_cut = True; lead_char(w); w.avoid = NOSAFFRON; w.run_wild = True
    for _ in range(4): w.g.press('B', 4, 30)
    return go((17,10))(w, s)
def koga(w, s):
    w.can_cut = True; lead_char(w); w.avoid = NOSAFFRON; w.run_wild = True
    if w.badges() & 0x10: return True
    for _ in range(4): w.g.press('B', 4, 30)
    gym((17,8), (17,10), (1,10))(w, s)
    w.log.append('バッジ %s' % bin(w.badges()))
    return bool(w.badges() & 0x10)
def safari_surf(w, s):
    w.can_cut = True; lead_char(w); w.avoid = NOSAFFRON; w.run_wild = True
    for _ in range(4): w.g.press('B', 4, 30)
    if not go((26,96))(w, s): return False
    for o in w.objs(): w.talk_to(o[0], o[1], shot=s); w.advance(s, n=100)
    return True
def teeth(w, s):
    w.run_wild = True; lead_char(w)
    if w.has_key(0x95) or w.count_item(0x95): return True
    if not go((26,94))(w, s): return False
    for o in w.objs():
        if o[2] == 84 and not (w.has_key(0x95) or w.count_item(0x95)):
            w.talk_to(o[0], o[1], shot=s, counter=False); w.advance(s, n=40)
    w.log.append('いれば %s' % (w.has_key(0x95) or w.count_item(0x95)))
    return w.has_key(0x95) or w.count_item(0x95) > 0
def strength(w, s):
    w.run_wild = True; lead_char(w); w.avoid = NOSAFFRON; w.can_cut = True
    if not teeth(w, s): return False
    if not go((17,12))(w, s): return False
    for o in w.objs(): w.talk_to(o[0], o[1], shot=s); w.advance(s, n=100)
    return True
def goodrod(w, s):
    w.run_wild = True; lead_char(w); w.avoid = NOSAFFRON; w.can_cut = True
    if not go((26,120))(w, s): return False
    w.talk_to(5, 3, shot=s); w.advance(s, n=60)
    w.log.append('key %s' % w.rd(0xD5D4, 10))
    return True
def to_pc(center):
    def f(w, s):
        if not go(center)(w, s): return False
        bg = w.maps[center]['attr']['bgs'][0]; y, x = bg[0], bg[1]
        w.goto(x, y + 1); w.face('U'); return True
    return f
to_fuchsia_center = go((17,10))
NOSEAFOAM = {(26,63),(26,64),(26,65),(26,66),(26,67)}
def to_cinnabar(w, s):
    w.can_cut = True; w.can_surf = True; lead_char(w); w.avoid = NOSAFFRON | NOSEAFOAM; w.run_wild = True
    for _ in range(4): w.g.press('B', 4, 30)
    return go((6,1))(w, s)
def press_bgs(w, s, tried):
    """今の マップの しらべる所（スイッチ など）を 1つ おす。おした ら True"""
    mid = w.pos()[:2]; r = w.reach()
    from walker import DIRS
    for b in w.maps[mid]['attr']['bgs']:
        y, x = b[0], b[1]
        if (mid, x, y) in tried: continue
        for d, (dx, dy) in DIRS.items():
            p = (x - dx, y - dy)
            if p in r:
                tried.add((mid, x, y))
                w.run_wild = True; w.advance(s); w.goto_safe(*p, shot=s); w.advance(s)
                w.face(d); w.g.press('A', 8, 60); s('しらべる')
                for _ in range(10):
                    if w.menu_kind() == 'yesno': w.g.press('A', 8, 60)
                    elif w.textbox(): w.g.press('A', 8, 40)
                    else: break
                w._rc = {}; w.log.append('しらべた %s %s' % (mid, (x, y)))
                return True
    return False
def mansion(w, s):
    w.can_cut = True; w.can_surf = True; lead_char(w); w.run_wild = True
    for _ in range(4): w.g.press('B', 4, 30)
    if w.has_key(0x93): return True
    tried = set()
    for it in range(30):
        if w.pos()[:2] == (26,60): break
        w._rc = {}
        if w.travel((26,60), s, tries=1): break
        if w.pos()[:2] not in ((26,57),(26,58),(26,59),(26,60)):
            if not go((26,57))(w, s): return False
            continue
        if not press_bgs(w, s, tried): tried = set()
    if w.pos()[:2] != (26,60): return False
    for it in range(20):
        if w.has_key(0x93): break
        balls = [o for o in w.objs() if o[2] == 84]
        got = False
        for o in balls:
            from walker import DIRS
            if any((o[0]+dx, o[1]+dy) in w.reach() for dx, dy in DIRS.values()):
                w.talk_to(o[0], o[1], shot=s, counter=False); w.advance(s, n=40); got = True; break
        if not got and not press_bgs(w, s, tried): tried = set()
    w.log.append('ひみつのカギ %s' % w.has_key(0x93))
    return w.has_key(0x93)
def press_at(w, s, x, y):
    from walker import DIRS
    w._rc = {}; r = w.reach()
    for d, (dx, dy) in DIRS.items():
        p = (x - dx, y - dy)
        if p in r:
            w.run_wild = True; w.advance(s); w.goto_safe(*p, shot=s); w.advance(s)
            if w.pos()[2:] != p: w.goto_safe(*p, shot=s); w.advance(s)
            w.face(d); w.g.press('A', 8, 60); s('スイッチ')
            for _ in range(10):
                if w.menu_kind() == 'yesno': w.g.press('A', 8, 60)
                elif w.textbox(): w.g.press('A', 8, 40)
                else: break
            w._rc = {}; w.log.append('スイッチ %s %s' % (w.pos()[:2], (x, y))); return True
    w.log.append('スイッチに とどかない %s %s' % (w.pos()[:2], (x, y))); return False
def warp_at(w, s, x, y, dest):
    w._rc = {}
    if w.pos()[:2] == dest: return True
    w.door(x, y, 'U', s); w.g.wait(60); w.settle(); w.advance(s); w._rc = {}
    ok = w.pos()[:2] == dest
    if not ok: w.log.append('とどかない %s → %s' % ((x, y), dest))
    return ok
def mansion2(w, s):
    w.can_cut = True; w.can_surf = True; lead_char(w); w.run_wild = True
    for _ in range(4): w.g.press('B', 4, 30)
    if w.has_key(0x93): return True
    if w.pos()[:2] not in ((26,57),(26,58),(26,59),(26,60)):
        if not go((26,57))(w, s): return False
    steps = [((26,57), 'p', (2,5)), ((26,57), 'w', (5,10), (26,58)),
             ((26,58), 'p', (2,11)), ((26,58), 'w', (6,1), (26,59)),
             ((26,59), 'p', (10,5)), ((26,59), 'w', (19,14), (26,58)),
             ((26,58), 'p', (2,11)), ((26,58), 'w', (6,1), (26,59)),
             ((26,59), 'w', (16,14), (26,57)),
             ((26,57), 'w', (21,23), (26,60))]
    for st in steps:
        if w.pos()[:2] == (26,60): break
        if w.pos()[:2] != st[0]: continue
        if st[1] == 'p': press_at(w, s, *st[2])
        else: warp_at(w, s, *st[2], st[3])
    if w.pos()[:2] != (26,60): return False
    from walker import DIRS
    for sw in (None, (20,3), (18,25), (20,3)):
        if sw: press_at(w, s, *sw)
        for o in w.objs():
            if w.has_key(0x93): break
            if o[2] == 84 and any((o[0]+dx, o[1]+dy) in w.reach() for dx, dy in DIRS.values()):
                w.talk_to(o[0], o[1], shot=s, counter=False); w.advance(s, n=40); w._rc = {}
        if w.has_key(0x93): break
    w.log.append('ひみつのカギ %s' % w.has_key(0x93))
    return w.has_key(0x93)
BLAINE_SPR = 13
def blaine(w, s):
    w.can_cut = True; w.can_surf = True; lead_char(w); w.run_wild = True
    for _ in range(4): w.g.press('B', 4, 30)
    if w.badges() & 0x40: return True
    if not w.heal((6,1), s): return False
    if not go((26,61))(w, s): return False
    tried = set()
    for it in range(25):
        if w.badges() & 0x40: break
        bl = [o for o in w.objs() if o[2] == BLAINE_SPR]
        if bl:
            from walker import DIRS
            o = bl[0]
            if any((o[0]+dx, o[1]+dy) in w.reach() for dx, dy in DIRS.values()):
                w.talk_to(o[0], o[1], shot=s, counter=False); w.advance(s, n=300); continue
        if not press_bgs(w, s, tried): tried = set()
        w.advance(s, n=100)
    w.log.append('バッジ %s' % bin(w.badges()))
    return bool(w.badges() & 0x40)
def leave_mansion(w, s):
    tried = set()
    for it in range(20):
        if w.pos()[:2] not in ((26,57),(26,58),(26,59),(26,60)): return True
        w._rc = {}
        if w.travel((6,8), s, tries=1): return True
        if not press_bgs(w, s, tried): tried = set()
    return w.pos()[:2] not in ((26,57),(26,58),(26,59),(26,60))
def blaine2(w, s):
    w.can_cut = True; w.can_surf = True
    if not leave_mansion(w, s): return False
    return blaine(w, s)
def leave_mansion2(w, s):
    if w.pos()[:2] == (26,57) and not w.travel((6,8), s, tries=1):
        warp_at(w, s, 21, 23, (26,60))
    if w.pos()[:2] == (26,60):
        press_at(w, s, 20, 3)
        w.travel((26,57), s, tries=1)
    w._rc = {}
    return w.travel((6,8), s, tries=2)
def blaine3(w, s):
    w.can_cut = True; w.can_surf = True
    if w.pos()[:2] in ((26,57),(26,60)) and not leave_mansion2(w, s): return False
    return blaine(w, s)
def leave_mansion3(w, s):
    tried = set()
    for it in range(16):
        mid = w.pos()[:2]
        if mid not in ((26,57),(26,58),(26,59),(26,60)): return True
        w._rc = {}
        if w.travel((6,8), s, tries=1): return True
        if mid == (26,60):
            w._rc = {}
            if w.travel((26,57), s, tries=1): continue
        if not press_bgs(w, s, tried): tried = set()
    return False
def blaine4(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True
    w.advance(s)
    if not leave_mansion3(w, s): return False
    return blaine(w, s)
def blaine_talk(w, s):
    w.run_wild = True; lead_char(w)
    w.talk_to(3, 3, shot=s); w.advance(s, n=300)
    w.log.append('バッジ %s' % bin(w.badges()))
    return bool(w.badges() & 0x40)
def blaine5(w, s):
    w.can_surf = True; w.run_wild = True; lead_char(w)
    for _ in range(4): w.g.press('B', 4, 30)
    w.heal((6,1), s)
    if not w.travel((26,61), s): return False
    w.settle()
    return blaine_talk(w, s)
def drink(w, s):
    w.can_cut = True; w.can_surf = True; lead_char(w); w.run_wild = True; w.avoid = NOSAFFRON
    for _ in range(4): w.g.press('B', 4, 30)
    if not go((26,131))(w, s): return False
    w.goto(10, 2); w.face('U'); w.g.press('A', 8, 60); s('自販機')
    for _ in range(8):
        if w.textbox() or w.menu_kind(): w.g.press('A', 8, 60); s('自販機')
        else: break
    for _ in range(4): w.g.press('B', 8, 40)
    w.log.append('items %s' % w.rd(0xD5AA, 12))
    return True
def sabrina(w, s):
    w.can_cut = True; w.can_surf = True; lead_char(w); w.run_wild = True; w.avoid = set()
    for _ in range(4): w.g.press('B', 4, 30)
    if w.badges() & 0x20: return True
    if not go((25,6))(w, s): return False
    w.heal((25,6), s)
    if not go((25,4))(w, s): return False
    w.settle()
    sb = [o for o in w.objs()][0]
    w.talk_to(sb[0], sb[1], shot=s); w.advance(s, n=300)
    w.log.append('バッジ %s' % bin(w.badges()))
    return bool(w.badges() & 0x20)
SILPH = {(26,26),(26,27),(26,28),(26,29),(26,30),(26,31),(26,32),(26,33),(26,34),(26,35),(25,10)}
def silph_key(w, s):
    w.can_cut = True; w.can_surf = True; lead_char(w); w.run_wild = True; w.avoid = {(26,36)}
    for _ in range(4): w.g.press('B', 4, 30)
    if w.has_key(0x89): return True
    if not go((26,29))(w, s): return False
    from walker import DIRS
    for it in range(12):
        if w.has_key(0x89): break
        w._rc = {}
        balls = [o for o in w.objs() if o[2] == 84]
        got = False
        for o in balls:
            if any((o[0]+dx, o[1]+dy) in w.reach() for dx, dy in DIRS.values()):
                w.talk_to(o[0], o[1], shot=s, counter=False); w.advance(s, n=40); got = True; break
        if not got:
            # 東がわへ：5F の ワープ床を ためす
            for x, y, d in w.maps[(26,29)]['warps']:
                if d == (26,29) and (x, y) in w.reach():
                    w.door(x, y, 'U', s); w.settle(); break
    w.log.append('カードキー %s' % w.has_key(0x89))
    return w.has_key(0x89)
def go_bgs(w, s, dest, tries=10):
    tried = set()
    for it in range(tries):
        w._rc = {}
        if w.pos()[:2] == dest: return True
        if w.route(dest) is not None and w.travel(dest, s, tries=1): return True
        if not press_bgs(w, s, tried): return False
    return w.pos()[:2] == dest
def silph_boss(w, s):
    w.can_cut = True; w.can_surf = True; lead_char(w); w.run_wild = True; w.avoid = {(26,36)}
    for _ in range(4): w.g.press('B', 4, 30)
    if w.pos()[:2] not in ((26,27),(26,31),(26,35)) and not go_bgs(w, s, (26,27), tries=16): w.log.append("3F へ 行けない"); return False
    if w.pos()[:2] != (26,35) and not go_bgs(w, s, (26,31)): w.log.append('7F へ 行けない'); return False
    if not go_bgs(w, s, (26,35)): w.log.append('11F へ 行けない'); return False
    for it in range(6):
        gv = [o for o in w.objs() if o[2] == 116]
        if not gv: break
        from walker import DIRS
        o = gv[0]
        if any((o[0]+dx, o[1]+dy) in w.reach() for dx, dy in DIRS.values()):
            w.talk_to(o[0], o[1], shot=s); w.advance(s, n=300)
        elif not press_bgs(w, s, set()): break
    w.log.append('サカキ %s' % [o for o in w.objs() if o[2] == 116])
    return True
def president(w, s):
    w.run_wild = True
    o = [o for o in w.objs() if o[2] == 98]
    if o: w.talk_to(o[0][0], o[0][1], shot=s); w.advance(s, n=200)
    w.log.append('ボール %s' % w.rd(0xD5EF, 8))
    return True
def president2(w, s):
    w.run_wild = True
    w.goto(5, 6); w.step('U'); w.g.wait(30); w.step('R'); w.g.wait(30)
    w.face('R'); w.g.press('A', 8, 60); w.advance(s, n=200)
    w.log.append('ボール %s' % w.rd(0xD5EF, 8))
    return True
def go_cell(w, s, cells, tries=12):
    """同じ マップの 中で ワープ床を つかって cells の どれかへ"""
    from collections import deque
    cells = set(cells)
    for it in range(tries):
        w.settle(); mid = w.pos()[:2]; x, y = w.pos()[2:]
        if (x, y) in cells: return True
        w._rc = {}
        st = w._reach(mid, x, y); prev = {st: None}; q = deque([st]); goal = None
        while q:
            comp = q.popleft()
            if comp & cells: goal = comp; break
            for how, dm, (nx, ny) in w._hops(mid, comp):
                if dm != mid or how[0] != 'w': continue
                n = w._reach(mid, nx, ny)
                if n not in prev: prev[n] = (comp, how[1]); q.append(n)
        if goal is None: w.log.append('行けない マス %s' % (cells,)); return False
        steps = []; c = goal
        while prev[c]: pc, wp = prev[c]; steps.append(wp); c = pc
        if not steps:
            t = min(goal & cells, key=lambda p: abs(p[0]-x)+abs(p[1]-y)); w.goto_safe(*t, shot=s); w.advance(s); continue
        wx, wy = steps[-1]
        w.goto_safe(wx, wy, shot=s); w.g.wait(60); w.advance(s)
    return (w.pos()[2:]) in cells
def sabrina2(w, s):
    w.can_cut = True; w.can_surf = True; lead_char(w); w.run_wild = True
    if w.badges() & 0x20: return True
    if w.pos()[:2] != (25,4): return False
    sb = (9, 8)
    from walker import DIRS
    if not go_cell(w, s, {(sb[0]+dx, sb[1]+dy) for dx, dy in DIRS.values()}): return False
    w.talk_to(*sb, shot=s); w.advance(s, n=300)
    w.log.append('バッジ %s' % bin(w.badges()))
    return bool(w.badges() & 0x20)
def viridian_gym(w, s):
    w.can_cut = True; w.can_surf = True; lead_char(w); w.run_wild = True; w.avoid = set()
    for _ in range(4): w.g.press('B', 4, 30)
    if w.badges() & 0x80: return True
    if w.pos()[:2] != (23,4):
        if not go((23,9))(w, s): return False
        w.heal((23,9), s)
        if not go((23,4))(w, s): return False
    w.settle()
    from walker import DIRS
    gv = [o for o in w.objs() if o[2] == 116] or [(2, 1, 0)]
    o = gv[0]; w.log.append('サカキ %s' % (o,))
    if not w.goto_safe(o[0], o[1] + 1, shot=s):
        for d, (dx, dy) in DIRS.items():
            if w.goto_safe(o[0] + dx, o[1] + dy, shot=s): break
    w.talk_to(o[0], o[1], shot=s); w.advance(s, n=300)
    w.log.append('バッジ %s' % bin(w.badges()))
    return bool(w.badges() & 0x80)
def buy_repel(w, s):
    """ヤマブキの フレンドリィショップで シルバースプレー（MAX_REPEL $2B）を 買う"""
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    if w.count_item(0x2B) >= 4: return True
    if not go((25,5))(w, s): return False
    w.settle(); clerk = w.objs()[0]; r = w.reach()
    for (tx, ty), d in (((clerk[0]+1, clerk[1]), 'L'), ((clerk[0]+2, clerk[1]), 'L'), ((clerk[0], clerk[1]+2), 'U'), ((clerk[0]-2, clerk[1]), 'R')):
        if (tx, ty) in r: w.goto_safe(tx, ty); w.face(d); break
    w.g.press('A', 8, 60); w.g.press('A', 8, 60); w.g.press('A', 8, 60); w.g.wait(30); s('みせ')
    for _ in range(2): w.g.press('D', 4, 12)
    w.g.press('A', 4, 40)
    for _ in range(5): w.g.press('U', 4, 10)
    s('かず'); w.g.press('A', 4, 40); w.g.press('A', 4, 60); s('かう')
    for _ in range(6): w.g.press('B', 4, 30)
    w.log.append('シルバースプレー %d' % w.count_item(0x2B))
    return w.count_item(0x2B) >= 4
def to_vroad(w, s):
    w.can_cut = True; w.can_surf = True; lead_char(w); w.run_wild = True; w.avoid = set()
    for _ in range(4): w.g.press('B', 4, 30)
    if w.pos()[:2] in ((26,68),(26,69),(26,70)): return True
    return go((26,68))(w, s)
def to_vroad2(w, s):
    from fielduse import field_use
    w.can_cut = True; w.can_surf = True; lead_char(w); w.run_wild = True; w.avoid = set()
    for _ in range(4): w.g.press('B', 4, 30)
    if w.rd(0xD9B1)[0] == 0: field_use(w, 0x2B, s); w.log.append('スプレー %d' % w.rd(0xD9B1)[0])
    if w.pos()[:2] in ((26,68),(26,69),(26,70)): return True
    return go((26,68))(w, s)
def vroad1(w, s):
    import soko
    w.can_cut = True; w.can_surf = True; lead_char(w); w.run_wild = True; w.avoid = set()
    if w.pos()[:2] == (26,68):
        oth = {(o[0], o[1]) for o in w.objs()} - {(5,15)}
        if not soko.push(w, s, (5,15), (5,11), oth): return False
    return go((26,69))(w, s)
def vroad_solve(sw, goal_map):
    def f(w, s):
        import soko
        w.can_cut = True; w.can_surf = True; lead_char(w); w.run_wild = True; w.avoid = set()
        from fielduse import field_use
        mid = w.pos()[:2]
        if w.rd(0xD9B1)[0] == 0: field_use(w, 0x2B, s)
        if mid != goal_map[0]:
            bs = [(o[0], o[1]) for o in w.objs() if o[2] == 90]
            ram = []
            for i in range(1, 13):
                b = w.rd(0xD1F2 + 0x28 * i, 0x14)
                if b[0] == 124: ram.append((b[0x10] - 4, b[0x11] - 4))
            m = soko.solve(w, mid, w.pos()[2:], bs, goal_map[1], sw)
            w.log.append('押し方 %s' % (m,))
            if m is None: return False
            if not soko.run_pushes(w, s, m): return False
            w._rc = {}
        return go(goal_map[2])(w, s)
    return f
vroad1b = vroad_solve({(17,13): {(8,12),(8,13),(9,12),(9,13)}}, ((26,69), {(1,1)}, (26,69)))
SW2 = {(1,16): {(6,8),(7,8),(6,9),(7,9)}, (9,16): {(22,14),(23,14),(22,15),(23,15)}}
vroad2a = vroad_solve(SW2, ((26,70), {(23,7)}, (26,70)))
to3f = go((26,70))
def vroad_east(w, s):
    import soko
    w.can_cut = True; w.can_surf = True; lead_char(w); w.run_wild = True; w.avoid = set()
    from fielduse import field_use
    if w.pos()[:2] == (26,70):
        if not go((26,69))(w, s): return False
    if w.rd(0xD9B1)[0] == 0: field_use(w, 0x2B, s)
    w.settle()
    bs = [(o[0], o[1]) for o in w.objs() if o[2] == 90]
    # 1つめの スイッチの 岩は (1,16) に ある
    bs = [b for b in bs if b != (4, 14)] + [(1, 16)]
    w.log.append('岩 %s' % bs)
    m = soko.solve(w, (26,69), w.pos()[2:], bs, {(25,14)}, SW2)
    w.log.append('押し方 %s' % (m,))
    if m is None: return False
    if not soko.run_pushes(w, s, m): return False
    w._rc = {}
    w.travel((26,70), s, tries=1)
    return w.pos()[:2] == (26,70)
def to_league(w, s):
    w.can_cut = True; w.can_surf = True; lead_char(w); w.run_wild = True; w.avoid = set()
    from fielduse import field_use
    if w.rd(0xD9B1)[0] == 0 and w.pos()[:2] in ((26,68),(26,69),(26,70)): field_use(w, 0x2B, s)
    return go((16,2))(w, s)
def to_league2(w, s):
    w.can_cut = True; w.can_surf = True; lead_char(w); w.run_wild = True; w.avoid = set()
    from fielduse import field_use
    if w.pos()[:2] == (26,70) and w.pos()[2] < 25:
        if not go((26,69))(w, s): return False
    if w.pos()[:2] == (26,69):
        if w.rd(0xD9B1)[0] == 0: field_use(w, 0x2B, s)
        w.settle(); w.goto_safe(25, 14, shot=s); w.g.wait(60); w.settle()
        w.log.append('3F? %s' % (w.pos(),))
    if w.rd(0xD9B1)[0] == 0 and w.pos()[:2] in ((26,68),(26,69),(26,70)): field_use(w, 0x2B, s)
    return go((16,2))(w, s)
def lv100(w, s):
    import team
    for _ in range(4): w.g.press('B', 4, 30)
    w.settle(); team.write(w); w.g.wait(10)
    w.log.append('手持ち %s' % [(p['sp'], p['lv'], p['hp']) for p in w.party()])
    w.g.press('S', 4, 40)
    for _ in range(10):
        if w.rd(0xCF14)[0] == 7: break
        w.g.press('D' if w.rd(0xCF14)[0] < 7 else 'U', 4, 12)
    s('メニュー'); w.g.press('A', 4, 60)
    for _ in range(12):
        if w.menu_kind() == 'yesno': w.g.press('A', 4, 60)
        elif w.textbox(): w.g.press('A', 4, 40)
        else: w.g.wait(30)
    s('レポート')
    for _ in range(4): w.g.press('B', 4, 30)
    w.g.bsave('/home/claude/work/wt/lv100.sav')
    return True
def league(w, s):
    w.run_wild = True; w.lead_for = None
    for it in range(14):
        w.advance(s, n=60); w.settle()
        mid = w.pos()[:2]; w.log.append('へや %s %s' % (mid, w.pos()[2:]))
        if mid == (16,2):
            w.travel((16,3), s, tries=1); continue
        if mid in ((16,3),(16,4),(16,5),(16,6)):
            nxt = (16, mid[1] + 1)
            w.travel(nxt, s, tries=1)
            if w.pos()[:2] == nxt: continue
            w.goto_safe(5, 8, shot=s); w.face('U'); w.g.press('A', 8, 60); w.advance(s, n=400)
            continue
        if mid == (16,7):
            if getattr(w, 'stop7', False): return True
            w.travel((16,8), s, tries=1)
            if w.pos()[:2] == (16,8): continue
            o = [x for x in w.objs()]
            w.log.append('チャンピオンの へや %s' % o)
            for x, y, sp in o: w.talk_to(x, y, shot=s); w.advance(s, n=400)
            continue
        if mid == (16,8):
            w.advance(s, n=800); s('殿堂'); return True
        else: return False
    return False

def league_to7(w, s):
    w.stop7 = True; return league(w, s)
