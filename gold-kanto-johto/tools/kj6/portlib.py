"""Porting helpers: Gen I (Pikachu full-color hack) tilesets/maps -> JP Crystal."""
import os, re, subprocess, tempfile, pickle
from lib import *
from jpchar import encode, decode

PY = SC + '/ref/pokeyellow'
LZ = PC + '/tools/lzcompress'
PKFC_PALMAPS = 0xEC200
T_TILESETS = 0x4D405; N_TILESETS = 33; R_TILESETS = [0x2CFC]
LSMP = 0x493FE                  # LoadSpecialMapPalette (bank 0x12)
HOUSEPAL_CALL = 0x49444         # LoadHousePalette: 3e 05 11 [wBGPals1] 21 .. 01 40 00 cd [FarCopyWRAM] c9
GROUP26_END = 0x94DEA           # end of the last map group's headers (bank 0x25)
G26 = 26; G26_COUNT = 13

COLL_FLOOR, COLL_WALL, COLL_TALL_GRASS, COLL_WATER = 0x00, 0x07, 0x18, 0x29
COLL_CARPET = {'down': 0x70, 'left': 0x76, 'up': 0x78, 'right': 0x7E}
COLL_STAIRCASE, COLL_DOOR, COLL_WARP_PANEL = 0x7A, 0x71, 0x7C


def lz(data):
    with tempfile.TemporaryDirectory() as d:
        open(d + '/a', 'wb').write(data)
        subprocess.run([LZ, d + '/a', d + '/b'], check=True, stdout=subprocess.DEVNULL)
        return open(d + '/b', 'rb').read()


def gen1_coll(name):
    src = open(PY + '/data/tilesets/collision_tile_ids.asm').read()
    m = re.search(name + r'_Coll::(?:\s*\n\s*\w+_Coll::)*\s*\n\s*coll_tiles\s*([^\n]*)', src)
    return set(int(x.strip().lstrip('$'), 16) for x in m.group(1).split(',') if x.strip())


def gen1_warp_tiles(name):
    src = open(PY + '/data/tilesets/warp_tile_ids.asm').read()
    out = set(); on = False
    for l in src.split('\n'):
        s = l.split(';')[0].strip()
        if s.startswith('.' + name + 'WarpTileIDs:'):
            on = True; continue
        if on:
            if s.startswith('.') and s.endswith(':'):
                continue
            m = re.match(r'(warp_tiles|db)\s+(.*)', s)
            if m:
                out |= set(int(x.strip().lstrip('$'), 16) for x in m.group(2).split(',') if x.strip() and x.strip() != '-1')
                if m.group(1) == 'warp_tiles':
                    break
    return out


class Tileset:
    def __init__(s, name, gen1_index, bst, dump_pkl, water=None, grass=None):
        s.name = name
        d = pickle.load(open(dump_pkl, 'rb'))
        s.gfx_raw = d['t0'][0x1000:0x1600]           # tiles $00-$5F at $9000
        pals = bytes.fromhex(d['pals'].split()[0][3:])
        s.pals = pals[:64]
        s.blocks = open(PY + '/gfx/blocksets/' + bst, 'rb').read()
        s.nblocks = len(s.blocks) // 16
        pm = open(SC + '/pkfc/pkfc.gbc', 'rb').read()[PKFC_PALMAPS + 0x100 * gen1_index:][:0x60]
        s.palmap = bytes(((pm[2 * i + 1] & 7) << 4) | (pm[2 * i] & 7) for i in range(0x30)) + b'\xff' * 16 + \
            bytes(((8 | (pm[2 * i + 1] & 7)) << 4) | (8 | (pm[2 * i] & 7)) for i in range(0x30))
        s.passable = gen1_coll(name)
        s.warp_tiles = gen1_warp_tiles(name)
        s.water = water; s.grass = grass
        s.coll = bytearray()
        for b in range(s.nblocks):
            t = s.blocks[16 * b:16 * b + 16]
            for (r, c) in ((1, 0), (1, 2), (3, 0), (3, 2)):     # TL, TR, BL, BR quadrants: bottom-left tile
                tile = t[r * 4 + c]
                if s.water is not None and tile == s.water:
                    v = COLL_WATER
                elif s.grass is not None and tile == s.grass:
                    v = COLL_TALL_GRASS
                elif tile in s.passable:
                    v = COLL_FLOOR
                else:
                    v = COLL_WALL
                s.coll.append(v)

    def quad_tile(s, block, q):
        r, c = ((1, 0), (1, 2), (3, 0), (3, 2))[q]
        return s.blocks[16 * block + r * 4 + c]


class MapPort:
    def __init__(s, name, tileset, w, h, blk_file):
        s.name = name; s.ts = tileset; s.w = w; s.h = h
        s.blk = open(PY + '/maps/' + blk_file, 'rb').read()
        assert len(s.blk) == w * h, (name, len(s.blk), w * h)

    def block_at(s, x, y):
        return s.blk[(y // 2) * s.w + (x // 2)], (y % 2) * 2 + (x % 2)


class Space:
    """allocator for free areas of the ROM"""
    def __init__(s, rom):
        s.rom = rom; s.cur = {}

    def set_area(s, bank, start_off, end_off):
        s.cur[bank] = [start_off, end_off]

    def put(s, bank, data):
        a, e = s.cur[bank]
        assert a + len(data) <= e, ('bank full', hex(bank), len(data))
        s.rom[a:a + len(data)] = data
        s.cur[bank][0] += len(data)
        return 0x4000 + a % 0x4000 if bank else a

    def here(s, bank):
        return 0x4000 + s.cur[bank][0] % 0x4000


def border_of(mapname):
    t = open(PY + '/data/maps/objects/%s.asm' % mapname, encoding='utf-8').read()
    return int(re.search(r'db \$([0-9a-fA-F]+) ; border block', t).group(1), 16)
