"""赤（pokered）の 回る 床の うごき → 移植版の jumps（walker.path が 使う）。座標は 赤と 同じ"""
import re, os
RED = '/home/claude/work/mod/ref/pokered'
D = {'PAD_RIGHT': (1, 0), 'PAD_LEFT': (-1, 0), 'PAD_UP': (0, -1), 'PAD_DOWN': (0, 1)}
def parse(name):
    t = open(os.path.join(RED, 'scripts', name + '.asm'), encoding='utf-8').read()
    tiles = [(int(x), int(y), lab) for x, y, lab in re.findall(r'map_coord_movement\s+(\d+),\s*(\d+),\s*(\w+)', t)]
    moves = {}
    for lab, body in re.findall(r'^(\w+):\n((?:\s+db .*\n)+)', t, re.M):
        seq = re.findall(r'db (PAD_\w+), (\d+)', body)
        moves[lab] = [(D[a], int(n)) for a, n in seq]
    out = {}
    for x, y, lab in tiles:
        px, py = x, y
        for (dx, dy), n in reversed(moves[lab]): px += dx * n; py += dy * n
        out[(x, y)] = (px, py)
    # 着いた 所が また 回る 床なら つづける
    def final(p, k=0):
        return final(out[p], k + 1) if p in out and k < 10 and out[p] != p else p
    return {p: final(q) for p, q in out.items()}
def jumps(mid, name):
    J = {}
    land = parse(name)
    for (x, y), f in land.items():
        for d, (dx, dy) in (('U', (0, -1)), ('D', (0, 1)), ('L', (-1, 0)), ('R', (1, 0))):
            J[(mid, (x - dx, y - dy), d)] = f
    return J
SPIN_MAPS = {(26, 22): 'RocketHideoutB2F', (26, 23): 'RocketHideoutB3F', (23, 4): 'ViridianGym'}
def all_jumps(extra=None):
    J = {}
    for mid, n in {**SPIN_MAPS, **(extra or {})}.items(): J.update(jumps(mid, n))
    return J
if __name__ == '__main__':
    print(parse('RocketHideoutB3F'))
