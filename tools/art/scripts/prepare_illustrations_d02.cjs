const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),sharp=require(process.argv[2]);
const root=path.resolve(__dirname,'../../..'),dir=path.join(root,'ImageReview/batches/card-illustrations-d02');
const registry=JSON.parse(fs.readFileSync(path.join(root,'docs/design/art-inventory/developer-asset-registry.json')));
const prompts=JSON.parse(fs.readFileSync(path.join(dir,'final-prompts.json')));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
async function main(){
 const assets=[],layers=[];
 for(let i=0;i<prompts.length;i++){
  const p=prompts[i],id=`card_${p.type}_${p.slug}_etching_d02`,rel='cards/'+id+'.png',src=path.join(root,'ImageReview',rel),m=await sharp(src).metadata();
  const frame=registry.items.find(a=>a.id===`border_card_${p.type}_ornate_${p.type==='attack'?'c04':'c05'}`),win=frame.spec.window;
  if(m.width!==m.height)throw Error('Expected square illustration');
  assets.push({id,name:p.name,category:'cards',png:rel,width:m.width,height:m.height,status:'pending-review',productionEligible:false,sha256:hash(src),sourceResolution:[m.width,m.height],exportMethod:'Unchanged generated original; opaque bone-white paper background',type:p.type});
  const insert=await sharp(src).resize(win.width,win.height,{fit:'contain',background:'#EDE8DC'}).png().toBuffer();
  const base=await sharp({create:{width:960,height:1280,channels:4,background:{r:0,g:0,b:0,alpha:0}}}).composite([{input:insert,left:win.x,top:win.y}]).png().toBuffer();
  const clipped=await sharp(base).composite([{input:path.join(root,frame.spec.windowMask),blend:'dest-in'}]).png().toBuffer();
  const assembled=await sharp(clipped).composite([{input:path.join(root,frame.paths.png)}]).png().toBuffer();
  fs.writeFileSync(path.join(dir,p.slug+'-framed.png'),assembled);
  const x=30+i*450;
  layers.push({input:await sharp(src).resize(320,320).toBuffer(),left:x,top:110});
  layers.push({input:await sharp(assembled).resize(240,320).toBuffer(),left:x,top:465});
  layers.push({input:await sharp(assembled).resize(144,192).toBuffer(),left:x+270,top:465});
  layers.push({input:await sharp(assembled).resize(96,128).toBuffer(),left:x+270,top:690});
 }
 let svg='<svg xmlns="http://www.w3.org/2000/svg" width="1380" height="850"><rect width="1380" height="850" fill="#dedbce"/><g font-family="Microsoft YaHei" fill="#26352b"><text x="30" y="40" font-size="28">D02 · 第二批普通奖励卡插画 / 待审</text><text x="30" y="73" font-size="17">上：独立插画　下：已确认卡框组合及144 / 96像素预览　卡名与效果由界面独立渲染</text>';
 prompts.forEach((p,i)=>svg+=`<text x="${30+i*450}" y="454" font-size="22">${p.name}</text>`);svg+='</g></svg>';
 await sharp(Buffer.from(svg)).composite(layers).png().toFile(path.join(dir,'review.png'));
 fs.writeFileSync(path.join(dir,'assets.json'),JSON.stringify({batch:'card-illustrations-d02',date:'2026-10-11',status:'pending-review',assets},null,2));
 console.log(JSON.stringify(assets.map(a=>({id:a.id,width:a.width,height:a.height}))));
}main().catch(e=>{console.error(e);process.exitCode=1});

