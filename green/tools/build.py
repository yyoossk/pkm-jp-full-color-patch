# 12種類の ROM を 組む（金の 改良と 同じ やり方）。
#   python3 tools/build.py 元の緑.gb [版の 名前 …]
#
# 1. 土台：元の ROM（1.0・1.1 の どちらでも）に base_ips/ の Ver.1.8.0 の パッチを 当てる。
# 2. これからの 直しや 追加：patches/main.asm（と そこから INCLUDE する ファイル）を rgbds で
#    アセンブルして、rgblink -O で 土台の ROM の 上に かさねる（決めた バンク・番地だけ かわる）。
#    版ごとに 当てる 場所が ちがう ときは、patches/editions/<版>.inc の 番地を 使う（-D ED_<番号> も わたす）。
# 3. out/<版>.gbc に 書いて、CRC32 を 出す。patches/main.asm が 空なら、Ver.1.8.0 と 同じ ROM になる。
import os, sys, shutil, subprocess, zlib, tempfile
sys.path.insert(0, os.path.dirname(__file__))
import ips

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITIONS = [
    'ポケットモンスター緑フルカラー',
    'ポケットモンスター緑初代グラフィックフルカラー',
    'ポケットモンスター緑フルカラー_カラー化のみ',
    'ポケットモンスター緑初代グラフィックフルカラー_カラー化のみ',
    'ポケットモンスター緑フルカラー_60fps',
    'ポケットモンスター緑初代グラフィックフルカラー_60fps',
    'ポケットモンスター緑フルカラー_カラー化のみ_60fps',
    'ポケットモンスター緑初代グラフィックフルカラー_カラー化のみ_60fps',
    'ポケットモンスター緑フルカラー_151匹そろう版',
    'ポケットモンスター緑初代グラフィックフルカラー_151匹そろう版',
    'ポケットモンスター緑フルカラー_151匹そろう版_60fps',
    'ポケットモンスター緑初代グラフィックフルカラー_151匹そろう版_60fps',
]
# Ver.1.8.0 の CRC32（土台が 正しく できたかを 見る）
BASE_CRC = {
    'ポケットモンスター緑フルカラー': 0x0EE87A90,
    'ポケットモンスター緑初代グラフィックフルカラー': 0x7814120C,
    'ポケットモンスター緑フルカラー_カラー化のみ': 0xA43386BF,
    'ポケットモンスター緑初代グラフィックフルカラー_カラー化のみ': 0x6DC756AD,
    'ポケットモンスター緑フルカラー_60fps': 0x9959DBBE,
    'ポケットモンスター緑初代グラフィックフルカラー_60fps': 0x926B3C64,
    'ポケットモンスター緑フルカラー_カラー化のみ_60fps': 0xC1B6A79E,
    'ポケットモンスター緑初代グラフィックフルカラー_カラー化のみ_60fps': 0x29FC5B38,
    'ポケットモンスター緑フルカラー_151匹そろう版': 0x8CC78F88,
    'ポケットモンスター緑初代グラフィックフルカラー_151匹そろう版': 0x6319700C,
    'ポケットモンスター緑フルカラー_151匹そろう版_60fps': 0x2EB1FD3A,
    'ポケットモンスター緑初代グラフィックフルカラー_151匹そろう版_60fps': 0x49C8A03C,
}
ORIG_CRC = {0xBAEACD2B: '1.0', 0x37AE8DC4: '1.1'}


def has_patches():
    p = os.path.join(ROOT, 'patches', 'main.asm')
    for line in open(p, encoding='utf-8'):
        s = line.split(';', 1)[0].strip()
        if s:
            return True
    return False


def rgbds(name):
    exe = shutil.which(name)
    if not exe:
        for cand in (name, name + '.exe'):   # Windows の rgbds は .exe
            exe = os.path.join(ROOT, 'tools', 'rgbds', cand)
            if os.path.exists(exe):
                break
    if not os.path.exists(exe):
        sys.exit('%s が 見つかりません。rgbds（https://rgbds.gbdev.io/）を 入れて PATH に 通すか、tools/rgbds/ に おいて ください。' % name)
    return exe


def main():
    orig = open(sys.argv[1], 'rb').read()
    ver = ORIG_CRC.get(zlib.crc32(orig))
    if not ver:
        sys.exit('元の 緑（1.0 か 1.1）の ROM では ありません（CRC32 %08X）' % zlib.crc32(orig))
    eds = sys.argv[2:] or EDITIONS
    os.makedirs(os.path.join(ROOT, 'out'), exist_ok=True)
    patch = has_patches()
    for i, ed in enumerate(EDITIONS):
        if ed not in eds:
            continue
        base = ips.apply(orig, open(os.path.join(ROOT, 'base_ips', ed + '.ips'), 'rb').read())
        assert zlib.crc32(base) == BASE_CRC[ed], ed + ' の 土台が Ver.1.8.0 と ちがいます'
        out = os.path.join(ROOT, 'out', ed + '.gbc')
        if not patch:
            open(out, 'wb').write(base)
        else:
            with tempfile.TemporaryDirectory() as tmp:
                bp = os.path.join(tmp, 'base.gbc')
                op = os.path.join(tmp, 'patch.o')
                open(bp, 'wb').write(base)
                inc = os.path.join('patches', 'editions', ed + '.inc')
                subprocess.run([rgbds('rgbasm'), '-I', 'patches', '-D', 'ED_%d' % i,
                                '-D', 'EDITION_INC="%s"' % inc, '-o', op, os.path.join('patches', 'main.asm')],
                               cwd=ROOT, check=True)
                subprocess.run([rgbds('rgblink'), '-O', bp, '-o', out, op], cwd=ROOT, check=True)
                subprocess.run([rgbds('rgbfix'), '-v', out], cwd=ROOT, check=True)
        r = open(out, 'rb').read()
        print('%08X  %s' % (zlib.crc32(r), ed))


if __name__ == '__main__':
    main()
