#!/bin/sh
# crystal_kj2.gbc：参照用の クリスタル版（crystal_kj.gbc ＝ 第94弾まで）に、crystal-satoshi-mod の
# build_phase95〜110 を 順に 当てた もの（第100弾は 追加機能キットの ぶんぷの 古い 形で 合わないので 当てない。金は gold_fixes.py の fix100）。
#  ・道具の 置き場：crystal-satoshi-mod（MODROOT）に crystal/（日本版クリスタル）・aka/（赤）・ref/（pret）を そろえる。
#    akafc/akafc.gbc は 赤（日本版）を 指す（第102弾は 赤の バンク 1F の 曲 だけ 読む。赤フルカラーと 同じ）。
#    pkfc/pkfc.gbc は 0 で うめた ダミー（第95〜110弾は 読まない。import の ときに 開く だけ）。
#    ref/pokered/gfx/tilesets/gym.2bpp は rgbgfx -c dmg=e4 で gym.png から 作る（第108弾）。
#  ・第110弾の 6（タマムシマンションの タイルセット）は 第40・41弾の 作りなおしの かわりに mansion.py で その 絵・色を 入れかえる。
#  ・第110弾の 1（クチバジムの ゴミばこの 文と 音：直した 第75弾）は trash110.py。
set -e
D=$(cd "$(dirname "$0")" && pwd)
MOD=${MODROOT:-/home/claude/yyoossk/crystal-satoshi-mod}
IN=${1:-/home/claude/work/ref/crystal_kj.gbc}; OUT=${2:-/home/claude/work/ref/crystal_kj2.gbc}
T=$(mktemp -d); cp "$IN" $T/c.gbc
cd $MOD/tools
for n in 95 96 97 98 99 101 102 103 104 105 106 107 108 109 110; do
  python3 build_phase$n.py $T/c.gbc $T/n.gbc $T/n.ips; mv $T/n.gbc $T/c.gbc
done
python3 $D/mansion.py $T/c.gbc $T/m.gbc
python3 $D/trash110.py $T/m.gbc "$OUT"
