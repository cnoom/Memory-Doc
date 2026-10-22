"""Upgrade flow preview assembled from approved assets; not game implementation."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path(__file__).resolve().parents[3]; B=R/'ImageReview/batches/event-m01'; B.mkdir(parents=True,exist_ok=True)
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

for state in ['choices','result']:
 im=asset('bg_map_i04');im.alpha_composite(Image.new('RGBA',im.size,(0,0,0,60)))
 im.alpha_composite(panel(1640,860),(140,135))
 # Header is independent UI, paper panel contains only the event content.
 txt(im,160,40,'生命 52 / 60',30,'#F1EEE2');txt(im,960,40,'事件',40,'#F1EEE2','mm');txt(im,1390,40,'金币 '+('65' if state=='result' else '50'),28,'#F1EEE2','mm');btn(im,1580,15,250,'旅途详情')
 txt(im,230,205,'古老日记',44)
 art=asset('ill_event_diary_etching_g01');im.alpha_composite(art.resize((720,480),Image.Resampling.LANCZOS),(225,280))
 ImageDraw.Draw(im).rectangle((222,277,948,763),outline='#48575A',width=3)
 for j,line in enumerate(['你在记忆回廊中发现一本古老的日记。','翻开它，一股力量涌入脑海……']):txt(im,230,815+j*44,line,28)
 ImageDraw.Draw(im).line((1000,270,1000,915),fill='#87918A',width=2)
 if state=='choices':
  txt(im,1060,298,'你将如何选择？',32)
  for y,title,benefit,cost in [(360,'仔细阅读','获得1张随机卡牌','失去3点生命'),(555,'快速翻阅','获得15金币',''),(750,'离开','无事发生','')]:
   btn(im,1070,y,600,title,secondary=title=='离开')
   txt(im,1090,y+130,benefit,27)
   if cost:txt(im,1670,y+130,cost,27,'#8D3D35','rm')
 else:
  txt(im,1070,330,'快速翻阅',36)
  txt(im,1070,415,'事件结果',27,'#48575A')
  txt(im,1070,492,'获得15金币',38,'#355C67')
  txt(im,1070,558,'金币：50 → 65',29)
  txt(im,1070,616,'生命：52 / 60（不变）',27)
  btn(im,1070,788,600,'继续旅途')
 im.convert('RGB').save(B/(state+'.png'))
(B/'assets.json').write_text(json.dumps({'status':'pending-review','productionEligible':False,'role':'event-composite-ui-reference','event':'E01','dependencies':deps,'note':'Approved illustration and UI assets composed without regeneration; choice/result values are examples.'},ensure_ascii=False,indent=2),encoding='utf-8')

