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
