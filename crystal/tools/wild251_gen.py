#!/usr/bin/env python3
# 251ひき そろう版の 出現表を 作る（クリスタル・金・銀 共通）
#   python3 wild251_gen.py <crystal|gold|silver> <pret/pokecrystal> <pret/pokegold> <data フォルダ>
#   → <data>/wild251_<版>.txt（wild_find.py で asm に する）と、どこを かえたかの 一覧（標準出力）
#
# きまり（ユーザーと きめた こと）
#   ・その 版で 野生（草むら・どうくつ・なみのり・つり・ずつき・大量発生）に 出ない ポケモンで、
#     ほかの 2つの 版で 野生（草むら・どうくつ・なみのり・つり・大量発生）に 出る ものを、その 版と まったく 同じ 場所・枠・レベルに 出す。
#   ・もとから いる ポケモンが その 枠を とられて どこにも 出なく なる ときは「時間で 分ける」：
#     朝・昼は 足した ポケモン、夜は 元の ポケモン（クリスタルの 37・7ばんどうろの デルビル なども 夜に のこる）。
#   ・殿堂入りの 前の 書きかえ（data/wild_<版>.txt）が ある マップは、その 書きかえた 表を 元に する。
#   ・草むら（朝・昼・夜 7わくずつ）と なみのり（3わく）を 書きかえる。つりざお・ずつきの 表は かえない
#     （足す ポケモンが つり・ずつき にしか いない ときは 一覧の「表に 入らない」に 出る。その ときは 別に きめる）。
import re, os, glob, sys
V = sys.argv[1]; PC = sys.argv[2]; PG = sys.argv[3]; DATA = sys.argv[4]
VS = ['crystal', 'gold', 'silver']

def consts(path):
    v, d = 0, {}
    for l in open(path):
        l = l.split(';')[0].strip()
        m = re.match(r'const_def\s*(\S*)', l)
        if m: v = int(m.group(1).replace('$', '0x'), 0) if m.group(1) else 0; continue
        m = re.match(r'const\s+(\w+)', l)
        if m: d[m.group(1)] = v; v += 1
    return d
MON = {k: v for k, v in consts(PC + '/constants/pokemon_constants.asm').items() if 1 <= v <= 251 and not k.startswith('UNOWN_')}
INV = {v: k for k, v in MON.items()}

def walk(path, variant):
    stack = []
    for l in open(path):
        l = l.split(';')[0].strip()
        if l.startswith('IF DEF(_GOLD)'): stack.append(variant == 'gold'); continue
        if l.startswith('IF DEF(_SILVER)'): stack.append(variant == 'silver'); continue
        if l.startswith('ELIF DEF(_SILVER)'): stack[-1] = (variant == 'silver'); continue
        if l.startswith('ELIF DEF(_GOLD)'): stack[-1] = (variant == 'gold'); continue
        if l.startswith('IF '): stack.append(True); continue
        if l.startswith('ELSE'): stack[-1] = not stack[-1]; continue
        if l.startswith('ENDC'): stack.pop(); continue
        if stack and not all(stack): continue
        yield l
def base(v): return PC if v == 'crystal' else PG

def mapids(v):
    g, n, d = 0, 0, {}
    for l in open(base(v) + '/constants/map_constants.asm'):
        l = l.split(';')[0].strip()
        if re.match(r'newgroup\s+\w+', l): g += 1; n = 0; continue
        m = re.match(r'map_const\s+(\w+)', l)
        if m: n += 1; d[m.group(1)] = (g, n)
    return d
def pct(s):
    m = re.match(r'(\d+)\s*percent', s.strip()); return int(m.group(1)) * 255 // 100

def tables(v):
    T, H = {}, {}
    ids = mapids(v)
    for f in ['johto_grass', 'johto_water', 'kanto_grass', 'kanto_water']:
        cur = None; kind = f.split('_')[1]
        for l in walk(f'{base(v)}/data/wild/{f}.asm', v):
            m = re.match(r'def_\w+_wildmons\s+(\w+)', l)
            if m: cur = (m.group(1), kind); T[cur] = []; H[cur] = None; continue
            if cur and H[cur] is None and 'percent' in l:
                g, n = ids[cur[0]]
                H[cur] = bytes([g, n] + [pct(x) for x in l[2:].split(',')]); continue
            m = re.match(r'db\s+(\d+),\s*([A-Z_0-9]+)\s*$', l)
            if m and cur and m.group(2) in MON: T[cur].append((int(m.group(1)), m.group(2)))
    hk = os.path.join(DATA, 'wild_%s.txt' % v)
    if os.path.exists(hk):
        for l in open(hk, encoding='utf-8'):
            if l.startswith('#') or not l.strip(): continue
            mp, a, b = l.split(); bb = bytes.fromhex(b)
            T[(mp, 'grass')] = [(bb[i], INV[bb[i + 1]]) for i in range(5, 47, 2)]
            H[(mp, 'grass')] = ('hack', a, bb[:5])
    return T, H

