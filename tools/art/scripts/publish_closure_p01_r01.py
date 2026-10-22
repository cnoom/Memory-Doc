"""Publish P01/Q01/Q02/R01 following the user's 2026-10-15 approval."""
from pathlib import Path
import json,shutil,re,hashlib
R=Path(__file__).resolve().parents[3]; B=R/'ImageReview/batches'; U=R/'Assets/UI'
def copy(src,dst):
 dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists(): assert dst.read_bytes()==src.read_bytes(),dst
 else: shutil.copy2(src,dst)
def write(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
for folder,target in [('v1-closure-p01','mockups/v1-closure-p01'),('fonts-q01','fonts/q01'),('ui-icons-q02','icons-q02'),('motion-r01','mockups/motion-r01')]:
 src=B/folder; dst=U/target;dst.mkdir(parents=True,exist_ok=True)
 for f in src.iterdir():
  if f.is_file():copy(f,R/'ImageReview/_archived/2026-10-15'/folder/f.name)
 for f in src.iterdir():
  if f.is_file() and f.name not in ['README.md','assets.json','manifest.json','index.html']:copy(f,dst/f.name)
 doc=(src/'README.md').read_text(encoding='utf-8')
 doc='> 2026-10-15 用户“可以”确认：本批已正式收录。下文待审字样为制作阶段记录，由本条覆盖。\n\n'+doc
 if folder=='motion-r01':
  doc+='\n正式版index.html及assets目录可一起独立拷贝，路径已重写；仍是设计参考。\n'
 (dst/'README.md').write_text(doc,encoding='utf-8')
 for name in ['assets.json','manifest.json']:
  if (src/name).exists():
   data=json.loads((src/name).read_text(encoding='utf-8-sig'));data.update(status='approved',approvedOn='2026-10-15',approvalQuote='可以',productionEligible=folder in ['fonts-q01','ui-icons-q02'])
   for a in data.get('assets',[])+data.get('files',[]):
    a['status']='approved'
    if 'productionEligible' in a:a['productionEligible']=True
   write(dst/name,data)
   data['publishedDirectory']='Assets/UI/'+target;write(src/name,data)
icons=json.loads((B/'ui-icons-q02/assets.json').read_text(encoding='utf-8'))
for a in icons['assets']:
 for ext in ['png','svg']:
  copy(R/'ImageReview'/a[ext],R/'ImageReview/_archived/2026-10-15/icons'/Path(a[ext]).name)
  copy(R/'ImageReview'/a[ext],U/a[ext])
dst=U/'mockups/motion-r01';html=(B/'motion-r01/index.html').read_text(encoding='utf-8-sig')
for rel in re.findall(r"A\+'([^']+)'",html):copy(U/rel,dst/'assets'/rel)
copy(B/'shop-k02/card_1_review.png',dst/'assets/card_1_review.png')
for name in ['SourceHanSansSC-Regular.otf','SourceHanSansSC-LICENSE.txt']:copy(U/'fonts/q01'/name,dst/'assets'/name)
html=html.replace('../../../Assets/UI/','assets/').replace('../shop-k02/card_1_review.png','assets/card_1_review.png').replace('../fonts-q01/SourceHanSansSC-Regular.otf','assets/SourceHanSansSC-Regular.otf')
(dst/'index.html').write_text(html,encoding='utf-8')
write(dst/'manifest.json',{'status':'approved-design-reference','approvalQuote':'可以','approvedOn':'2026-10-15','productionEligible':False,'files':[{'path':p.relative_to(dst).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in (dst/'assets').rglob('*') if p.is_file()]})
print('Published P01, Q01, Q02, R01; archived original previews.')
