#!/usr/bin/env python3
"""Phase 127 (report 2026-11-23):
 1. Hikers on Routes 9, 10 and 25 looked like the player: phase 110 made them POKEFAN_M ($2D), which the Cerulean map
    group's outdoor sprite list (05:4539, the sprites an outdoor map can load) did not have; an object whose sprite is
    not loaded is drawn with the player's tiles.  The list's FISHING_GURU ($3B; no outdoor map of the group uses it now)
    -> POKEFAN_M.
 2. Diglett's Cave, Pewter (Route 2) side entrance (26:86): its border block was $0A (a floor-and-wall block) instead
    of the cave rock $7D (as the Vermilion side, and Red): the area around the room was drawn broken.
 3. Moves that flash the screen (Thunderbolt, Confuse Ray ...): a black box in the text box.  The PP cells (14-18, 13)
    had the 6th BG palette all battle long (the kit's PP color: palette 6's color 3), and the flash changes palettes
    0-6 (not 7, the text box's): its white became black.  Now the cells have palette 6 only while the move menu is
    shown (StatusColor_PP) and palette 7 again after the move is chosen (StatusColor_PPReset), in the attribute map and
    in VRAM (96:4813 / 96:485A hooks; the battle layout sets 7).
 4. The bike sprite (phase 110: Red's) looked like Crystal's player: Satoshi's head (his standing frames' top 9 rows)
    on the bike frames.
 5. A trainer saw the player through a wall / over a ledge (Route 9's youngster walked onto the ledge): asm/
    trainer_sight.asm (FacingPlayerDistance_bc -> bank $8E).
 6. Oak's lab, Shigeru's challenge after the starter: he walked his fixed way to (4,6) whatever the player's column;
    with the player at (5,7) he talked from aside and his way out (right, then down) went through the player (the
    player looked pushed).  When the player is at x = 5, Shigeru steps right after his approach (above the player),
    and his way out (right, down) passes beside the player.
 7. Gym guides (phase 122): the "wait!" coord events in front of the doors also ran when the player came in (walking
    up) — e.g. back in Cerulean Gym after leaving by Fly / Dig.  They now run only when the player faces down.
 8. Pewter City: the gym guy (who takes the player to the gym) stays after Brock is beaten: now he is hidden once the
    player has the Boulder Badge (object flag $A20, set / cleared by an objects callback).
usage: build_phase127.py IN.gbc OUT.gbc OUT.ips
"""
import os, sys, re, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import Space
from evedit import MapEvents
from build_phase52 import rgbds

HERE = os.path.dirname(os.path.abspath(__file__))
FREE_BANK = 0x8E
HIDE_GYM_GUY = 0xA20
BOULDER = 0x23


def expect(rom, o, hexs):
    b = bytes.fromhex(hexs.replace(' ', ''))
    assert rom[o:o + len(b)] == b, (hex(o), rom[o:o + len(b)].hex(' '), hexs)
    return b


def w16(v): return bytes([v & 0xFF, v >> 8])


class Free:
    def __init__(s, rom, bank, margin=2):
        s.rom, s.bank = rom, bank
        s.o = bank_free_tail(rom, bank)[0] + margin
        s.end = (bank + 1) * 0x4000
    def addr(s): return 0x4000 + s.o - s.bank * 0x4000
    def put(s, data):
        assert s.o + len(data) <= s.end, (hex(s.bank), len(data))
        a = s.addr(); s.rom[s.o:s.o + len(data)] = data; s.o += len(data); return a


def assemble(rom, asm, bank, defs):
    f = Free(rom, bank)
    with tempfile.TemporaryDirectory() as d:
        open(d + '/in.gbc', 'wb').write(rom)
        args = [rgbds('rgbasm')]
        for k, v in dict(defs, CODE_BANK=bank, CODE_ADDR=f.addr()).items(): args += ['-D', '%s=$%X' % (k, v)]
        subprocess.run(args + ['-o', d + '/a.o', os.path.join(HERE, 'asm', asm)], check=True)
        subprocess.run([rgbds('rgblink'), '-O', d + '/in.gbc', '-o', d + '/out.gbc', '-n', d + '/out.sym', d + '/a.o'],
                       check=True)
        new = open(d + '/out.gbc', 'rb').read()
        sym = {l.split()[1]: int(l.split()[0].split(':')[1], 16) for l in open(d + '/out.sym')
               if re.match(r'[0-9a-f]+:[0-9a-f]+ ', l)}
    diff = [i for i in range(len(rom)) if rom[i] != new[i]]
    assert min(diff) >= f.o and max(diff) < f.end
    rom[:] = new
    return sym


