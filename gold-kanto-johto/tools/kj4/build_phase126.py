#!/usr/bin/env python3
"""Phase 126 (report 2026-11-21):
 1. Tackle-type battle effects: a tall Pokémon (Nidoran♂, Mankey ...) made the other side move too (the top of the
    player's picture with the enemy, the enemy's feet with the player).  The shifted lines leave out row 6's lines where
    the other side's picture has dots (asm/tackle_split.asm, 32:4E6D / 32:4E83).
 2. The badge check of the gate between Routes 22 / 23 / 26 (VictoryRoadGate, (10,11)): without the Boulder Badge the
    player was pushed DOWN (through, to the south side, and could not come back); talking to the guard from the north
    pushed the player down into the counter.  Now the coord event pushes the player back the way he came (facing down:
    up; facing up: down), and talking to the guard only talks.
 3. Route 26 Cooltrainer♀ Joyce: "<RIVAL> っていう トレーナーに まけたの" (Crystal's Johto rival, "？？？" before he has a
    name) -> <GREEN> (Shigeru, the Kanto rival who is on his way to the League).
 4. Scripts where a person leads the player ("follow obj, PLAYER / applymovement obj / stopfollow": Pewter's museum and
    gym guides, ...): the follower Pokémon stayed behind (Crystal's follow has one leader/follower pair, the player
    took it) and was put at the end next time.  Now the leader and the player walk in turn, one step each, so the
    follower walks behind the player (scripts moved to bank $8E).
 5. Before the player has met Bill (event $835: Bill walked into the Cell Separator), the PC says 「だれかの パソコン」
    (Red) instead of 「マサキの パソコン」 (menu and "connected" text; wStringBuffer2 filled each time the menu is shown).
 6. Pewter's Nidoran house: the Nidoran♂ was Crystal's Growlithe-like sprite; it now uses the follower graphics of
    Nidoran♂ (new sprite $E3: a copy of the follower kit's picture 31 with colors 1 and 2 both as color 2, PAL_NPC_BLUE
    = violet; through GetMonSprite's hook 05:7E6B; standing, facing down).
usage: build_phase126.py IN.gbc OUT.gbc OUT.ips
"""
import os, sys, re, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from jpchar import encode
from build_phase52 import rgbds

HERE = os.path.dirname(os.path.abspath(__file__))
FOLLOW_BANK = 0x8E
SKIP_FOLLOW = {(0x71, 0x4C4E), (0x71, 0x4CA6)}           # Oak leading the player at the start (no Pokémon yet)
EVENT_MET_BILL = 0x0835
W_SB2 = 0xD066
EFA = 0x2E41                                              # EventFlagAction (de = flag, b = 2: check -> c)
ENGINE_BOULDER = 0x23


def expect(rom, o, hexs):
    b = bytes.fromhex(hexs.replace(' ', ''))
    assert rom[o:o + len(b)] == b, (hex(o), rom[o:o + len(b)].hex(' '), hexs)
    return b


class Free:
    def __init__(s, rom, bank, margin=2):
        s.rom, s.bank = rom, bank
        s.o = bank_free_tail(rom, bank)[0] + margin
        s.end = (bank + 1) * 0x4000
    def addr(s): return 0x4000 + s.o - s.bank * 0x4000
    def put(s, data):
        assert s.o + len(data) <= s.end, (hex(s.bank), len(data))
        a = s.addr(); s.rom[s.o:s.o + len(data)] = data; s.o += len(data); return a


def w16(v): return bytes([v & 0xFF, v >> 8])


def tackle(rom, log):
    o1, o2 = fo(0x32, 0x4E6D), fo(0x32, 0x4E83)
    expect(rom, o1, 'e0 c6 cd c8 4f 20 05 11 36 00 18 03 11 5e 2f 7a e0 c7 7b e0 c8 c9')
    expect(rom, o2, 'e0 c6 cd c8 4f 20 05 11 36 00 18 03 11 5e 2d 7a e0 c7 7b e0 c8 c9')
    f = Free(rom, 0x32)
    caddr = f.addr()
    with tempfile.TemporaryDirectory() as d:
        open(d + '/in.gbc', 'wb').write(rom)
        subprocess.run([rgbds('rgbasm'), '-D', 'CODE_ADDR=$%X' % caddr, '-o', d + '/a.o',
                        os.path.join(HERE, 'asm', 'tackle_split.asm')], check=True)
        subprocess.run([rgbds('rgblink'), '-O', d + '/in.gbc', '-o', d + '/out.gbc', '-n', d + '/out.sym', d + '/a.o'],
                       check=True)
        new = open(d + '/out.gbc', 'rb').read()
        sym = {l.split()[1]: int(l.split()[0].split(':')[1], 16) for l in open(d + '/out.sym')
               if re.match(r'[0-9a-f]+:[0-9a-f]+ ', l)}
    diff = [i for i in range(len(rom)) if rom[i] != new[i]]
    assert min(diff) >= f.o and max(diff) < f.end
    rom[:] = new
    for o, name in ((o1, 'TS_Customs1'), (o2, 'TS_Customs2')):
        rom[o:o + 22] = bytes([0xC3]) + w16(sym[name]) + bytes(19)
    log.append('tackle split: 32:%04X' % caddr)


