"""日本版クリスタル（改造後）のマップのデータを、スクリプト・セリフ・移動データまで たどって 集める。
   集めたものは「かたまり（blob）」の一覧：kind, bank, addr, bytes, fixups（中のポインター）, notes
"""
import re, sys
sys.path.insert(0, '/home/claude/work/scripts')
from consts import R

def fo(b, a): return a if a < 0x4000 else b * 0x4000 + a - 0x4000
def w(r, o): return r[o] | r[o + 1] << 8

# --- スクリプト命令の引数（pokegold のマクロから）
def load_spec():
    s = open(R + 'pokegold/macros/scripts/events.asm').read()
    parts = re.split(r'\n\s*const (\w+)_command[^\n]*\n', s)
    spec = []
    for i in range(1, len(parts), 2):
        name = parts[i]; body = parts[i + 1].split('ENDM')[0]
        args = []
        for l in body.splitlines():
            l = l.strip()
            m = re.match(r'(db|dw|dba|map_id|bigdt)\s+(.*?)(?:;\s*(.*))?$', l)
            if not m or l.startswith('db ' + name + '_command'): continue
            args.append((m.group(1), (m.group(3) or m.group(2)).strip()))
        spec.append((name, args))
    return spec
SPEC = load_spec()
FIX = {  # 引数の形を手で決めるもの（if があるマクロ）
    'givepoke': None, 'giveitem': [('db', 'item'), ('db', 'quantity')], 'takeitem': [('db', 'item'), ('db', 'quantity')],
    'verbosegiveitem': [('db', 'item'), ('db', 'quantity')], 'loadvar': [('db', 'variable_id'), ('db', 'value')],
    'reanchormap': [('db', 'dummy')], 'jumpstd': [('dw', 'std')], 'callstd': [('dw', 'std')], 'special': [('dw', 'special')],
    'variablesprite': [('db', 'spritevar'), ('db', 'sprite')],
}
for i, (n, a) in enumerate(SPEC):
    if n in FIX and FIX[n] is not None: SPEC[i] = (n, FIX[n])
OP = {n: i for i, (n, a) in enumerate(SPEC)}
END = {'end', 'endcallback', 'endall', 'reloadend', 'sjump', 'farsjump', 'memjump', 'jumptext', 'jumptextfaceplayer',
       'jumpstd', 'stopandsjump'}
SIZE = {'db': 1, 'dw': 2, 'dba': 3, 'map_id': 2, 'bigdt': 3}

