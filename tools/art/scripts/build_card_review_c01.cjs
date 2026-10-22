// Native SVG card-frame proposals. Existing illustration is composited unchanged.
const fs = require('node:fs'), path = require('node:path');
const sharp = require(process.argv[2]);
const root = path.resolve(__dirname, '../../..');
const review = path.join(root, 'ImageReview');
const out = path.join(review, 'batches/card-refinement-c01');
fs.mkdirSync(out, {recursive:true});
const ink='#293331', paper='#EDE8DC', muted='#929581', red='#A44436';
const wrap = body => `<svg xmlns="http://www.w3.org/2000/svg" width="960" height="1280" viewBox="0 0 960 1280">${body}</svg>`;
const lines = (x,y,n,dx,dy,len,color,opacity=.4) => Array.from({length:n},(_,i)=>`<path d="M${x+i*dx} ${y+i*dy}l${len} 0" stroke="${color}" stroke-width="2" opacity="${opacity}"/>`).join('');
const corners = (color) => `<g fill="none" stroke="${color}" stroke-width="4"><path d="M90 180V80h110M760 80h110v100M90 1100v100h110M760 1200h110v-100"/><path d="M105 160v-65h65M790 95h65v65M105 1120v65h65M790 1185h65v-65"/></g>`;
const feather = `<path d="M405 750 488 556 594 477 548 620Z" fill="none" stroke="${paper}" stroke-width="7"/><path d="M385 787 594 477M443 695l68-38M468 638l68-42M497 573l49-29" fill="none" stroke="${paper}" stroke-width="4"/>`;
function frame(variant) {
 const common=`<defs><mask id="window"><rect width="960" height="1280" fill="white"/><rect x="64" y="250" width="832" height="430" fill="black"/></mask><linearGradient id="page" x2=".85" y2="1"><stop stop-color="#F1EDE1"/><stop offset="1" stop-color="#DED8C5"/></linearGradient></defs>`;
 const base=`<rect x="4" y="4" width="952" height="1272" rx="28" fill="${ink}"/><path d="M18 16H935V1248L910 1262H18Z" fill="url(#page)"/><path d="M32 32H918V1237H32Z" fill="none" stroke="${muted}" stroke-width="3"/><path d="M923 48v1163m8-1150v1139" stroke="#B2B39B" stroke-width="3"/>`;
 const windowTrim=`<path d="M56 241H904V690H56Z" fill="none" stroke="${ink}" stroke-width="6"/><path d="M75 226H885M75 704H885" stroke="${muted}" stroke-width="3"/><path d="M56 280v-39h39m770 0h39v39M56 651v39h39m770 0h39v-39" fill="none" stroke="${red}" stroke-width="8"/>`;
 const stitches=Array.from({length:8},(_,i)=>`<circle cx="37" cy="${308+i*102}" r="6" fill="#556055"/><path d="M22 ${298+i*102}l30 20" stroke="#B5B295" stroke-width="5"/>`).join('');
 const footer=`<path d="M118 1138h252m220 0h252" stroke="${muted}" stroke-width="3"/><path d="m430 1138 25-11 25 11-25 11Zm50 0 25-11 25 11-25 11Z" fill="none" stroke="${muted}" stroke-width="3"/><path d="M115 1180h144m-144 13h95" stroke="${muted}" stroke-width="2" opacity=".45"/>`;
 const body= variant==='a' ? `${base}<path d="M13 40h42v1180H13Z" fill="#76816C" opacity=".32"/>${stitches}<path d="M94 69 864 61 881 198 89 206Z" fill="#C5BEA6" opacity=".6"/><path d="M80 57 868 70 859 195 91 182Z" fill="#F6F0E3" stroke="#A6A58D" stroke-width="3"/><path d="M84 59h26v125H90Z" fill="${red}"/><path d="M720 71 793 73 788 109 716 107Z" fill="#B0B69A" opacity=".65"/>${windowTrim}<path d="M100 752h760v329H100Z" fill="#F2EEE3" stroke="#C5C4AF" stroke-width="3"/><path d="M112 764h22v21m704-21h10v21M112 1054v13h22m714-13v13h-22" fill="none" stroke="${muted}" stroke-width="3"/>${footer}<path d="m858 1193 53-9-1 64-52-2Z" fill="#D3CCB6"/><path d="m858 1193 52 55-5-59Z" fill="#F5EFDF" stroke="#A4A38A" stroke-width="2"/>` : `${base}<path d="M18 16H935V211H18Z" fill="${ink}"/><path d="M61 49H895V184H61Z" fill="none" stroke="#A9AD96" stroke-width="3"/><path d="M78 64h49m-49 0v36m804-36h-49m49 0v36M78 169h49m-49 0v-36m804 36h-49m49 0v-36" fill="none" stroke="${paper}" stroke-width="4"/><path d="M18 210h917" stroke="${red}" stroke-width="12"/>${windowTrim}<path d="M83 744h794v342H83Z" fill="#F6F1E6"/><path d="M110 770v280m740-280v280" stroke="#A5AA92" stroke-width="3"/><path d="M140 729h680M140 1100h680" stroke="${ink}" stroke-width="3"/>${lines(140,1114,5,0,6,680,muted,.22)}${footer}<path d="M37 243v936m872-936v936" stroke="${ink}" stroke-width="3"/>${Array.from({length:14},(_,i)=>`<path d="M30 ${255+i*64}l14 14m858-14 14 14" stroke="${muted}" stroke-width="3"/>`).join('')}`;
 return wrap(common+`<g mask="url(#window)">${body}</g>`);
}
function back(variant){
 let body=`<rect x="4" y="4" width="952" height="1272" rx="28" fill="${ink}" stroke="#D5D0BF" stroke-width="7"/><rect x="35" y="35" width="890" height="1210" rx="10" fill="none" stroke="#A3AA94" stroke-width="3"/>${corners('#A3AA94')}`;
 if(variant==='a') body+=`<path d="M26 36h31v1208H26Z" fill="#596351"/>${Array.from({length:11},(_,i)=>`<circle cx="42" cy="${126+i*102}" r="6" fill="#151E1B"/><path d="M29 ${117+i*102}l26 18" stroke="#B9B89F" stroke-width="4"/>`).join('')}<path d="M176 260 759 246 779 1022 186 1037Z" fill="none" stroke="#959E88" stroke-width="3"/><path d="M198 281 740 268 758 1000 208 1013Z" fill="none" stroke="#66745F" stroke-width="3"/><circle cx="480" cy="640" r="216" fill="#23302B" stroke="#818D76" stroke-width="3"/><circle cx="480" cy="640" r="177" fill="none" stroke="${paper}" stroke-width="6" stroke-dasharray="240 38"/>${feather}<path d="M307 341h346m-304 18h262M307 935h346m-304 18h262" stroke="#9DA48E" stroke-width="3"/><path d="m470 323 10-16 10 16-10 16Zm0 657 10-16 10 16-10 16Z" fill="#B6B69F"/>`;
 else body+=`<path d="M480 207 807 640 480 1073 153 640Z" fill="none" stroke="#89957D" stroke-width="3"/><path d="M480 245 776 640 480 1035 184 640Z" fill="none" stroke="#566951" stroke-width="7"/><circle cx="480" cy="640" r="259" fill="#273731" stroke="#B7B9A1" stroke-width="4"/><circle cx="480" cy="640" r="224" fill="none" stroke="#829277" stroke-width="2"/>${Array.from({length:48},(_,i)=>`<path d="M480 396v${i%4===0?20:9}" transform="rotate(${i*7.5} 480 640)" stroke="#B8BCA4" stroke-width="3"/>`).join('')}<circle cx="480" cy="640" r="190" fill="none" stroke="${paper}" stroke-width="6" stroke-dasharray="255 43"/>${feather}<path d="M480 124v142m0 748v142M109 640h96m550 0h96" stroke="#B4B8A0" stroke-width="3"/><path d="M380 139h200m-169 16h138M380 1141h200m-169-16h138" stroke="#829277" stroke-width="3"/>`;
 return wrap(body);
}
const uri=file=>'data:image/png;base64,'+fs.readFileSync(file).toString('base64');
const svguri=svg=>'data:image/svg+xml;base64,'+Buffer.from(svg).toString('base64');
const img=(href,x,y,w,h)=>`<image href="${href}" x="${x}" y="${y}" width="${w}" height="${h}"/>`;
const text=(s,x,y,size=20,color=ink)=>`<text x="${x}" y="${y}" font-family="Microsoft YaHei,SimSun,sans-serif" font-size="${size}" fill="${color}">${s}</text>`;
async function main(){
 const assets=[];
 for(const v of ['a','b']) for(const [cat,id,svg] of [['cardframes','border_card_attack_journal_c01'+v,frame(v)],['cardbacks','cardback_universal_journal_c01'+v,back(v)]]){
   const base=path.join(review,cat,id);fs.writeFileSync(base+'.svg',svg);await sharp(Buffer.from(svg)).png().toFile(base+'.png');
   assets.push({id,category:cat,status:'pending-review',png:cat+'/'+id+'.png',svg:cat+'/'+id+'.svg',width:960,height:1280,...(cat==='cardframes'?{window:{x:64,y:250,width:832,height:430},textBaked:false}:{universal:true,identityIndependent:true})});
 }
 const art=uri(path.join(review,'cards/card_attack_daji_etching_b01.png'));
 function card(frameUri,dark=false){return wrap(`<rect x="3" y="3" width="954" height="1274" rx="28" fill="${paper}"/>${img(art,64,250,832,430)}${img(frameUri,0,0,960,1280)}${text('打击',130,155,72,dark?paper:ink)}${text('攻击',715,151,42,dark?'#C9CAB6':'#666E60')}${text('造成',150,882,60)}${text('6',315,890,94,red)}${text('点伤害',399,882,60)}`);}
 const variants=[{title:'原版 B01',note:'当前候选 · 单线分区',frame:'cardframes/border_card_attack_etching_b01.png',back:'cardbacks/cardback_universal_etching_b01.png'}, {title:'A · 贴页手记',note:'纸层 / 装订 / 贴签 / 折角',frame:assets[0].png,back:assets[1].png},{title:'B · 版画藏书',note:'深墨题签 / 窗口刻线 / 藏书印',frame:assets[2].png,back:assets[3].png}];
 let body=`<rect width="1680" height="1020" fill="#E5E0D3"/>${text('卡面与卡背 · 细节方向对照',48,62,34)}${text('C01  /  待审方向稿  /  沿用同一张打击插画；文字为独立排版示例',48,99,18,'#656D60')}`;
 for(let i=0;i<3;i++){
  let x=40+i*548, v=variants[i], front=svguri(card(uri(path.join(review,v.frame)),i===2)), reverse=uri(path.join(review,v.back));
  body+=`<rect x="${x}" y="132" width="528" height="839" rx="8" fill="#F2EEE3" stroke="#BABCA9"/>${text(v.title,x+24,178,28)}${text(v.note,x+24,211,18,'#69715F')}${img(front,x+24,239,240,320)}${img(reverse,x+290,279,204,272)}${text('卡面放大',x+24,591,16)}${text('统一卡背',x+300,591,16)}<path d="M${x+24} 614h480" stroke="#B5BAA5"/>${text('1080p 实际尺寸 144 × 192',x+24,650,18)}${img(front,x+24,676,144,192)}${img(reverse,x+186,676,144,192)}${text('720p',x+374,712,15)}${img(front,x+376,738,96,128)}${text('装饰集中边缘；插画窗与正文保持独立',x+24,931,16,'#69715F')}`;
 }
 const sheet=`<svg xmlns="http://www.w3.org/2000/svg" width="1680" height="1020">${body}</svg>`;
 fs.writeFileSync(path.join(out,'comparison.svg'),sheet);await sharp(Buffer.from(sheet)).png().toFile(path.join(out,'comparison.png'));
 const checks=[];
 for(const a of assets){const f=path.join(review,a.png),meta=await sharp(f).metadata(); const pixels=await sharp(f).ensureAlpha().raw().toBuffer();const alpha=(x,y)=>pixels[(y*960+x)*4+3];checks.push({id:a.id,width:meta.width,height:meta.height,hasAlpha:meta.hasAlpha,cornerAlpha:alpha(0,0),windowAlpha:a.category==='cardframes'?alpha(480,400):null});if(meta.width!==960||meta.height!==1280||alpha(0,0)!==0||(a.category==='cardframes'&&alpha(480,400)!==0))throw Error('Asset validation failed: '+a.id);}
 fs.writeFileSync(path.join(out,'assets.json'),JSON.stringify({date:'2026-10-07',status:'pending-review',scope:'Attack frame and universal back direction proposals only. Other types await direction choice.',assets},null,2));
 fs.writeFileSync(path.join(out,'validation.json'),JSON.stringify(checks,null,2));
 fs.writeFileSync(path.join(out,'README.md'),'# 卡面与卡背精修 C01\n\n2026-10-07，待审方向稿。用户反馈：卡背和卡面有一点单调，特别是卡面。\n\nB01 四类卡框和统一卡背：需要修改；三张插画仍待审，未获批准。\n\n本轮以攻击卡框验证 A 贴页手记与 B 版画藏书两个方向，未扩展四类型全套。插画沿用 B01 原文件，示例卡名与数值只存在于组合预览，不烘焙到独立资产。透明插画窗保持 x64/y250/w832/h430；3:4 源尺寸960×1280。\n\nA：装订侧脊、错位标题纸、轻胶带、效果贴页、折角；卡背为手记封皮。\nB：深墨标题栏、版画边刻、正文贴页；卡背为断环羽笔藏书印。\n\n所有实例共用同一卡背，装饰不承载隐藏类型或稀有度信息。未覆盖 B01、未移动旧候选，未发布至 Assets/UI。方向经用户确认后再收口四类卡框与实际战斗组合。\n');
 console.log(JSON.stringify({out,assets:assets.length,checks},null,2));
}
main().catch(e=>{console.error(e);process.exitCode=1});
