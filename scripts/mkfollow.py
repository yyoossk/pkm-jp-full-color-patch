#!/usr/bin/env python3
"""連れ歩きの絵・下じき・色を作る（build.py からよぶ）
使い方: mkfollow.py 土台のROM 出す所
  kit/follow/follow_icon.bin（キットの絵 151匹×24タイル）の正面（止まり 0〜3・歩き 12〜15）を、
  土台の ROM の手持ちのアイコン（バンク$3E:$4000、ずかん番号−1 × 128バイト、2コマ）にかえる。
  下じき（目・顔の白）は、後ろ・横はキットの mask.bin、正面はアイコンの絵から作る
  （外とつながっていない すきま（色0）を 色1 にする）。
  色: 正面 = 手持ちのアイコンの色（バンク$2C:$5A40、8バイト）の色1・色2、後ろ・横 = キットの色。
出すもの: follow_gfx.bin（151×384）、follow_mask.bin（151×384）、follow_pals.bin（151×8）
"""
import sys, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON = 0x3E * 0x4000
ICONPAL = 0x2C * 0x4000 + 0x1A40

def tile_px(t):
    px = []
    for y in range(8):
        lo, hi = t[y*2], t[y*2+1]
        px.append([((lo >> (7-x)) & 1) | (((hi >> (7-x)) & 1) << 1) for x in range(8)])
    return px

def frame_px(tiles):   # 4タイル（左上・右上・左下・右下）→ 16×16
    p = [[0]*16 for _ in range(16)]
    for i in range(4):
        tp = tile_px(tiles[i*16:i*16+16]); ox, oy = (i & 1)*8, (i >> 1)*8
        for y in range(8):
            for x in range(8): p[oy+y][ox+x] = tp[y][x]
    return p

def px_tiles(p):       # 16×16（0/1）→ 4タイル（色1）
    out = bytearray()
    for i in range(4):
        ox, oy = (i & 1)*8, (i >> 1)*8
        for y in range(8):
            lo = 0
            for x in range(8): lo |= (p[oy+y][ox+x] & 1) << (7-x)
            out += bytes([lo, 0])
    return bytes(out)

def holes(p):          # 外とつながっていない 色0 → 1
    out = [[0]*16 for _ in range(16)]
    seen = [[False]*16 for _ in range(16)]
    st = [(x, y) for x in range(16) for y in (0, 15)] + [(x, y) for y in range(16) for x in (0, 15)]
    while st:
        x, y = st.pop()
        if not (0 <= x < 16 and 0 <= y < 16) or seen[y][x] or p[y][x]: continue
        seen[y][x] = True
        st += [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
    for y in range(16):
        for x in range(16):
            if p[y][x] == 0 and not seen[y][x]: out[y][x] = 1
    return out

def main(rom, outdir):
    d = open(rom, 'rb').read()
    gfx = bytearray(open(os.path.join(R, 'kit/follow/follow_icon.bin'), 'rb').read())
    mask = bytearray(open(os.path.join(R, 'kit/follow/mask.bin'), 'rb').read())
    walk = open(os.path.join(R, 'kit/follow/walkpals.bin'), 'rb').read()
    pals = bytearray()
    for n in range(151):
        icon = d[ICON + n*128: ICON + n*128 + 128]
        for f, dst in ((0, 0), (1, 12)):
            t = icon[f*64:f*64+64]
            gfx[n*384 + dst*16: n*384 + dst*16 + 64] = t
            mask[n*384 + dst*16: n*384 + dst*16 + 64] = px_tiles(holes(frame_px(t)))
        p = d[ICONPAL + n*8: ICONPAL + n*8 + 8]
        pals += p[2:6] + walk[n*4:n*4+4]
    os.makedirs(outdir, exist_ok=True)
    open(os.path.join(outdir, 'follow_gfx.bin'), 'wb').write(gfx)
    open(os.path.join(outdir, 'follow_mask.bin'), 'wb').write(mask)
    open(os.path.join(outdir, 'follow_pals.bin'), 'wb').write(pals)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
