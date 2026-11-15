"""外の マップの 人の絵の 表（金 05:$465E、グループごとに 11こ）と、マップが 使う 人の絵を くらべる"""
import sys; sys.path.insert(0,'/home/claude/work/scripts')
from cwalk import Walk, fo
from cmaps import maplist; from maps import GMGP
from collections import defaultdict
TAB = (0x05, 0x465E); N = 11
def used_by_group(g):
    used = defaultdict(set); names = defaultdict(list)
    for m in maplist(g, GMGP, 'pokegold'):
        if g[m['hdr'] + 2] not in (1, 2): continue
        at = Walk(g).map(m['attr'], m['name'])
        for o in at['objs']: used[m['group']].add(o[0])
        names[m['group']].append(m['name'])
    return used, names
def lists(g):
    t = fo(*TAB); res = {}
    for gr in range(1, 27):
        lp = fo(5, g[t + 2 * (gr - 1)] | g[t + 2 * (gr - 1) + 1] << 8); res[gr] = (lp, list(g[lp:lp + N]))
    return res
if __name__ == '__main__':
    g = open(sys.argv[1], 'rb').read()
    used, names = used_by_group(g); L = lists(g)
    for gr in sorted(used):
        lst = L[gr][1]; miss = sorted(x for x in used[gr] - set(lst) if x < 0xF0)
        u = sorted(x for x in used[gr] if x < 0xF0)
        print(gr, 'used %d' % len(u), 'miss', [hex(x) for x in miss], names[gr][:5])
