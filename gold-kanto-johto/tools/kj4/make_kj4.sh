#!/bin/sh
# crystal_kj4.gbc：crystal_kj3.gbc（kj3/make_kj3.sh）に 第126弾の MOD 側（2 ゲート・3 26番道路）を 当てた もの。
set -e
D=$(cd "$(dirname "$0")" && pwd)
IN=${1:-/home/claude/work/ref/crystal_kj3.gbc}; OUT=${2:-/home/claude/work/ref/crystal_kj4.gbc}
MODROOT=${MODROOT:-/home/claude/k123root} python3 $D/kj4_mod.py "$IN" "$OUT"
