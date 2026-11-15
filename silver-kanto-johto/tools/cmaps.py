"""クリスタル版（完成 ROM）の マップを ぜんぶ 読んで、スクリプト・テキスト・動きなどの 使って いる ものを 集める"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gsc, cscript
from gsc import fo, r16

CMOD = os.environ.get('CMOD', '/home/claude/work/cmod.gbc')
CORIG = os.environ.get('CORIG', '/home/claude/work/crystal.gbc')
G26_JP = 13        # 日本版クリスタルの グループ26 の マップ数（英語版は 11）


class CMaps(gsc.Maps):
    """クリスタル版の マップの 表（グループ26 に 足された マップも）"""
    def __init__(s, rom):
        gsc.Maps.__init__(s, rom, gsc.PC + '/constants/map_constants.asm')
        g26 = fo(0x25, r16(rom, s.table + 2 * 25))
        n = len(s.groups[25][1])
        for i in range(n, G26_JP): s.hdr[(26, i + 1)] = g26 + 9 * i; s.name[(26, i + 1)] = 'JP26_%d' % (i + 1)
        i = G26_JP
        while True:
            o = g26 + 9 * i; h = rom[o:o + 9]
            if not (h[0] >= 0x25 and 0x4000 <= r16(rom, o + 3) < 0x8000 and h[2] < 8): break
            s.hdr[(26, i + 1)] = o; s.name[(26, i + 1)] = 'NEW26_%d' % (i + 1); i += 1
        s.count26 = i


def map_scripts(rom, bank, addr):
    """マップの スクリプトの ヘッダー：scene_scripts と callbacks"""
    o = fo(bank, addr); scenes = []; cbs = []
    n = rom[o]; o += 1
    for i in range(n): scenes.append(r16(rom, o)); o += 4
    n = rom[o]; o += 1
    for i in range(n): cbs.append((rom[o], r16(rom, o + 1))); o += 3
    return scenes, cbs, fo(bank, addr), o


def entries(M, k):
    """マップ k の スクリプトの 入り口を ぜんぶ（bank, addr, 種類）"""
    rom = M.rom; a = M.attributes(k); b = a['scripts_bank']; out = []
    scenes, cbs, so, se = map_scripts(rom, b, a['scripts'])
    for x in scenes: out.append((b, x, 'scene'))
    for t, x in cbs: out.append((b, x, 'callback%d' % t))
    ev = M.events(k)
    for c in ev['coords']: out.append((b, c[4] | c[5] << 8, 'coord'))
    for g in ev['bgs']:
        x, y, f, lo, hi = g; p = lo | hi << 8
        if f <= 4: out.append((b, p, 'bg'))                              # 読む・上・下・右・左
        elif f in (5, 6): out.append((b, r16(rom, fo(b, p) + 2), 'bgif'))  # IFSET / IFNOTSET：dw フラグ, dw スクリプト
    for ob in ev['objects']:
        typ = ob[7] & 0x0f; p = ob[9] | ob[10] << 8
        if typ == 0 and p: out.append((b, p, 'obj'))
        elif typ == 2:                                                     # トレーナー：dw フラグ, db グループ, db 番号, dw テキスト×3, dw スクリプト
            out.append((b, r16(rom, fo(b, p) + 10), 'trainer'))
    return out


if __name__ == '__main__':
    rom = open(CMOD, 'rb').read()
    M = CMaps(rom)
    print('グループ26 の マップ', M.count26)
