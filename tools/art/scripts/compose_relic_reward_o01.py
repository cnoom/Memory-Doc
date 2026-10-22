"""Upgrade flow preview assembled from approved assets; not game implementation."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path(__file__).resolve().parents[3]; B=R/'ImageReview/batches/relic-reward-o01'; B.mkdir(parents=True,exist_ok=True)
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

relics=[('全知之眼','relic_omniscient_eye_etching_e02',['场上可同时翻开的牌数量 +1','由1张提升至2张。']),('混沌核心','relic_chaos_core_etching_e02',['每回合开始时，随机将桌面','2张牌互换位置，然后揭示','互换后的2张牌内容，持续可见。']),('记忆王冠','relic_memory_crown_etching_e02',['所有能力牌的持续效果翻倍。','例如：持续增加1点伤害','变为持续增加2点伤害。'])]
for state in ['unselected','selected','partial','empty','claimed']:
 im=asset('bg_battle_empty_a01');im.alpha_composite(Image.new('RGBA',im.size,(0,0,0,150)));im.alpha_composite(panel(1640,940),(140,70))
 txt(im,960,140,'Boss 遗物奖励',44,anchor='mm')
 txt(im,960,210,'选择一件遗物。' if state not in ['empty','claimed'] else '本次遗物奖励已结算。',27,anchor='mm')
 ids=[0,1] if state=='partial' else [0,1,2]
 if state in ['unselected','selected','partial']:
  start=510 if state=='partial' else 265
  for pos,i in enumerate(ids):
   x=start+pos*490;name,aid,lines=relics[i];im.alpha_composite(panel(420,565),(x,280))
   if state=='selected' and i==0:ImageDraw.Draw(im).rounded_rectangle((x-4,276,x+424,849),radius=10,outline='#648891',width=5)
   im.alpha_composite(asset(aid),(x+82,310));txt(im,x+210,604,name,32,anchor='mm');txt(im,x+210,652,'Boss 遗物',21,'#48575A','mm')
   for j,line in enumerate(lines):txt(im,x+30,708+j*35,line,23)
  if state=='selected':txt(im,475,879,'已选中',24,'#355C67','mm')
  if state=='partial':txt(im,960,880,'仅展示尚未持有的遗物',23,'#48575A','mm')
  btn(im,1310,922,320,'确认选择',disabled=state!='selected')
 elif state=='empty':
  txt(im,960,425,'已持有全部可掉落遗物',36,anchor='mm');txt(im,960,510,'本次改为获得20金币',34,'#355C67','mm');txt(im,960,580,'金币：50 → 70',28,anchor='mm');btn(im,755,770,410,'继续')
 else:
  im.alpha_composite(asset(relics[0][1]),(470,355));txt(im,1100,420,'已获得：全知之眼',36);txt(im,1100,500,'场上可同时翻开的牌数量 +1',28);txt(im,1100,560,'由1张提升至2张。',26);btn(im,1120,745,410,'继续')
 im.convert('RGB').save(B/(state+'.png'))
(B/'assets.json').write_text(json.dumps({'status':'pending-review','productionEligible':False,'role':'boss-relic-reward-flow-reference','dependencies':deps,'states':['unselected','selected','partial','empty','claimed']},ensure_ascii=False,indent=2),encoding='utf-8')

