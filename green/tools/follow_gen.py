"""連れ歩きの データを 作る（キットの 絵と色 と、緑の ROM の 手持ちの 色から）
   python3 tools/follow_gen.py キットの「絵と色」フォルダ 組んだ緑の.gbc pokered の ディレクトリ"""
import sys, os, re
K, ROM, PR = sys.argv[1:4]
OUT = os.path.join(os.path.dirname(__file__), '..', 'patches', 'follow')
mask = open(os.path.join(K, 'follow_icon', 'mask.bin'), 'rb').read()
for part in range(4):                       # 1 バンク 40 匹
    g = b''; m = b''
    for n in range(part * 40, min(151, part * 40 + 40)):
        g += open(os.path.join(K, 'follow_icon', '%03d.2bpp' % n), 'rb').read()
        m += mask[n * 384:(n + 1) * 384]
    open(os.path.join(OUT, 'gfx%d.bin' % part), 'wb').write(g)
    open(os.path.join(OUT, 'mask%d.bin' % part), 'wb').write(m)
# 手持ちの アイコンの 色（緑の 20:58c8 + ずかん番号 × 8：白・色1・色2・黒）
r = open(ROM, 'rb').read(); o = 0x20 * 0x4000 + 0x58c8 - 0x4000
open(os.path.join(OUT, 'pals.bin'), 'wb').write(b''.join(r[o + d * 8 + 2:o + d * 8 + 6] for d in range(152)))
# 内部の 番号 → ずかん番号（pokered の dex_order と pokedex_constants）
dexno = {}
for l in open(os.path.join(PR, 'constants', 'pokedex_constants.asm')):
    m = re.match(r'\s*const (DEX_\w+)', l)
    if m: dexno[m.group(1)] = len(dexno) + 1
order = [l.split()[1] for l in open(os.path.join(PR, 'data', 'pokemon', 'dex_order.asm')) if l.strip().startswith('db ')]
open(os.path.join(OUT, 'dex.bin'), 'wb').write(bytes(dexno.get(x, 0) for x in order))
print(len(order), 'ok')
