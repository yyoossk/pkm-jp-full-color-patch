#!/usr/bin/env python3
# カントーのジムリーダー再戦：元の ROM からアドレスを探して rematch_<名前>.inc を作る
#   python3 rematch_find.py 元のROM.gbc 出力.inc
# 金・銀・クリスタル（日本版）用。見つからないときは止まるので、そこを手で調べる。
import re,sys
rom=open(sys.argv[1],'rb').read()
out=[]
def ba(o): return o//0x4000, o%0x4000+(0x4000 if o>=0x4000 else 0)
def one(pat,what,start=0,end=None,group=0):
    ms=[m for m in re.finditer(pat,rom[start:end],re.S)]
    if len(ms)!=1: sys.exit('%s が %d か所 見つかった（1か所のはず）'%(what,len(ms)))
    return start+ms[0].start(group) if group else start+ms[0].start()
# ---- スクリプトの命令の番号（日本版）
#   faceplayer / opentext / checkflag / iftrue を ジムリーダーの話しかけの頭から読む
LEADERS=[('BROCK',0x23,0x11),('MISTY',0x24,0x12),('SURGE',0x25,0x13),('ERIKA',0x26,0x15),
         ('JANINE',0x27,0x1a),('SABRINA',0x28,0x23),('BLAINE',0x29,0x2e),('BLUE',0x2a,0x40)]
# checkflag = $34, iftrue = $09（金銀クリスタル共通の番号）
flags=[]
for name,flag,cls in LEADERS:
    # ジムリーダー：「checkflag バッジ / iftrue」のあと 80バイト以内に loadtrainer 人, 1 がある
    #   （バッジの番号は 版によってちがうので 探す）
    cands=[]
    for m in re.finditer(rb'\x34(.)\x00\x09',rom,re.S):
        a=m.start()
        tail=rom[a+6:a+80]
        if re.search(rb'[\x5d\x5e]'+re.escape(bytes([cls,1])),tail):
            cands.append(a)
    if len(cands)!=1: sys.exit('%s の話しかけが %d か所（1か所のはず）'%(name,len(cands)))
    flags.append(rom[cands[0]+1])
    a=cands[0]; bank,addr=ba(a)
    fd=rom[a+4]|rom[a+5]<<8
    out.append('DEF RM_%s_MAPBANK EQU $%02x'%(name,bank))
    out.append('DEF RM_%s_PATCH   EQU $%04x ; checkflag の所（6バイト）'%(name,addr))
    out.append('DEF RM_%s_AFTER   EQU $%04x ; 初めて戦うとき'%(name,addr+6))
    out.append('DEF RM_%s_DONE    EQU $%04x ; 勝ったあと（.FightDone）'%(name,fd))
    out.append('DEF RM_%s_CLASS   EQU $%02x'%(name,cls))
    # 1回目の戦い（winlosstext のあとの loadtrainer）の前に faceplayer / opentext があるか
    pre=rom[a-2:a]
    out.append('DEF RM_%s_OPEN    EQU %d ; 1 = 先に faceplayer・opentext 済み'%(name,1 if pre[1]==0x47 else 0))
    if pre[1]!=0x47:
        # アンズ：.FightDone の頭の faceplayer・opentext（2バイト）をとばした所
        fo=bank*0x4000+fd-0x4000
        out.append('DEF RM_%s_DONE2   EQU $%04x ; .FightDone の faceplayer・opentext のあと'%(name,fd+2))
if flags!=list(range(flags[0],flags[0]+8)): sys.exit('バッジの番号が つづいていない %s'%flags)
out.append('DEF RM_KANTO_BADGE0 EQU $%02x ; グレーバッジ（カントーのバッジ 8つは このあとに つづく）'%flags[0])
# ---- トレーナーのデータ
a=one(rb'\x21(.[\x40-\x7f])\x09\x09\x2a\x66\x6f\xfa','ReadTrainerParty の TrainerGroups')
tb,_=ba(a); tg=rom[a+1]|rom[a+2]<<8
out.append('DEF RM_PARTY_BANK  EQU $%02x'%tb)
out.append('DEF RM_TrainerGroups EQU $%04x'%tg)
for name,flag,cls in LEADERS:
    po=tb*0x4000+tg-0x4000+(cls-1)*2
    p=rom[po]|rom[po+1]<<8
    o=tb*0x4000+p-0x4000
    e=rom.index(0xff,o)+1
    out.append('DEF RM_%s_PARTY1 EQU $%04x ; 1回目の手持ち（%dバイト、元のデータをそのまま使う）'%(name,p,e-o))
    out.append('DEF RM_%s_PARTY1_LEN EQU %d'%(name,e-o))
    out.append('DEF RM_%s_NAME_LEN EQU %d ; 名前（@まで）'%(name,rom.index(0x50,o)+1-o))
    out.append('DEF RM_%s_PARTY1_OFS EQU $%x ; ROM の中の位置'%(name,o))
