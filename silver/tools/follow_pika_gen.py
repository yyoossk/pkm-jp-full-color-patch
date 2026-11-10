# ピカチュウに 話しかけた ときの 表情の 絵（ピカチュウフルカラーの ROM で うごかして とった もの）→ src/follow_pika_data.inc
# gfxdata/pikapic/ypikadata.pkl：{番号: (タイル（2bpp 16バイト）の 表, コマ（5×5 の タイルの 番号）, 順番（コマ, フレーム数）)}
import pickle
d = pickle.load(open('gfxdata/pikapic/ypikadata.pkl', 'rb'))
L = ['; tools/follow_pika_gen.py で 作る（手で 書きかえない）']
banks = {}
cur = 0x4c; used = 0
for n in sorted(d):
    tiles, frames, order = d[n]
    sz = len(tiles) * 16 + len(frames) * 25 + len(order) * 2 + 8
    if used + sz > 0x3f00:
        cur += 1; used = 0
    used += sz
    banks[n] = cur
addr = {}
for n in sorted(d):
    tiles, frames, order = d[n]
    b = banks[n]; a = addr.get(b, 0x4000)
    sz = len(tiles) * 16 + len(frames) * 25 + len(order) * 2 + 1 + 7
    addr[b] = a + sz
    L.append('SECTION "pikapic %d", ROMX[$%04x], BANK[$%02x]' % (n, a, b))
    L.append('PikaPic%d:' % n)
    L.append('\tdb %d' % len(tiles))
    L.append('\tdw PikaPic%d_Tiles' % n)
    L.append('\tdw PikaPic%d_Frames' % n)
    L.append('\tdw PikaPic%d_Seq' % n)
    L.append('PikaPic%d_Seq:' % n)
    for f, du in order:
        L.append('\tdb %d, %d' % (f, du))
    L.append('\tdb $ff')
    L.append('PikaPic%d_Frames:' % n)
    for fm in frames:
        L.append('\tdb ' + ', '.join('$%02x' % (0x80 + t) for t in fm))
    L.append('PikaPic%d_Tiles:' % n)
    for t in tiles:
        L.append('\tdb ' + ', '.join('$%02x' % b for b in t))
L.append('')
L.append('SECTION "pikapic table", ROMX[$7d00], BANK[FW_BANK]')
L.append('PikaPicTable:')
for n in sorted(d):
    L.append('\tdb BANK(PikaPic%d)\n\tdw PikaPic%d' % (n, n))
open('src/follow_pika_data.inc', 'w').write('\n'.join(L) + '\n')
print('banks', sorted(set(banks.values())))
