import re,sys,align as A
A.load('/home/claude/work/rom/kin1.gbc')
EN=A.EN; JP=A.JP
T={'FastShipCabins_SE_SSE_CaptainsCabin':[('TrainerPsychicRodney','SPRITE_YOUNGSTER',None)],
 'LakeOfRage':[('TrainerFisherAndre',None,'PAL_NPC_GREEN'),('TrainerFisherRaymond',None,'PAL_NPC_GREEN')],
 'Route13':[('TrainerHikerKenny',None,'PAL_NPC_BROWN')],
 'Route44':[('TrainerBirdKeeperVance1',None,'PAL_NPC_BLUE'),('TrainerPokemaniacZach',None,'PAL_NPC_BLUE')],
 'UnionCaveB2F':[('TrainerCooltrainermNick','SPRITE_COOLTRAINER_M',None)],
 'FuchsiaPokecenter1F':[('FuchsiaPokecenter1FNurseScript',None,'PAL_NPC_RED')],
 'NationalParkBugContest':[], 'Route36NationalParkGate':[]}
for m,l in (('NationalParkBugContest','A'),('Route36NationalParkGate','B')):
    for n,spr,pal in ((1,'SPRITE_BUG_CATCHER','PAL_NPC_BROWN'),(2,'SPRITE_BUG_CATCHER','PAL_NPC_BROWN'),(3,'SPRITE_COOLTRAINER_M','PAL_NPC_RED'),
                      (4,None,'PAL_NPC_RED'),(5,'SPRITE_BUG_CATCHER','PAL_NPC_BROWN'),(7,None,'PAL_NPC_GREEN'),(8,'SPRITE_BUG_CATCHER','PAL_NPC_BROWN'),(9,None,'PAL_NPC_BLUE')):
        T[m].append(('BugCatchingContestant%d%sScript'%(n,l),spr,pal))
def rx(parts):
    return re.compile(b''.join(re.escape(p) if isinstance(p,bytes) else b'.'*p for p in parts),re.S)
lines=[]
for mp,tg in T.items():
    src=open('/home/claude/work/pokegold/maps/%s.asm'%mp).read()
    objs=[l for l in src.splitlines() if l.strip().startswith('object_event')]
    b,a=A.SYM[mp+'_MapEvents']; o=A.off(b,a)
    parts=[EN[o:o+2]]; p=o+2
    n=EN[p]; parts.append(EN[p:p+1+5*n]); p+=1+5*n
    n=EN[p]; parts.append(EN[p:p+1]); p+=1
    for i in range(n): parts+= [EN[p:p+4],2,EN[p+6:p+8]]; p+=8
    n=EN[p]; parts.append(EN[p:p+1]); p+=1
    for i in range(n): parts+= [EN[p:p+3],2]; p+=5
    nobj=EN[p]; parts.append(EN[p:p+1]); p+=1
    assert nobj==len(objs),(mp,nobj,len(objs))
    hits=[m.start() for m in rx(parts).finditer(JP)]
    if len(hits)!=1: print('??',mp,len(hits)); continue
    jo=hits[0]+(p-o)
    for name,spr,pal in tg:
        k=[i for i,l in enumerate(objs) if name+',' in l.replace(' ','') or (', '+name+',') in l][0]
        j=jo+13*k; e=p+13*k
        assert JP[j:j+9]==EN[e:e+9],(name,JP[j:j+9].hex(),EN[e:e+9].hex())
        bank=j//0x4000; addr=j%0x4000+0x4000
        if spr: lines.append('SECTION "BF63 %s s", ROMX[$%04x], BANK[$%02x]\n\tdb %s'%(name,addr,bank,spr))
        if pal: lines.append('SECTION "BF63 %s p", ROMX[$%04x], BANK[$%02x]\n\tdn %s, $%x'%(name,addr+7,bank,pal,JP[j+7]&15))
        print(name,'%02x:%04x'%(bank,addr),JP[j:j+13].hex())
open('/home/claude/work/goldkit/bf/npc63.inc','w').write('\n'.join(lines)+'\n')
