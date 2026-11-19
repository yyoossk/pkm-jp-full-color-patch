#!/usr/bin/env python3
"""Phase 123: a user's report (2026-11-19) on the start of the game, and the Time Capsule items.
 1. A new game starts as in Red: Red's room in front of the game console (3,6), facing up, a Potion in the PC.
 2. Text lines too long for the window (19+ characters): Mom (after the Pokégear), the S.S. Anne / port sailors (x3),
    James in the Slowpoke Well.  The line breaks are moved (same bytes).
 3. Shigeru in Oak's lab before Oak comes: Red's 「なんだー　<PLAYER>か！／オーキドの　じいさんなら　いねーよ」
    (he said the line of the starter choice, 「へへーんだ！　おれは　おとな　だから…」, which is for after Oak comes).
 4. Oak on Pallet Town's north edge faces the player (up) while he talks (he faced right, his last step).
 5. The locked Viridian Gym door: the player faces the door (up) while reading (from the side he faced left).
 6. The follower after a ledge jump (also the Viridian Gym door's jump): it was put back at the player's left whatever
    side it came from (the follower code read wPlayerStepDirection, which is $FF once the player stands, as RIGHT);
    now it waits on the player's tile (hidden, as after a door) and comes out behind the player at the next step.
 7. Oak's lab: Red's aides (the girl and two scientists) with Red's lines.
 8. The catching demonstration: the old man's back picture stood 6 dots above the text box (bottom-aligned now).
 9. The items that only the Time Capsule gave in Crystal are held by wild Pokémon (item 1 = 23%, item 2 = 2%):
    Pikachu: Light Ball (2%, was Berry) / Abra, Kadabra: TwistedSpoon (2%) / Ditto: Metal Powder (2%) /
    Chansey: Lucky Punch (23%, Lucky Egg 2% stays) / Jigglypuff: Polkadot Bow (2%) / Machop: Brick Piece (2%) /
    Oddish: Gold Leaf (2%) / Bellsprout: Silver Leaf (2%) / Articuno, Zapdos, Moltres, Mewtwo: BrightPowder (23%).
10. Fly in Kanto: Crystal shows Kanto's map only once Indigo Plateau's flypoint is visited, else Johto's (in this MOD
    the whole Kanto story: Johto's map, a flight to Johto, or a crash with no Johto flypoint).  Now Pallet Town's
    flypoint (visited from the start), and Kanto's first flypoint is the cursor's start (not Indigo Plateau).
11. The stats screen: a second type (two rows under the first) was hidden by the friendship hearts (kit, row 8): the
    hearts go one row lower (row 9, above the experience box).
usage: build_phase123.py IN.gbc OUT.gbc OUT.ips
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from evedit import MapEvents
from jpchar import encode
from portlib import lz

PR = os.path.join(os.path.dirname(PC), 'pokered')
RED = SC + '/aka/Pocket Monsters - Aka (Japan) (SGB Enhanced).gb'


def expect(rom, o, hexs):
    b = bytes.fromhex(hexs.replace(' ', ''))
    assert rom[o:o + len(b)] == b, (hex(o), rom[o:o + len(b)].hex(' '), hexs)
    return b


def w16(v): return bytes([v & 0xFF, v >> 8])
def ga(o): return o % 0x4000 + (0x4000 if o >= 0x4000 else 0)


def main():
    src, outrom, outips = sys.argv[1:4]
    orig = open(JP_BASE, 'rb').read()
    rom = bytearray(open(src, 'rb').read())
    red = open(RED, 'rb').read()
    log = []
    free = {}
    def put(bank, code):
        if bank not in free: free[bank] = bank_free_tail(rom, bank)[0] + 2
        a = free[bank]; assert a + len(code) <= bank * 0x4000 + 0x4000 and not any(rom[a:a + len(code)]), hex(bank)
        rom[a:a + len(code)] = code; free[bank] += len(code); return ga(a)
    def here(bank):
        if bank not in free: free[bank] = bank_free_tail(rom, bank)[0] + 2
        return ga(free[bank])
    def put_asm(bank, a):
        blob = a.done(); assert put(bank, blob) == a.base; return a.base

    # 1. new game: SPAWN_HOME (3,3) -> (3,6); NewGame: farcall a routine (spawn point, facing up, PC Potion, map setup)
    expect(rom, 0x15346, '0d 04 03 03'); rom[0x15349] = 6
    o = 0x5B5A + 0x13; expect(rom, o, '3e 01 ea d8 c2 3e 00 ea 01 d0 3e f1 e0 9f c3 46 5e')
    W_SPAWN, W_SETUP, W_PC = 0xD001, 0xD44C, 0xD8E4         # wDefaultSpawnpoint, wPlayerSpriteSetupFlags, wNumPCItems
    code = bytes([0xAF, 0xEA]) + w16(W_SPAWN) + bytes([0x3E, 0x21, 0xEA]) + w16(W_SETUP) + \
        bytes([0x21]) + w16(W_PC) + bytes([0x3E, 1, 0x22, 0x3E, 0x12, 0x22, 0x3E, 1, 0x22, 0x3E, 0xFF, 0x77]) + \
        bytes([0x3E, 0xF1, 0xE0, 0x9F, 0xC9])
    h = put(0x2C, code)
    rom[o + 5:o + 14] = bytes([0x3E, 0x2C, 0x21]) + w16(h) + bytes([0xCF, 0, 0, 0])
    log.append('1 new game: (3,6) facing up, PC Potion (2C:%04X)' % h)

    # 2. lines too long: (offset, old text, new text) of the same length
    def retext(pre, old, new):
        pb = encode(pre[:-1]) + b'\x72'; a, b = pb + encode(old), pb + encode(new)
        assert len(a) == len(b) and rom.count(a) == 1, (pre, old, rom.count(a))
        o = rom.find(a); rom[o:o + len(a)] = b
    retext('おかあさん『', 'となりの　オーキドはかせが<LINE>あなたを　よんでたわよ', 'となりの<LINE>オーキドはかせが　あなたを<CONT>よんでたわよ')
    retext('ふなのり『', 'おお　きみが　<PLAYER>か！<LINE>', 'おお<LINE>きみが　<PLAYER>か！<CONT>')
    retext('ふなのり『', 'いあいぎりで　きを　きるには<LINE>ブルーバッジが　ひつようだよ',
           'いあいぎりで<LINE>きを　きるには　ブルーバッジが<CONT>ひつようだよ')
    retext('ふなのり『', 'きみが　<PLAYER>くんだね？<LINE>', 'きみが<LINE><PLAYER>くんだね？<CONT>')
    retext('コジロウ『', 'ジョウトの　ヤドンの　シッポは<LINE>ロケットだんが　いただくぜ！',
           'ジョウトの<LINE>ヤドンの　シッポは　ロケットだんが<CONT>いただくぜ！')
    log.append('2 five lines re-broken')

    # 3. Shigeru before Oak comes (62:4A0A writetext the starter-choice line)
    o = fo(0x62, 0x4A0A); expect(rom, o, '4c ec 4b 53 49 90')
    a = Asm(here(0x62))
    a.checkevent(0x0908); a.iffalse('early')
    a.writetext(0x4BEC); a.waitbutton(); a.closetext(); a.end()
    a.label('early'); a.writetext('t'); a.waitbutton(); a.closetext(); a.end()
    a.label('t'); a.raw(bytes([0x00, 0x39, 0x50, 0x00, 0x72]) + encode('なんだー　<PLAYER>か！<LINE>オーキドの　じいさんなら　いねーよ<DONE>'))
    s = put_asm(0x62, a)
    rom[o:o + 3] = bytes([0x03]) + w16(s)
    log.append('3 Shigeru before Oak 62:%04X' % s)

    # 4. Oak faces up (turnobject 00, DOWN -> turnobject 02, UP, after his walk)
    for ad in (0x4C45, 0x4C9D):
        o = fo(0x71, ad); expect(rom, o, '75 00 00 47 4c 9a 4d'); rom[o + 1] = 2; rom[o + 2] = 1
    # 5. the Viridian Gym door: turnobject PLAYER, UP first
    o = fo(0x6F, 0x4DFF); expect(rom, o, '47 4c 3e 51 53 49 68 00 0a 4e 90')
    a = Asm(here(0x6F))
    a.turnobject(0, 1); a.opentext(); a.writetext(0x513E); a.waitbutton(); a.closetext(); a.applymovement(0, 0x4E0A); a.end()
    s = put_asm(0x6F, a); rom[o:o + 3] = bytes([0x03]) + w16(s)
    log.append('4-5 Oak faces up, Viridian Gym door 6F:%04X' % s)

    # 6. the follower put back after the player stopped: wPlayerStepDirection $FF -> the player's tile (.place)
    o = 0x264662
    expect(rom, o, 'fa 21 d1 a7 20 03 25 18 0d 3d 20 03 24 18 07 3d 20 03 2c 18 01 2d e5 7a cd 9d 18')
    place = o + 22 + 17; expect(rom, place, 'fa d0 d4 3c c0 7a cd 9d 18')
    new = bytes([0xFA, 0x21, 0xD1, 0x3C, 0x28, place - (o + 6),
                 0x25, 0x3D, 0x28, 22 - 10,
                 0x24, 0x24, 0x3D, 0x28, 22 - 15,
                 0x25, 0x2C, 0x3D, 0x28, 22 - 20,
                 0x2D, 0x2D])
    assert len(new) == 22
    rom[o:o + 22] = new
    log.append('6 follower: standing player -> waits on the player\'s tile')

    # 7. Oak's lab: Red's girl and two scientists
    def red_text(off):
        e = red.index(b'\x57', off); return bytes(red[off:e + 1])
    girl = red_text(0x1D0D3); sci = red_text(0x1D584)
    assert girl.startswith(b'\x00') and encode('そんけい') in girl and encode('じょしゅ') in sci
    me = MapEvents(rom, 'OaksLab')
    a = Asm(here(0x62)); a.bank = 0x62
    me.add_object(0x28, 1, 9, 0x04, 'girl', rng=0x10)
    me.add_object(0x3C, 2, 10, 0x06, 'sci')
    me.add_object(0x3C, 8, 10, 0x06, 'sci')
    a.label('girl'); a.jumptextfaceplayer('tgirl')
    a.label('sci'); a.jumptextfaceplayer('tsci')
    a.label('tgirl'); a.raw(girl); a.label('tsci'); a.raw(sci)
    me.write(a, None)
    s = put_asm(0x62, a); me.install(a)
    log.append('7 Oak\'s lab aides: events 62:%04X' % s)

    # 8. the old man's back picture, bottom-aligned
    from PIL import Image
    im = Image.open(PR + '/gfx/battle/oldmanb.png').convert('L')
    big = im.resize((48, 48), Image.NEAREST)
    px0 = big.load(); rows = [y for y in range(48) if any(px0[x, y] < 200 for x in range(48))]
    sh = 47 - rows[-1]
    img = Image.new('L', (48, 48), 255); img.paste(big.crop((0, 0, 48, 48 - sh)), (0, sh)); px = img.load()
    data = bytearray()
    for tx in range(6):
        for ty in range(6):
            for r in range(8):
                lo_ = hi_ = 0
                for c in range(8):
                    v = 3 - px[8 * tx + c, 8 * ty + r] // 85
                    lo_ |= (v & 1) << (7 - c); hi_ |= (v >> 1) << (7 - c)
                data += bytes([lo_, hi_])
    st = 0x3FFB8; expect(rom, st + 20, '06 70 21 40 40 af c9')
    pic = put(0x70, lz(bytes(data)))
    rom[st + 23:st + 25] = w16(pic)
    log.append('8 old man back picture: %d dots lower (70:%04X)' % (sh, pic))

    # 9. wild held items (base stats: item 1 at +11, item 2 at +12)
    BASE = 0x514BA
    assert rom[BASE:BASE + 7] == bytes([1, 45, 49, 49, 45, 65, 65])
    LIGHT_BALL, TWISTEDSPOON, METAL_POWDER, LUCKY_PUNCH, POLKADOT_BOW, BRICK_PIECE, GOLD_LEAF, SILVER_LEAF, BRIGHTPOWDER = \
        0xA3, 0x60, 0x23, 0x1E, 0xAA, 0xB4, 0x4B, 0x3C, 0x03
    HELD = {25: (None, LIGHT_BALL, (0, 0xAD)), 63: (None, TWISTEDSPOON, (0, 0)), 64: (None, TWISTEDSPOON, (0, 0)),
            132: (None, METAL_POWDER, (0, 0)), 113: (LUCKY_PUNCH, None, (0, 0x7E)), 39: (None, POLKADOT_BOW, (0, 0)),
            66: (None, BRICK_PIECE, (0, 0)), 43: (None, GOLD_LEAF, (0, 0)), 69: (None, SILVER_LEAF, (0, 0)),
            144: (BRIGHTPOWDER, None, (0, 0)), 145: (BRIGHTPOWDER, None, (0, 0)), 146: (BRIGHTPOWDER, None, (0, 0)),
            150: (BRIGHTPOWDER, None, (0, 0x98))}
    for dex, (i1, i2, was) in HELD.items():
        o = BASE + 32 * (dex - 1); assert rom[o] == dex and (rom[o + 11], rom[o + 12]) == was, (dex, rom[o + 11:o + 13].hex())
        if i1 is not None: rom[o + 11] = i1
        if i2 is not None: rom[o + 12] = i2
    log.append('9 wild held items for %d kinds' % len(HELD))

    # 10. Fly: HasVisitedSpawn SPAWN_INDIGO -> SPAWN_PALLET; the start cursor = KANTO_FLYPOINT
    o = 0x91DE1; expect(rom, o, 'f5 0e 0d cd 6a 5d a7 28 18 3e 0c ea 05 d0 3e 17 ea 06 d0 ea 02 d0')
    rom[o + 2] = 0x02
    rom[o + 9:o + 22] = bytes.fromhex('3e 0c ea 05 d0 ea 02 d0 3e 17 ea 06 d0'.replace(' ', ''))
    # 11. the hearts: hlcoord 9, 8 -> 9, 9
    expect(rom, 0x25AA23, '21 49 c5'); expect(rom, 0x25AA48, '21 4e c5')
    rom[0x25AA24] = 0x5D; rom[0x25AA49] = 0x62
    log.append('10-11 Kanto fly map, hearts row 9')

    fix_checksum(rom)
    open(outrom, 'wb').write(rom)
    o2 = orig + bytes(len(rom) - len(orig))
    p = ips(o2, bytes(rom))
    p = p[:-3] + (len(rom) - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + rom[-1:] + b'EOF'
    open(outips, 'wb').write(p)
    print('\n'.join(log))


if __name__ == '__main__':
    main()