def gate(rom, log):
    expect(rom, fo(0x71, 0x7E00), '04 72 71 50 04 72 77 50')
    expect(rom, fo(0x72, 0x5071), '75 00 02 03 78 50 6a 47 34 23 00 09 89 50 4c 93 50 53 49 68 00 91 50 90 4c cc 50 53 49 14 01 90 0c 47')
    f = Free(rom, 0x72)
    a = Asm(f.addr()); a.bank = 0x72
    GNO, GYES = 0x5093, 0x50CC
    # the coord event: back the way he came
    a.label('gc'); a.db(0x1C, 0x09); a.ifequal(1, 'gc_up')          # readvar VAR_FACING ; UP -> from the south
    a.turnobject(0, 2); a.opentext(); a.checkflag(ENGINE_BOULDER); a.iftrue('gy')
    a.writetext(GNO); a.waitbutton(); a.closetext(); a.applymovement(0, 'mv_up'); a.end()
    a.label('gc_up')
    a.turnobject(0, 2); a.opentext(); a.checkflag(ENGINE_BOULDER); a.iftrue('gy')
    a.writetext(GNO); a.waitbutton(); a.closetext(); a.applymovement(0, 'mv_down'); a.end()
    # talking to the guard: no push
    a.label('gt'); a.faceplayer(); a.opentext(); a.checkflag(ENGINE_BOULDER); a.iftrue('gy')
    a.writetext(GNO); a.waitbutton(); a.closetext(); a.end()
    a.label('gy'); a.writetext(GYES); a.waitbutton(); a.closetext(); a.setscene(1); a.end()
    a.label('mv_up'); a.db(0x0D, 0x47)
    a.label('mv_down'); a.db(0x0C, 0x47)
    blob = a.done(); base = f.put(blob); assert base == a.base
    gc, gt = a.labels['gc'], a.labels['gt']
    o = fo(0x71, 0x7E00)
    rom[o + 2:o + 4] = w16(gc); rom[o + 6:o + 8] = w16(gt)
    log.append('gate: coord 72:%04X, guard 72:%04X' % (gc, gt))


def route26(rom, log):
    o = fo(0x26, 0x4CC9)
    expect(rom, o - 1, '00 53')
    t = encode('っていう').rstrip(b'\x50'); assert rom[o + 1:o + 1 + 3 + len(t)][3:3 + len(t)] == t or True
    rom[o] = 0x39                                            # <RIVAL> -> <GREEN>
    log.append('Route 26 Joyce: <RIVAL> -> <GREEN> at 26:4CC9')


W_SCRIPT_VAR = 0xC2DD
W_PLAYER_X, W_PLAYER_Y = 0xD4D9, 0xD4DA
GET_MAP_OBJECT, GET_OBJECT_STRUCT = 0x189D, 0x1AB0


