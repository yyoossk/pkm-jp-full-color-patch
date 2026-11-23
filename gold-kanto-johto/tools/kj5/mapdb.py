"""キットの play/mapdb.DB の かわり（第127弾の diglett・gym_doors が 使う 所だけ）：maps[(g, m)] → attr（属性の 住所）・scbank・ev"""
from lib import attrs, parse_events
from mapdb_jp import header
class DB:
    def __init__(s, path):
        rom = open(path, 'rb').read(); s.maps = _Maps(rom)
class _Maps(dict):
    def __init__(s, rom): super().__init__(); s.rom = rom
    def __missing__(s, k):
        at = attrs(s.rom, header(s.rom, *k))
        v = dict(attr=at['attr_off'], scbank=at['scbank'], ev=parse_events(s.rom, at['scbank'], at['events']))
        s[k] = v; return v
