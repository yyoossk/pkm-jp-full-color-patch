#!/bin/sh
# crystal_kj6.gbc：crystal_kj5.gbc（kj5/make_kj5.sh）に 第128弾の MOD 側（おつきみ山 B2F の 隠し道具）を 当てた もの。gold_full.py は MODROM（ふだんは kj6）を 読む。
set -e
D=$(cd "$(dirname "$0")" && pwd)
IN=${1:-/home/claude/work/ref/crystal_kj5.gbc}; OUT=${2:-/home/claude/work/ref/crystal_kj6.gbc}
MODROOT=${MODROOT:-/home/claude/k123root} python3 $D/kj6_mod.py "$IN" "$OUT"