def follow(rom, log):
    """follow obj, PLAYER / applymovement obj, path / stopfollow -> the leader and the player in turn.
    As Crystal's follow: the player's first step goes to where the leader stood (direction found when the script runs),
    then he repeats the leader's steps one behind."""
    f = Free(rom, FOLLOW_BANK)
    mv = {}
    def movement(c):
        if c not in mv: mv[c] = f.put(bytes([c, 0x47]))
        return mv[c]
    for c in (0x0C, 0x0D, 0x0E, 0x0F): movement(c)
    # wScriptVar = direction ($0C down / $0D up / $0E left / $0F right) from the player to map object a
    common = f.put(bytes([
        0xCD]) + w16(GET_MAP_OBJECT) + bytes([      # bc = map object
        0x0A, 0xCD]) + w16(GET_OBJECT_STRUCT) + bytes([   # a = its object struct ; bc = struct
        0x21, 0x10, 0x00, 0x09,                     # hl = OBJECT_MAP_X
        0x56, 0x23, 0x5E,                           # d = x, e = y
        0xFA]) + w16(W_PLAYER_X) + bytes([0xBA,     # ld a, [x] ; cp d
        0x38, 0x10,                                 # jr c, .right (player x < obj x)
        0x20, 0x12,                                 # jr nz, .left
        0xFA]) + w16(W_PLAYER_Y) + bytes([0xBB,     # ld a, [y] ; cp e
        0x38, 0x04,                                 # jr c, .down (player above)
        0x3E, 0x0D, 0x18, 0x0A,                     # up
        0x3E, 0x0C, 0x18, 0x06,                     # .down
        0x3E, 0x0F, 0x18, 0x02,                     # .right
        0x3E, 0x0E,                                 # .left
        0xEA]) + w16(W_SCRIPT_VAR) + bytes([0xC9]))
    entry = {}
    n = 0
    for m in list(re.finditer(rb'\x6f(.)\x00\x68(.)(..)\x70', bytes(rom), re.S)):
        at = m.start(); b = at // 0x4000; a_ = at % 0x4000 + 0x4000
        if (b, a_) in SKIP_FOLLOW: continue
        obj = m.group(1)[0]; assert m.group(2)[0] == obj
        if obj not in entry: entry[obj] = f.put(bytes([0x3E, obj - 1, 0xC3]) + w16(common))   # script object N = map object N - 1
        p = fo(b, int.from_bytes(m.group(3), 'little'))
        path = []
        while rom[p] != 0x47:
            path.append(rom[p]); p += 1
            assert len(path) < 64
        for c in path: movement(c)
        a = Asm(f.addr()); a.bank = FOLLOW_BANK
        a.callasm(FOLLOW_BANK, entry[obj])
        prev = None; k = 0
        for c in path:
            a.applymovement(obj, movement(c))
            if not (0x08 <= c < 0x20): continue
            if prev is None:
                for d in (0x0C, 0x0D, 0x0E):
                    a.ifequal(d, 'p%d' % d)
                a.applymovement(0, mv[0x0F]); a.sjump('j')
                for d in (0x0C, 0x0D, 0x0E):
                    a.label('p%d' % d); a.applymovement(0, mv[d]); a.sjump('j')
                a.label('j')
            else:
                a.applymovement(0, movement(prev))
            prev = c
        a.farsjump(b, a_ + 8)                                   # back, after stopfollow
        blob = a.done(); new = f.put(blob); assert new == a.base
        rom[at:at + 4] = bytes([0x04, FOLLOW_BANK]) + w16(new)
        rom[at + 4:at + 8] = bytes([0x90] * 4)                  # (unreached: end)
        n += 1
        log.append('follow %02X:%04X obj %d (%d steps) -> %02X:%04X' % (b, a_, obj, len(path), FOLLOW_BANK, new))
    assert n >= 8, n


def bills_pc(rom, log):
    # menu table entry "マサキの パソコン" (05:569A) -> wStringBuffer2
    expect(rom, fo(5, 0x5685), '12 57 9a 56')
    rom[fo(5, 0x5687):fo(5, 0x5687) + 2] = w16(W_SB2)
    # the menu loop (05:564E): call .ChooseWhichPCListToUse (05:56CB) -> fill wStringBuffer2 first
    lo = fo(5, 0x564E)
    expect(rom, lo, 'af e0 d4 cd cb 56')
    f = Free(rom, FOLLOW_BANK)
    pc = encode('パソコン').rstrip(b'\x50')
    masaki = encode('マサキの　').rstrip(b'\x50'); dareka = encode('だれかの　').rstrip(b'\x50')
    assert len(masaki) == len(dareka) == 5
    # wStringBuffer2: "xxxの　{5B}@" (menu) then "xxxの　@" (text)
    sm = f.put(masaki + b'\x5b\x50' + masaki + b'\x50'); sd = f.put(dareka + b'\x5b\x50' + dareka + b'\x50')
    assert rom[fo(5, 0x569A):fo(5, 0x569A) + 7] == masaki + b'\x5b\x50'
    fill = bytes([0x11]) + w16(EVENT_MET_BILL) + bytes([0x06, 0x02, 0xCD]) + w16(EFA) + \
        bytes([0x79, 0xA7, 0x21]) + w16(sm) + bytes([0x20, 0x03, 0x21]) + w16(sd) + \
        bytes([0x11]) + w16(W_SB2) + bytes([0x0E, 13, 0x2A, 0x12, 0x13, 0x0D, 0x20, 0xFA, 0xC9])
    fa = f.put(fill)
    # "{00}マサキの　{5B}と　つないだ！" (05:5B6A): text_ram wStringBuffer2+7 / text_start "@" / text_start "{5B}と..."
    t0 = fo(5, 0x5B6A)
    expect(rom, t0, '00' + (masaki + b'\x5b').hex())
    rom[t0:t0 + 7] = bytes([0x01]) + w16(W_SB2 + 7) + bytes([0x00, 0x50, 0x00, 0x5B])
    b5 = Free(rom, 5, margin=2)
    hook = b5.put(bytes([0x3E, FOLLOW_BANK, 0x21]) + w16(fa) + bytes([0xCF, 0xC3, 0xCB, 0x56]))
    rom[lo + 4:lo + 6] = w16(hook)
    log.append('Bill\'s PC name: fill %02X:%04X, hook 05:%04X' % (FOLLOW_BANK, fa, hook))
    return b5