class Walk:
    def __init__(s, rom):
        s.r = rom; s.blobs = {}; s.todo = []; s.notes = []
    def add(s, kind, b, a, ctx=''):
        if a == 0 or a == 0xFFFF: return
        key = (b if a >= 0x4000 else 0, a)
        if key not in s.blobs and (kind, key) not in [(k, x) for k, x, _ in s.todo]:
            s.todo.append((kind, key, ctx))
    def run(s):
        while s.todo:
            kind, key, ctx = s.todo.pop()
            if key in s.blobs: continue
            getattr(s, 'w_' + kind)(key[0], key[1], ctx)
    def put(s, kind, b, a, n, fix, extra=None):
        o = fo(b, a)
        s.blobs[(b if a >= 0x4000 else 0, a)] = dict(kind=kind, bank=b, addr=a, data=bytes(s.r[o:o + n]), fix=fix, extra=extra or {})

    # ---------- スクリプト
    def w_script(s, b, a, ctx):
        o = fo(b, a); p = o; fix = []
        while True:
            op = s.r[p]
            if op >= len(SPEC):
                s.notes.append('不明な命令 %02X at %02X:%04X (%s)' % (op, b, a + p - o, ctx)); p += 1; break
            name, args = SPEC[op]
            q = p + 1
            if name == 'givepoke':
                args = [('db', 'pokemon'), ('db', 'level'), ('db', 'item'), ('db', 'trainer')]
                if s.r[q + 3]: args += [('dw', 'text_pointer'), ('dw', 'text_pointer')]
            for t, sem in args:
                v = s.r[q:q + SIZE[t]]
                fix.append((q - o, t, sem, name))
                if t == 'dw' and ('pointer' in sem) and sem not in ('music_pointer', 'sound_pointer', 'queue_pointer', 'caller_name', 'menu_header'):
                    ptr = w(s.r, q)
                    k = 'text' if 'text' in sem else 'movement' if (name in ('applymovement', 'applymovementlasttalked')) else \
                        'mart' if name == 'pokemart' else 'elevator' if name == 'elevator' else 'script'
                    if name in ('givepokemail', 'checkpokemail'): k = 'raw'
                    s.add(k, b, ptr, ctx)
                elif t == 'dw' and sem == 'data':
                    s.add('movement', b, w(s.r, q), ctx)
                elif t == 'dw' and sem == 'menu_header':
                    s.add('menu', b, w(s.r, q), ctx)
                elif t == 'dw' and sem in ('win_text_pointer', 'loss_text_pointer'):
                    s.add('text', b, w(s.r, q), ctx)
                elif t == 'dba':
                    bb = s.r[q]; aa = w(s.r, q + 1)
                    if name in ('farscall', 'farsjump'): s.add('script', bb, aa, ctx)
                    elif name == 'farwritetext': s.add('text', bb, aa, ctx)
                    elif name == 'changemapblocks': s.add('raw', bb, aa, ctx)
                    elif name in ('callasm', 'autoinput'): s.notes.append('%s %02X:%04X（%s）' % (name, bb, aa, ctx))
                q += SIZE[t]
            p = q
            if name in END: break
            if name == 'memcallasm': s.notes.append('memcallasm（%s）' % ctx)
        s.put('script', b, a, p - o, fix)

    # ---------- セリフ
    def w_text(s, b, a, ctx):
        o = fo(b, a); p = o; fix = []; mode = 'cmd'
        while True:
            c = s.r[p]
            if mode == 'str':
                p += 1
                if c == 0x50: mode = 'cmd'
                elif c in (0x57, 0x58): break
                continue
            p += 1
            if c == 0x00: mode = 'str'
            elif c in (0x01, 0x03): fix.append((p - o, 'dw', 'ram', 'text')); p += 2
            elif c == 0x02: p += 3
            elif c == 0x04: p += 4
            elif c == 0x09: p += 3
            elif c in (0x0C, 0x14): p += 1
            elif c == 0x16:
                fix.append((p - o, 'dba', 'textfar', 'text')); s.add('text', s.r[p + 2], w(s.r, p), ctx); p += 3
            elif c == 0x08:
                s.notes.append('text_asm at %02X:%04X（%s）' % (b, a + p - o, ctx)); break
            elif c == 0x50: break
            elif c in (0x05, 0x06, 0x07, 0x0A, 0x0B, 0x0D, 0x0E, 0x0F, 0x10, 0x11, 0x12, 0x13, 0x15): pass
            else:
                s.notes.append('不明なセリフ命令 %02X at %02X:%04X（%s）' % (c, b, a + p - o - 1, ctx)); break
        s.put('text', b, a, p - o, fix)

    def w_movement(s, b, a, ctx):
        o = fo(b, a); p = o
        while True:
            c = s.r[p]; p += 1
            if c == 0x47: break            # step_end
            if c == 0x48: p += 1; break        # step_wait_end n
            if c in (0x46, 0x4F, 0x55): p += 1  # step_sleep n / step_dig n / step_shake n
            if c in (0x49, 0x4A, 0x4B): break   # remove_object / loop / stop
        s.put('movement', b, a, p - o, [])
    def w_raw(s, b, a, ctx):
        s.notes.append('raw データ %02X:%04X（%s）大きさ不明' % (b, a, ctx)); s.put('raw', b, a, 0, [])
    def w_mart(s, b, a, ctx): s.put('raw', b, a, 0, [])
    def w_elevator(s, b, a, ctx):
        o = fo(b, a); n = s.r[o]; s.put('elevator', b, a, 1 + 4 * n, [])
    def w_menu(s, b, a, ctx):
        s.notes.append('menu %02X:%04X（%s）' % (b, a, ctx)); s.put('raw', b, a, 0, [])

    # ---------- マップ
    def map(s, attr_off, name):
        r = s.r; A = r[attr_off:attr_off + 12]
        at = dict(border=A[0], h=A[1], w=A[2], blkbank=A[3], blk=w(A, 4), scbank=A[6], scripts=w(A, 7), events=w(A, 9), conn=A[11])
        n = bin(at['conn'] & 0xF).count('1')
        at['connections'] = bytes(r[attr_off + 12:attr_off + 12 + 12 * n])
        b = at['scbank']
        # scripts header
        o = fo(b, at['scripts']); p = o
        ns = r[p]; p += 1; scenes = []
        for i in range(ns): scenes.append(w(r, p)); s.add('script', b, w(r, p), name + ' scene'); p += 4
        nc = r[p]; p += 1; cbs = []
        for i in range(nc): cbs.append((r[p], w(r, p + 1))); s.add('script', b, w(r, p + 1), name + ' callback'); p += 3
        at['scenes'] = scenes; at['callbacks'] = cbs
        # events
        o = fo(b, at['events']); p = o + 2
        nw = r[p]; p += 1; warps = [bytes(r[p + 5 * i:p + 5 * i + 5]) for i in range(nw)]; p += 5 * nw
        ncd = r[p]; p += 1; coords = [bytes(r[p + 8 * i:p + 8 * i + 8]) for i in range(ncd)]; p += 8 * ncd
        for c in coords: s.add('script', b, w(c, 4), name + ' coord')
        nb = r[p]; p += 1; bgs = [bytes(r[p + 5 * i:p + 5 * i + 5]) for i in range(nb)]; p += 5 * nb
        for g in bgs:
            t = g[2]; ptr = w(g, 3)
            if t == 7: s.add('raw4', b, ptr, name + ' hiddenitem')   # BGEVENT_ITEM: dw flag, db item
            elif t == 8: s.add('copy', b, ptr, name + ' bg copy')
            else: s.add('script', b, ptr, name + ' bg')
        no = r[p]; p += 1; objs = [bytes(r[p + 13 * i:p + 13 * i + 13]) for i in range(no)]; p += 13 * no
        for ob in objs:
            typ = ob[7] & 0xF; ptr = w(ob, 9)
            if typ == 1: s.add('raw2', b, ptr, name + ' itemball')
            elif typ == 2: s.add('trainer', b, ptr, name + ' trainer')
            else: s.add('script', b, ptr, name + ' obj')
        at.update(warps=warps, coords=coords, bgs=bgs, objs=objs, ev0=bytes(r[o:o + 2]))
        return at
    def w_raw4(s, b, a, ctx): s.put('hiddenitem', b, a, 3, [(0, 'dw', 'event_flag', 'hiddenitem'), (2, 'db', 'item', 'hiddenitem')])
    def w_raw2(s, b, a, ctx): s.put('itemball', b, a, 2, [(0, 'db', 'item', 'itemball')])
    def w_copy(s, b, a, ctx): s.notes.append('BGEVENT_COPY %02X:%04X（%s）' % (b, a, ctx)); s.put('raw', b, a, 0, [])
    def w_trainer(s, b, a, ctx):
        o = fo(b, a); r = s.r
        for k in (4, 6, 8): s.add('text', b, w(r, o + k), ctx + ' trainer text')
        s.add('script', b, w(r, o + 10), ctx + ' after')
        s.put('trainer', b, a, 12, [(0, 'dw', 'event_flag', 'trainer'), (2, 'db', 'trainer_group', 'trainer'), (3, 'db', 'trainer_id', 'trainer'),
                                    (4, 'dw', 'text_pointer', 'trainer'), (6, 'dw', 'text_pointer', 'trainer'), (8, 'dw', 'text_pointer', 'trainer'), (10, 'dw', 'pointer', 'trainer')])
