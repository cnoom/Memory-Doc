"""Removal flow preview assembled from approved assets; not game implementation."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[3]; B=R/'ImageReview/batches/shop-k04'; B.mkdir(parents=True,exist_ok=True)
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
for selected in [False,True]:
 im=Image.open(R/'ImageReview/batches/shop-k03/mockup_shop_k03_normal.png').convert('RGBA');im.alpha_composite(Image.new('RGBA',im.size,(0,0,0,165)));im.alpha_composite(panel(1660,870),(130,105))
 txt(im,200,168,'移除卡牌',42);txt(im,1705,168,'金币 150',28,anchor='rm');txt(im,200,222,'选择牌库中的一张卡牌；确认后花费75金币，仅移除所选单张。',25)
 txt(im,200,288,'当前牌库 · 4张（示例）',27);txt(im,1705,288,'关闭 ×',24,anchor='rm')
 names=['火球术','火球术','连锁雷','魔力共鸣']
 for i,source in enumerate([1,1,2,3]):
  x=185+i*250;card=Image.open(R/f'ImageReview/batches/shop-k02/card_{source}_review.png').convert('RGBA');im.alpha_composite(card.resize((245,327),Image.Resampling.LANCZOS),(x,350))
  txt(im,x+122,711,f'{names[i]} · 第{i+1}张',21,anchor='mm')
  if selected and i==1:
   draw=ImageDraw.Draw(im);draw.rounded_rectangle((x+5,340,x+240,681),radius=8,outline='#648891',width=4);txt(im,x+122,753,'已选中',24,'#355C67','mm')
 ImageDraw.Draw(im).line((1210,315,1210,810),fill='#87918A',width=2)
 txt(im,1260,360,'移除预览',30)
 for j,s in enumerate(['火球术 · 第2张','仅移除此单张','牌库：4张 → 3张','金币：150 → 75','同名的另一张会保留'] if selected else ['尚未选择卡牌','点击左侧卡牌查看','移除费用：75金币']):txt(im,1260,425+j*57,s,26)
 txt(im,200,853,'取消或关闭不会扣除金币。',23,'#48575A')
 btn(im,1045,862,300,'取消',secondary=True);btn(im,1390,862,320,'确认移除 · 75金币',disabled=not selected)
 im.convert('RGB').save(B/('selected.png' if selected else 'unselected.png'))
(B/'assets.json').write_text(json.dumps({'status':'pending-review','productionEligible':False,'role':'composite-flow-reference','dependencies':deps,'cardCompositions':'ImageReview/batches/shop-k02/card_1_review.png through card_3_review.png','note':'Four library entries are illustrative, not store stock. Existing per-card compositions reused.'},ensure_ascii=False,indent=2),encoding='utf-8')
