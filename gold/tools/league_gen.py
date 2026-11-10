# 16この バッジの あとの 四天王・ワタル・ライバルの 手持ち（src/league_parties.inc）を 作る
#   名前 → 番号は pokecrystal の constants（金・銀・クリスタル 共通の 番号）
#   python3 tools/league_gen.py [pokecrystal の フォルダ]
import sys, os, re
PC = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('POKECRYSTAL', '/home/claude/pokecrystal')
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src', 'league_parties.inc')

def consts(path, start=0):
    v, d = start, {}
    for l in open(os.path.join(PC, path), encoding='utf-8'):
        l = l.split(';')[0].strip()
        m = re.match(r'const_def\s*(\S*)', l)
        if m:
            v = int(m.group(1).replace('$', '0x'), 0) if m.group(1) else 0
            continue
        m = re.match(r'const\s+(\w+)', l)
        if m: d[m.group(1)] = v; v += 1; continue
        if l.startswith('const_skip'): v += 1
    return d
MON = consts('constants/pokemon_constants.asm')
MOVE = consts('constants/move_constants.asm')
ITEM = consts('constants/item_constants.asm')

# 1ぴき：(レベル, ポケモン, 持ち物 または None, わざ×4)
WILL = [
    (68, 'GIRAFARIG', None,          'PSYCHIC_M CRUNCH EARTHQUAKE THUNDERBOLT'),
    (68, 'JYNX',      None,          'BLIZZARD PSYCHIC_M LOVELY_KISS ICE_PUNCH'),
    (69, 'EXEGGUTOR', None,          'PSYCHIC_M GIGA_DRAIN SLEEP_POWDER EXPLOSION'),
    (69, 'SLOWBRO',   'LEFTOVERS',   'SURF PSYCHIC_M ICE_BEAM AMNESIA'),
    (70, 'ESPEON',    None,          'PSYCHIC_M SHADOW_BALL MORNING_SUN REFLECT'),
    (72, 'XATU',      'TWISTEDSPOON','PSYCHIC_M DRILL_PECK CONFUSE_RAY FUTURE_SIGHT'),
]
KOGA = [
    (68, 'ARIADOS',   None,          'SLUDGE_BOMB GIGA_DRAIN PSYCHIC_M BATON_PASS'),
    (68, 'VENOMOTH',  None,          'PSYCHIC_M SLUDGE_BOMB SLEEP_POWDER GIGA_DRAIN'),
    (69, 'TENTACRUEL',None,          'SURF SLUDGE_BOMB ICE_BEAM BARRIER'),
    (69, 'FORRETRESS','LEFTOVERS',   'EXPLOSION SPIKES EARTHQUAKE TOXIC'),
    (70, 'MUK',       None,          'SLUDGE_BOMB FIRE_BLAST THUNDERBOLT EXPLOSION'),
    (72, 'CROBAT',    'POISON_BARB', 'WING_ATTACK CONFUSE_RAY MEAN_LOOK TOXIC'),
]
BRUNO = [
    (68, 'HITMONTOP', None,          'TRIPLE_KICK MACH_PUNCH DIG DETECT'),
    (68, 'HITMONLEE', None,          'HI_JUMP_KICK MEGA_KICK EARTHQUAKE FORESIGHT'),
    (69, 'HITMONCHAN',None,          'ICE_PUNCH FIRE_PUNCH THUNDERPUNCH MACH_PUNCH'),
    (69, 'STEELIX',   'LEFTOVERS',   'IRON_TAIL EARTHQUAKE ROCK_SLIDE CRUNCH'),
    (70, 'HERACROSS', None,          'MEGAHORN EARTHQUAKE ROCK_SLIDE REVERSAL'),
    (72, 'MACHAMP',   'BLACKBELT_I', 'CROSS_CHOP EARTHQUAKE ROCK_SLIDE VITAL_THROW'),
]
KAREN = [
    (68, 'UMBREON',   'LEFTOVERS',   'FAINT_ATTACK CONFUSE_RAY MEAN_LOOK MOONLIGHT'),
    (68, 'VILEPLUME', None,          'SLUDGE_BOMB GIGA_DRAIN STUN_SPORE MOONLIGHT'),
    (69, 'SNEASEL',   None,          'FAINT_ATTACK SLASH ICY_WIND QUICK_ATTACK'),
    (69, 'MURKROW',   None,          'DRILL_PECK FAINT_ATTACK PURSUIT NIGHT_SHADE'),
    (70, 'GENGAR',    None,          'SHADOW_BALL THUNDERBOLT HYPNOSIS DREAM_EATER'),
    (72, 'HOUNDOOM',  'BLACKGLASSES','CRUNCH FLAMETHROWER SOLARBEAM SUNNY_DAY'),
]
LANCE = [
    (72, 'GYARADOS',  None,          'HYDRO_PUMP THUNDERBOLT ICE_BEAM HYPER_BEAM'),
    (72, 'KINGDRA',   None,          'HYDRO_PUMP DRAGONBREATH ICE_BEAM SMOKESCREEN'),
    (73, 'AERODACTYL',None,          'WING_ATTACK ROCK_SLIDE EARTHQUAKE HYPER_BEAM'),
    (73, 'CHARIZARD', None,          'FIRE_BLAST WING_ATTACK EARTHQUAKE SLASH'),
    (74, 'DRAGONITE', 'LEFTOVERS',   'OUTRAGE THUNDERBOLT FIRE_BLAST SAFEGUARD'),
    (76, 'DRAGONITE', 'DRAGON_FANG', 'OUTRAGE THUNDER BLIZZARD HYPER_BEAM'),
]
RIVAL_BASE = [
    (70, 'SNEASEL',   None,          'FAINT_ATTACK ICY_WIND SLASH SCREECH'),
    (71, 'CROBAT',    None,          'WING_ATTACK CONFUSE_RAY BITE TOXIC'),
    (70, 'MAGNETON',  None,          'THUNDERBOLT ZAP_CANNON LOCK_ON THUNDER_WAVE'),
    (72, 'GENGAR',    None,          'SHADOW_BALL PSYCHIC_M HYPNOSIS DESTINY_BOND'),
    (72, 'ALAKAZAM',  None,          'PSYCHIC_M RECOVER FIRE_PUNCH THUNDERPUNCH'),
]
RIVAL_ACE = {
    'MEGANIUM':   (75, 'MEGANIUM',   'LEFTOVERS',   'PETAL_DANCE EARTHQUAKE BODY_SLAM SYNTHESIS'),
    'TYPHLOSION': (75, 'TYPHLOSION', 'CHARCOAL',    'FIRE_BLAST EARTHQUAKE THUNDERPUNCH SWIFT'),
    'FERALIGATR': (75, 'FERALIGATR', 'MYSTIC_WATER','HYDRO_PUMP EARTHQUAKE ICE_BEAM SLASH'),
}
def rival(ace, down):
    return [(lv - down, m, it, mv) for lv, m, it, mv in RIVAL_BASE + [RIVAL_ACE[ace]]]

