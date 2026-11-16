"""目の 前が まっくらに なった とき、まだ ポケモンセンターで 回復して いなければ
   赤と 同じく マサラタウンの 家の 前（SPAWN_PALLET、(5,6)）に もどる。
   銀は 自分の 部屋（SPAWN_HOME ＝ 2かい）に もどって いた。
   GetWhiteoutSpawn（$04:$6787）を 同じ 長さに 書きなおす（ld hl で 2バイト つめて、xor a → ld a, SPAWN_PALLET）。"""
import os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
from gsc import fo

OLD = bytes.fromhex('fa c1 d9 57 fa c2 d9 5f 3e 05 21 d2 53 cf 79 38 01 af ea 20 cf c9')
NEW = bytes.fromhex('21 c1 d9 56 23 5e'        # ld hl, wLastSpawnMapGroup / ld d,[hl] / inc hl / ld e,[hl]
                    '3e 05 21 d2 53 cf'        # farcall IsSpawnPoint
                    '79 38 02 3e 02'           # ld a,c / jr c,.yes / ld a, SPAWN_PALLET
                    'ea 20 cf c9 00')          # .yes ld [wDefaultSpawnpoint],a / ret
SPAWN_PALLET = 2


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    o = fo(4, 0x6787)
    assert rom[o:o + len(OLD)] == OLD and len(NEW) == len(OLD)
    rom[o:o + len(NEW)] = NEW
    log.append('まっくらに なった ときの 行き先：家の 中 → マサラタウンの 家の 前（04:6787）')
    return rom
