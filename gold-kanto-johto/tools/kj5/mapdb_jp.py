"""the JP/MOD ROM's map headers and events by map id (group, number)"""
from lib import fo, attrs, parse_events
MGP = 0x94000                                     # MapGroupPointers (bank $25)
def header(rom, g, m):
    G = rom[MGP + 2 * (g - 1)] | rom[MGP + 2 * (g - 1) + 1] << 8
    return fo(0x25, G) + 9 * (m - 1)
def events(rom, g, m):
    at = attrs(rom, header(rom, g, m)); return parse_events(rom, at['scbank'], at['events'])
def coords(rom, g, m): return events(rom, g, m)['coords']