# トレーナーのバンクの空き（おわりの 0 のつづき）
bk=rom[tb*0x4000:(tb+1)*0x4000]
i=len(bk)
while i and bk[i-1]==0: i-=1
free=0x4000+i+16
out.append('DEF RM_PARTY_FREE  EQU $%04x ; ここから %d バイト空いている'%(free,0x8000-free))
# ---- PrintWinLossText の call GetMapScriptsBank
a=one(rb'\xfa..\xfe\x01\x18.\x21..\x18.\xfa..\x21..(?:\xe6\x0f|\xa7)\x28\x03\x21..\x2a\x66\x6f\xcd','PrintWinLossText',0,0x4000)
c=re.compile(rb'\x2a\x66\x6f\xcd').search(rom,a).start()+3
out.append('DEF RM_PrintWinLoss_Call EQU $%04x'%c)
out.append('DEF RM_GetMapScriptsBank EQU $%04x'%(rom[c+1]|rom[c+2]<<8))
# ---- wScriptBank（ExitScriptSubroutine）
a=one(rb'\x21..\x7e\xa7\x28.\x35\x5e\x16\x00\x21..\x19\x19\x19\x2a\x47\xe6\x7f\xea','ExitScriptSubroutine')
a+=22
out.append('DEF RM_wScriptBank EQU $%04x'%(rom[a]|rom[a+1]<<8))
# ---- RM_PARTY_FAR 用（トレーナーのバンクに空きがないとき。日本版 金銀）
#   ReadTrainerParty：ld a,[wLinkMode] / and a / ret nz / ld hl,wOTPartyCount / xor a / ld [hli],a / dec a / ld [hl],a /
#   ld hl,wOTPartyMons / ld bc,$120 / xor a / call ByteFill / ld a,[wOtherTrainerClass]
a=one(rb'\xfa..\xa7\xc0\x21..\xaf\x22\x3d\x77\x21..\x01\x20\x01\xaf\xcd..\xfa','ReadTrainerParty')
b,ad=ba(a)
out.append('DEF RM_ReadTrainerParty_Class EQU $%04x ; ld a, [wOtherTrainerClass]（RM_PARTY_FAR）'%(ad+22))
out.append('DEF RM_wOtherTrainerClass EQU $%04x'%(rom[a+23]|rom[a+24]<<8))
d=rom.index(b'\xc5\xe9\xc3',a)+2
out.append('DEF RM_ReadTrainerParty_Done EQU $%04x ; .done（jp ComputeTrainerReward）'%ba(d)[1])
# TrainerType4：ld h,d / ld l,e / .loop … predef TryAddMonToParty / … call AddNTimes / ld d,h / ld e,l / pop hl / ld a,[hli] / ld [de],a / push hl
t=one(rb'\x62\x6b\x2a\xfe\xff\xc8\xea..\x2a\xea..\x3e\x01\xea..\xe5\x3e.\xcd..\xfa..\x3d\x21..\x01\x30\x00\xcd..\x54\x5d\xe1\x2a\x12\xe5','TrainerType4')
e=rom.index(b'\xe1\x18',t)+3          # 最後の pop hl / jr .loop
assert rom[e-1]==(0x100-(e-(t+2)))&0xff, 'TrainerType4 の終わり'
out.append('DEF RM_TrainerType4_OFS EQU $%x ; 元の TrainerType4（ROM の中の位置）'%t)
out.append('DEF RM_TrainerType4_LEN EQU %d'%(e-t))
open(sys.argv[2],'w').write('\n'.join(out)+'\n')
print('\n'.join(out))
