"""小さな アセンブリ（rgbasm の 書き方。SECTION で 場所を きめる）を 今の ROM に 重ねる。"""
import os, subprocess, tempfile, shutil


def tool(n):
    p = shutil.which(n)
    if p: return p
    for d in ('/home/claude/rgbds1/src', os.environ.get('RGBDS', '')):
        if d and os.path.exists(os.path.join(d, n)): return os.path.join(d, n)
    raise FileNotFoundError(n)


def overlay(rom, src, inc=(), cwd=None):
    """inc：INCLUDE を さがす フォルダ。src の {ROM} は 今の ROM（INCBIN 用）"""
    with tempfile.TemporaryDirectory() as d:
        open(d + '/a.asm', 'w', encoding='utf-8').write(src.replace('{ROM}', d + '/in.gbc'))
        open(d + '/in.gbc', 'wb').write(rom)
        a = [tool('rgbasm')]
        for i in inc: a += ['-I', i if i.endswith('/') else i + '/']
        subprocess.run(a + ['-o', d + '/a.o', d + '/a.asm'], check=True, cwd=cwd)
        subprocess.run([tool('rgblink'), '-O', d + '/in.gbc', '-o', d + '/out.gbc', d + '/a.o'], check=True)
        new = open(d + '/out.gbc', 'rb').read()
    assert len(new) == len(rom)
    rom[:] = new
    return rom
