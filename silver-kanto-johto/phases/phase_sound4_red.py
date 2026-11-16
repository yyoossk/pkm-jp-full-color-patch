"""カントーの マップの 曲を 全部 赤と 同じに。
   どの マップが 赤の どの マップか：赤の .blk と ブロックが 同じ マップ・同じ 名前の マップを 足がかりに、
   赤の ワープ（data/maps/objects）と こちらの ワープの 座標を くらべて たどった（/home/claude/mus/prop.py）。
   その 赤の マップの 曲（data/maps/songs.asm）を：
   ・金銀に 同じ 曲が ある もの → その 曲（1ばんどうろ・3ばんどうろ・12ばんどうろ・トキワ・タマムシ・クチバ・シオン・
     マサラ・ジム・ポケモンセンター・セキエイ・ゲームコーナー・おつきみやま（赤の Dungeon3））
   ・ない もの → 赤フルカラーの 曲を tools/gen1audio.py で 変えて 新しい 番号に：
     $63 ハナダ（Cities2）$65 グレン $66 サントアンヌ $67 サファリ $68 24・25ばんどうろ（Routes2）$69 研究所
     $6A ロケット団アジト・発電所・ハナダの どうくつ（Dungeon1）$6B ポケモン屋敷 $6C ポケモンタワー $6D シルフ
     （$64 は MUSIC_MAHOGANY_MART で 使えない）。トキワのもり（Dungeon2）は $52（phase_sound2_forest）。
   曲の 番号を ふやす しくみ：$3A の 曲の 表を 読む 所（$4B39 の call）を、$5D 以上なら $F1 の 関数を farcall し、
   $F1 の 表（$5D〜$6D）から 3バイトを WRAM $C6FC（wUnusedMapBuffer の 使われて いない 所）に 写して その 場所を 返す 形に。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
from gsc import fo, r16
from gen1audio import Song

AKAFC = os.environ.get('AKAFC', '/home/claude/in/aka/akafc.gbc')
AB, MUSIC, FREE, CALL = 0x3A, 0x506E, 0x7FB7, 0x4B39
DB, TB = 0xF0, 0xF1                     # 曲の データ / 表と 関数
BUF = 0xC6FC
FIRST, LAST = 0x5D, 0x6D
RED = {2: 0x6F31, 0x1F: 0x6EC2}          # 赤フルカラーの 音の バンクの 見出しの はじめ（SFX_Headers_N）
KITS = {0: {i: i for i in range(1, 13)}, 1: {i: i - 7 for i in range(8, 20)}}
# 曲番号: (赤の バンク, 見出しの 位置（はじめから）, ドラムの 組)
NEW = {0x63: ('CITIES2', 2, 0x252, 0), 0x65: ('CINNABAR', 2, 0x264, 0), 0x66: ('SS_ANNE', 2, 0x285, 0),
       0x67: ('SAFARI_ZONE', 2, 0x2AC, 0), 0x68: ('ROUTES2', 2, 0x2CA, 0),
       0x69: ('OAKS_LAB', 0x1F, 0x264, 0), 0x6A: ('DUNGEON1', 0x1F, 0x29D, 1),
       0x6B: ('CINNABAR_MANSION', 0x1F, 0x2C1, 1), 0x6C: ('POKEMON_TOWER', 0x1F, 0x2CD, 0),
       0x6D: ('SILPH_CO', 0x1F, 0x2D6, 0)}
GS = {'ROUTES1': 2, 'ROUTES3': 3, 'ROUTES4': 4, 'CITIES1': 21, 'CELADON': 22, 'VERMILION': 62, 'LAVENDER': 14,
      'PALLET_TOWN': 28, 'GYM': 27, 'POKECENTER': 9, 'INDIGO_PLATEAU': 70, 'GAME_CORNER': 18, 'DUNGEON2': 0x52,
      'DUNGEON3': 16}
GS.update({v[0]: k for k, v in NEW.items()})
# (グループ, 番号, 今の 曲, 赤の マップ, 赤の 曲)
MAPS = [
    (3, 75, 16, 'DIGLETTS_CAVE', 'DUNGEON2'),
    (6, 8, 21, 'CINNABAR_ISLAND', 'CINNABAR'),
    (7, 7, 21, 'CERULEAN_MART', 'POKECENTER'),
    (7, 10, 21, 'POWER_PLANT', 'DUNGEON1'),
    (7, 11, 21, 'BILLS_HOUSE', 'CITIES2'),
    (7, 15, 3, 'ROUTE_24', 'ROUTES2'),
    (7, 16, 3, 'ROUTE_25', 'ROUTES2'),
    (7, 17, 21, 'CERULEAN_CITY', 'CITIES2'),
    (12, 9, 62, 'VERMILION_MART', 'POKECENTER'),
    (13, 6, 29, 'OAKS_LAB', 'OAKS_LAB'),
    (14, 5, 21, 'PEWTER_MART', 'POKECENTER'),
    (15, 9, 62, 'VERMILION_DOCK', 'SS_ANNE'),
    (17, 5, 22, 'FUCHSIA_CITY', 'CITIES2'),
    (17, 6, 22, 'FUCHSIA_MART', 'POKECENTER'),
    (17, 7, 22, 'FUCHSIA_MEETING_ROOM', 'CITIES2'),
    (17, 12, 22, 'WARDENS_HOUSE', 'CITIES2'),
    (18, 9, 14, 'NAME_RATERS_HOUSE', 'CITIES2'),
    (18, 10, 14, 'LAVENDER_MART', 'POKECENTER'),
    (18, 14, 21, 'ROUTE_12_SUPER_ROD_HOUSE', 'CELADON'),
    (23, 1, 15, 'ROUTE_2', 'ROUTES1'),
    (23, 8, 21, 'VIRIDIAN_MART', 'POKECENTER'),
    (23, 12, 15, 'ROUTE_2_GATE', 'CITIES1'),
    (23, 13, 70, 'ROUTE_22_GATE', 'DUNGEON2'),
    (25, 5, 21, 'SAFFRON_MART', 'POKECENTER'),
    (25, 10, 21, 'SILPH_CO_1F', 'SILPH_CO'),
    (26, 12, 14, 'POKEMON_TOWER_1F', 'POKEMON_TOWER'),
    (26, 13, 14, 'POKEMON_TOWER_2F', 'POKEMON_TOWER'),
    (26, 14, 14, 'POKEMON_TOWER_3F', 'POKEMON_TOWER'),
    (26, 15, 14, 'POKEMON_TOWER_4F', 'POKEMON_TOWER'),
    (26, 16, 14, 'POKEMON_TOWER_5F', 'POKEMON_TOWER'),
    (26, 17, 14, 'POKEMON_TOWER_6F', 'POKEMON_TOWER'),
    (26, 18, 14, 'POKEMON_TOWER_7F', 'POKEMON_TOWER'),
    (26, 19, 72, 'ROCKET_HIDEOUT_B1F', 'DUNGEON1'),
    (26, 20, 72, 'ROCKET_HIDEOUT_B2F', 'DUNGEON1'),
    (26, 21, 72, 'ROCKET_HIDEOUT_B3F', 'DUNGEON1'),
    (26, 22, 72, 'ROCKET_HIDEOUT_B4F', 'DUNGEON1'),
    (26, 23, 72, 'ROCKET_HIDEOUT_ELEVATOR', 'DUNGEON1'),
    (26, 24, 21, 'SILPH_CO_2F', 'SILPH_CO'),
    (26, 25, 21, 'SILPH_CO_3F', 'SILPH_CO'),
    (26, 26, 21, 'SILPH_CO_4F', 'SILPH_CO'),
    (26, 27, 21, 'SILPH_CO_5F', 'SILPH_CO'),
    (26, 28, 21, 'SILPH_CO_6F', 'SILPH_CO'),
    (26, 29, 21, 'SILPH_CO_7F', 'SILPH_CO'),
    (26, 30, 21, 'SILPH_CO_8F', 'SILPH_CO'),
    (26, 31, 21, 'SILPH_CO_9F', 'SILPH_CO'),
    (26, 32, 21, 'SILPH_CO_10F', 'SILPH_CO'),
    (26, 33, 21, 'SILPH_CO_11F', 'SILPH_CO'),
    (26, 34, 21, 'SILPH_CO_ELEVATOR', 'SILPH_CO'),
    (26, 38, 62, 'VERMILION_DOCK', 'SS_ANNE'),
    (26, 39, 62, 'SS_ANNE_1F', 'SS_ANNE'),
    (26, 40, 62, 'SS_ANNE_2F', 'SS_ANNE'),
    (26, 41, 62, 'SS_ANNE_3F', 'SS_ANNE'),
    (26, 42, 62, 'SS_ANNE_B1F', 'SS_ANNE'),
    (26, 43, 62, 'SS_ANNE_BOW', 'SS_ANNE'),
    (26, 44, 62, 'SS_ANNE_KITCHEN', 'SS_ANNE'),
    (26, 45, 62, 'SS_ANNE_CAPTAINS_ROOM', 'SS_ANNE'),
    (26, 46, 62, 'SS_ANNE_1F_ROOMS', 'SS_ANNE'),
    (26, 47, 62, 'SS_ANNE_2F_ROOMS', 'SS_ANNE'),
    (26, 48, 62, 'SS_ANNE_2F_ROOMS', 'SS_ANNE'),
    (26, 49, 21, 'BILLS_HOUSE', 'CITIES2'),
    (26, 51, 9, 'CINNABAR_LAB', 'CINNABAR'),
    (26, 52, 9, 'CINNABAR_LAB_TRADE_ROOM', 'CINNABAR'),
    (26, 53, 9, 'CINNABAR_LAB_METRONOME_ROOM', 'CINNABAR'),
    (26, 54, 9, 'CINNABAR_LAB_FOSSIL_ROOM', 'CINNABAR'),
    (26, 55, 67, 'POKEMON_MANSION_1F', 'CINNABAR_MANSION'),
    (26, 56, 67, 'POKEMON_MANSION_2F', 'CINNABAR_MANSION'),
    (26, 57, 67, 'POKEMON_MANSION_3F', 'CINNABAR_MANSION'),
    (26, 58, 67, 'POKEMON_MANSION_B1F', 'CINNABAR_MANSION'),
    (26, 59, 9, 'CINNABAR_GYM', 'GYM'),
    (26, 60, 21, 'POWER_PLANT', 'DUNGEON1'),
    (26, 66, 79, 'VICTORY_ROAD_1F', 'DUNGEON3'),
    (26, 67, 79, 'VICTORY_ROAD_2F', 'DUNGEON3'),
    (26, 68, 79, 'VICTORY_ROAD_3F', 'DUNGEON3'),
    (26, 70, 21, 'CERULEAN_TRASHED_HOUSE', 'CITIES2'),
    (26, 71, 21, 'CERULEAN_TRADE_HOUSE', 'CITIES2'),
    (26, 72, 21, 'BIKE_SHOP', 'CITIES2'),
    (26, 74, 79, 'CERULEAN_CAVE_1F', 'DUNGEON1'),
    (26, 75, 79, 'CERULEAN_CAVE_2F', 'DUNGEON1'),
    (26, 76, 79, 'CERULEAN_CAVE_B1F', 'DUNGEON1'),
    (26, 79, 15, 'ROUTE_2_GATE', 'CITIES1'),
    (26, 81, 15, 'VIRIDIAN_FOREST_SOUTH_GATE', 'CITIES1'),
    (26, 83, 15, 'VIRIDIAN_FOREST_NORTH_GATE', 'CITIES1'),
    (26, 85, 22, 'SAFARI_ZONE_GATE', 'CITIES2'),
    (26, 86, 35, 'SAFARI_ZONE_CENTER', 'SAFARI_ZONE'),
    (26, 87, 22, 'SAFARI_ZONE_CENTER_REST_HOUSE', 'SAFARI_ZONE'),
    (26, 88, 35, 'SAFARI_ZONE_EAST', 'SAFARI_ZONE'),
    (26, 89, 22, 'SAFARI_ZONE_EAST_REST_HOUSE', 'SAFARI_ZONE'),
    (26, 90, 35, 'SAFARI_ZONE_NORTH', 'SAFARI_ZONE'),
    (26, 91, 22, 'SAFARI_ZONE_NORTH_REST_HOUSE', 'SAFARI_ZONE'),
    (26, 92, 35, 'SAFARI_ZONE_WEST', 'SAFARI_ZONE'),
    (26, 93, 22, 'SAFARI_ZONE_WEST_REST_HOUSE', 'SAFARI_ZONE'),
    (26, 94, 22, 'SAFARI_ZONE_SECRET_HOUSE', 'SAFARI_ZONE'),
    (26, 99, 3, 'ROUTE_6_GATE', 'CITIES1'),
    (26, 100, 3, 'ROUTE_7_GATE', 'CITIES1'),
    (26, 101, 3, 'ROUTE_8_GATE', 'CITIES1'),
    (26, 102, 4, 'ROUTE_11_GATE_1F', 'VERMILION'),
    (26, 103, 4, 'ROUTE_11_GATE_2F', 'VERMILION'),
    (26, 104, 4, 'ROUTE_12_GATE_1F', 'CITIES1'),
    (26, 105, 4, 'ROUTE_12_GATE_2F', 'CITIES1'),
    (26, 106, 4, 'ROUTE_15_GATE_1F', 'CITIES1'),
    (26, 107, 4, 'ROUTE_15_GATE_2F', 'CITIES1'),
    (26, 109, 4, 'ROUTE_16_GATE_1F', 'CITIES1'),
    (26, 110, 4, 'ROUTE_16_GATE_2F', 'CITIES1'),
    (26, 112, 4, 'ROUTE_18_GATE_1F', 'CITIES1'),
    (26, 113, 4, 'ROUTE_18_GATE_2F', 'CITIES1'),
    (26, 116, 62, 'VERMILION_OLD_ROD_HOUSE', 'CITIES2'),
    (26, 117, 22, 'FUCHSIA_BILLS_GRANDPAS_HOUSE', 'CITIES2'),
    (26, 118, 22, 'FUCHSIA_GOOD_ROD_HOUSE', 'CITIES2'),
    (26, 124, 22, 'CELADON_MART_1F', 'POKECENTER'),
    (26, 125, 22, 'CELADON_MART_2F', 'POKECENTER'),
    (26, 126, 22, 'CELADON_MART_3F', 'POKECENTER'),
    (26, 127, 22, 'CELADON_MART_4F', 'POKECENTER'),
    (26, 128, 22, 'CELADON_MART_5F', 'POKECENTER'),
    (26, 129, 22, 'CELADON_MART_ROOF', 'POKECENTER'),
    (26, 130, 22, 'CELADON_MART_ELEVATOR', 'POKECENTER'),
    (26, 137, 3, 'UNDERGROUND_PATH_ROUTE_5', 'CITIES1'),
    (26, 138, 3, 'UNDERGROUND_PATH_ROUTE_6', 'CITIES1'),
    (26, 139, 3, 'UNDERGROUND_PATH_ROUTE_7', 'CITIES1'),
    (26, 140, 3, 'UNDERGROUND_PATH_ROUTE_8', 'CITIES1'),
    (26, 141, 16, 'UNDERGROUND_PATH_NORTH_SOUTH', 'ROUTES1'),
    (26, 142, 16, 'UNDERGROUND_PATH_WEST_EAST', 'ROUTES1'),
]


def w(v): return bytes([v & 0xFF, v >> 8])


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    F = open(AKAFC, 'rb').read()
    assert not any(rom[fo(DB, 0x4000):fo(DB, 0x8000)]) and not any(rom[fo(TB, 0x4000):fo(TB, 0x8000)])
    # 1. 今の 足した 表（$5D〜$62）
    o = fo(AB, CALL); assert rom[o] == 0xCD and rom[o + 3:o + 6] == b'\0\0\0'
    mh = r16(rom, o + 1)
    m = fo(AB, mh); assert rom[m:m + 4] == bytes([0x21, MUSIC & 0xFF, MUSIC >> 8, 0x7B])
    old_tab = r16(rom, m + 9) + 3 * FIRST
    assert old_tab == FREE
    ext = [bytes(rom[fo(AB, FREE) + 3 * i:fo(AB, FREE) + 3 * i + 3]) for i in range(0x63 - FIRST)]
    none = bytes(rom[fo(AB, MUSIC):fo(AB, MUSIC) + 3])
    # 2. 赤の 曲を 変える
    a = 0x4000; tab = {}
    for mid, (nm, bank, off, kit) in NEW.items():
        hdr = RED[bank] + off
        h0 = F[fo(bank, hdr)]; assert h0 & 0x3F == 0 and (h0 >> 6) in (2, 3), (nm, hex(h0))
        s = Song(F, bank, hdr, KITS[kit], kit)
        h, data = s.build(a); assert a + len(data) <= 0x8000, nm
        rom[fo(DB, a):fo(DB, a) + len(data)] = data; a += len(data)
        tab[mid] = bytes([DB]) + w(h)
    # 3. $F1：表と 関数
    T = 0x4000
    for i in range(FIRST, LAST + 1):
        e = ext[i - FIRST] if i < 0x63 else tab.get(i, none)
        rom[fo(TB, T) + 3 * (i - FIRST):fo(TB, T) + 3 * (i - FIRST) + 3] = e
    FN = 0x4100
    fn = bytes([0x7B, 0xD6, FIRST,             # ld a,e / sub FIRST
                0x6F, 0x26, 0x00, 0x5D, 0x54,  # ld l,a / ld h,0 / ld e,l / ld d,h
                0x29, 0x19,                    # add hl,hl / add hl,de
                0x11]) + w(T) + bytes([0x19,   # ld de,T / add hl,de
                0x11]) + w(BUF) + bytes([      # ld de,BUF
                0x2A, 0x12, 0x13, 0x2A, 0x12, 0x13, 0x7E, 0x12,
                0x21]) + w(BUF) + bytes([0xC9])
    rom[fo(TB, FN):fo(TB, FN) + len(fn)] = fn
    # 4. $3A：読む 所
    disp = bytes([0x7B, 0xFE, FIRST, 0x30, (mh - (FREE + 5)) & 0xFF,
                  0x21, MUSIC & 0xFF, MUSIC >> 8, 0x19, 0x19, 0x19, 0xC9])
    assert 0 < mh - (FREE + 5) < 0x80 and len(disp) <= 3 * (0x63 - FIRST)
    rom[fo(AB, FREE):fo(AB, FREE) + 3 * (0x63 - FIRST)] = disp + bytes(3 * (0x63 - FIRST) - len(disp))
    stub = bytes([0x3E, TB, 0x21]) + w(FN) + bytes([0xCF, 0xC9])
    rom[m:m + 15] = stub + bytes(15 - len(stub))
    rom[o + 1:o + 3] = w(FREE)
    # 5. マップの 曲
    gt = fo(0x25, 0x40ED); n = 0
    for g, mm, old, rn, rs in MAPS:
        hp = fo(0x25, r16(rom, gt + 2 * (g - 1))) + 9 * (mm - 1)
        assert rom[hp + 6] == old, (g, mm, rom[hp + 6], old)
        rom[hp + 6] = GS[rs]; n += 1
    log.append('カントーの 曲を 赤と 同じに：%d マップ。赤の 曲 %d つを $%02X に（%d バイト）、曲の 表を $%02X に のばした'
               % (n, len(NEW), DB, a - 0x4000, TB))
    return rom
