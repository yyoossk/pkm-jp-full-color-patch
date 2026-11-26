"""Move a Crystal map's scripts header + events into another bank so objects / coord events can be added.
Existing script pointers become trampolines (farsjump old_bank:addr) in the new bank; item / hidden-item data is
copied.  New scripts are written into the same Asm and referenced by label."""
from lib import *


def r16(rom, o): return rom[o] | rom[o + 1] << 8


def copy_text(rom, o):
    """the bytes of a JP Crystal text at o (to the end of the text)"""
    out = bytearray()
    ARGS = {0x01: 2, 0x02: 3, 0x09: 3, 0x03: 2, 0x05: 0, 0x06: 0, 0x07: 0, 0x0A: 0, 0x0C: 1, 0x0D: 0, 0x14: 1, 0x15: 0}
    while True:
        c = rom[o]
        if c == 0x00:
            e = o + 1
            while rom[e] not in (0x50, 0x57, 0x58): e += 1
            out += rom[o:e + 1]
            if rom[e] != 0x50: return bytes(out)
            o = e + 1
        elif c == 0x50: out.append(0x50); return bytes(out)
        elif c in ARGS: out += rom[o:o + 1 + ARGS[c]]; o += 1 + ARGS[c]
        else: raise ValueError('text command %02X at %X' % (c, o))


class MapEvents:
    def __init__(s, rom, name):
        s.rom = rom; s.name = name
        s.a = attrs(rom, hdr_index(name)); sb = s.sb = s.a['scbank']
        so = fo(sb, s.a['scripts'])
        n = rom[so]; s.scenes = [r16(rom, so + 1 + 4 * i) for i in range(n)]
        co = so + 1 + 4 * n; n = rom[co]
        s.callbacks = [(rom[co + 1 + 3 * i], ('far', sb, r16(rom, co + 2 + 3 * i))) for i in range(n)]
        ev = parse_events(rom, sb, s.a['events'])
        s.warps = [bytes(w) for _, w in ev['warps']]
        s.coords = [(c[0], c[1], c[2], ('far', sb, c[4] | c[5] << 8)) for _, c in ev['coords']]
        s.bgs = []
        for _, b in ev['bgs']:
            y, x, t, p = b[0], b[1], b[2], b[3] | b[4] << 8
            if t <= 4: s.bgs.append((y, x, t, ('far', sb, p)))
            elif t in (5, 6):
                q = fo(sb, p); s.bgs.append((y, x, t, ('ifset', r16(rom, q), ('far', sb, r16(rom, q + 2)))))
            elif t == 7:
                q = fo(sb, p); s.bgs.append((y, x, t, ('data', bytes(rom[q:q + 3]))))
            else: raise ValueError('bg type %d in %s' % (t, name))
        s.objs = []
        for _, o in ev['objs']:
            o = bytearray(o); t = o[7] & 0x0F; p = o[9] | o[10] << 8
            if t == 0: ref = ('far', sb, p)
            elif t == 1: ref = ('data', bytes(rom[fo(sb, p):fo(sb, p) + 2]))
            elif t == 2: ref = ('keep', p)              # trainer header: only valid if the bank stays the same
            else: raise ValueError('object type %d in %s' % (t, name))
            s.objs.append([o, ref])

    def add_object(s, sprite, x, y, movement, script, flag=0xFFFF, pal_type=0x00, rng=0, sight=0):
        o = bytearray([sprite, y + 4, x + 4, movement, rng, 0xFF, 0xFF, pal_type, sight, 0, 0, flag & 0xFF, flag >> 8])
        s.objs.append([o, script]); return len(s.objs)            # object id for scripts = index + 1 (player = 0)... +1 below

    def write(s, a, sp):
        """emit header + events into Asm a (its bank becomes the map's script bank)"""
        bank = a.bank; tramp = {}
        def ref(r):
            if isinstance(r, str): return r
            kind = r[0]
            if kind == 'keep':
                if bank == s.sb: return r[1]
                key = ('tr', r[1])                      # a trainer header copied into the new bank
                if key not in tramp: tramp[key] = 'th%d' % len(tramp)
                return tramp[key]
            if kind == 'far' and r[1] == bank: return r[2]
            if kind == 'far':
                key = (r[1], r[2])
                if key not in tramp: tramp[key] = 'tr%d' % len(tramp)
                return tramp[key]
            raise ValueError(r)
        datas = []
        def data(b):
            l = 'dt%d' % len(datas); datas.append((l, b)); return l
        a.label('mapscripts'); a.db(len(s.scenes))
        for p in s.scenes: a.dw(p if isinstance(p, str) else ref(('far', s.sb, p))); a.dw(0)
        a.db(len(s.callbacks))
        for t, r in s.callbacks: a.db(t); a.dw(ref(r))
        a.label('events'); a.db(0, 0)
        a.db(len(s.warps))
        for w in s.warps: a.raw(w)
        a.db(len(s.coords))
        for sc, y, x, r in s.coords: a.db(sc, y, x, 0); a.dw(ref(r)); a.db(0, 0)
        a.db(len(s.bgs))
        for y, x, t, r in s.bgs:
            a.db(y, x, t)
            if isinstance(r, tuple) and r[0] == 'data': a.dw(data(r[1]))
            elif isinstance(r, tuple) and r[0] == 'ifset':
                l = 'if%d_%d' % (y, x); datas.append((l, ('ifset', r[1], ref(r[2])))); a.dw(l)
            else: a.dw(ref(r))
        a.db(len(s.objs))
        for o, r in s.objs:
            a.raw(bytes(o[:9]))
            if isinstance(r, tuple) and r[0] == 'data': a.dw(data(r[1]))
            else: a.dw(ref(r))
            a.raw(bytes(o[11:13]))
        for l, b in datas:
            a.label(l)
            if isinstance(b, tuple): a.dw(b[1]); a.dw(b[2])
            else: a.raw(b)
        for (b, p), l in tramp.items():
            if b == 'tr':                               # flag, class, id; texts -> text_far stubs; script -> farsjump
                h = s.rom[fo(s.sb, p):fo(s.sb, p) + 12]
                a.label(l); a.raw(bytes(h[:4]))
                for k in range(3):
                    t = h[4 + 2 * k] | h[5 + 2 * k] << 8
                    a.dw(l + 't%d' % k if t else 0)
                a.dw(l + 's')
                for k in range(3):
                    t = h[4 + 2 * k] | h[5 + 2 * k] << 8
                    if t: a.label(l + 't%d' % k); a.raw(copy_text(s.rom, fo(s.sb, t)))     # (JP: no text_far)
                sc = h[10] | h[11] << 8
                a.label(l + 's'); a.farsjump(s.sb, sc)
                continue
            a.label(l); a.farsjump(b, p)

    def install(s, a):
        """point the map attributes at the new header/events (call after the Asm was placed)"""
        rom = s.rom; ao = s.a['attr_off']
        rom[ao + 6] = a.bank
        m = a.labels['mapscripts']; e = a.labels['events']
        rom[ao + 7] = m & 0xFF; rom[ao + 8] = m >> 8; rom[ao + 9] = e & 0xFF; rom[ao + 10] = e >> 8
