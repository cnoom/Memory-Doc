// Refine existing native vector panels, preserving dimensions and separate text layers.
const fs=require('node:fs'),path=require('node:path'),sharp=require(process.argv[2]);
const root=path.resolve(__dirname,'../../..'),review=path.join(root,'ImageReview'),out=path.join(review,'batches/panel-refinement-a03');fs.mkdirSync(out,{recursive:true});
const assets=[];
const existingManifest=path.join(out,'assets.json');
if(fs.existsSync(existingManifest)&&JSON.parse(fs.readFileSync(existingManifest,'utf8').replace(/^\uFEFF/,'')).status==='approved')throw Error('A03 is approved. Create a new version instead of overwriting published art or metadata.');
const svg=(w,h,b)=>`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">${b}</svg>`;
function decoration(w,h,dark){
 const edge=dark?'#A7B39A':'#6C7E66', faint=dark?'#687E68':'#ACB095';
 const leaf=`<g fill="none" stroke="${edge}" stroke-width="1.25"><path d="M8 29Q12 12 30 8M9 23Q6 13 12 11Q16 16 9 23ZM14 17Q14 6 22 7Q23 13 14 17ZM21 12Q25 4 30 8Q29 12 21 12Z"/><path d="M5 32V5h27" stroke-width="1.7"/><path d="M4 30V4h26" stroke="${faint}"/></g>`;
 let x=`<rect x="10" y="10" width="${w-20}" height="${h-20}" fill="none" stroke="${edge}" stroke-width="1.2"/><rect x="14" y="14" width="${w-28}" height="${h-28}" fill="none" stroke="${faint}" stroke-opacity=".5" stroke-width=".6"/>`;
 x+=leaf+`<g transform="translate(${w} 0) scale(-1 1)">${leaf}</g><g transform="translate(0 ${h}) scale(1 -1)">${leaf}</g><g transform="translate(${w} ${h}) scale(-1 -1)">${leaf}</g>`;
 // Tiny book-edge hatch marks stay inside the nine-slice border.
 for(let i=42;i<h-40;i+=7)x+=`<path d="M5 ${i}l3-3m${w-14} 3 3-3" stroke="${faint}" stroke-opacity=".5" stroke-width=".6"/>`;
 return x;
}
async function emit(a,body){const id=a.id.replace(/_a0[12]$/,'_a03'),f=a.category+'/'+id;const data=svg(a.width,a.height,body);fs.mkdirSync(path.join(review,a.category),{recursive:true});fs.writeFileSync(path.join(review,f+'.svg'),data);await sharp(Buffer.from(data)).png().toFile(path.join(review,f+'.png'));assets.push({...a,id,png:f+'.png',svg:f+'.svg',status:'pending-review',publishedPng:undefined,publishedSvg:undefined,approvedOn:undefined,approvalScope:undefined,replaces:a.id,textBaked:false});}
const read=p=>JSON.parse(fs.readFileSync(path.join(review,p),'utf8').replace(/^\uFEFF/,''));
async function main(){
 const source=[...read('batches/foundation-a01/assets.json').assets.filter(a=>a.category==='panels'),...read('batches/core-a02/assets.json').assets.filter(a=>['panels','bars'].includes(a.category))];
 if(source.length!==14)throw Error('Expected fourteen assets');
 for(const a of source){
  const w=a.width,h=a.height,dark=/ink|enemy|intent/.test(a.id);
  const color=dark?'#273A32':'#EAE3CD', light=dark?'#344A3E':'#F5EEDC';
  let b='';
  if(a.category==='bars'){
   const fill=/critical/.test(a.id)?'#B96049':/filled/.test(a.id)?'#91B1AB':/health_fill/.test(a.id)?'#B7765E':'#17271F';
   b=`<rect x="1" y="1" width="${w-2}" height="${h-2}" rx="1" fill="${fill}" stroke="#718673" stroke-width="1"/><path d="M3 3H${w-3}" stroke="#D1D9BB" stroke-opacity=".45"/><path d="M3 ${h-3}H${w-3}" stroke="#101F18" stroke-opacity=".6"/>`;
   if(h>16)b+=`<path d="M4 10V4h9m${w-26} 0h9v6M4 ${h-10}v6h9m${w-26} 0h9v-6" stroke="#D4D9BA" stroke-opacity=".5" fill="none"/>`;
   if(/health_track/.test(a.id))b+=`<path d="M1 0v${h}M${w-1} 0v${h}" stroke="#B8BE9F" stroke-width="2"/>`;
  }else if(h<90){
   b=`<defs><linearGradient id="paper" x2="0" y2="1"><stop stop-color="${light}"/><stop offset="1" stop-color="${color}"/></linearGradient></defs><path d="M1 4 ${w-10} 1 ${w-1} 9 ${w-9} ${h-3} 6 ${h-1}Z" fill="#98A188"/><path d="M1 1H${w-4}L${w-13} ${h/2} ${w-4} ${h-5}H1Z" fill="url(#paper)"/><path d="M12 9H${w-29}M12 ${h-13}H${w-29}" stroke="${dark?'#8FA68A':'#7E8C6E'}" stroke-width="1"/><path d="M6 5v${h-16}" stroke="${dark?'#9CB294':'#6F8367'}" stroke-width="4"/><path d="M17 15v10m0 13v10" stroke="${dark?'#8FA68A':'#7E8C6E'}"/>`;
  }else{
   b=`<defs><linearGradient id="paper" x2="1" y2="1"><stop stop-color="${light}"/><stop offset=".5" stop-color="${color}"/><stop offset="1" stop-color="${dark?'#203028':'#D8D2B9'}"/></linearGradient></defs><path d="M3 5 ${w-7} 1 ${w-1} ${h-9} ${w-9} ${h-1} 1 ${h-5}Z" fill="${dark?'#17241E':'#8F9D7E'}"/><rect x="3" y="3" width="${w-9}" height="${h-9}" rx="2" fill="url(#paper)"/><path d="M${w-3} 13v${h-26}M13 ${h-3}h${w-26}" stroke="${dark?'#819174':'#B9B79B'}" stroke-width="1"/>${decoration(w-3,h-3,dark)}`;
   if(a.id.includes('hud_')){
    b+=`<path d="M20 42V${h-40}" stroke="${dark?'#7C9379':'#8B9B7D'}" stroke-width="2"/>`;
    for(let y=52;y<h-40;y+=31)b+=`<circle cx="19" cy="${y}" r="2.4" fill="${dark?'#15251D':'#7C8A6D'}"/><path d="M13 ${y-4}l12 8" stroke="${dark?'#B4B69A':'#DDD8BD'}" stroke-width="1.2"/>`;
    const mid=w/2;b+=`<path d="M${mid-46} ${h-22}h29m34 0h29m-58 0 12-5 12 5-12 5Z" stroke="${dark?'#92A387':'#8B997B'}" fill="none" stroke-width="1"/>`;
   }
  }
  await emit(a,b);
 }
 const uri=f=>'data:image/png;base64,'+fs.readFileSync(path.join(review,f)).toString('base64');
 const img=(f,x,y,w,h)=>`<image href="${uri(f)}" x="${x}" y="${y}" width="${w}" height="${h}"/>`;
 const text=(s,x,y,n=20,c='#263A30')=>`<text x="${x}" y="${y}" font-family="Microsoft YaHei,sans-serif" font-size="${n}" fill="${c}">${s}</text>`;
 let body='<rect width="1500" height="1040" fill="#E8E2D2"/>'+text('面板与战斗信息 · 细节精修 A03',36,51,31)+text('左：原版　　右：修改稿 · 纸层、装订与版画角饰；文字均为独立排版示例',36,88,18);
 for(let col=0;col<2;col++){
  const x=32+col*748;const file=id=>{let a=source.find(a=>a.id===id);return col?assets.find(b=>b.replaces===id).png:a.png;};
  body+=`<rect x="${x}" y="115" width="716" height="895" rx="6" fill="#F0EADB" stroke="#BDC5AC"/>`+text(col?'A03 · 手记细节版':'A01 / A02 · 原版',x+22,155,25);
  ['paper','tooltip','ink'].forEach((v,i)=>{body+=img(file(`panel_${v}_a01`),x+24+i*226,181,190,190)+text(['纸白面板','提示面板','深墨面板'][i],x+24+i*226,400,18);});
  body+=img(file('hud_enemy_base_a02'),x+24,430,660,232)+img(file('hud_name_tag_a02'),x+60,454,300,46)+text('混乱史莱姆',x+82,486,24);
  body+=text('生命',x+64,533,18,'#E7E4CC')+text('35 / 35',x+563,533,19,'#E7E4CC')+img(file('hud_health_track_a02'),x+130,520,400,12)+img(file('hud_health_fill_a02'),x+132,522,394,8);
  body+=text('行动条',x+64,577,19,'#E7E4CC');
  for(let k=0;k<8;k++)body+=img(file(k<5?'hud_action_filled_a02':'hud_action_empty_a02'),x+163+k*49,554,42,24);
  body+=img(file('hud_intent_tag_a02'),x+61,588,400,50)+text('下次行动 · 攻击 6',x+81,620,19,'#E7E4CC');
  body+=img(file('hud_player_base_a02'),x+24,697,362,180)+text('学者',x+59,736,24)+text('生命   60 / 60',x+59,780,21)+text('格挡   0',x+59,821,20);
  body+=text('姓名签与意图签同步精修',x+417,735,19)+text('生命槽增加内凹边沿',x+417,777,19)+text('行动格增加压印端饰',x+417,819,19);
  body+=text('空槽',x+28,924,17)+text('累计',x+242,924,17)+text('临界',x+456,924,17);
  ['empty','filled','critical'].forEach((v,i)=>body+=img(file(`hud_action_${v}_a02`),x+78+i*214,899,108,48));
  body+=text('紧凑底板沿用同一装饰规则；本轮未发布',x+24,983,17,'#687862');
 }
 fs.writeFileSync(path.join(out,'comparison.svg'),svg(1500,1040,body));await sharp(Buffer.from(svg(1500,1040,body))).png().toFile(path.join(out,'comparison.png'));
 for(const a of assets){const m=await sharp(path.join(review,a.png)).metadata();if(m.width!==a.width||m.height!==a.height||!m.hasAlpha)throw Error(a.id);}
 fs.writeFileSync(path.join(out,'assets.json'),JSON.stringify({batch:'panel-refinement-a03',status:'pending-review',assets},null,2));
 fs.writeFileSync(path.join(out,'README.md'),'# 面板与战斗信息 A03\n\n2026-10-07，用户反馈原A01/A02的14项面板、HUD、条形「感觉有点素」，本轮原生SVG精修。原候选记为需要修改；新增14项仍待审，不覆盖旧文件或发布。\n\n增加纸层、版画植物角饰、装订边与刻槽端饰，尺寸保持原规格。三种256方形面板保持32px九宫格边界，角饰限制在切片角区；实际伸缩、长文本与组合版面仍需进一步验收。HUD的装饰侵占边缘，接入时正文从x=36起，并避开上下角饰及页脚。比较图仅包含示例文字，数值均非固定规则。其他已通过的书体、按钮与控件不改。\n');
 console.log('14 A03 candidates and before/after comparison exported; dimensions/alpha checked.');
}
main().catch(e=>{console.error(e);process.exitCode=1});

