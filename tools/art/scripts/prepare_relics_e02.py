import json,hashlib,shutil
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
folder=ROOT/'ImageReview/batches/relics-e02'
source=Path('C:/Users/Administrator/.codex/generated_images/01a11676-0a6c-7dd3-b7c7-20ab00b8e9c9')
ids=json.loads((folder/'source-ids.json').read_text())
prompts=json.loads((folder/'final-prompts.json').read_text(encoding='utf-8'))
canvas=Image.new('RGB',(1310,1450),'#e7e0d0');draw=ImageDraw.Draw(canvas)
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20)
draw.text((18,12),'E02 剩余15件遗物候选 · 256 / 64 / 48像素检查',fill='#252c2d',font=font)
assets=[]
for i,(p,uid) in enumerate(zip(prompts,ids)):
    aid='relic_'+p['slug']+'_etching_e02'
    original=folder/(aid+'_source.png');shutil.copy2(source/f'exec-{uid}.png',original)
    im=Image.open(original).convert('RGBA');assert im.getchannel('A').getextrema()==(0,255)
    dest=ROOT/'ImageReview/relics'/f'{aid}.png';dest.parent.mkdir(exist_ok=True)
    im.resize((256,256),Image.Resampling.LANCZOS).save(dest)
    x=10+(i%5)*260; y=(i//5)*460
    canvas.paste(im.resize((256,256),Image.Resampling.LANCZOS),(x,62+y),im.resize((256,256),Image.Resampling.LANCZOS))
    draw.text((x+12,325+y),p['name'],fill='#252c2d',font=font)
    for size,offset in [(64,10),(48,100)]:
        icon=im.resize((size,size),Image.Resampling.LANCZOS)
        canvas.paste(icon,(x+offset,365+y),icon)
        draw.text((x+offset,438+y),str(size),fill='#252c2d',font=font)
    assets.append(dict(id=aid,name=p['name'],category='relics',png='relics/'+dest.name,width=256,height=256,rarity=p['rarity'],sourceResolution=list(im.size),status='pending-review',productionEligible=False,sha256=hashlib.sha256(dest.read_bytes()).hexdigest()))
canvas.save(folder/'review.png')
(folder/'assets.json').write_text(json.dumps(dict(batch='relics-e02',assets=assets),ensure_ascii=False,indent=2),encoding='utf-8')
print('15 transparent PNGs exported at 256x256; alpha verified.')
