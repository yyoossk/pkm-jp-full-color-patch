"""手持ちを Lv100 の チームに 書きかえる（RAM）"""
import re, math
PG = '/home/claude/work/ref_pokegold'
cm = {}
for l in open('/home/claude/repo/gold/src/charmap_jp.inc', encoding='utf-8'):
    m = re.match(r'\s*charmap "(.+?)",\s*\$([0-9a-fA-F]+)', l)
    if m and m.group(1) not in cm: cm[m.group(1)] = int(m.group(2), 16)
def enc(s, n=6):
    b = [cm[c] for c in s] + [0x50]; return (b + [0x50] * n)[:n]
def consts(path, start=0):
    out = {}; n = start
    for l in open(path):
        m = re.match(r'\s*const_def\s*(\d+)?', l)
        if m: n = int(m.group(1)) if m.group(1) else 0; continue
        m = re.match(r'\s*const (\w+)', l)
        if m: out[m.group(1)] = n; n += 1
    return out
MV = consts(PG + '/constants/move_constants.asm')
SP = consts(PG + '/constants/pokemon_constants.asm')
def pp(move):
    t = open(PG + '/data/moves/moves.asm').read()
    m = re.search(r'move ' + move + r',\s*\w+,\s*\d+,\s*\w+,\s*\d+,\s*(\d+)', t); return int(m.group(1))
def base(name):
    t = open(PG + '/data/pokemon/base_stats/%s.asm' % name.lower()).read()
    m = re.search(r'db\s+(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)', t)
    hp, at, de, sp, sa, sd = map(int, m.groups())
    g = re.search(r'db (GROWTH_\w+)', t).group(1)
    return (hp, at, de, sp, sa, sd), g
EXP100 = {'GROWTH_MEDIUM_FAST': 1000000, 'GROWTH_MEDIUM_SLOW': 1059860, 'GROWTH_FAST': 800000, 'GROWTH_SLOW': 1250000}
TEAM = [('CHARIZARD', 'リザードン', ['FLAMETHROWER', 'EARTHQUAKE', 'WING_ATTACK', 'SLASH']),
        ('LAPRAS', 'ラプラス', ['ICE_BEAM', 'SURF', 'THUNDERBOLT', 'PSYCHIC_M']),
        ('ZAPDOS', 'サンダー', ['THUNDERBOLT', 'DRILL_PECK', 'THUNDER_WAVE', 'AGILITY']),
        ('ALAKAZAM', 'フーディン', ['PSYCHIC_M', 'THUNDERPUNCH', 'ICE_PUNCH', 'RECOVER']),
        ('VENUSAUR', 'フシギバナ', ['RAZOR_LEAF', 'SLUDGE_BOMB', 'EARTHQUAKE', 'SLEEP_POWDER']),
        ('SNORLAX', 'カビゴン', ['BODY_SLAM', 'EARTHQUAKE', 'REST', 'FIRE_PUNCH'])]
def mon(name, moves, oid):
    sp = SP[name]; (b, g) = base(name); L = 100
    st = lambda bs: (((bs + 15) * 2 + 64) * L) // 100
    hp = st(b[0]) + L + 10
    stats = [hp, hp] + [st(x) + 5 for x in (b[1], b[2], b[3], b[4], b[5])]
    e = EXP100[g]
    d = [sp, 0] + [MV[m] for m in moves] + list(oid) + [e >> 16 & 255, e >> 8 & 255, e & 255] + [255] * 10 + [0xFF, 0xFF] \
        + [pp(m) | 0xC0 for m in moves] + [255, 0, 0, 0, L, 0, 0]
    for v in stats: d += [v >> 8, v & 255]
    assert len(d) == 0x30, len(d)
    return sp, d
def write(w):
    g = w.g; oid = w.rd(0xD1B3, 2); ot = w.rd(0xD1B5, 6)
    g.poke(0xD9E8, len(TEAM))
    for i, (n, jp, mv) in enumerate(TEAM):
        sp, d = mon(n, mv, oid)
        g.poke(0xD9E9 + i, sp)
        for k, v in enumerate(d): g.poke(0xD9F0 + 0x30 * i + k, v)
        for k, v in enumerate(ot): g.poke(0xDB10 + 6 * i + k, v)
        for k, v in enumerate(enc(jp)): g.poke(0xDB34 + 6 * i + k, v)
    g.poke(0xD9E9 + len(TEAM), 0xFF)