def others(v):
    S = {}
    for f in ['fish', 'treemons', 'bug_contest_mons', 'swarm_grass', 'swarm_water']:
        p = f'{base(v)}/data/wild/{f}.asm'
        if not os.path.exists(p): continue
        lab = None
        for l in walk(p, v):
            m = re.match(r'^(\.?\w+):', l) or re.match(r'def_\w+_wildmons\s+(\w+)', l)
            if m: lab = m.group(1)
            for t in re.findall(r'\b[A-Z_][A-Z0-9_]+\b', l):
                if t in MON: S.setdefault(t, set()).add((f, lab))
    return S

TB, HD, OT = {}, {}, {}
for v in VS: TB[v], HD[v] = tables(v); OT[v] = others(v)
def wildset(v): return {s for t in TB[v].values() for _, s in t} | {s for s, w in OT[v].items() if any(f in ('fish', 'swarm_grass', 'swarm_water') for f, _ in w)}
def allwild(v): return {s for t in TB[v].values() for _, s in t} | set(OT[v])

oth = [w for w in VS if w != V]
add = (wildset(oth[0]) | wildset(oth[1])) - allwild(V)
NT = {k: list(t) for k, t in TB[V].items()}
for key in NT:
    for i in range(len(NT[key])):
        for w in oth:
            t = TB[w].get(key)
            if t and i < len(t) and t[i][1] in add: NT[key][i] = t[i]; break
old = {s for t in TB[V].values() for _, s in t}; new = {s for t in NT.values() for _, s in t}
gone = old - new - set(OT[V])
# 時間で 分ける：消える 種類の 枠は 夜（草むらの 15〜21わくめ）は 元の まま
for key in NT:
    for i in range(len(NT[key])):
        if TB[V][key][i][1] in gone and NT[key][i] != TB[V][key][i] and (key[1] != 'grass' or i >= 14):
            NT[key][i] = TB[V][key][i]

TIMES = ['朝', '昼', '夜']
lines = ['# 251匹そろう版の 出現表（%s。殿堂入りの前の 書きかえ wild_%s.txt ＋ ほかの 2つの 版の 野生を 同じ 枠に）' % (V, V),
         '# マップ  元の表(hex)  新しい表(hex)']
for key in sorted(NT):
    if NT[key] == TB[V][key] and not (HD[V][key] and HD[V][key][0] == 'hack'): continue
    ent = b''.join(bytes([l, MON[s]]) for l, s in NT[key])
    h = HD[V][key]
    if h and h[0] == 'hack':
        a, hdr = h[1], h[2]
    else:
        hdr = h; a = (h + b''.join(bytes([l, MON[s]]) for l, s in TB[V][key])).hex()
    lines.append('%s %s %s' % (key[0] + ('' if key[1] == 'grass' else '_WATER'), a, (hdr + ent).hex()))
    for i in range(len(NT[key])):
        if NT[key][i] != TB[V][key][i]:
            slot = '%s %dわくめ' % (TIMES[i // 7], i % 7 + 1) if key[1] == 'grass' else 'なみのり %dわくめ' % (i + 1)
            print('%-28s %-14s %s Lv%d → %s Lv%d' % (key[0], slot, TB[V][key][i][1], TB[V][key][i][0], NT[key][i][1], NT[key][i][0]))
out = os.path.join(DATA, 'wild251_%s.txt' % V)
open(out, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
new = {s for t in NT.values() for _, s in t}
print('足す ポケモン:', sorted(add, key=lambda s: MON[s]))
print('表に 入らない（つり・ずつき・大量発生 だけ）:', sorted(add - new, key=lambda s: MON[s]))
print('消える ポケモン:', sorted(old - new - set(OT[V]), key=lambda s: MON[s]))
print('ok', out)