PARTIES = [
    ('WILL', WILL), ('KOGA', KOGA), ('BRUNO', BRUNO), ('KAREN', KAREN), ('LANCE', LANCE),
    # ライバル：1〜3 は オツキミやま、4〜6 は セキエイこうげん（1・4 メガニウム、2・5 バクフーン、3・6 オーダイル）
    ('RIVAL_1', rival('MEGANIUM', 3)), ('RIVAL_2', rival('TYPHLOSION', 3)), ('RIVAL_3', rival('FERALIGATR', 3)),
    ('RIVAL_4', rival('MEGANIUM', 0)), ('RIVAL_5', rival('TYPHLOSION', 0)), ('RIVAL_6', rival('FERALIGATR', 0)),
]
o = ['; 16この バッジの あとの 四天王・ワタル・ライバルの 手持ち（tools/league_gen.py で 作った もの）',
     '; 1ぴき：レベル, 種類, 持ち物, わざ×4（TRAINERTYPE_ITEM_MOVES）。数字は 金・銀・クリスタル 共通', '']
for name, party in PARTIES:
    assert len(party) == 6
    o.append(f'MACRO LG_PARTY_{name}')
    for lv, m, it, mv in party:
        mv = mv.split(); assert len(mv) == 4
        b = [lv, MON[m], ITEM[it] if it else 0] + [MOVE[x] for x in mv]
        o.append('\tdb ' + ', '.join(f'${x:02x}' for x in b) + f' ; Lv{lv} {m} {it or "-"} / {" ".join(mv)}')
    o += ['\tdb $ff', 'ENDM', '']
open(OUT, 'w', encoding='utf-8').write('\n'.join(o))
print(OUT)
