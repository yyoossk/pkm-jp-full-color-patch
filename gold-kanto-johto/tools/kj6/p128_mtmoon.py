#!/usr/bin/env python3
"""Phase 128 part (report 2026-11-26): Mt. Moon as in Red, and gift Pokémon sent to the box.
 1. Mt. Moon B2F (the TM01 floor) had none of Red's two hidden items (pokered hidden_events: MOON_STONE at (18, 12),
    ETHER at (33, 9)): added as hidden items (bg events BGEVENT_ITEM, new flags HID_MOON_STONE / HID_ETHER).
 2. Mt. Moon 1F: Red's ball at (5, 32) is TM12 Water Gun; here it was Crystal's TM12 (Sweet Scent, which Crystal gives
    in Johto anyway), and Water Gun was not to be had (Charmander's way is harder than in Red).  The ball now holds
    "the Water Gun TM": picking it up offers Water Gun to a Pokémon that can learn Red's TM12 (pokered tmhm lists,
    through phase 122's tutor wrapper: a Water Gun entry added to its table); once taught the ball is gone, if the
    player says no it stays (to be used later, as Red's TM in the bag).
 3. A Pokémon given by a script (givepoke) to a full party goes to the box with LoadEnemyMon's item: outside a battle
    LoadEnemyMon takes the trainer-battle way and reads the item of the last trainer's party (wOTPartyMon), and
    GivePoke wrote its own item only when it was not 0 (Crystal's bug): the Magikarp bought at the Mt. Moon Pokémon
    Center held the Old Amber.  GivePoke wrote its own item only when it was not 0, and with SRAM closed (so even a
    gift item was lost).  GivePoke (03:652B) now opens SRAM (OpenSRAM $2F9D / CloseSRAM $2FAC) and always writes the
    given item (0: none) to the box Pokémon.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from portlib import Space
import evedit
from evedit import MapEvents
from jpchar import encode

MT1F, MTB2F = (26, 37), (26, 39)
HID_MOON_STONE, HID_ETHER = 0xA2C, 0xA2D            # extended flags (phase 127 used 0xA20)
TM12_FLAG = 0x805                                     # the 1F ball's flag (kept)
WRAP_PTR = 0x8595                                     # predef CanLearnTMHMMove -> phase 122's wrapper (bank $20)
CODE_BANK = 0x20
SPECIAL_MOVE_TUTOR = 131


def w16(v): return bytes([v & 0xFF, v >> 8])


def T(s): return b'\x00' + encode(s + '<DONE>')


def map_events(rom, key):
    g, m = key; G = 0x94000                           # JP MapGroupPointers (bank $25)
    hdr = fo(0x25, rom[G + 2 * (g - 1)] | rom[G + 2 * (g - 1) + 1] << 8) + 9 * (m - 1)
    old = evedit.hdr_index
    evedit.hdr_index = lambda n: hdr
    try: return MapEvents(rom, str(key))
    finally: evedit.hdr_index = old


def givepoke_box_item(rom, log):
    # ld a,[wCurItem] / and a / jr z,.done / ld a,[wCurItem] / ld [sBoxMon1Item],a (SRAM closed: lost) /
    # ld a,[wCurPartySpecies] / ld [wNamedObjectIndex],a / ld [wTempEnemyMonSpecies],a (already that species)
    o = fo(3, 0x652B)
    assert rom[o:o + 21] == bytes.fromhex('fac6d0a72806fac6d0ea31adfac8d0ea96d2ea35d2'), rom[o:o + 21].hex(' ')
    rom[o:o + 21] = bytes.fromhex('3e01cd9d2f' 'fac6d0ea31ad' 'cdac2f' 'fac8d0ea96d2' '00')   # OpenSRAM 1 ... CloseSRAM
    log.append('GivePoke: the box Pokémon gets the given item (0: none), SRAM opened (03:652B)')


def water_gun_learners(rom, sp, log):
    import build_phase122 as P122
    MV = P122.move_ids(); wg = MV['WATER_GUN']
    assert rom[WRAP_PTR + 2] == CODE_BANK
    wrap = fo(CODE_BANK, rom[WRAP_PTR] | rom[WRAP_PTR + 1] << 8)
    assert rom[wrap:wrap + 2] == b'\xd5\xfa' and rom[wrap + 5] == 0x21
    mt = fo(CODE_BANK, rom[wrap + 6] | rom[wrap + 7] << 8)
    ents = []
    while rom[mt]: ents.append(bytes(rom[mt:mt + 3])); mt += 3
    assert all(e[0] != wg for e in ents)
    lst = bytes(P122.red_learners('WATER_GUN')) + b'\xff'
    la = sp.here(CODE_BANK); sp.put(CODE_BANK, lst)
    ta = sp.put(CODE_BANK, b''.join(ents) + bytes([wg]) + w16(la) + b'\x00')
    rom[wrap + 6:wrap + 8] = w16(ta)
    log.append('tutor table + WATER_GUN (%d learners, Red TM12): %02X:%04X' % (len(lst) - 1, CODE_BANK, ta))
    return wg


def apply(rom, log):
    sp = Space(rom)
    f, n = bank_free_tail(rom, CODE_BANK); sp.set_area(CODE_BANK, f + 16, CODE_BANK * 0x4000 + 0x4000)
    givepoke_box_item(rom, log)
    wg = water_gun_learners(rom, sp, log)
    ITEM = load_consts(PC + '/constants/item_constants.asm')

    # ---- B2F: Red's hidden items; the Water Gun ball's script goes in the same bank
    me = map_events(rom, MTB2F); B = me.sb
    f, n = bank_free_tail(rom, B); sp.set_area(B, f + 16, B * 0x4000 + 0x4000)
    have = {(x, y) for y, x, t, r in me.bgs}
    for (x, y), it, fl in (((18, 12), 'MOON_STONE', HID_MOON_STONE), ((33, 9), 'ETHER', HID_ETHER)):
        assert (x, y) not in have
        me.bgs.append((y, x, 7, ('data', w16(fl) + bytes([ITEM[it]]))))
    a = Asm(sp.here(B)); a.bank = B
    # the 1F ball (reached by a farsjump from bank $7A)
    texts = {'wg_find': T('<PLAYER>は　わざマシンを　みつけた！<PARA>なかには　みずでっぽうが<LINE>はいっている！<PARA>'
                          'みずでっぽうを<LINE>おぼえさせますか？'),
             'wg_keep': T('<PLAYER>は　わざマシンを<LINE>そのまま　のこしておいた')}
    a.label('wgball'); a.opentext(); a.writetext('wg_find'); a.yesorno(); a.iffalse('wg_no')
    a.db(0x15, wg); a.special(SPECIAL_MOVE_TUTOR); a.ifequal(0, 'wg_ok')       # setval WATER_GUN ; MoveTutor
    a.label('wg_no'); a.writetext('wg_keep'); a.waitbutton(); a.closetext(); a.end()
    a.label('wg_ok'); a.closetext(); a.setevent(TM12_FLAG); a.disappear(0xFE); a.end()   # LAST_TALKED
    for k_, v in texts.items(): a.label(k_); a.raw(v)
    me.write(a, sp)
    base = a.base; blob = a.done(); assert sp.put(B, blob) == base
    me.install(a)
    wgball = a.labels['wgball']
    log.append('Mt. Moon B2F: hidden Moon Stone (18,12) flag %X, Ether (33,9) flag %X; events %02X:%04X'
               % (HID_MOON_STONE, HID_ETHER, B, base))

    # ---- 1F: the ball at (5, 32) -> script (a farsjump in bank $7A's tail)
    m1 = map_events(rom, MT1F); B1 = m1.sb
    a1 = m1.a; ev = parse_events(rom, B1, a1['events'])
    hit = [(p, o) for p, o in ev['objs'] if (o[2] - 4, o[1] - 4) == (5, 32)]
    assert len(hit) == 1; p, o = hit[0]
    assert o[0] == 0x54 and o[7] & 0x0F == 1 and (o[11] | o[12] << 8) == TM12_FLAG
    f, n = bank_free_tail(rom, B1); assert n >= 5, n
    t = f + 1; tr = 0x4000 + t % 0x4000
    rom[t:t + 4] = bytes([0x04, B]) + w16(wgball)                             # farsjump
    rom[p + 7] = o[7] & 0xF0                                                  # OBJECTTYPE_SCRIPT
    rom[p + 9:p + 11] = w16(tr)
    log.append('Mt. Moon 1F: Water Gun ball (5,32) -> %02X:%04X -> %02X:%04X' % (B1, tr, B, wgball))


if __name__ == '__main__':
    src, out = sys.argv[1:3]
    rom = bytearray(open(src, 'rb').read()); log = []
    apply(rom, log); fix_checksum(rom)
    open(out, 'wb').write(rom); print('\n'.join(log))