def hikers(rom, log):
    o = fo(5, 0x4539)
    expect(rom, o, '07 07 07 07 07 07 07 07 07 07 07 07 23 2b 24 43 27 3b 07 35 07 54 45')
    rom[o + 17] = 0x2D
    log.append('Cerulean group outdoor sprites: $3B -> $2D (05:%04X)' % (0x4539 + 17))


def diglett(rom, log):
    sys.path.insert(0, os.path.join(SC, 'play'))
    from mapdb import DB
    with tempfile.NamedTemporaryFile(suffix='.gbc') as tf:
        tf.write(rom); tf.flush(); db = DB(tf.name)
    p, v = db.maps[(26, 86)]['attr'], db.maps[(26, 110)]['attr']
    assert rom[p] == 0x0A and rom[v] == 0x7D and rom[p + 1:p + 3] == rom[v + 1:v + 3] == b'\x04\x04'
    rom[p] = 0x7D
    log.append('Diglett\'s Cave Route 2 entrance: border $0A -> $7D')


def pp_attr(rom, log):
    expect(rom, fo(0x96, 0x4761), '21 df ce 3e 06 22 22 22 22 77')
    rom[fo(0x96, 0x4765)] = 0x07                                     # the battle layout: palette 7
    expect(rom, fo(0x96, 0x4813), 'c5 21 b2 c5 cd')
    expect(rom, fo(0x96, 0x485A), '11 06 01 af cd')
    f = Free(rom, 0x96)
    # a = palette: the attribute map and VRAM bank 1 (9800 + 13 * 32 + 14), 5 cells
    setp = f.put(bytes([0xC5, 0xD5, 0xE5,                               # push bc / de / hl
                        0x21, 0xDF, 0xCE, 0x06, 0x05, 0x22, 0x05, 0x20, 0xFC, 0x4F,
                        0xF0, 0x4F, 0xF5, 0x3E, 0x01, 0xE0, 0x4F,
                        0x21, 0xAE, 0x99, 0x06, 0x05,
                        0xF0, 0x41, 0xE6, 0x02, 0x20, 0xFA, 0x71, 0x23, 0x05, 0x20, 0xF5,
                        0xF1, 0xE0, 0x4F, 0xE1, 0xD1, 0xC1, 0xC9]))
    pp = f.put(bytes([0x3E, 0x06, 0xCD]) + w16(setp) + bytes([0xC5, 0x21, 0xB2, 0xC5, 0xC3, 0x17, 0x48]))
    rs = f.put(bytes([0x3E, 0x07, 0xCD]) + w16(setp) + bytes([0x11, 0x06, 0x01, 0xC3, 0x5D, 0x48]))
    rom[fo(0x96, 0x4813):fo(0x96, 0x4813) + 3] = bytes([0xC3]) + w16(pp)
    rom[fo(0x96, 0x485A):fo(0x96, 0x485A) + 3] = bytes([0xC3]) + w16(rs)
    log.append('PP cells palette: 96:%04X (menu 6 at 96:%04X, back to 7 at 96:%04X)' % (setp, pp, rs))


def bike(rom, log):
    def px(g):
        P = [[0] * 16 for _ in range(16)]
        for t, (dx, dy) in enumerate(((0, 0), (8, 0), (0, 8), (8, 8))):
            d = rom[g + t * 16:g + t * 16 + 16]
            for y in range(8):
                lo, hi = d[2 * y], d[2 * y + 1]
                for x in range(8): P[dy + y][dx + x] = ((lo >> (7 - x)) & 1) | (((hi >> (7 - x)) & 1) << 1)
        return P
    def enc(P):
        out = bytearray()
        for dx, dy in ((0, 0), (8, 0), (0, 8), (8, 8)):
            for y in range(8):
                lo = hi = 0
                for x in range(8):
                    v = P[dy + y][dx + x]; lo |= (v & 1) << (7 - x); hi |= (v >> 1) << (7 - x)
                out += bytes([lo, hi])
        return out
    e1, e2 = fo(5, 0x4727), fo(5, 0x4727) + 6
    expect(rom, e1, 'c0 46 c0 30 01 00'); expect(rom, e2, '51 79 c0 71 01 00')
    walk, bk = fo(0x30, 0x46C0), fo(0x71, 0x7951)
    out = bytearray()
    for f in range(6):
        s = px(walk + (f % 3) * 64); k = px(bk + f * 64)
        out += enc([s[y][:] if y < 9 else k[y][:] for y in range(16)])
    rom[bk:bk + 384] = out
    log.append('bike sprite: Satoshi\'s head on the bike (71:7951)')


