"""スクリプトの 逆アセンブル： sdis.py rom bank addr [n]（クリスタルの 命令表。g を つけると 金）"""
import sys; sys.path.insert(0, '/home/claude/work/scripts')
import cwalk
def sdis(R, b, a, n=40, spec=None):
    spec = spec or cwalk.SPEC; o = cwalk.fo(b, a); p = o; out = []
    for _ in range(n):
        op = R[p]
        if op >= len(spec): out.append('%04X ?? %02X' % (a + p - o, op)); break
        name, args = spec[op]; q = p + 1; vals = []
        if name == 'givepoke':
            args = [('db', 'pokemon'), ('db', 'level'), ('db', 'item'), ('db', 'trainer')] + ([('dw', 't'), ('dw', 't')] if R[q + 3] else [])
        for t, sem in args:
            sz = cwalk.SIZE[t]; v = R[q:q + sz]
            vals.append(('%04X' % (v[0] | v[1] << 8)) if t == 'dw' else v.hex())
            q += sz
        out.append('%04X %-22s %s' % (a + p - o, name, ' '.join(vals)))
        p = q
        if name in cwalk.END: break
    return '\n'.join(out)
if __name__ == '__main__':
    R = open(sys.argv[1], 'rb').read()
    spec = None
    if len(sys.argv) > 5 and sys.argv[5] == 'g':
        import gold_rebuild; spec = gold_rebuild.gw.SPEC
    print(sdis(R, int(sys.argv[2], 16), int(sys.argv[3], 16), int(sys.argv[4]) if len(sys.argv) > 4 else 40, spec))
