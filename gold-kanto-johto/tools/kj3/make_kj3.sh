#!/bin/sh
# crystal_kj3.gbc：crystal_kj2.gbc（make_kj2.sh）に、クリスタル版 第123弾（追加の直し 第123弾 キット）の
# build_phase123.py を 当てた もの。gold_full.py は MODROM（ふだんは kj3）を 読む。
#  ・この フォルダの build_phase123.py と 道具（lib.py ほか）は キットの ソース/tools の まま。
#  ・MODROOT に crystal/（日本版クリスタル）・aka/（赤 日本版）・ref/（pret：pokecrystal・pokered）を そろえる。
#  ・MOD 側（スクリプト・マップ・文）の 直しは c2g で そのまま 金に 入る。エンジンの 直しは 金では gold_p123.py。
set -e
D=$(cd "$(dirname "$0")" && pwd)
IN=${1:-/home/claude/work/ref/crystal_kj2.gbc}; OUT=${2:-/home/claude/work/ref/crystal_kj3.gbc}
T=$(mktemp -d)
MODROOT=${MODROOT:-/home/claude/k123root} python3 $D/build_phase123.py "$IN" "$OUT" $T/p.ips
