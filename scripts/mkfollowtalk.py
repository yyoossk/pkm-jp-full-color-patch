#!/usr/bin/env python3
"""連れ歩きの会話の表（src/follow_talk.inc）を作る"""
# 会話の表を作る（会話文案.md の 1・3・4 章、初代に合わせたもの）
N='〈なまえ〉'
E_SHOCK,E_Q,E_HAPPY,E_SAD,E_HEART,E_BOLT,E_SLEEP=range(7)
texts=[]  # (label, emote, text)
def T(lbl,emo,s): texts.append((lbl,emo,s)); return lbl
status=[('Sleep',E_SLEEP,N+'は/すこし　ねむそうだ'),
        ('Poison',E_SAD,N+'は/ぐあいが　わるそうだ'),
        ('Burn',E_SHOCK,N+'は/すこし　いたそうだ'),
        ('Freeze',E_SHOCK,N+'は/こおりづけに　なっている！'),
        ('Paralyze',E_BOLT,N+'は/うごきが　にぶく　なっている')]
for l,e,s in status: T(l,e,s)
# 条件: (kind, value, maps, [ (emote,text) ... ])  kind: 'sp' 種類 / 'ty' タイプ
rules=[
 ('sp',[0x99],[0x0C],[(E_HAPPY,N+'は/つるを　くねくね　させた！'),(E_HAPPY,N+'は/つるを　ぴしっと　ならした！')]),
 ('sp',[0xB0],[0x0D],[(E_HAPPY,N+'は/しっぽの　ほのおを　もやした！')]),
 ('sp',[0x54,0x55],[0x0D,0x53],[(E_HEART,N+'は/たのしく　おどった！'),(E_HEART,N+'は　うれしくて/おどりだした！')]),
 ('sp',[0xB1],[0x0E],[(E_SAD,N+'は　ころんで/ちょっと　くやしそうだ！')]),
 ('sp',[0x04,0x8E],[0x3B,0x3C,0x3D],[(E_HAPPY,N+'は/そらを　みあげている！'),(E_HEART,N+'は/とつぜん　おどりだした！')]),
 ('sp',[0x22],[0x52,0xE8],[(E_HAPPY,N+'は　たのしそうに/じめんに　もぐっている！')]),
 ('ty',[0x05],[0x52,0xE8],[(E_HAPPY,N+'は　たのしそうに/ころがっている！'),(E_HAPPY,N+'は/いわを　けずりはじめた！'),(E_HAPPY,N+'は　たのしそうに/いわを　ぶつけている！'),(E_HAPPY,N+'は　じめんを/たたいて　ならしはじめた！')]),
 ('sp',[0x3B,0x76],[0xC5],[(E_HAPPY,N+'は　からだを/のばして　くつろいでいる！')]),
 ('ty',[0x18],[0xB7],[(E_Q,'……　……　……　……¶'+N+'は/だまって　うなずいた！')]),
 ('sp',[0xAA],[0x06],[(E_Q,N+'は/なにか　つぶやいた……')]),
 ('sp',[0x4C],[0x1A],[(E_Q,'……おや？　'+N+'の/すがたは……¶かわらなかった！')]),
 ('ty',[0x02],[0x1D],[(E_HAPPY,N+'は/ゆうがに　そらを　とんでいる！')]),
 ('ty',[0x08],[0x04],[(E_HAPPY,N+'は　たのしそうに/ゆらゆら　ゆれている')]),
]
out=[]
out.append('; 会話の表（scripts/mkfollowtalk.py で作る。会話文案.md の 1・3・4 章。初代にない行は入れていない）')
out.append('; 気持ちのアイコン: 0 びっくり・1 はてな・2 うれしい・3 かなしい・4 ハート・5 いなずま・6 ねむり')
ri=[]
for k,(kind,vals,maps,lines) in enumerate(rules):
    labs=[T(f'Kanto{k}_{j}',e,s) for j,(e,s) in enumerate(lines)]
    ri.append((kind,vals,maps,labs))
T('Normal',E_HAPPY,N+'は/あなたと　いっしょで　うれしそうだ！')
T('Found',E_SHOCK,N+'は/なにか　みつけた　ようだ¶ひろいますか？')
T('Got',E_HAPPY,'<PLAYER>は　'+'きんのたま'+'を/てにいれた！')
idx={l:i for i,(l,e,s) in enumerate(texts)}
out.append('FwTalkRules: ; 種類なら 0・タイプなら 1、あてはまるもの（$FF まで）、マップ（$FF まで）、文の数、はじめの文の番号')
for kind,vals,maps,labs in ri:
    out.append('\tdb %d, %s, $FF, %s, $FF, %d, %d' % (0 if kind=='sp' else 1, ', '.join('$%02X'%v for v in vals), ', '.join('$%02X'%m for m in maps), len(labs), idx[labs[0]]))
out.append('\tdb $FF')
for l in ('Sleep','Poison','Burn','Freeze','Paralyze','Normal','Found','Got'):
    out.append(f'DEF FWT_{l.upper()} EQU {idx[l]}')
out.append('FwTalkEmotes:')
out.append('\tdb '+', '.join(str(e) for l,e,s in texts))
out.append('FwTalkTexts: ; テキスト番号 $81 + n（DisplayTextID の表）')
for l,e,s in texts: out.append(f'\tdw FwText_{l}')
def enc(s):
    parts=[]; buf=''
    i=0
    res=[]
    while i<len(s):
        if s.startswith(N,i):
            if buf: res.append(f'"{buf}"'); buf=''
            res.append('$01, LOW(wNameBuffer), HIGH(wNameBuffer), $00'); i+=len(N); continue
        if s.startswith('<PLAYER>',i):
            if buf: res.append(f'"{buf}"'); buf=''
            res.append('$52'); i+=8; continue
        c=s[i]
        if c=='/':
            if buf: res.append(f'"{buf}"'); buf=''
            res.append('$4F')
        elif c=='¶':
            if buf: res.append(f'"{buf}"'); buf=''
            res.append('$51')
        else: buf+=c
        i+=1
    if buf: res.append(f'"{buf}"')
    first='$00, ' if not s.startswith(N) else ''
    return first+', '.join(res)
for l,e,s in texts:
    if l=='Found':
        out.append('FwText_Found:\n\tdb $08\n\tjp FwFoundAsm')
        out.append(f'FwText_FoundMsg:\n\tdb {enc(s)}, $50, $50')
    elif l=='Got':
        out.append(f'FwText_Got:\n\tdb {enc(s)}, $50, $0B, $50')
    else:
        out.append(f'FwText_{l}:\n\tdb {enc(s)}, $57')
import os
open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'src','follow_talk.inc'),'w',encoding='utf-8').write('\n'.join(out)+'\n')
print(len(texts))
