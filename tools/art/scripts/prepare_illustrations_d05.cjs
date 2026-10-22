const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),sharp=require(process.argv[2]);
const root=path.resolve(__dirname,'../../..'),dir=path.join(root,'ImageReview/batches/card-illustrations-d05');
const prompts=JSON.parse(fs.readFileSync(path.join(dir,'final-prompts.json'))),reg=JSON.parse(fs.readFileSync(path.join(root,'docs/design/art-inventory/developer-asset-registry.json')));
async function main(){let assets=[],layers=[],labels='';
for(let i=0;i<prompts.length;i++){
 const p=prompts[i],id=`card_${p.type}_${p.slug}_etching_d05`,rel='cards/'+id+'.png',src=path.join(root,'ImageReview',rel),m=await sharp(src).metadata();
 if(m.width!==m.height)throw Error('Expected square');
 assets.push({id,name:p.name,category:'cards',png:rel,width:m.width,height:m.height,status:'generated-awaiting-agent-review',productionEligible:false,sha256:crypto.createHash('sha256').update(fs.readFileSync(src)).digest('hex'),type:p.type});
 const f=reg.items.find(a=>a.id===`border_card_${p.type}_rare_${p.type==='attack'?'r01':'r02'}`),w=f.spec.window;
 const art=await sharp(src).resize(w.width,w.height,{fit:'contain',background:'#EDE8DC'}).toBuffer();
 const base=await sharp({create:{width:960,height:1280,channels:4,background:{r:0,g:0,b:0,alpha:0}}}).composite([{input:art,left:w.x,top:w.y}]).png().toBuffer();
 const masked=await sharp(base).composite([{input:path.join(root,f.spec.windowMask),blend:'dest-in'}]).png().toBuffer();
 const card=await sharp(masked).composite([{input:path.join(root,f.paths.png)}]).png().toBuffer();
 fs.writeFileSync(path.join(dir,p.slug+'-framed.png'),card);
 const x=20+(i%3)*345,y=90+Math.floor(i/3)*520;
 layers.push({input:await sharp(src).resize(280,280).toBuffer(),left:x,top:y});
 layers.push({input:await sharp(card).resize(144,192).toBuffer(),left:x,top:y+312});
 layers.push({input:await sharp(card).resize(96,128).toBuffer(),left:x+165,top:y+312});
 labels+=`<text x="${x}" y="${y+303}">${p.name}</text>`;
}
const svg=`<svg xmlns="http://www.w3.org/2000/svg" width="1050" height="1150"><rect width="1050" height="1150" fill="#dedbce"/><g font-family="Microsoft YaHei" fill="#26352b"><text x="20" y="35" font-size="27">D05 · 学者稀有奖励卡插画</text><text x="20" y="67" font-size="17">独立插画与144 / 96像素装框检查 · 原图不含卡名与规则</text><g font-size="21">${labels}</g></g></svg>`;
await sharp(Buffer.from(svg)).composite(layers).png().toFile(path.join(dir,'review.png'));
fs.writeFileSync(path.join(dir,'assets.json'),JSON.stringify({batch:'card-illustrations-d05',date:'2026-10-11',assets},null,2));console.log(assets.map(a=>a.id).join('\n'));}
main().catch(e=>{console.error(e);process.exitCode=1});