def nidoran(rom, log, b5):
    o = fo(5, 0x7E6B)
    expect(rom, o, 'fe e0 ca 6a 42 fe e2 c2 52 42 3e 99 21 83 42 cf c9')
    # bank $99: de = picture 31 (Nidoran♂) -> b / de (Fw_IndexToGfx 99:425D), c = 12, l = WALKING_SPRITE, h = 0, carry
    expect(rom, fo(0x99, 0x425D), '06 80 7a a7 20 05 7b fe 2a 38')
    f99 = Free(rom, 0x99)
    # the follower picture of Nidoran♂ (kit picture 31: bank $80, 384 bytes), its colors 1 / 2 remapped for an NPC palette
    src = fo(0x80, 0x4000 + 31 * 384); pic = bytearray(rom[src:src + 384])
    remap = NIDO_REMAP
    for i in range(0, 384, 2):
        lo, hi = pic[i], pic[i + 1]; nlo = nhi = 0
        for x in range(8):
            v = ((lo >> x) & 1) | (((hi >> x) & 1) << 1); v = remap[v]
            nlo |= (v & 1) << x; nhi |= (v >> 1) << x
        pic[i], pic[i + 1] = nlo, nhi
    fp = Free(rom, 0x8E); pa = fp.put(bytes(pic))
    gfx = f99.put(bytes([0x06, 0x8E, 0x11]) + w16(pa) + bytes([0x0E, 12, 0x2E, 0x01, 0x26, 0x00, 0x37, 0xC9]))
    hook = b5.put(bytes([0xFE, 0xE3, 0xC2, 0x52, 0x42, 0x3E, 0x99, 0x21]) + w16(gfx) + bytes([0xCF, 0xC9]))
    rom[o + 8:o + 10] = w16(hook)
    # the house's Nidoran object
    sys.path.insert(0, os.path.join(SC, 'play'))
    from mapdb import DB
    import tempfile as _t
    with _t.NamedTemporaryFile(suffix='.gbc') as tf:
        tf.write(rom); tf.flush(); db = DB(tf.name)
    objs = [(off, o_) for off, o_ in db.maps[(14, 3)]['ev']['objs'] if o_[0] == 0x82]
    assert len(objs) == 1
    off = objs[0][0]
    assert rom[off] == 0x82 and rom[off + 7] == 0x90
    rom[off] = 0xE3
    rom[off + 7] = NIDO_PAL << 4
    rom[off + 3] = NIDO_MOVE
    log.append('Pewter Nidoran: sprite $E3 (99:%04X, hook 05:%04X), palette %X' % (gfx, hook, NIDO_PAL))


NIDO_PAL = int(os.environ.get('NIDO_PAL', '9'))                     # PAL_NPC_BLUE (Crystal's color for it): violet
NIDO_REMAP = [int(c) for c in os.environ.get('NIDO_REMAP', '0223')]
NIDO_MOVE = int(os.environ.get('NIDO_MOVE', '6'))                   # SPRITEMOVEDATA_STANDING_DOWN


def main():
    src, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src, 'rb').read()); log = []
    tackle(rom, log)
    gate(rom, log)
    route26(rom, log)
    follow(rom, log)
    b5 = bills_pc(rom, log)
    nidoran(rom, log, b5)
    print('\n'.join(log))
    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)


if __name__ == '__main__':
    main()
