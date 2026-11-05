"""「ぶんぷをみる」の釣りの場所の表（src/fishnest_maps.inc）を作る。
   python3 tools/fishnest_maps.py ROM.gbc ROM.sym [使わないマップ（グループ.番号）...] > src/fishnest_maps.inc
   ROM・sym は pret の pokegold（金・銀）か pokecrystal（クリスタル）を組み立てたもの。
   （日本版も マップ・地名・釣りのグループ は同じなので、英語版のデータから作ってよい。
     sym の代わりに アドレスを書けば、日本版の ROM から直接作ることもできる：
       python3 tools/fishnest_maps.py 金.gbc MapGroupPointers=25:40ed,Tilesets=05:562b,CollisionPermissionTable=3e:734a 5.8）
   使われていないマップ（行けないマップ）は 後ろに「グループ.番号」で書いて除く。
     金・銀：5.8（SAFARI_ZONE_BETA。セキチクシティの地名で、うみべ の釣りのグループが入っている）

   釣りができる所 = マップに 釣りのグループ があり、そのマップに 水のタイル（WATER_TILE）がある所。
   （ほとんどのマップには 釣りのグループ が入っているので、水があるかで決める）
   出力：地名（landmark）・釣りのグループ の組（同じ組は1つ）と、釣りのグループごとに 釣れるポケモン。
   （sym の代わりに アドレスを書くときは FishGroups=..,TimeFishGroups=.. も足す）"""
import sys, re

def load_sym(p):
    s = {}
    for l in open(p):
        m = re.match(r'([0-9a-f]+):([0-9a-f]+) (\S+)', l)
        if m: s[m.group(3)] = (int(m.group(1), 16), int(m.group(2), 16))
    return s

def main(rom, syms, skip=()):
    d = open(rom, 'rb').read()
    off = lambda b, a: a if a < 0x4000 else b * 0x4000 + a - 0x4000
    rd16 = lambda o: d[o] | d[o + 1] << 8
    mgb, mga = syms['MapGroupPointers']
    tsb, tsa = syms['Tilesets']
    cpb, cpa = syms['CollisionPermissionTable']
    # マップグループ：ポインタの表は 最初のグループのデータの直前まで。
    # 最後のグループの終わりは、sym で次にあるラベル（金銀クリスタルとも MapAttributes が続く）
    o = off(mgb, mga); groups = []
    while not groups or o < off(mgb, groups[0]):
        groups.append(rd16(o)); o += 2
    # 最後のグループの終わり：ほかのグループのマップの MapAttributes のうち、いちばん前の所
    # （金銀クリスタルとも、マップのグループの表のすぐ後ろに MapAttributes が続く）
    attrs = []
    for gi in range(len(groups) - 1):
        for k in range(off(mgb, groups[gi]), off(mgb, groups[gi + 1]), 9):
            if d[k] == mgb: attrs.append(rd16(k + 3))
    last_end = min(a for a in attrs if a > groups[-1])
    pairs = []; out = []
    for gi, gp in enumerate(groups):
        go = off(mgb, gp)
        end = off(mgb, groups[gi + 1]) if gi + 1 < len(groups) else off(mgb, last_end)
        mi = 0
        while go + 9 * (mi + 1) <= end:
            h = d[go + 9 * mi:go + 9 * mi + 9]
            attr_bank, tileset, env, attr = h[0], h[1], h[2], h[3] | h[4] << 8
            landmark, fishgroup = h[5], h[8]
            mi += 1
            if fishgroup == 0 or landmark == 0 or (gi + 1, mi) in skip: continue
            ao = off(attr_bank, attr)
            height, width = d[ao + 1], d[ao + 2]
            bb, bp = d[ao + 3], rd16(ao + 4)
            blocks = d[off(bb, bp):off(bb, bp) + width * height]
            t = off(tsb, tsa) + tileset * 15
            collb, collp = d[t + 6], rd16(t + 7)
            co = off(collb, collp)
            water = False
            for blk in set(blocks):
                for c in d[co + blk * 4:co + blk * 4 + 4]:
                    if d[off(cpb, cpa) + c] & 0x0f == 1:   # WATER_TILE
                        water = True
            if water and (landmark, fishgroup) not in pairs:
                pairs.append((landmark, fishgroup))
                out.append((gi + 1, mi, landmark, fishgroup))
    return pairs, out

def fish_species(rom, syms, ngroups):
    """釣りのグループごとの ポケモン（ボロ・いい・すごいつりざお、朝昼・夜の両方）"""
    d = open(rom, 'rb').read()
    off = lambda b, a: a if a < 0x4000 else b * 0x4000 + a - 0x4000
    fb, fa = syms['FishGroups']; tb, ta = syms['TimeFishGroups']
    res = []
    for g in range(ngroups):
        o = off(fb, fa) + g * 7 + 1
        mons = []
        for r in range(3):
            p = off(fb, d[o + r * 2] | d[o + r * 2 + 1] << 8)
            while True:
                chance, sp, lv = d[p], d[p + 1], d[p + 2]
                if sp == 0:
                    t = off(tb, ta) + lv * 4
                    cand = [d[t], d[t + 2]]          # 朝昼・夜
                else:
                    cand = [sp]
                for c in cand:
                    if c not in mons: mons.append(c)
                p += 3
                if chance == 0xff: break
        res.append(mons)
    return res

if __name__ == '__main__':
    # 2つめは sym ファイル、または「MapGroupPointers=25:40ed,Tilesets=05:562b,CollisionPermissionTable=3e:734a」
    if '=' in sys.argv[2]:
        syms = {}
        for kv in sys.argv[2].split(','):
            k, v = kv.split('='); b, a = v.split(':'); syms[k] = (int(b, 16), int(a, 16))
    else:
        syms = load_sym(sys.argv[2])
    # 使われていないマップを除く（グループ.番号 で指定。sym があれば名前から）
    skip = set()
    for n in sys.argv[3:]:
        g, m = n.split('.'); skip.add((int(g), int(m)))
    pairs, out = main(sys.argv[1], syms, skip)
    ngroups = max(f for l, f in pairs)
    mons = fish_species(sys.argv[1], syms, ngroups)
    print('; 「ぶんぷをみる」の釣りの場所の表。tools/fishnest_maps.py で作った（%s）' % sys.argv[1].split('/')[-1])
    print()
    print('; 釣りができる所（地名, 釣りのグループ）。マップ（グループ.番号）は確かめ用')
    print('FishNestMaps:')
    for g, m, l, f in out:
        print('\tdb $%02x, $%02x ; map %d.%d' % (l, f, g, m))
    print('\tdb 0')
    print()
    print('; 釣りのグループごとに 釣れるポケモン（ボロ・いい・すごいつりざお、朝昼・夜）')
    print('FishNestGroupMons:')
    for g in range(ngroups): print('\tdw .group%d' % (g + 1))
    print('.end_ptrs')
    for g in range(ngroups):
        print('.group%d' % (g + 1))
        print('\tdb ' + ', '.join('$%02x' % m for m in mons[g]) + ', 0')
