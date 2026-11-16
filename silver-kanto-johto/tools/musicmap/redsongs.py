import re
D='/home/claude/ref/pokered/audio/headers/'
def offs(n):
    off={}; c=0
    for f in ('sfxheaders%d.asm'%n,'musicheaders%d.asm'%n):
        for l in open(D+f):
            m=re.match(r'(\w+)::',l)
            if m: off[m.group(1)]=c
            if re.match(r'\s*channel\s+\d',l): c+=3
    return off
O={1:offs(1),2:offs(2),3:offs(3)}
if __name__=='__main__':
    print('MeetRival',hex(O[1]['Music_MeetRival']),'Dungeon2',hex(O[3]['Music_Dungeon2']))
    print('base1', hex(0x71C8-O[1]['Music_MeetRival']), 'base3', hex(0x716B-O[3]['Music_Dungeon2']))
    for n in (1,2,3): print(n,[k for k in O[n] if k.startswith('Music')])
