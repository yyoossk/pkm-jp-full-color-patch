#!/usr/bin/env python3
"""リリース用 zip を作る: mkrelease.py 元の青.gb 出力.zip
out/<版>.gbc と元の青から ips を作り、Ver.2.32 と同じフォルダ・名前で zip にまとめる。
名前は Shift_JIS（Windows 用）＋ Unicode Path 拡張（UTF-8、ほかの環境用）で入れる。"""
import sys, os, zlib, zipfile, struct
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ips import apply
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOP = 'ポケットモンスター青フルカラー'
ED = {'full': ('1_完全版', ''), 'color': ('2_カラー化のみ', 'カラー化のみ'), 'all151': ('3_151匹そろう版', '151匹そろう版')}
def relpath(v):
    ed, g = v.split('_')[:2]; fps = v.endswith('_60')
    folder, tag = ED[ed]
    sub = '初代グラフィック版' if g == 'sho' else '金銀グラフィック版'
    parts = [t for t in (tag, '初代グラフィック版' if g == 'sho' else '') if t]
    name = 'ポケットモンスター青フルカラー' + ('60fps版' if fps else '') + ('（' + '・'.join(parts) + '）' if parts else '') + '.ips'
    return f'{TOP}/{folder}/{sub}/{name}'
def mkips(a, b):
    out = bytearray(b'PATCH'); n = len(b)
    a = a[:n] + bytes(max(0, n - len(a)))
    i = 0
    while i < n:
        if a[i] == b[i]: i += 1; continue
        if i == 0x454F46: i -= 1          # "EOF" と同じ番地をさける
        j = i; same = 0
        while j < n and j - i < 0xFFFF:
            if a[j] == b[j]:
                same += 1
                if same > 6: break
            else: same = 0
            j += 1
        if same > 6: j -= same - 1     # j は7つめの同じバイト。同じバイトの手前でおわる
        else: j -= same
        out += i.to_bytes(3, 'big') + (j - i).to_bytes(2, 'big') + b[i:j]; i = j
    if n > len(a.rstrip(b'\0')) or True:
        out += (n - 1).to_bytes(3, 'big') + (1).to_bytes(2, 'big') + b[n-1:n]   # 大きさを合わせる
    return bytes(out + b'EOF')
class SJISInfo(zipfile.ZipInfo):
    def _encodeFilenameFlags(self):
        return self.filename.encode('cp932'), self.flag_bits & ~0x800
def add(z, name, data=None):
    zi = SJISInfo(name, date_time=(2026, 11, 10, 0, 0, 0))
    zi.create_system = 3
    raw = name.encode('cp932')
    zi.extra = struct.pack('<HHB', 0x7075, 5 + len(name.encode()), 1) + struct.pack('<I', zlib.crc32(raw)) + name.encode()
    if data is None:
        zi.external_attr = (0o40755 << 16) | 0x10; z.writestr(zi, b'')
    else:
        zi.external_attr = 0o100644 << 16; zi.compress_type = zipfile.ZIP_DEFLATED; z.writestr(zi, data)
if __name__ == '__main__':
    base = open(sys.argv[1], 'rb').read(); assert '%08X' % zlib.crc32(base) == 'E4468D14'
    VARS = ['full_kin','full_kin_60','full_sho','full_sho_60','color_kin','color_kin_60','color_sho','color_sho_60','all151_kin','all151_kin_60','all151_sho','all151_sho_60']
    files = {}
    for v in VARS:
        rom = open(os.path.join(R, 'out', v + '.gbc'), 'rb').read()
        p = mkips(base, rom); assert apply(base, p) == rom, v
        files[relpath(v)] = p
        print('%-14s %08X  %s' % (v, zlib.crc32(rom), relpath(v)))
    dirs = sorted({'/'.join(k.split('/')[:i]) + '/' for k in files for i in range(1, k.count('/') + 1)})
    with zipfile.ZipFile(sys.argv[2], 'w') as z:
        for d in dirs: add(z, d)
        for k in sorted(files): add(z, k, files[k])
