"""Upgrade flow preview assembled from approved assets; not game implementation."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path(__file__).resolve().parents[3]; B=R/'ImageReview/batches/campfire-l03'; B.mkdir(parents=True,exist_ok=True)
reg={a['id']:a for a in json.loads((R/'docs/design/art-inventory/developer-asset-registry.json').read_text(encoding='utf-8'))['items']}; deps={}
def asset(i):
 a=reg[i]; p=R/a['paths']['png']; assert a['productionEligible'] and hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256'];deps[i]=a['paths']['png'];return Image.open(p).convert('RGBA')
def panel(w,h):
 im=asset('panel_paper_a03'); o=Image.new('RGBA',(w,h)); xs=[0,32,224,256];ys=xs;dx=[0,32,w-32,w];dy=[0,32,h-32,h]
 for i in range(3):
  for j in range(3):o.alpha_composite(im.crop((xs[i],ys[j],xs[i+1],ys[j+1])).resize((dx[i+1]-dx[i],dy[j+1]-dy[j]),Image.Resampling.LANCZOS),(dx[i],dy[j]))
 return o
def txt(im,x,y,s,n=25,c='#252F32',anchor='lm'):
 ImageDraw.Draw(im).text((x,y),s,font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',n),fill=c,anchor=anchor)
def btn(im,x,y,w,s,disabled=False,secondary=False):
 a=asset('btn_'+('secondary' if secondary else 'primary')+'_'+('disabled' if disabled else 'normal')+'_b03');h=round(w*112/640);im.alpha_composite(a.resize((w,h),Image.Resampling.LANCZOS),(x,y));txt(im,x+w/2,y+h/2,s,24,'#485356' if disabled or secondary else '#F1EEE2','mm')

fid='border_card_skill_rare_r02'; spec=reg[fid]['spec'];win=spec['window']
def magic(upgraded):
 frame=asset(fid);a=asset('card_skill_moligongming_etching_d10');o=Image.new('RGBA',frame.size)
 o.alpha_composite(ImageOps.fit(a,(win['width'],win['height']),method=Image.Resampling.LANCZOS),(win['x'],win['y']))
 o.putalpha(Image.open(R/spec['windowMask']).convert('L'));o.alpha_composite(frame)
 t=spec['textSafe']['title'];txt(o,t['x']+t['width']/2,t['y']+t['height']/2,'魔力共鸣',76,anchor='mm')
 lines=['造成6点伤害','抽2张牌到桌面','[共鸣] [消耗]'] if upgraded else ['造成4点伤害','抽1张牌到桌面','[共鸣] [消耗]']
 for j,line in enumerate(lines):txt(o,480,918+j*76,line,58,'#355C67' if upgraded and j<2 else '#252F32','mm')
 return o
im=Image.open(R/'ImageReview/batches/campfire-l01/mockup_campfire_l01_1920x1080.png').convert('RGBA');im.alpha_composite(Image.new('RGBA',im.size,(0,0,0,165)));im.alpha_composite(panel(1660,870),(130,105))
txt(im,200,168,'升级卡牌',42);txt(im,1705,168,'关闭 ×',25,anchor='rm')
txt(im,200,225,'选择卡牌，查看强化后的卡面。',26)
txt(im,200,289,'可升级卡牌 · 4张',26)
for i,n in enumerate([1,1,2,3]):
 x=190+(i%2)*195;y=340+(i//2)*235
 card=Image.open(R/f'ImageReview/batches/shop-k02/card_{n}_review.png').convert('RGBA');im.alpha_composite(card.resize((165,220),Image.Resampling.LANCZOS),(x,y))
 if i==3:ImageDraw.Draw(im).rounded_rectangle((x-2,y-3,x+167,y+222),radius=6,outline='#648891',width=4)
ImageDraw.Draw(im).line((610,280,610,820),fill='#87918A',width=2)
txt(im,860,300,'强化前',30,anchor='mm');txt(im,1450,300,'强化后',30,'#355C67','mm')
for x,up in [(650,False),(1240,True)]:
 card=magic(up);card.save(B/('card_after.png' if up else 'card_before.png'));im.alpha_composite(card.resize((420,560),Image.Resampling.LANCZOS),(x,330))
# Native UI arrow between the exact existing card assets.
d=ImageDraw.Draw(im);d.line((1090,585,1200,585),fill='#648891',width=10);d.polygon([(1205,585),(1175,563),(1175,607)],fill='#648891')
txt(im,1150,637,'强化',23,'#355C67','mm')
txt(im,200,853,'仅强化所选单张',24,'#48575A');txt(im,200,890,'取消可返回篝火',23,'#48575A')
btn(im,1030,900,280,'取消',secondary=True);btn(im,1370,900,320,'确认升级')
im.convert('RGB').save(B/'selected.png')
(B/'assets.json').write_text(json.dumps({'status':'pending-review','productionEligible':False,'role':'upgrade-before-arrow-after-reference','dependencies':deps,'mask':spec['windowMask'],'changes':{'damage':[4,6],'draw':[1,2]},'note':'Exact approved art and frame, independent before/after text, no rarity or illustration change.'},ensure_ascii=False,indent=2),encoding='utf-8')
