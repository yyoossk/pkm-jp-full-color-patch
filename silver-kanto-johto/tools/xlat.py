"""クリスタル（日本版）の 番号 → 銀（日本版）の 番号 の 読みかえ表
   名前は pret の pokecrystal / pokegold（英語版）から。日本版の ROM の 表と くらべて 確かめる。"""
import os, re
from gsc import fo, r16
REF = os.environ.get('PRETREF', '/home/claude/ref')


def consts(path, prefix=None):
    """const_def の 並びを 読む → {名前: 番号}"""
    d = {}; v = 0; step = 1
    for l in open(path, encoding='utf-8'):
        l = l.split(';')[0].strip()
        m = re.match(r'const_def\s*(\S*)\s*,?\s*(\S*)', l)
        if m and l.startswith('const_def'):
            a = m.group(1).rstrip(','); v = int(a.replace('$', '0x'), 0) if a else 0
            step = int(m.group(2)) if m.group(2) else 1; continue
        m = re.match(r'const_skip\s*(\d*)', l)
        if m and l.startswith('const_skip'): v += (int(m.group(1)) if m.group(1) else 1) * step; continue
        m = re.match(r'const_next\s+(\S+)', l)
        if m:
            try: v = int(m.group(1).replace('$', '0x'), 0)
            except ValueError: pass
            continue
        m = re.match(r'const\s+(\w+)', l)
        if m and (prefix is None or m.group(1).startswith(prefix)):
            d[m.group(1)] = v
        if m: v += step
    return d


def names(path, macro):
    """add_special Foo の 並び → [名前]"""
    out = []
    for l in open(path, encoding='utf-8'):
        m = re.match(r'\s*' + macro + r'\s+(\w+)', l)
        if m: out.append(m.group(1))
    return out


def classes(path):
    d = {}; v = 0
    for l in open(path, encoding='utf-8'):
        m = re.match(r'\s*trainerclass\s+(\w+)', l)
        if m: d[m.group(1)] = v; v += 1
    return d


def inv(d): return {v: k for k, v in d.items()}


class Tables:
    def __init__(s):
        C = REF + '/pokecrystal'; G = REF + '/pokegold'
        s.c_special = names(C + '/data/events/special_pointers.asm', 'add_special')
        s.g_special = names(G + '/data/events/special_pointers.asm', 'add_special')
        s.c_std = names(C + '/engine/events/std_scripts.asm', 'add_stdscript')
        s.g_std = names(G + '/engine/events/std_scripts.asm', 'add_stdscript')
        s.c_ev = consts(C + '/constants/event_flags.asm', 'EVENT_'); s.g_ev = consts(G + '/constants/event_flags.asm', 'EVENT_')
        s.c_eng = consts(C + '/constants/engine_flags.asm', 'ENGINE_'); s.g_eng = consts(G + '/constants/engine_flags.asm', 'ENGINE_')
        s.c_spr = consts(C + '/constants/sprite_constants.asm', 'SPRITE_'); s.g_spr = consts(G + '/constants/sprite_constants.asm', 'SPRITE_')
        s.c_mus = consts(C + '/constants/music_constants.asm', 'MUSIC_'); s.g_mus = consts(G + '/constants/music_constants.asm', 'MUSIC_')
        s.c_sfx = consts(C + '/constants/sfx_constants.asm', 'SFX_'); s.g_sfx = consts(G + '/constants/sfx_constants.asm', 'SFX_')
        s.c_item = consts(C + '/constants/item_constants.asm'); s.g_item = consts(G + '/constants/item_constants.asm')
        s.c_tc = classes(C + '/constants/trainer_constants.asm'); s.g_tc = classes(G + '/constants/trainer_constants.asm')
        s.c_lm = consts(C + '/constants/landmark_constants.asm'); s.g_lm = consts(G + '/constants/landmark_constants.asm')
        s.c_ts = consts(C + '/constants/tileset_constants.asm', 'TILESET_'); s.g_ts = consts(G + '/constants/tileset_constants.asm', 'TILESET_')

    @staticmethod
    def by_name(cd, gd, v, kind):
        n = inv(cd).get(v)
        if n is None or n not in gd: return None, n
        return gd[n], n
