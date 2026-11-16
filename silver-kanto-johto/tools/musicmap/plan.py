import pickle
exec(open('redmap.py').read().split("if __name__")[0])
M=pickle.load(open('M.pkl','rb'))
NEWID={'MUSIC_CITIES2':0x63,'MUSIC_CINNABAR':0x65,'MUSIC_SS_ANNE':0x66,'MUSIC_SAFARI_ZONE':0x67,'MUSIC_ROUTES2':0x68,
 'MUSIC_OAKS_LAB':0x69,'MUSIC_DUNGEON1':0x6A,'MUSIC_CINNABAR_MANSION':0x6B,'MUSIC_POKEMON_TOWER':0x6C,'MUSIC_SILPH_CO':0x6D}
GS={'MUSIC_ROUTES1':2,'MUSIC_ROUTES3':3,'MUSIC_ROUTES4':4,'MUSIC_CITIES1':21,'MUSIC_CELADON':22,'MUSIC_VERMILION':62,
 'MUSIC_LAVENDER':14,'MUSIC_PALLET_TOWN':28,'MUSIC_GYM':27,'MUSIC_POKECENTER':9,'MUSIC_INDIGO_PLATEAU':70,
 'MUSIC_GAME_CORNER':18,'MUSIC_DUNGEON2':0x52,'MUSIC_DUNGEON3':16}
GS.update(NEWID)
EXCL={(16,5),(16,8),(20,2),(20,3)}
plan={}
for o,n in sorted(M.items()):
    if o in EXCL or o[0] in (16,20): continue
    s=song.get(n)
    if s not in GS: print('NOSONG',o,n,s); continue
    h=ours(*o)[0]
    if h[6]!=GS[s]: plan[o]=(n,s,h[6],GS[s])
for o,v in plan.items(): print(o,v)
pickle.dump(plan,open('plan.pkl','wb')); print(len(plan))
