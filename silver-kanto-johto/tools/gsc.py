"""金銀・クリスタル（日本版）の ROM を 読む 道具（マップの 表・マップの ヘッダー など）
   クリスタル版の 完成 ROM から 銀へ 写す ときに 使う。"""
import os, re
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PG = os.path.join(H, '..', 'silver', 'pokegold')                 # pret/pokegold の 定数
PC = os.path.join(H, 'ref', 'pokecrystal')                        # pret/pokecrystal の 定数（キットから 写した もの）


def fo(bank, addr):
    """バンク:アドレス → ROM の 位置"""
    return addr if bank == 0 and addr < 0x4000 else bank * 0x4000 + (addr - 0x4000)


def ba(off):
    """ROM の 位置 → (バンク, アドレス)"""
    return (off // 0x4000, off % 0x4000 + (0x4000 if off >= 0x4000 else 0))


def r16(rom, o): return rom[o] | rom[o + 1] << 8


def map_consts(path):
    """map_constants.asm → [(グループ名, [(マップ名, 幅, 高さ), ...]), ...]（グループは 1 から）"""
    groups = []
    for l in open(path, encoding='utf-8'):
        m = re.match(r'\s*newgroup (\w+)', l)
        if m: groups.append((m.group(1), [])); continue
        m = re.match(r'\s*map_const (\w+),\s*(\d+),\s*(\d+)', l)
        if m: groups[-1][1].append((m.group(1), int(m.group(2)), int(m.group(3))))
    return groups


def find_group_table(rom, groups, bank=0x25):
    """MapGroupPointers を さがす：グループの 数だけ ならんだ ポインタで、つぎとの 差が 9×マップ数"""
    n = len(groups)
    base = bank * 0x4000
    for s in range(base, base + 0x4000 - 2 * n):
        ps = [r16(rom, s + 2 * i) for i in range(n)]
        if not all(0x4000 <= p < 0x8000 for p in ps): continue
        if all(ps[i + 1] - ps[i] == 9 * len(groups[i][1]) for i in range(n - 1)):
            return s
    raise ValueError('MapGroupPointers が 見つからない')


class Maps:
    """ROM の マップの 表。maps[(グループ, 番号)] = ヘッダー（9バイト）の 位置"""
    def __init__(s, rom, constpath, bank=0x25, extra=None):
        s.rom = rom; s.bank = bank
        s.groups = map_consts(constpath)
        s.table = find_group_table(rom, s.groups, bank)
        s.name = {}; s.id = {}; s.hdr = {}
        for gi, (gn, ms) in enumerate(s.groups):
            p = fo(bank, r16(rom, s.table + 2 * gi))
            for mi, (mn, w, h) in enumerate(ms):
                k = (gi + 1, mi + 1)
                s.name[k] = mn; s.id[mn] = k; s.hdr[k] = p + 9 * mi

    def header(s, k):
        o = s.hdr[k]; r = s.rom
        return dict(attr_bank=r[o], tileset=r[o + 1], env=r[o + 2], attr=r16(r, o + 3), landmark=r[o + 5],
                    music=r[o + 6], palette=r[o + 7], fish=r[o + 8])

    def attributes(s, k):
        h = s.header(k); r = s.rom; o = fo(h['attr_bank'], h['attr'])
        a = dict(border=r[o], height=r[o + 1], width=r[o + 2], blocks_bank=r[o + 3], blocks=r16(r, o + 4),
                 scripts_bank=r[o + 6], scripts=r16(r, o + 7), events=r16(r, o + 9), conn_flags=r[o + 11], off=o)
        conns = []; p = o + 12
        for d in ('NORTH', 'SOUTH', 'WEST', 'EAST'):       # ビットは 東3 西2 南1 北0（並びは 北・南・西・東）
            bit = {'NORTH': 3, 'SOUTH': 2, 'WEST': 1, 'EAST': 0}[d]
            if a['conn_flags'] & (1 << bit):
                conns.append(dict(dir=d, group=r[p], map=r[p + 1], src=r16(r, p + 2), dst=r16(r, p + 4), len=r[p + 6],
                                  width=r[p + 7], yoff=r[p + 8], xoff=r[p + 9], window=r16(r, p + 10)))
                p += 12
        a['conns'] = conns
        return a

    def events(s, k):
        a = s.attributes(k); r = s.rom; o = fo(a['scripts_bank'], a['events'])
        ev = dict(off=o); o += 2                            # db 0, 0（filler）
        n = r[o]; o += 1; ev['warps'] = [tuple(r[o + 5 * i:o + 5 * i + 5]) for i in range(n)]; o += 5 * n
        n = r[o]; o += 1; ev['coords'] = [tuple(r[o + 8 * i:o + 8 * i + 8]) for i in range(n)]; o += 8 * n
        n = r[o]; o += 1; ev['bgs'] = [tuple(r[o + 5 * i:o + 5 * i + 5]) for i in range(n)]; o += 5 * n
        n = r[o]; o += 1; ev['objects'] = [tuple(r[o + 13 * i:o + 13 * i + 13]) for i in range(n)]; o += 13 * n
        ev['end'] = o
        return ev
