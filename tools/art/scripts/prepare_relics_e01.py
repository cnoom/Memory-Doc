import json,hashlib,shutil
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
folder=ROOT/'ImageReview/batches/relics-e01'
source=Path('C:/Users/Administrator/.codex/generated_images/01a11676-0a6c-7dd3-b7c7-20ab00b8e9c9')
ids=['5f42c158-2f5d-4519-8e87-81abed27b330','feb36fec-f78c-4a34-b060-e8bf61eadb97','76c10caa-524c-4146-8f31-f183d36d5f82','2a400090-f80d-466d-803a-875085c2c377']
prompts=json.loads((folder/'final-prompts.json').read_text(encoding='utf-8'))
canvas=Image.new('RGB',(1040,520),'#e7e0d0');draw=ImageDraw.Draw(canvas)
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20)
draw.text((18,12),'E01 遗物首批候选 · 256 / 64 / 48像素检查',fill='#252c2d',font=font)
assets=[]
for i,(p,uid) in enumerate(zip(prompts,ids)):
    aid='relic_'+p['slug']+'_etching_e01'
    original=folder/(aid+'_source.png');shutil.copy2(source/f'exec-{uid}.png',original)
    im=Image.open(original).convert('RGBA');assert im.getchannel('A').getextrema()==(0,255)
    dest=ROOT/'ImageReview/relics'/f'{aid}.png';dest.parent.mkdir(exist_ok=True)
    im.resize((256,256),Image.Resampling.LANCZOS).save(dest)
    x=10+i*260
    canvas.paste(im.resize((256,256),Image.Resampling.LANCZOS),(x,62),im.resize((256,256),Image.Resampling.LANCZOS))
    draw.text((x+12,325),p['name'],fill='#252c2d',font=font)
    for size,offset in [(64,10),(48,100)]:
        icon=im.resize((size,size),Image.Resampling.LANCZOS)
        canvas.paste(icon,(x+offset,365),icon)
        draw.text((x+offset,438),str(size),fill='#252c2d',font=font)
    assets.append(dict(id=aid,name=p['name'],category='relics',png='relics/'+dest.name,width=256,height=256,rarity=p['rarity'],sourceResolution=list(im.size),status='pending-review',productionEligible=False,sha256=hashlib.sha256(dest.read_bytes()).hexdigest()))
canvas.save(folder/'review.png')
(folder/'assets.json').write_text(json.dumps(dict(batch='relics-e01',assets=assets),ensure_ascii=False,indent=2),encoding='utf-8')
print('4 transparent PNGs exported at 256x256; alpha verified.')
