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
def oak_ticket(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    if not go((13,6))(w, s): return False
    w.settle(); w.log.append('研究所 %s' % (w.objs(),))
    oak = [o for o in w.objs() if o[2] in (0x0B, 11)] or w.objs()[:1]
    w.talk_to(oak[0][0], oak[0][1], shot=s); w.advance(s, n=300)
    w.log.append('大事な どうぐ %s' % w.rd(0xD5D4, 12))
    return True
def to_port(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    if not go((26,40))(w, s): return False
    w.settle(); w.log.append('みなと %s 曜日 %d' % (w.objs(), w.rd(0xD1E5)[0]))
    return True
def board(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    w.log.append('曜日 %d' % w.rd(0xD1E5)[0])
    if w.pos()[:2] != (15,2):
        if not go((15,2))(w, s): return False
    w.settle(); w.goto_safe(7, 16, shot=s); w.face('D'); w.g.press('A', 8, 60); w.advance(s, n=400)
    w.g.wait(300); w.settle(); w.log.append('いま %s' % (w.pos(),))
    return True
def board2(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    w.log.append('曜日 %d' % w.rd(0xD1E5)[0])
    w.settle()
    for d in 'L':
        w.step(d)
    w.advance(s, n=400); w.g.wait(200)
    for _ in range(10):
        w.settle()
        if w.pos()[:2] != (15,2): break
        p = w.pos()[2:]
        w.goto_safe(7, 16, shot=s); w.advance(s, n=200)
    w.g.wait(300); w.advance(s, n=400); w.settle(); w.log.append('いま %s' % (w.pos(),))
    return w.pos()[:2] != (15,2)
def ship(w, s):
    w.run_wild = True
    for i in range(6):
        w.advance(s, n=300); w.g.wait(120); w.settle(); s('ふね')
        w.log.append('いま %s %s' % (w.pos(), w.objs()))
    return True
def ship_trip(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    if w.pos()[:2] == (15,3):
        w.goto_safe(25, 6, shot=s); w.advance(s, n=300); w.settle()
        w.log.append('じいさん 後 %s' % (w.pos(),))
    if not go((15,6))(w, s): return False
    w.settle()
    tw = [o for o in w.objs() if (o[0], o[1]) == (2, 25)]
    w.log.append('船長室 %s' % (w.objs(),))
    if tw: w.talk_to(2, 25, shot=s); w.advance(s, n=400)
    w.settle(); w.log.append('むすめ 後 %s' % (w.pos(),))
    if not go((15,5))(w, s): return False
    w.settle(); w.goto_safe(6, 1, shot=s); w.face('R'); w.g.press('A', 8, 60); w.advance(s, n=500)
    w.settle(); w.log.append('ベッド 後 %s' % (w.pos(),))
    return True
def ship_girl(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    if not go((15,7))(w, s): return False
    w.settle(); w.goto_safe(5, 11, shot=s); w.g.wait(60); w.settle(); w.log.append('1F 左 %s' % (w.pos(),))
    w.goto_safe(3, 13, shot=s); w.g.wait(60); w.settle()
    w.log.append('へや %s %s' % (w.pos(), w.objs()))
    w.talk_to(2, 25, shot=s); w.advance(s, n=500); w.settle()
    w.log.append('むすめ 後 %s' % (w.pos(),))
    if not go((15,5))(w, s): return False
    w.settle(); w.goto_safe(6, 1, shot=s); w.face('R'); w.g.press('A', 8, 60); w.advance(s, n=600)
    w.settle(); w.log.append('ベッド 後 %s' % (w.pos(),))
    return True
def ship_sailors(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    if not go((15,7))(w, s): return False
    w.settle(); sl = [o for o in w.objs() if o[1] == 6 and o[0] in (30, 31)]
    w.log.append('B1F %s' % (sl,))
    if sl: w.talk_to(sl[0][0], 6, shot=s); w.advance(s, n=200)
    if not go((15,4))(w, s): return False
    w.settle(); w.log.append('NNE %s' % (w.objs(),))
    for o in w.objs():
        if o[2] == 73:
            w.talk_to(o[0], o[1], shot=s); w.advance(s, n=300); break
    return True
def ship_lazy(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    if w.pos()[:2] != (15,3):
        if not go((15,3))(w, s): return False
    w.settle(); w.goto_safe(19, 7, shot=s); w.door(19, 8, 'D', s); w.g.wait(60); w.settle()
    w.log.append('へや %s' % (w.pos(),))
    w.talk_to(4, 26, shot=s); w.advance(s, n=400); w.settle()
    w.log.append('後 %s %s' % (w.pos(), w.objs()))
    return True
def ship_exit(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    if not go((15,3))(w, s): return False
    w.settle(); w.goto_safe(25, 2, shot=s); w.door(25, 1, 'U', s); w.advance(s, n=300); w.g.wait(120); w.settle()
    w.log.append('おりた %s' % (w.pos(),))
    for i in range(3): w.advance(s, n=200); w.settle()
    w.log.append('いま %s' % (w.pos(),))
    return True
def elm(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    if not go((24,5))(w, s): return False
    for i in range(4): w.advance(s, n=300); w.settle()
    w.log.append('研究所 %s %s 手持ち %d' % (w.pos(), w.objs(), len(w.party())))
    return True
def starter(w, s):
    w.run_wild = True
    w.talk_to(7, 3, shot=s); w.advance(s, n=400); w.settle()
    for i in range(3): w.advance(s, n=200); w.settle()
    w.log.append('あと %s %s PC? party %d' % (w.pos(), w.objs(), len(w.party())))
    return True
def mrpoke(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    for i in range(3): w.advance(s, n=200); w.settle()
    w.log.append('研究所 %s %s' % (w.pos(), w.objs()))
    if not go((26,10))(w, s): return False
    w.settle()
    for i in range(4): w.advance(s, n=300); w.settle()
    w.log.append('ポケモンじいさん %s %s' % (w.pos(), w.objs()))
    return True
def story(dest, n=4):
    def f(w, s):
        w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
        for i in range(n): w.advance(s, n=300); w.settle()
        w.log.append('はじめ %s %s' % (w.pos(), w.objs()))
        if not go(dest)(w, s): return False
        w.settle()
        for i in range(n): w.advance(s, n=300); w.settle()
        w.log.append('着 %s %s' % (w.pos(), w.objs()))
        return True
    return f
back_elm = story((24,5))
def adv(w, s):
    w.run_wild = True
    for i in range(6): w.advance(s, n=300); w.settle()
    w.log.append('いま %s %s' % (w.pos(), w.objs()))
    return True
def talk_obj(sp):
    def f(w, s):
        w.run_wild = True
        o = [o for o in w.objs() if o[2] == sp]
        if o: w.talk_to(o[0][0], o[0][1], shot=s)
        for i in range(4): w.advance(s, n=300); w.settle()
        w.log.append('いま %s %s' % (w.pos(), w.objs()))
        return bool(o)
    return f
talk_elm = talk_obj(60)
def lab_in(w, s):
    w.run_wild = True
    w.goto_safe(4, 5, shot=s); w.settle()
    for i in range(4): w.advance(s, n=300); w.settle()
    w.log.append('いま %s %s' % (w.pos(), w.objs()))
    return True
def elm_egg(w, s):
    w.run_wild = True; w.can_cut = True; w.can_surf = True; w.avoid = set()
    for i in range(3): w.advance(s, n=200); w.settle()
    w.talk_to(5, 2, shot=s)
    for i in range(4): w.advance(s, n=300); w.settle()
    w.log.append('はかせ 後 %s %s' % (w.pos(), w.objs()))
    w.goto_safe(4, 8, shot=s)
    for i in range(4): w.advance(s, n=300); w.settle()
    w.log.append('助手 後 %s %s どうぐ' % (w.pos(), w.objs()))
    return True
def jgym(gmap, leader=None):
    def f(w, s):
        w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
        b0 = w.rd(0xD56F)[0]
        if not go(gmap)(w, s): return False
        w.settle()
        lo = leader
        if lo is None:
            w.log.append('ジム %s' % (w.objs(),)); return True
        w.talk_to(*lo, shot=s)
        for i in range(5): w.advance(s, n=300); w.settle()
        w.log.append('バッジ %02x -> %02x %s' % (b0, w.rd(0xD56F)[0], w.pos()))
        return w.rd(0xD56F)[0] != b0
    return f
falkner = jgym((10,7), (5,1))
def talk_all(w, s, sps=None, n=3):
    for o in list(w.objs()):
        if sps and o[2] not in sps: continue
        cur = [x for x in w.objs() if x[:2] == o[:2]]
        if not cur: continue
        w.talk_to(o[0], o[1], shot=s)
        for i in range(n): w.advance(s, n=300); w.settle()
def kurt(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    if not go((8,4))(w, s): return False
    w.settle(); w.talk_to(3, 2, shot=s)
    for i in range(4): w.advance(s, n=300); w.settle()
    w.log.append('クルト 後 %s %s' % (w.pos(), w.objs()))
    return True
def well(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    if not go((3,32))(w, s): return False
    w.settle(); w.log.append('いど %s' % (w.objs(),))
    if [o for o in w.objs() if o[:2] == (15, 12)]:
        w.talk_to(15, 12, shot=s)
        for i in range(4): w.advance(s, n=300); w.settle()
        w.log.append('ムサシ・コジロウ 後 %s' % (w.objs(),))
    for k in range(4):
        r = [o for o in w.objs() if o[1] < 12 and o[2] not in (0x55,)]
        w.log.append('のこり %s' % (w.objs(),))
        ro = [o for o in w.objs() if (o[0], o[1]) in ((15,7),(5,2),(5,6),(10,4))]
        if not ro: break
        o = ro[0]; w.talk_to(o[0], o[1], shot=s)
        for i in range(4): w.advance(s, n=300); w.settle()
    w.log.append('いど 後 %s %s' % (w.pos(), w.objs()))
    return True
def drop6(w, s):
    w.g.poke(0xD9E8, 5); w.g.poke(0xD9EE, 0xFF); w.g.wait(2)
    return True
def aide_egg(w, s):
    drop6(w, s)
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    if not go((10,10))(w, s): return False
    w.settle()
    for i in range(6): w.advance(s, n=300); w.settle()
    w.log.append('PC %s %s 手持ち %s' % (w.pos(), w.objs(), [p['sp'] for p in w.party()]))
    return True
def aide_talk(w, s):
    w.run_wild = True
    w.talk_to(4, 3, shot=s)
    for i in range(5): w.advance(s, n=300); w.settle()
    w.log.append('PC %s %s 手持ち %s' % (w.pos(), w.objs(), [p['sp'] for p in w.party()]))
    return True
def r32cave(w, s):
    w.run_wild = True
    w.goto_safe(7, 81, shot=s); s('x'); w.log.append('いま %s' % (w.pos(),))
    w.step('U'); w.g.wait(30); s('u'); w.log.append('いま %s' % (w.pos(),))
    return True
def r32fence(w, s):
    w.run_wild = True
    w.goto_safe(7, 75, shot=s); w.log.append('いま %s' % (w.pos(),))
    return True
def rocket2(w, s):
    w.run_wild = True
    w.talk_to(15, 12, shot=s)
    for i in range(4): w.advance(s, n=300); w.settle()
    return True
def well2(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set(); w.no_still = True
    for xy in ((10,4),(5,6),(5,2)):
        if not [o for o in w.objs() if o[:2] == xy]: continue
        w.talk_to(*xy, shot=s)
        for i in range(4): w.advance(s, n=300); w.settle()
        w.log.append('%s 後 %s %s' % (xy, w.pos(), w.objs()))
    for i in range(4): w.advance(s, n=300); w.settle()
    return not [o for o in w.objs() if o[2] == 53]
bugsy = jgym((8,5), (5,7))
to_goldenrod = story((11,2), n=3)
def whitney(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    b0 = w.rd(0xD56F)[0]
    if not go((11,3))(w, s): return False
    w.settle(); w.talk_to(8, 3, shot=s)
    for i in range(4): w.advance(s, n=300); w.settle()
    w.log.append('1回目 %02x %s' % (w.rd(0xD56F)[0], w.pos()))
    w.goto_safe(8, 6, shot=s); w.goto_safe(8, 5, shot=s)
    for i in range(3): w.advance(s, n=300); w.settle()
    w.talk_to(8, 3, shot=s)
    for i in range(4): w.advance(s, n=300); w.settle()
    w.log.append('バッジ %02x -> %02x %s' % (b0, w.rd(0xD56F)[0], w.pos()))
    return w.rd(0xD56F)[0] != b0
def visit_talk(mid, xy, n=4):
    def f(w, s):
        w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
        if not go(mid)(w, s): return False
        w.settle()
        if not [o for o in w.objs() if o[:2] == xy]:
            w.log.append('いない %s %s' % (xy, w.objs())); return True
        w.talk_to(*xy, shot=s)
        for i in range(n): w.advance(s, n=300); w.settle()
        w.log.append('%s %s 後 %s %s' % (mid, xy, w.pos(), w.objs()))
        return True
    return f
def seq(*fs):
    def f(w, s):
        for g in fs:
            if not g(w, s): return False
        return True
    return f
sudowoodo = seq(visit_talk((10,3), (33,12)), visit_talk((11,8), (2,4)), visit_talk((10,3), (35,9), 6))
def burned(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    if not go((3,13))(w, s): return False
    w.settle(); w.goto_safe(11, 9, shot=s)
    for i in range(5): w.advance(s, n=300); w.settle()
    w.log.append('ライバル 後 %s' % (w.pos(),))
    if w.pos()[:2] != (3,14):
        go((3,14))(w, s)
    w.settle(); w.goto_safe(10, 6, shot=s)
    for i in range(6): w.advance(s, n=300); w.settle()
    w.log.append('B1F 後 %s %s' % (w.pos(), w.objs()))
    return True
morty = jgym((4,7), (5,1))
to_bt = go((3,13))
def bt_fight(w, s):
    w.run_wild = True
    w.goto_safe(10, 13, shot=s)
    for i in range(3):
        w.advance(s, n=300); w.settle()
    s('end')
    return True
def bt_cap(w, s):
    w.run_wild = True
    of = w.fight
    def f2(*a, **k):
        r = of(*a, **k); w.g.wait(30); w.g.save_state('/home/claude/work/wt/bt_after.st'); s('after'); return r
    w.fight = f2
    if not go((3,13))(w, s): return False
    w.goto_safe(9, 14, shot=s)
    for i in range(3): w.advance(s, n=300); w.settle()
    return True
def burned2(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    if w.pos()[:2] != (3,13) and not go((3,13))(w, s): return False
    for i in range(3): w.advance(s, n=300); w.settle()
    w.log.append('ライバル 後 %s %s' % (w.pos(), w.objs()))
    w.goto_safe(10, 6, shot=s); w.step('D'); w.g.wait(60); w.advance(s); w.settle()
    w.log.append('穴 %s' % (w.pos(),))
    w.goto_safe(9, 5, shot=s)
    for i in range(6): w.advance(s, n=300); w.settle()
    w.log.append('B1F 後 %s %s' % (w.pos(), w.objs()))
    return True
def burned3(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    w.goto_safe(10, 6, shot=s); w.log.append('上 %s' % (w.pos(),))
    w.door(10, 7, 'D', s); w.g.wait(60); w.advance(s); w.settle()
    w.log.append('穴 %s' % (w.pos(),))
    w.goto_safe(9, 5, shot=s)
    for i in range(6): w.advance(s, n=300); w.settle()
    w.log.append('B1F 後 %s %s' % (w.pos(), w.objs()))
    return True
def bt_smash(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    if not visit_talk((10,3), (44,9))(w, s): return False
    if not go((3,13))(w, s): return False
    w.settle(); w.talk_to(4, 3, shot=s)
    for i in range(3): w.advance(s, n=200); w.settle()
    w.log.append('いわ 後 %s %s' % (w.pos(), w.objs()))
    w.goto_safe(10, 6, shot=s); w.log.append('上 %s' % (w.pos(),))
    w.door(10, 7, 'D', s); w.g.wait(60); w.advance(s); w.settle()
    w.log.append('穴 %s' % (w.pos(),))
    w.goto_safe(9, 5, shot=s)
    for i in range(6): w.advance(s, n=300); w.settle()
    w.log.append('B1F 後 %s %s' % (w.pos(), w.objs()))
    return True
lighthouse = visit_talk((3,39), (8,8), 5)
def r39(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    w.talk_to(13, 22, shot=s)
    for i in range(3): w.advance(s, n=300); w.settle()
    w.log.append('後 %s' % (w.pos(),))
    return lighthouse(w, s)
pharmacy = visit_talk((22,7), (2,3), 4)
to_cgym = go((22,5))
cian = seq(pharmacy, to_cgym)
cgym_push = vroad_solve({}, ((22,5), {(4,2),(3,2),(5,2)}, (22,5)))
def chuck(w, s):
    b0 = w.rd(0xD56F)[0]
    if not cgym_push(w, s): return False
    w.talk_to(4, 1, shot=s)
    for i in range(5): w.advance(s, n=300); w.settle()
    w.log.append('バッジ %02x -> %02x %s' % (b0, w.rd(0xD56F)[0], w.pos()))
    return w.rd(0xD56F)[0] != b0
def chuck2(w, s):
    import soko
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    b0 = w.rd(0xD56F)[0]
    mid = w.pos()[:2]; c = w.coll(mid)
    bs = [(o[0], o[1]) for o in w.objs() if o[2] == 90]
    people = {(o[0], o[1]) for o in w.objs() if o[2] != 90}
    op = w.passable
    def pas2(cc, frm, d, _op=op):
        return _op(cc, frm, d)
    # 人の マスは 通れない
    orig = soko.solve
    cw = w.coll
    def coll2(m, _cw=cw):
        f = _cw(m)
        return lambda x, y: (0x07 if (x, y) in people and m == mid else f(x, y))
    w.coll = coll2
    mv = soko.solve(w, mid, w.pos()[2:], bs, {(4,2),(3,2)})
    w.coll = cw
    w.log.append('押し方 %s' % (mv,))
    if mv is None: return False
    if not soko.run_pushes(w, s, mv): return False
    w._rc = {}
    w.talk_to(4, 1, shot=s)
    for i in range(5): w.advance(s, n=300); w.settle()
    w.log.append('バッジ %02x -> %02x %s' % (b0, w.rd(0xD56F)[0], w.pos()))
    return w.rd(0xD56F)[0] != b0
jasmine = seq(visit_talk((3,39), (8,8), 6), jgym((1,2), (5,3)))
def gyarados(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = False; w.avoid = set()
    if not go((9,6))(w, s): return False
    w.settle(); w.talk_to(18, 22, shot=s)
    for i in range(4): w.advance(s, n=300); w.settle()
    w.log.append('ギャラドス 後 %s %s' % (w.pos(), w.objs()))
    w.run_wild = True
    if [o for o in w.objs() if o[:2] == (21,28)]:
        w.talk_to(21, 28, shot=s)
        for i in range(5): w.advance(s, n=300); w.settle()
    w.log.append('ワタル 後 %s %s' % (w.pos(), w.objs()))
    return True
def gyarados2(w, s):
    w.can_cut = True; w.can_surf = True; w.avoid = set()
    w.run_wild = False
    w.fight(run=False, shot=s)
    for i in range(4): w.advance(s, n=300); w.settle()
    w.log.append('ギャラドス 後 %s %s' % (w.pos(), w.objs()))
    w.run_wild = True
    if [o for o in w.objs() if o[:2] == (21,28)]:
        w.talk_to(21, 28, shot=s)
        for i in range(5): w.advance(s, n=300); w.settle()
    w.log.append('ワタル 後 %s %s' % (w.pos(), w.objs()))
    return True
mart_lance = story((3,40), n=3)
to_rb2 = story((3,42), n=3)
def rb3(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    if w.pos()[:2] == (3,42):
        w.goto_safe(4, 13, shot=s)
        for i in range(3): w.advance(s, n=300); w.settle()
        w.log.append('ワタル 後 %s' % (w.pos(),))
    if not go((3,43))(w, s): return False
    w.settle(); w.log.append('B3F %s %s' % (w.pos(), w.objs()))
    for xy in ((7,2),(5,15),(21,7)):
        o = [o for o in w.objs() if o[:2] == xy]
        if not o: continue
        w.talk_to(*xy, shot=s)
        for i in range(4): w.advance(s, n=300); w.settle()
        w.log.append('%s 後 %s' % (xy, w.pos()))
    w.goto_safe(10, 8, shot=s)
    for i in range(6): w.advance(s, n=300); w.settle()
    w.log.append('扉 後 %s %s' % (w.pos(), w.objs()))
    return True
def rb3door(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    w.goto_safe(10, 10, shot=s); w.face('U'); w.g.press('A', 8, 60)
    for i in range(3): w.advance(s, n=300); w.settle()
    w.log.append('扉 %s' % (w.pos(),))
    w._rc = {}
    w.goto_safe(10, 8, shot=s)
    for i in range(6): w.advance(s, n=300); w.settle()
    w.log.append('ボス 後 %s %s' % (w.pos(), w.objs()))
    return True
def rb3door2(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    w.door(27, 2, 'U', s); w.g.wait(60); w.advance(s); w.settle()
    w.log.append('B2F %s' % (w.pos(),))
    w.door(3, 2, 'U', s); w.g.wait(60); w.advance(s); w.settle()
    w.log.append('B3F %s' % (w.pos(),))
    return rb3door(w, s)
def rb3pw(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    w.door(3, 2, 'U', s); w.g.wait(60); w.advance(s); w.settle()
    w.door(27, 2, 'U', s); w.g.wait(60); w.advance(s); w.settle()
    w.log.append('B3F 右 %s' % (w.pos(),))
    for xy in ((5,15),(21,7)):
        for k in range(2):
            w.talk_to(*xy, shot=s)
            for i in range(4): w.advance(s, n=300); w.settle()
        w.log.append('%s 後 %s' % (xy, w.pos()))
    w.door(27, 2, 'U', s); w.g.wait(60); w.advance(s); w.settle()
    w.door(3, 2, 'U', s); w.g.wait(60); w.advance(s); w.settle()
    return rb3door(w, s)
def rb2boss(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    for (x, y) in ((3,2),(27,2),(27,14)):
        w._rc = {}
        w.door(x, y, 'U', s); w.g.wait(60); w.advance(s); w.settle()
        w.log.append('→ %s' % (w.pos(),))
    w._rc = {}
    w.goto_safe(14, 13, shot=s); w.log.append('扉前 %s' % (w.pos(),))
    w.step('U'); w.advance(s); w.settle(); w.step('U')
    for i in range(6): w.advance(s, n=300); w.settle()
    w.log.append('B2F ボス 後 %s %s' % (w.pos(), w.objs()))
    return True
def rb2door(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    w.face('U'); w.g.press('A', 8, 60)
    for i in range(3): w.advance(s, n=300); w.settle()
    w._rc = {}
    w.step('U'); w.advance(s); w.settle(); w.step('U')
    for i in range(8): w.advance(s, n=300); w.settle()
    w.log.append('B2F ボス 後 %s %s' % (w.pos(), w.objs()))
    return True
def rb_murkrow(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    for (x, y) in ((27,14),(27,2),(3,2)):
        w._rc = {}
        w.door(x, y, 'U', s); w.g.wait(60); w.advance(s); w.settle()
        w.log.append('→ %s' % (w.pos(),))
    w._rc = {}
    w.talk_to(7, 2, shot=s)
    for i in range(3): w.advance(s, n=300); w.settle()
    w.log.append('ヤミカラス 後 %s' % (w.pos(),))
    for (x, y) in ((3,2),(27,2),(27,14)):
        w._rc = {}
        w.door(x, y, 'U', s); w.g.wait(60); w.advance(s); w.settle()
        w.log.append('→ %s' % (w.pos(),))
    w._rc = {}
    w.goto_safe(14, 13, shot=s)
    return rb2door(w, s)
def electrodes(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = False; w.avoid = set()
    for xy in ((7,5),(7,7),(7,9)):
        if not [o for o in w.objs() if o[:2] == xy]: continue
        w.talk_to(*xy, shot=s)
        w.run_wild = False
        for i in range(4): w.advance(s, n=300); w.settle()
        w.log.append('%s 後 %s' % (xy, w.pos()))
    for i in range(5): w.advance(s, n=300); w.settle()
    w.log.append('後 %s %s' % (w.pos(), w.objs()))
    return True
to_pgym = go((2,2))
def ice_bfs(goal_cells, maxn=500):
    """こおりの 床：エミュレーターで ためして 行ける 所を さがす（ステートを ファイルに）"""
    def f(w, s):
        import collections, os
        w.run_wild = True
        g = w.g; d0 = '/tmp/ice'; os.makedirs(d0, exist_ok=True)
        start = w.pos(); g.save_state('%s/s0.st' % d0)
        seen = {start: ('%s/s0.st' % d0, [])}; q = collections.deque([start]); n = 0
        while q and n < maxn:
            p = q.popleft(); st, path = seen[p]
            if p[2:] in goal_cells and p[:2] == start[:2]:
                g.load_state(st); g.wait(2); w.log.append('こおり 道 %s' % (path,)); return True
            for d in 'UDLR':
                g.load_state(st); g.wait(2)
                w.step(d)
                for _ in range(40):
                    a = w.pos(); g.wait(6)
                    if w.pos() == a and not w.moving(): break
                if w.textbox() or w.in_battle():
                    idle = 0
                    for _k in range(60):
                        if w.textbox() or w.in_battle(): w.advance(s, n=200); idle = 0
                        else:
                            g.wait(40); idle += 1
                            if idle >= 4: break
                    w.settle()
                    if w.pos() == p:
                        w.step(d)
                        for _ in range(40):
                            a = w.pos(); g.wait(6)
                            if w.pos() == a and not w.moving(): break
                np_ = w.pos(); n += 1
                if np_ in seen or np_[:2] != start[:2]: continue
                fn = '%s/s%d.st' % (d0, len(seen)); g.save_state(fn)
                seen[np_] = (fn, path + [d]); q.append(np_)
        w.log.append('こおり 見つからない %d %s' % (len(seen), sorted(k[2:] for k in seen))); return False
    return f
def pryce(w, s):
    b0 = w.rd(0xD56F)[0]
    if not ice_bfs({(5,4),(4,3),(6,3)})(w, s): return False
    w.talk_to(5, 3, shot=s)
    for i in range(5): w.advance(s, n=300); w.settle()
    w.log.append('バッジ %02x -> %02x %s' % (b0, w.rd(0xD56F)[0], w.pos()))
    return w.rd(0xD56F)[0] != b0
def rt5(w, s):
    if not story((3,21), n=3)(w, s): return False
    w.goto_safe(0, 3, shot=s)
    for i in range(5): w.advance(s, n=300); w.settle()
    w.log.append('ニセ局長 後 %s %s' % (w.pos(), w.objs()))
    return True
def exit_ice(w, s):
    if not ice_bfs({(4,16),(5,16),(4,15),(5,15),(4,14),(5,14)})(w, s): return False
    w.door(4, 17, 'D', s); w.g.wait(60); w.advance(s); w.settle()
    w.log.append('外 %s' % (w.pos(),))
    return True
rt5b = seq(exit_ice, rt5)
def to_switch(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    if not go((3,45))(w, s): return False
    w.settle(); w.goto_safe(18, 7, shot=s); w.face('U'); w.g.press('A', 8, 60)
    for i in range(3): w.advance(s, n=200); w.settle()
    w._rc = {}
    w.log.append('扉 %s' % (w.pos(),))
    w.door(18, 6, 'U', s); w.g.wait(60); w.advance(s); w.settle()
    for i in range(4): w.advance(s, n=300); w.settle()
    w.log.append('スイッチの へや %s %s' % (w.pos(), w.objs()))
    return True
def into_switch(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    w.door(22, 27, 'U', s); w.g.wait(60); w.advance(s); w.settle()
    for i in range(3): w.advance(s, n=300); w.settle()
    w.goto_safe(19, 4, shot=s)
    for i in range(5): w.advance(s, n=300); w.settle()
    w.log.append('スイッチの へや %s %s' % (w.pos(), w.objs()))
    return True
def switches(w, s):
    import itertools
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    g = w.g; base = '/tmp/sw_base_%d.st' % id(w); g.save_state(base)
    for n in range(0, 4):
        for combo in itertools.permutations([(16,2),(10,2),(2,2)], n):
            g.load_state(base); g.wait(2); w._rc = {}
            for (x, y) in combo:
                w.goto_safe(x, y, shot=None); w.face('U'); g.press('A', 8, 40)
                for _ in range(6):
                    if w.menu_kind() == 'yesno': g.press('A', 8, 40)
                    elif w.textbox(): g.press('A', 8, 30)
                    else: break
                w.advance(None, n=100); w.settle(); w._rc = {}
            w._rc = {}
            r = w.reach()
            ok = (22, 9) in r or (23, 9) in r or (22, 10) in r
            w.log.append('%s %s' % (combo, ok))
            if ok:
                w.goto_safe(22, 9, shot=s); w.door(22, 10, 'D', s); g.wait(60); w.advance(s); w.settle()
                w.log.append('倉庫 %s' % (w.pos(),)); return True
    return False
def cardkey(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    w.talk_to(12, 8, shot=s)
    for i in range(4): w.advance(s, n=300); w.settle()
    w.log.append('局長 後 %s' % (w.pos(),))
    if not go((3,19))(w, s): return False
    w.goto_safe(14, 3, shot=s); w.face('U'); w.g.press('A', 8, 60)
    for i in range(3): w.advance(s, n=300); w.settle()
    w._rc = {}
    w.log.append('カードキー 後 %s' % (w.pos(),))
    if not go((3,21))(w, s): return False
    w.goto_safe(16, 5, shot=s)
    for i in range(8): w.advance(s, n=300); w.settle()
    w.log.append('5F 後 %s %s' % (w.pos(), w.objs()))
    return True
def cardkey2(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    w.door(2, 12, 'D', s); w.g.wait(60); w.advance(s); w.settle(); w._rc = {}
    w.log.append('スイッチの へや %s' % (w.pos(),))
    r = w.reach()
    for t in [(4,29),(5,29),(20,29),(21,29),(5,25),(21,25)]:
        if t in r or any((t[0]+dx, t[1]+dy) in r for dx, dy in ((0,-1),(1,0),(-1,0))):
            w.log.append('出口 %s' % (t,))
            d = 'D' if t[1] == 29 else 'U'
            w.door(t[0], t[1], d, s); w.g.wait(60); w.advance(s); w.settle(); break
    w._rc = {}
    w.log.append('出た %s' % (w.pos(),))
    if not go((3,19))(w, s): return False
    w.goto_safe(14, 3, shot=s); w.face('U'); w.g.press('A', 8, 60)
    for i in range(3): w.advance(s, n=300); w.settle()
    w._rc = {}
    w.log.append('カードキー 後 %s' % (w.pos(),))
    if not go((3,21))(w, s): return False
    w.goto_safe(16, 5, shot=s)
    for i in range(8): w.advance(s, n=300); w.settle()
    w.log.append('5F 後 %s %s' % (w.pos(), w.objs()))
    return True
def emerg(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    w.goto_safe(20, 12, shot=s); w.face('U'); w.g.press('A', 8, 60)
    for _ in range(6):
        if w.menu_kind() == 'yesno': w.g.press('A', 8, 40)
        elif w.textbox(): w.g.press('A', 8, 30)
        else: break
    w.advance(s); w.settle(); w._rc = {}
    r = w.reach(); w.log.append('非常 後 %s %d' % (w.pos(), len(r)))
    for t in [(4,29),(5,29),(20,29),(21,29),(5,25),(21,25)]:
        if t in r or any((t[0]+dx, t[1]+dy) in r for dx, dy in ((0,-1),(1,0),(-1,0))):
            w.log.append('出口 %s' % (t,))
            d = 'D' if t[1] == 29 else 'U'
            w.door(t[0], t[1], d, s); w.g.wait(60); w.advance(s); w.settle(); break
    w._rc = {}
    w.log.append('出た %s' % (w.pos(),))
    if not go((3,19))(w, s): return False
    w.goto_safe(14, 3, shot=s); w.face('U'); w.g.press('A', 8, 60)
    for i in range(3): w.advance(s, n=300); w.settle()
    w._rc = {}
    w.log.append('カードキー 後 %s' % (w.pos(),))
    if not go((3,21))(w, s): return False
    w.goto_safe(16, 5, shot=s)
    for i in range(8): w.advance(s, n=300); w.settle()
    w.log.append('5F 後 %s %s' % (w.pos(), w.objs()))
    return True
def rt_boss(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    def hop(x, y):
        w._rc = {}; w.door(x, y, 'U', s); w.g.wait(60); w.advance(s); w.settle(); w._rc = {}
        w.log.append('→ %s' % (w.pos(),))
    hop(0, 0)                      # 5F → 4F
    if (12, 1) not in w.reach():
        hop(9, 0)                  # 4F → 3F
        hop(17, 0)                 # 3F → 4F 右
    hop(12, 0)                     # 4F → 5F 右
    w.goto_safe(16, 5, shot=s)
    for i in range(8): w.advance(s, n=300); w.settle()
    w.log.append('5F 後 %s %s' % (w.pos(), w.objs()))
    return True
to_bt_city = go((5,10))
def rt_out(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    def hop(x, y):
        w._rc = {}; w.door(x, y, 'U', s); w.g.wait(60); w.advance(s); w.settle(); w._rc = {}
        w.log.append('→ %s' % (w.pos(),))
    hop(12, 0); hop(17, 0)
    return go((5,10))(w, s)
def to_bt2(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True
    w.avoid = set()
    if w.pos()[:2] in ((5,8),(5,9)):
        go((24,3))(w, s)
    w.avoid = {(5,8), (5,9)}
    r = w.route((5,10)); w.log.append('道 %s' % (None if r is None else [m for _, m in r],))
    if r is None: return False
    while tleft(w) > 20:
        if w.pos()[:2] == (5,10): return True
        w.travel((5,10), s, tries=1)
        if w.log and w.log[-1].startswith('行けない'): return False
    return w.pos()[:2] == (5,10)
def world_bfs(goal_maps, maxn=3000, tag='wb', allow=None):
    """エミュレーターで ためして 進む（こおり・かいりきの 岩・穴 も そのまま）。key ＝ マップ・位置・岩の 位置"""
    def f(w, s):
        import collections, os
        w.run_wild = True; g = w.g; d0 = '/tmp/%s_%d' % (tag, os.getpid()); os.makedirs(d0, exist_ok=True)
        def key():
            p = w.pos(); bs = []
            mo = w.rd(0xD438, 16 * 16)
            for i in range(1, 16):
                e = mo[16 * i:16 * i + 16]
                if e[1] not in (0x5a, 0x78): continue
                if e[0] != 0xFF and e[0] < 13:
                    b = w.rd(0xD1F0 + 0x28 * e[0], 0x14); bs.append((i, b[0x10], b[0x11]))
                else:
                    fl = e[12] | e[13] << 8
                    if fl != 0xFFFF and w.flag(fl): bs.append((i, 'x'))
                    else: bs.append((i, e[3], e[2]))
            return p + (tuple(bs),)
        def settle_all():
            idle = 0
            for _k in range(60):
                if w.textbox() or w.in_battle():
                    if w.menu_kind() == 'yesno': g.press('A', 8, 40)
                    else: w.advance(s, n=200)
                    idle = 0
                else:
                    g.wait(30); idle += 1
                    if idle >= 3: break
            w.settle()
        def move(d):
            before = w.pos()
            w.step(d)
            for _ in range(40):
                a = w.pos(); g.wait(6)
                if w.pos() == a and not w.moving(): break
            settle_all()
            if w.pos() == before:            # 岩なら かいりき
                w.face(d); g.press('A', 8, 40)
                for _ in range(20):
                    if w.menu_kind() == 'yesno': g.press('A', 8, 40)
                    elif w.textbox(): g.press('A', 8, 30)
                    else:
                        g.wait(20)
                        if not w.textbox(): break
                w.step(d); g.wait(40); settle_all()
        k0 = key(); g.save_state('%s/0.st' % d0)
        seen = {k0: ('%s/0.st' % d0, [])}; q = collections.deque([k0]); n = 0
        while q and n < maxn and tleft(w) > 30:
            k = q.popleft(); st, path = seen[k]
            if k[:2] in goal_maps:
                g.load_state(st); g.wait(2); w.log.append('道 %d手 %s' % (len(path), ''.join(path))); return True
            for d in 'UDLR':
                g.load_state(st); g.wait(2); g.poke(0xD9B1, 200); move(d); n += 1
                nk = key()
                if nk in seen: continue
                if allow and nk[:2] not in allow and nk[:2] not in goal_maps: continue
                fn = '%s/%d.st' % (d0, len(seen)); g.save_state(fn)
                seen[nk] = (fn, path + [d]); q.append(nk)
                if nk[:2] in goal_maps:
                    w.log.append('道 %d手 %s' % (len(path) + 1, ''.join(path + [d]))); return True
        w.log.append('見つからない %d %s' % (len(seen), sorted({k[:2] for k in seen})))
        return False
    return f
def icepath(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    if not go((3,53))(w, s): return False
    return world_bfs({(5,10)}, allow={(3,53),(3,54),(3,55),(3,56),(3,57)})(w, s)
def icepath2(w, s):
    w.can_cut = True; w.can_surf = True; w.run_wild = True
    w.avoid = {(5,8), (5,9)}
    if w.pos()[:2] != (3,53):
        while tleft(w) > 20 and w.pos()[:2] != (2,6):
            w.travel((2,6), s, tries=1)
            if w.log and w.log[-1].startswith('行けない'): return False
        w.log.append('44番 %s' % (w.pos(),))
        w.avoid = set()
        wp = [x for x in w.maps[(2,6)]['warps'] if x[2] == (3,53)][0]
        w.door(wp[0], wp[1], 'U', s); w.g.wait(60); w.advance(s); w.settle()
        w.log.append('こおりの ぬけみち %s' % (w.pos(),))
    w.g.save_state('/home/claude/work/wt/ice_in.st')
    w.g.poke(0xD9B1, 200)
    return world_bfs({(5,10)}, allow={(3,53),(3,54),(3,55),(3,56),(3,57)})(w, s)
def ice_b1f(w, s):
    import soko, itertools
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set(); w.g.poke(0xD9B1, 200)
    pits = [(17,3),(11,2),(4,7),(5,12),(12,13)]
    mid = w.pos()[:2]
    for rnd in range(4):
        bs = [(o[0], o[1]) for o in w.objs() if o[2] == 90]
        w.log.append('岩 %s' % (bs,))
        if not bs: break
        done = False
        for b in bs:
            for t in pits:
                others = set(bs) - {b}
                pl = soko.plan(w, mid, w.pos()[2:], b, t, others)
                if pl is None: continue
                w.log.append('押す %s→%s %s' % (b, t, pl))
                if soko.push(w, s, b, t, others):
                    w.g.wait(60)
                    for i in range(3): w.advance(s, n=200); w.settle()
                    w._rc = {}; done = True; break
            if done: break
        if not done: w.log.append('押せる 岩が ない'); return False
    w.log.append('のこり %s' % ([o for o in w.objs() if o[2] == 90],))
    return True
to_bgym = go((5,1))
def boulders(w):
    mo = w.rd(0xD438, 16 * 16); out = []
    for i in range(1, 16):
        e = mo[16 * i:16 * i + 16]
        if e[1] != 0x5a: continue
        fl = e[12] | e[13] << 8
        if fl != 0xFFFF and w.flag(fl): continue
        if e[0] != 0xFF and e[0] < 13:
            b = w.rd(0xD1F0 + 0x28 * e[0], 0x14); out.append((b[0x10] - 4, b[0x11] - 4))
        else: out.append((e[3] - 4, e[2] - 4))
    return out
def boulder_pits(pits, goal_map):
    def f(w, s):
        import soko
        w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
        if not go(goal_map)(w, s): return False
        mid = w.pos()[:2]; left = list(pits)
        for rnd in range(len(pits)):
            bs = boulders(w)
            done = False
            for t in list(left):
                for b in sorted(bs, key=lambda b: abs(b[0]-t[0]) + abs(b[1]-t[1])):
                    others = set(bs) - {b}
                    pl = soko.plan(w, mid, w.pos()[2:], b, t, others)
                    if pl is None: continue
                    w.log.append('押す %s→%s' % (b, t))
                    if soko.push(w, s, b, t, others):
                        w.g.wait(60)
                        for i in range(3): w.advance(s, n=200); w.settle()
                        w._rc = {}; done = True; left.remove(t); break
                if done: break
            if not done: w.log.append('押せる 岩が ない %s' % (left,)); return False
            if w.pos()[:2] != mid:
                w.log.append('落ちた %s' % (w.pos(),)); go(mid)(w, s)
        return True
    return f
bgym2 = boulder_pits([(8,3),(8,7),(2,5)], (5,2))
bgym2b = boulder_pits([(8,3),(8,7)], (5,2))
def bgym_solve(w, s):
    import soko
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    mv = soko.solve_pits(w, w.pos()[:2], w.pos()[2:], boulders(w), [(8,3),(8,7),(2,5)], people=frozenset((o[0], o[1]) for o in w.objs() if o[2] != 90))
    w.log.append('押し方 %d' % (len(mv) if mv else -1))
    if not mv: return False
    if not soko.run_pushes(w, s, mv): return False
    w.log.append('のこり %s %s' % (boulders(w), w.pos()))
    return True
def clair(w, s):
    b0 = w.rd(0xD56F)[0]
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    if not go((5,1))(w, s): return False
    w.talk_to(5, 3, shot=s)
    for i in range(5): w.advance(s, n=300); w.settle()
    w.log.append('バッジ %02x -> %02x %s' % (b0, w.rd(0xD56F)[0], w.pos()))
    return True
def clair2(w, s):
    b0 = w.rd(0xD56F)[0]
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set()
    w._rc = {}; w.door(1, 7, 'U', s); w.g.wait(60); w.advance(s); w.settle(); w._rc = {}
    w.log.append('2F %s' % (w.pos(),))
    w.door(7, 9, 'D', s); w.g.wait(60); w.advance(s); w.settle(); w._rc = {}
    w.log.append('1F %s' % (w.pos(),))
    w.talk_to(5, 3, shot=s)
    for i in range(5): w.advance(s, n=300); w.settle()
    w.log.append('バッジ %02x -> %02x %s' % (b0, w.rd(0xD56F)[0], w.pos()))
    return w.rd(0xD56F)[0] != b0
def clair3(w, s):
    b0 = w.rd(0xD56F)[0]
    w.can_cut = True; w.can_surf = True; w.run_wild = True; w.avoid = set(); w._rc = {}
    if w.pos()[:2] == (5,2):
        w.door(7, 9, 'D', s); w.g.wait(60); w.advance(s); w.settle(); w._rc = {}
    w.log.append('1F %s' % (w.pos(),))
    w.talk_to(5, 3, shot=s)
    for i in range(5): w.advance(s, n=300); w.settle()
    w.log.append('バッジ %02x -> %02x %s' % (b0, w.rd(0xD56F)[0], w.pos()))
    return w.rd(0xD56F)[0] != b0
def fang(w, s):
    w.can_whirl = True
    b0 = w.rd(0xD56F)[0]
    if not visit_talk((3,73), (35,16), 6)(w, s): return False
    w.log.append('バッジ %02x -> %02x %s' % (b0, w.rd(0xD56F)[0], w.pos()))
    return w.rd(0xD56F)[0] != b0
to_indigo = go((16,2))
def to_indigo2(w, s):
    w.can_whirl = True
    return go((16,2))(w, s)
def to_indigo3(w, s):
    w.can_whirl = True; w.can_surf = True; w.can_cut = True; w.avoid = set()
    return go((16,2))(w, s)
def r27east(w, s):
    w.can_whirl = True; w.can_surf = True; w.can_cut = True; w.avoid = set()
    w.leave('R', s); w.log.append('→ %s' % (w.pos(),))
    return w.pos()[:2] == (24,1)
def r26(w, s):
    w.can_whirl = True; w.can_surf = True; w.can_cut = True; w.avoid = set(); w.run_wild = True
    for k in range(6):
        if w.pos()[:2] != (24,1): break
        w.goto_safe(7, 6, shot=s); w.log.append('r26 %s' % (w.pos(),))
        if w.pos()[2:] == (7, 6): w.door(7, 5, 'U', s); w.g.wait(60); w.advance(s); w.settle()
    w.log.append('→ %s' % (w.pos(),))
    if w.pos()[:2] == (24,1): return False
    return go((16,2))(w, s)
def to_vr(w, s):
    w.can_whirl = True; w.can_surf = True; w.can_cut = True; w.avoid = set(); w.run_wild = True
    of = w.fight; cnt = [0]
    def f2(*a, **k):
        cnt[0] += 1
        w.g.save_state('/home/claude/work/wt/vr_b%d.st' % cnt[0])
        w.log.append('戦い %d %s' % (cnt[0], w.pos()))
        open('/tmp/vr.log','a').write('戦い %d %s\n' % (cnt[0], w.pos()))
        return of(*a, **k)
    w.fight = f2
    for k in range(6):
        if w.pos()[:2] != (24,1): break
        w.goto_safe(7, 6, shot=s)
        if w.pos()[2:] == (7, 6): w.door(7, 5, 'U', s); w.g.wait(60); w.advance(s); w.settle()
    while tleft(w) > 30 and cnt[0] < 40:
        w.travel((16,2), s, tries=1)
        w.log.append('いま %s' % (w.pos(),))
        if w.pos()[:2] == (16,2): return True
    return False
def vr_fix(w, s):
    w.can_whirl = True; w.can_surf = True; w.can_cut = True; w.avoid = set(); w.run_wild = True
    w.fight(run=False); w.advance(s); w.settle()
    w.log.append('D6DE=%d D7A5=%d いま %s' % (w.rd(0xD6DE)[0], w.rd(0xD7A5)[0], w.pos()))
    s('after')
    return True
def warp_league(w, s):
    g = w.g
    g.poke(0xD9C6, 16); g.poke(0xD9C7, 2); g.poke(0xD9C9, 9); g.poke(0xD9C8, 12)
    g.poke(0xCF20, 255); g.poke(0xFFA1, 0xF1); g.poke(0xD14B, 1); g.wait(200); w.settle(); w._rc = {}
    w.log.append('ワープ %s' % (w.pos(),)); s('高原')
    return w.pos()[:2] == (16,2)
def champ_rec(w, s):
    w.run_wild = True; w.lead_for = None
    w.g.rec('/tmp/champ')
    for k in range(6):
        mid = w.pos()[:2]
        if mid != (16,7): break
        w.travel((16,8), s, tries=1)
        if w.pos()[:2] == (16,8): break
        for x, y, sp in w.objs(): w.talk_to(x, y, shot=s); w.advance(s, n=400)
    w.log.append('いま %s' % (w.pos(),))
    for k in range(40):
        w.g.wait(300); w.g.press('A', 4, 10)
        if k % 3 == 0: s('hof%d' % k)
    w.g.stop()
    return True
