#!/bin/sh
# crystal_kj5.gbc：crystal_kj4.gbc（kj4/make_kj4.sh）に 第127弾の MOD 側（2・6・7・8）を 当てた もの。gold_full.py は MODROM（ふだんは kj5）を 読む。
set -e
D=$(cd "$(dirname "$0")" && pwd)
IN=${1:-/home/claude/work/ref/crystal_kj4.gbc}; OUT=${2:-/home/claude/work/ref/crystal_kj5.gbc}
MODROOT=${MODROOT:-/home/claude/k123root} python3 $D/kj5_mod.py "$IN" "$OUT"
