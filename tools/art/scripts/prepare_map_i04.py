import json,shutil,hashlib
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[3]; B=R/'ImageReview/batches/map-i04'; S=Path('C:/Users/Administrator/.codex/generated_images/01a11676-0a6c-7dd3-b7c7-20ab00b8e9c9')
ids={'map_background':'762d2fb6-b633-4183-a80a-a0d87be9ea3d','profile':'f1f02798-3bb2-4995-96bf-60e52832902a','cards':'16a8b04b-8eff-4aca-9884-9fc497a84578','relics':'a76626c7-edee-4e00-9ab2-ca6f50edc63c'}
assets=json.loads((B/'components.json').read_text())['assets'];refs=[]
for slug,uid in ids.items():
 src=B/(slug+'_source.png');shutil.copy2(S/f'exec-{uid}.png',src);im=Image.open(src)
 dest=R/'ImageReview/backgrounds/bg_map_i04.png' if slug=='map_background' else B/f'mockup_journey_{slug}_1920x1080.png'
 ImageOps.fit(im.convert('RGB'),(1920,1080),Image.Resampling.LANCZOS).save(dest)
 a=dict(id=dest.stem,width=1920,height=1080,sourceResolution=list(im.size),native1080p=False,status='pending-review',productionEligible=False)
 if slug=='map_background':a['png']='backgrounds/'+dest.name;assets.append(a)
 else:a['path']=dest.relative_to(R).as_posix();refs.append(a)
for a in assets:
 im=Image.open(R/'ImageReview'/a['png']);assert im.size==(a['width'],a['height'])
 if a['png'].startswith('map/'):assert im.mode=='RGBA' and im.getchannel('A').getextrema()==(0,255)
 a['sha256']=hashlib.sha256((R/'ImageReview'/a['png']).read_bytes()).hexdigest()
(B/'assets.json').write_text(json.dumps(dict(batch='map-i04',assets=assets,references=refs),ensure_ascii=False,indent=2),encoding='utf-8')
# Assemble an accurate graph from independent candidate pieces; review only.
im=Image.open(R/'ImageReview/backgrounds/bg_map_i04.png').convert('RGBA');d=ImageDraw.Draw(im)
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',26)
nodes={'start':(960,938),'boss':(960,160)}; xs=[570,830,1090,1350];ys=[790,630,470,310]
types=[['battle','battle','event','battle'],['event','campfire','battle','shop'],['battle','elite','battle','event'],['battle','event','campfire','battle']]
for row in range(4):
 for c in range(4):nodes[f'{row}-{c}']=(xs[c],ys[row])
edges=[('start',f'0-{c}') for c in range(4)]+[(f'3-{c}','boss') for c in range(4)]
edges += [(f'{row}-{c}',f'{row+1}-{n}') for row in range(3) for c in range(4) for n in range(max(0,c-1),min(4,c+2))]
for a,b in edges:
 color='#252F32' if (a,b)==('start','0-1') else '#648891' if a=='0-1' else '#A0A69D'
 d.line([nodes[a],nodes[b]],fill=color,width=4 if color!='#A0A69D' else 2)
def paste(name,center,size):
 p=Image.open(R/'ImageReview/map'/f'{name}_i04.png').convert('RGBA').resize((size,size),Image.Resampling.LANCZOS);im.alpha_composite(p,(int(center[0]-size/2),int(center[1]-size/2)))
for key,xy in nodes.items():
 state='current' if key=='0-1' else 'selected' if key=='1-1' else 'available' if key in ['1-0','1-2'] else 'completed' if key=='start' else 'future'
 paste('node_ring_'+state,xy,128 if key=='boss' else 112)
 if key=='boss':
  p=Image.open(R/'Assets/UI/enemies/enemy_memory_devourer_etching_f01.png').convert('RGBA');p.thumbnail((80,100));im.alpha_composite(p,(xy[0]-p.width//2,xy[1]-p.height//2))
 else:paste('node_'+('start' if key=='start' else types[int(key[0])][int(key[2])]),xy,92)
d=ImageDraw.Draw(im);d.text((65,22),'生命 52 / 60',font=font,fill='#F1EEE2');d.text((760,22),'第一章 · 记忆回廊',font=font,fill='#F1EEE2');d.text((1660,22),'旅途详情',font=font,fill='#F1EEE2');d.text((765,851),'当前位置',font=font,fill='#252F32');d.text((870,229),'记忆吞噬者',font=font,fill='#252F32');d.text((930,992),'起点',font=font,fill='#252F32')
d.text((100,1032),'战斗：迎战敌人    精英：强敌与遗物    事件：未知遭遇    商店：购买与移除    篝火：休息或升级',font=font,fill='#252F32')
im.convert('RGB').save(B/'map_composed_review.png')
print('14 standalone candidates, 3 detail-page concepts, and deterministic 18-node review saved.')