def trainer_sight(rom, log):
    expect(rom, 0x3675, 'd5 cd 7d 36 42 4b d1 c9')
    sym = assemble(rom, 'trainer_sight.asm', FREE_BANK, {})
    rom[0x3675:0x367D] = bytes([0x3E, FREE_BANK, 0x21]) + w16(sym['TSight']) + bytes([0xCF, 0xC9, 0x00])
    log.append('trainer sight: %02X:%04X' % (FREE_BANK, sym['TSight']))


def lab_rival(rom, log):
    o = fo(0x62, 0x4B17)
    expect(rom, o, '75 00 01 63 84 4c a4 4c')
    f = Free(rom, 0x62)
    a = Asm(f.addr()); a.bank = 0x62
    a.db(0x1C, 0x12); a.ifnotequal(5, 'x')                          # readvar VAR_X ; player at x = 5:
    a.applymovement(6, 'mv')                                          # Shigeru one step right (above him)
    a.label('x'); a.turnobject(0, 1); a.sjump(0x4B1A)
    a.label('mv'); a.db(0x0F, 0x47)
    blob = a.done(); base = f.put(blob); assert base == a.base
    rom[o:o + 3] = bytes([0x03]) + w16(base)
    log.append('lab: Shigeru beside the player 62:%04X' % base)


def gym_doors(rom, log):
    sys.path.insert(0, os.path.join(SC, 'play'))
    from mapdb import DB
    with tempfile.NamedTemporaryFile(suffix='.gbc') as tf:
        tf.write(rom); tf.flush(); db = DB(tf.name)
    f = Free(rom, FREE_BANK)
    n = 0
    for g in ('PewterGym', 'CeruleanGym', 'VermilionGym', 'CeladonGym', 'SaffronGym', 'ViridianGym'):
        m = db.maps[mapid(g)]; b = m['scbank']
        for _, c in m['ev']['coords']:
            p = c[4] | c[5] << 8; o = fo(b, p)
            if not (rom[o] == 0x34 and rom[o + 2] == 0x00 and rom[o + 3] == 0x08 and rom[o + 6] == 0x31): continue
            badge = rom[o + 1]; skip = rom[o + 4] | rom[o + 5] << 8
            a = Asm(f.addr()); a.bank = FREE_BANK
            a.db(0x1C, 0x09); a.ifequal(1, 'up')                     # readvar VAR_FACING ; coming in: nothing
            a.checkflag(badge); a.iffalse('nb')
            a.farsjump(b, p + 6)
            a.label('nb'); a.farsjump(b, skip)
            a.label('up'); a.end()
            blob = a.done(); base = f.put(blob); assert base == a.base
            rom[o:o + 4] = bytes([0x04, FREE_BANK]) + w16(base)
            n += 1
    assert n == 12, n
    log.append('gym doors: %d coord events only when facing down' % n)


def pewter_guy(rom, log):
    me = MapEvents(rom, 'PewterCity')
    sp = Space(rom)
    fo_, n_ = bank_free_tail(rom, FREE_BANK); sp.set_area(FREE_BANK, fo_ + 16, FREE_BANK * 0x4000 + 0x4000)
    gy = [i for i, (o, r) in enumerate(me.objs) if (o[2] - 4, o[1] - 4) == (35, 16)]
    assert len(gy) == 1, gy
    o = me.objs[gy[0]][0]
    assert o[11:13] == b'\xff\xff'
    o[11:13] = w16(HIDE_GYM_GUY)
    a = Asm(sp.here(FREE_BANK)); a.bank = FREE_BANK
    me.callbacks.append((2, 'cb_obj'))                                 # MAPCALLBACK_OBJECTS
    a.label('cb_obj'); a.checkflag(BOULDER); a.iffalse('cb_show'); a.setevent(HIDE_GYM_GUY); a.endcallback()
    a.label('cb_show'); a.clearevent(HIDE_GYM_GUY); a.endcallback()
    me.write(a, sp)
    base = a.base; blob = a.done(); assert sp.put(FREE_BANK, blob) == base
    me.install(a)
    log.append('Pewter gym guy: hidden with the Boulder Badge (flag %X), events %02X:%04X' % (HIDE_GYM_GUY, FREE_BANK, base))


def main():
    src, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src, 'rb').read()); log = []
    hikers(rom, log)
    diglett(rom, log)
    pp_attr(rom, log)
    bike(rom, log)
    trainer_sight(rom, log)
    lab_rival(rom, log)
    gym_doors(rom, log)
    pewter_guy(rom, log)
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    sys.stdout.write('\n'.join(log) + '\n')


if __name__ == '__main__':
    main()
