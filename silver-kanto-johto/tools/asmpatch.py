"""小さな アセンブリ（rgbasm の 書き方。SECTION で 場所を きめる）を 今の ROM に 重ねる。"""
import os, subprocess, tempfile, shutil


def tool(n):
    p = shutil.which(n)
    if p: return p
    for d in ('/home/claude/rgbds1/src', os.environ.get('RGBDS', '')):
        if d and os.path.exists(os.path.join(d, n)): return os.path.join(d, n)
    raise FileNotFoundError(n)


def overlay(rom, src):
    with tempfile.TemporaryDirectory() as d:
        open(d + '/a.asm', 'w', encoding='utf-8').write(src)
        open(d + '/in.gbc', 'wb').write(rom)
        subprocess.run([tool('rgbasm'), '-o', d + '/a.o', d + '/a.asm'], check=True)
        subprocess.run([tool('rgblink'), '-O', d + '/in.gbc', '-o', d + '/out.gbc', d + '/a.o'], check=True)
        new = open(d + '/out.gbc', 'rb').read()
    assert len(new) == len(rom)
    rom[:] = new
    return rom
