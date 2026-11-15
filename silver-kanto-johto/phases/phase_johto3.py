"""ジョウトの 御三家 3びき（第61弾。キット「御三家・セレビィキット」の src/johto3_crystal.asm を 銀の 値で）：
   ウツギ はかせの けんきゅうじょで 1ぴき えらぶと のこりの 2ひきも もらえる。すでに 1ぴき もらった セーブでは はかせが くれる。
   銀の けんきゅうじょ（24-5。スクリプト バンク$13）：givepoke $13:$65BB・$65FD・$6639、「〜を もらった！」$13:$6A87、
   ウツギ はかせの スクリプト $13:$64F9（object_event の 場所 $13:$74AB）→ $13:$7FF8 の farsjump。本体 $E8:$4600・$4800。
   しるしは クリスタル版の $D837（銀では ctx['amap'][$D837]）の ビット4〜6。"""
import os, sys, re
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(H, 'tools'))
import asmpatch
from gsc import fo, r16

KIT = os.environ.get('KIT_STARTERS', '/home/claude/in/kit/金銀移植キット/ソース/kitgs/御三家・セレビィキット')
SB = 0x13


def sub(s, a, b, n=1):
    assert s.count(a) == n, (a, s.count(a)); return s.replace(a, b)


def apply(rom, ctx):
    log = ctx.setdefault('log', [])
    flags = ctx['amap'][0xD837]
    for a, mon in ((0x65BB, 0x9B), (0x65FD, 0x9E), (0x6639, 0x98)):
        assert rom[fo(SB, a):fo(SB, a) + 5] == bytes([0x2D, mon, 5, 0xAD, 0])
    assert r16(rom, fo(SB, 0x74AB)) == 0x64F9 and not any(rom[fo(SB, 0x7FF8):fo(SB, 0x8000)])
    for a in (0x4600, 0x4800): assert not any(rom[fo(0xE8, a):fo(0xE8, a) + 0x200])
    s = open(os.path.join(KIT, 'src', 'johto3_crystal.asm'), encoding='utf-8').read()
    s = sub(s, 'DEF ED_BANK            EQU $6e', 'DEF ED_BANK            EQU $e8')
    s = sub(s, 'DEF ED_wEventFlags     EQU $da65', 'DEF ED_wEventFlags     EQU $d7aa')
    s = sub(s, 'DEF ED_wScriptVar      EQU $c2dd', 'DEF ED_wScriptVar      EQU $d165')
    s = sub(s, 'DEF wEdFlags           EQU $d837', 'DEF wEdFlags           EQU $%04x' % flags)
    s = sub(s, 'ROMX[\\1], BANK[$1b]', 'ROMX[\\1], BANK[$%02x]' % SB)
    s = sub(s, 'ed_starter_hook $62b7,', 'ed_starter_hook $65bb,')
    s = sub(s, 'ed_starter_hook $62f9,', 'ed_starter_hook $65fd,')
    s = sub(s, 'ed_starter_hook $6335,', 'ed_starter_hook $6639,')
    s = sub(s, '\tdb $4b, $1b\n\tdw $68ba', '\tdb $4b, $%02x\n\tdw $6a87' % SB, 2)
    s = sub(s, 'ROMX[$4000], BANK[ED_BANK]', 'ROMX[$4600], BANK[ED_BANK]')
    s = sub(s, 'ROMX[$6e00], BANK[ED_BANK]', 'ROMX[$4800], BANK[ED_BANK]')
    s = sub(s, 'SECTION "johto3 elm ptr", ROMX[$7302], BANK[$1b]', 'SECTION "johto3 elm ptr", ROMX[$74ab], BANK[$%02x]' % SB)
    s = sub(s, 'SECTION "johto3 elm stub", ROMX[$7ff8], BANK[$1b]', 'SECTION "johto3 elm stub", ROMX[$7ff8], BANK[$%02x]' % SB)
    s = sub(s, 'db farsjump_command, $1b          ; 元の ウツギ はかせの スクリプト\n\tdw $61f5',
            'db farsjump_command, $%02x          ; 元の ウツギ はかせの スクリプト\n\tdw $64f9' % SB)
    asmpatch.overlay(rom, s, inc=[os.path.join(KIT, 'pokecrystal')], cwd=KIT)
    log.append('ジョウトの 御三家 3びき（しるし $%04X）$E8:$4600・$4800、はかせ $%02X:$7FF8' % (flags, SB))
    return rom
