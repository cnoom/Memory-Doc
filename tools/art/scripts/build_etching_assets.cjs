// Code-native frames and UI glyphs for the approved V02 art direction.
// AI illustrations are not modified by this exporter. Writes previews only.
const fs=require('node:fs');const path=require('node:path');
const sharp=require(process.argv[2]||'sharp');
const root=path.resolve(__dirname,'../../..');const review=path.join(root,'ImageReview');
const v='etching_b01';const paper='#EDE8DC',ink='#242629';
const entries=[];
function svg(w,h,body){return `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">${body}</svg>`}
async function emit(folder,name,w,h,body,meta={}){const dir=path.join(review,folder);fs.mkdirSync(dir,{recursive:true});const source=svg(w,h,body);fs.writeFileSync(path.join(dir,name+'.svg'),source);await sharp(Buffer.from(source)).png().toFile(path.join(dir,name+'.png'));entries.push({id:name,category:folder,png:`${folder}/${name}.png`,svg:`${folder}/${name}.svg`,width:w,height:h,status:'preview',...meta});}
const colors={attack:'#A44436',skill:'#396577',ability:'#705A80',curse:'#45414A'};
const symbol=`<g fill="none" stroke="#DBD7C9" stroke-linecap="round"><path d="M42 20A35 35 0 0 0 16 50M15 64A35 35 0 0 0 42 89M58 90A35 35 0 0 0 85 65M85 50A35 35 0 0 0 58 20" stroke-width="2.4"/><path d="M50 5v23M50 84v23" stroke-width="1.2"/><path d="m34 74 14-23 18-14-13 24z" stroke-width="1.4"/><path d="m34 74 32-37M42 67l8-7M48 51l10-7" stroke-width=".9"/></g>`;
const sword='<path d="m21 43 24-30 12-5-5 13-28 26M12 39l16 16M20 47l-11 11M7 55l5 6"/>';
const shield='<path d="M32 7c8 7 15 7 23 8v19c-2 12-12 19-23 25C21 53 11 46 9 34V15c8-1 15-1 23-8Z"/><path d="M32 16v32"/>';
const scroll='<path d="M18 10h31c10 0 10 14 0 14H39M18 10c-10 0-10 14 0 14h3v25c0 9 14 9 14 0v-3H12c-8 0-8 13 0 13h20c9 0 13-4 13-13V18M24 30h13M24 37h10"/>';
const icons=[
 ['type_attack','攻击类型',48,colors.attack,`<g transform="translate(0 -2)">${sword}</g>`],
 ['type_skill','技能类型',48,colors.skill,scroll],
 ['type_ability','能力类型',48,colors.ability,'<path d="m32 5 23 26-23 28L9 31Z"/><path d="m32 5 9 26-9 28-9-28Zm-23 26h46"/>'],
 ['type_curse','诅咒类型',48,colors.curse,'<path d="M25 8H10v20m0 13v15h16m14 0h14V39m0-15V8H40M36 7 24 25l13 8-13 24M15 33h7m22-5h8"/>'],
 ['status_burn','灼烧',40,'#A44436','<path d="M34 5c3 15-11 18-6 30 4-1 8-9 8-14 13 12 18 21 12 31-7 10-28 10-35-2-8-13 2-24 8-30-2 12 1 17 4 17C16 23 28 17 34 5Z"/><path d="M31 42c-8 8-3 16 4 15 7-2 6-9 2-13"/>'],
 ['status_freeze','冰冻',40,'#396577','<path d="M32 6v52M10 19l44 26M10 45l44-26M24 11l8 8 8-8M24 53l8-8 8 8M12 28l10-3-1-11M52 36l-10 3 1 11M12 36l10 3-1 11M52 28l-10-3 1-11"/>'],
 ['status_poison','中毒',40,'#4E6C46','<path d="M23 8h18m-15 0v17L12 47c-5 8-1 11 7 11h26c8 0 12-3 7-11L38 25V8M19 40h26"/><circle cx="27" cy="47" r="2"/><circle cx="38" cy="52" r="2"/><circle cx="31" cy="33" r="2"/>'],
 ['status_armor','护甲',40,'#59636B','<path d="m19 8 9 5h8l9-5 12 14-8 8v27H15V30l-8-8Zm9 5 4 9 4-9M21 32h22M21 43h22M32 23v34"/>'],
 ['status_vulnerable','易伤',40,'#805B72','<circle cx="32" cy="32" r="23"/><path d="m34 5-9 22 14 7-9 25M10 32h9m28 0h8M32 9v7m0 32v7"/>'],
 ['status_weak','虚弱',40,'#747044','<path d="M11 13h42M14 22h36M21 31h22M32 29v28m-13-13 13 13 13-13"/>'],
 ['intent_attack','攻击意图',48,'#A44436',sword],
 ['intent_charge','蓄力意图',48,'#976A36','<path d="m36 7-19 27h15l-3 24 20-30H34Z"/><path d="M10 12v8M6 16h8m39 31v9m-4-4h8"/>'],
 ['intent_defend','防御意图',48,'#396577',shield],
 ['intent_special','特殊意图',48,'#705A80','<path d="M21 20c0-16 25-16 25 0 0 10-14 10-14 22"/><circle cx="32" cy="54" r="2"/>'],
 ['intent_berserk','狂暴意图',48,'#933E37','<path d="M5 34s11-17 27-17 27 17 27 17-11 17-27 17S5 34 5 34ZM14 8l8 6m28-6-8 6"/><path d="m33 23-7 12h8l-3 12 10-16h-8Z"/>']
];
(async()=>{
 await emit('cardbacks',`cardback_universal_${v}`,960,1280,`<defs><linearGradient id="ink" x2="1" y2="1"><stop stop-color="#2C3336"/><stop offset="1" stop-color="#242B2F"/></linearGradient></defs><rect x="3" y="3" width="954" height="1274" rx="33" fill="url(#ink)" stroke="#DBD5C5" stroke-width="6"/><rect x="43" y="43" width="874" height="1194" rx="13" fill="none" stroke="#B6B3A3" stroke-opacity=".65" stroke-width="5"/><g transform="translate(160 236) scale(6.4)">${symbol}</g>`,{name:'统一卡背',display:[144,192],alpha:'仅圆角外透明'});
 for(const [type,color]of Object.entries(colors)){
 const body=`<defs><mask id="window"><rect width="960" height="1280" fill="white"/><rect x="64" y="250" width="832" height="430" fill="black"/></mask></defs><g mask="url(#window)"><rect x="3" y="3" width="954" height="1274" rx="33" fill="${paper}" stroke="#E4DECF" stroke-width="6"/><rect x="27" y="27" width="906" height="1226" rx="10" fill="none" stroke="#777B6C" stroke-width="4"/><path d="M68 231h824M68 711h824" stroke="#959889" stroke-width="4"/><rect x="4" y="67" width="26" height="147" fill="${color}"/></g>`;
 await emit('cardframes',`border_card_${type}_${v}`,960,1280,body,{name:{attack:'攻击卡框',skill:'技能卡框',ability:'能力卡框',curse:'诅咒卡框'}[type],typeColor:color,window:{x:64,y:250,width:832,height:430},display:[144,192],alpha:'矩形插画窗和圆角外透明',textBaked:false});
 }
 for(const[id,name,size,color,body]of icons){const native=size*4;await emit('icons',`icon_${id}_${v}`,native,native,`<g transform="scale(${native/64})" fill="none" stroke="${color}" stroke-width="3.3" stroke-linecap="round" stroke-linejoin="round">${body}</g>`,{name,display:[size,size],color,alpha:'透明背景',variant:id==='intent_special'?'通用问号：具体特殊效果必须配意图文字':''});}
 const manifest={batch:'etching-b01',status:'awaiting-user-review',palette:colors,assets:entries};
 fs.mkdirSync(path.join(review,'batches/etching-b01'),{recursive:true});fs.writeFileSync(path.join(review,'batches/etching-b01/components.json'),JSON.stringify(manifest,null,2));
 console.log(JSON.stringify({assets:entries.length,outputs:entries.length*2,manifest:'ImageReview/batches/etching-b01/components.json'}));
})().catch(e=>{console.error(e);process.exitCode=1});

