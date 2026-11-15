"""pret の constants/*.asm を読んで 名前→値 を作る（const_def / const / const_skip / const_next / DEF = ）"""
import re, os
R='/home/claude/work/mod/ref/'
def parse(repo, files):
    d={}; val=0; step=1
    for f in files:
        p=R+repo+'/'+f
        if not os.path.exists(p): continue
        for l in open(p, encoding='utf-8', errors='replace'):
            l=l.split(';')[0].strip()
            m=re.match(r'const_def(?:\s+([^,\s]+))?(?:\s*,\s*(\S+))?',l)
            if m:
                val=ev(m.group(1),d) if m.group(1) else 0; step=ev(m.group(2),d) if m.group(2) else 1; continue
            m=re.match(r'const\s+(\w+)$',l)
            if m: d[m.group(1)]=val; val+=step; continue
            m=re.match(r'const_skip(?:\s+(\S+))?',l)
            if m: val+=step*(ev(m.group(1),d) if m.group(1) else 1); continue
            m=re.match(r'const_next\s+(\S+)',l)
            if m: val=ev(m.group(1),d); continue
            m=re.match(r'DEF\s+(\w+)\s+EQU\s+(.+)',l) or re.match(r'DEF\s+(\w+)\s*=\s*(.+)',l)
            if m:
                try: d[m.group(1)]=ev(m.group(2).replace('const_value',str(val)),d)
                except Exception: pass
    return d
def ev(s,d):
    s=s.replace('$','0x').replace('%','0b')
    s=re.sub(r'\b([A-Za-z_]\w*)\b',lambda m: str(d[m.group(1)]) if m.group(1) in d else m.group(1),s)
    return int(eval(s,{'__builtins__':{}},{}))
def table_names(repo,f,pat):
    """データの表の並び（例：special_pointers の add_special）"""
    out=[]
    for l in open(R+repo+'/'+f,encoding='utf-8'):
        m=re.match(pat,l.strip())
        if m: out.append(m.group(1))
    return out

def all_tables(repo):
    T={}
    T['event']=parse(repo,['constants/event_flags.asm'])
    T['engine']=parse(repo,['constants/engine_flags.asm'])
    T['sprite']=parse(repo,['constants/sprite_constants.asm'])
    T['music']=parse(repo,['constants/music_constants.asm'])
    T['sfx']=parse(repo,['constants/sfx_constants.asm'])
    T['trainer']=parse(repo,['constants/trainer_constants.asm'])
    T['landmark']=parse(repo,['constants/landmark_constants.asm'])
    T['item']=parse(repo,['constants/item_constants.asm'])
    T['pokemon']=parse(repo,['constants/pokemon_constants.asm'])
    T['tileset']=parse(repo,['constants/tileset_constants.asm'])
    T['special']={n:i for i,n in enumerate(table_names(repo,'data/events/special_pointers.asm',r'add_special (\w+)'))}
    T['std']={n:i for i,n in enumerate(table_names(repo,'engine/events/std_scripts.asm',r'add_stdscript (\w+)'))}
    return T
def xlat(kind, Tc, Tg, prefix=''):
    """クリスタルの値 → 金の値（同じ名前で）。見つからないものは None"""
    inv={}
    for n,v in Tc[kind].items():
        if prefix and not n.startswith(prefix): continue
        inv.setdefault(v,n)
    return {v:(n,Tg[kind].get(n)) for v,n in inv.items()}
