// Export generated PNGs at the exact 3:4 canvas size without repainting/cropping.
// Compose unchanged illustration and independently rendered UI text for review.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const sharp=require(process.argv[2]);
const revision=process.argv[3]||'c03';if(!['c03','c04'].includes(revision))throw Error('Unsupported revision');
const root=path.resolve(__dirname,'../../..'),review=path.join(root,'ImageReview'),out=path.join(review,'batches/card-production-'+revision);
const W=960,H=1280,assets=[];
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
async function exportAsset(kind,category,id){
 const src=path.join(out,'sources',kind+'_generated.png'),dst=path.join(review,category,id+'.png');
 const m=await sharp(src).metadata();if(m.width*4!==m.height*3||!m.hasAlpha)throw Error('Unexpected source aspect or alpha');
 await sharp(src).resize(W,H,{fit:'contain',kernel:'lanczos3',background:{r:0,g:0,b:0,alpha:0}}).png().toFile(dst);
 const a={id,category,png:category+'/'+id+'.png',width:W,height:H,status:'pending-review',productionEligible:false,scaling:'uniform-only',textBaked:false,source:path.relative(root,src).replaceAll('\\','/'),sourceResolution:[m.width,m.height],exportMethod:'Uniform Lanczos3 downsampling; no cropping, repainting or color changes; generated alpha preserved.',sha256:hash(dst),sourceSha256:hash(src)};assets.push(a);return dst;
}
function internalWindow(raw){
 const visited=new Uint8Array(W*H),queue=new Int32Array(W*H);let begin=0,end=1;queue[0]=640*W+480;visited[queue[0]]=1;
 let l=W,t=H,r=0,b=0;
 while(begin<end){const p=queue[begin++],x=p%W,y=Math.floor(p/W);l=Math.min(l,x);r=Math.max(r,x);t=Math.min(t,y);b=Math.max(b,y);
  for(const [nx,ny]of [[x-1,y],[x+1,y],[x,y-1],[x,y+1]]){if(nx<0||ny<0||nx>=W||ny>=H)continue;let n=ny*W+nx;if(!visited[n]&&raw[n*4+3]<128){visited[n]=1;queue[end++]=n;}}
 }
 if(l<50||r>W-50||t<100||b>H-100||end<100000)throw Error('Illustration alpha hole not enclosed correctly');
 return {x:l,y:t,width:r-l+1,height:b-t+1,pixels:end};
}
async function main(){
 const frame=await exportAsset('frame','cardframes','border_card_attack_ornate_'+revision),back=revision==='c03'?await exportAsset('back','cardbacks','cardback_universal_ornate_c03'):path.join(review,'cardbacks/cardback_universal_ornate_c03.png');
 const raw=await sharp(frame).ensureAlpha().raw().toBuffer(),win=internalWindow(raw);
 // Derive a renderer mask from the actual alpha hole, restricted to the measured opening.
 const mask=Buffer.alloc(W*H*4);
 for(let y=win.y;y<win.y+win.height;y++)for(let x=win.x;x<win.x+win.width;x++){let k=(y*W+x)*4;mask[k]=mask[k+1]=mask[k+2]=255;mask[k+3]=255-raw[k+3];}
 const maskPath=path.join(out,'illustration-window-mask.png');await sharp(mask,{raw:{width:W,height:H,channels:4}}).png().toFile(maskPath);
 assets[0].window=win;assets[0].windowMask=path.relative(root,maskPath).replaceAll('\\','/');
 assets[0].textSafe={title:{x:235,y:153,width:545,height:107},effect:{x:180,y:858,width:600,height:revision==='c04'?280:192}};
 assets[0].note='Measured C03 opening differs from B01; do not use old x64/y250/w832/h430. Art below mask, frame above, UI text last.';
 if(assets[1]){assets[1].universal=true;assets[1].note='All hidden cards use the exact same texture and UVs. No random wear, type color or rarity signals.';}
 const illustration=path.join(root,'Assets/UI/cards/card_attack_daji_etching_b01.png');
 const insert=await sharp(illustration).resize(win.width,win.height,{fit:'contain',background:'#EDE8DC'}).png().toBuffer();
 const backing=await sharp({create:{width:W,height:H,channels:4,background:{r:0,g:0,b:0,alpha:0}}}).composite([{input:insert,left:win.x,top:win.y}]).png().toBuffer();
 const clipped=await sharp(backing).composite([{input:maskPath,blend:'dest-in'}]).png().toBuffer();
 const assembled=await sharp(clipped).composite([{input:frame}]).png().toBuffer();
 fs.writeFileSync(path.join(out,'attack-without-text.png'),assembled);
 const font='Microsoft YaHei,SimSun,sans-serif';
 function labelSvg(width,height,detail=false){
  const k=width/W,ty=212*k, title=detail?32:width===144?15:10.5;
  // Responsive display text: full sentence on inspection view; concise effect on play-size card.
  const lines=detail?`<text x="${480*k}" y="${948*k}" text-anchor="middle" font-size="${26}">造成 <tspan fill="#A44436" font-size="40">6</tspan> 点伤害</text>`:`<text x="${480*k}" y="${954*k}" text-anchor="middle" font-size="${width===144?13:10}"><tspan fill="#A44436" font-size="${width===144?24:18}">6</tspan> 伤害</text>`;
  return Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}"><g fill="#22332A" font-family="${font}"><text x="${250*k}" y="${ty}" dominant-baseline="middle" font-size="${title}">打击</text>${detail?`<text x="${760*k}" y="${ty}" dominant-baseline="middle" text-anchor="end" font-size="15">攻击</text>`:''}${lines}</g></svg>`);
 }
 const renders={};
 for(const width of [300,144,96]){const height=width*4/3;const png=await sharp(assembled).resize(width,height).composite([{input:labelSvg(width,height,width===300)}]).png().toBuffer();fs.writeFileSync(path.join(out,`attack-${width}.png`),png);renders[width]=png;}
 const checker=Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="960" height="1280"><defs><pattern id="c" width="48" height="48" patternUnits="userSpaceOnUse"><rect width="48" height="48" fill="#CBD0C4"/><path d="M0 0h24v24H0Zm24 24h24v24H24Z" fill="#E2E5DB"/></pattern></defs><rect width="960" height="1280" fill="url(#c)"/></svg>`);
 const checkedFull=await sharp(checker).composite([{input:frame}]).png().toBuffer();
 const frameCheck=await sharp(checkedFull).resize(300,400).png().toBuffer();
 const image=(buf,x,y,w,h)=>`<image href="data:image/png;base64,${buf.toString('base64')}" x="${x}" y="${y}" width="${w}" height="${h}"/>`;
 const txt=(s,x,y,n=20,c='#293A31')=>`<text x="${x}" y="${y}" font-family="${font}" font-size="${n}" fill="${c}">${s}</text>`;
 let sheet='<rect width="1500" height="920" fill="#E8E2D3"/>'+txt(revision.toUpperCase()+' · 攻击卡框与统一卡背',34,48,30)+txt('独立无字PNG · 保留透明插画窗 · 原打击插画与文字单独叠加 · 待审',34,84,18);
 sheet+=txt('独立卡框 / 透明格检查',34,130,22)+image(frameCheck,34,151,300,400)+txt('打击 / 组合效果',398,130,22)+image(renders[300],398,151,300,400)+txt('统一卡背',764,130,22)+image(fs.readFileSync(back),764,151,300,400);
 sheet+=txt('图层顺序',1120,177,23)+txt('文字与数值',1120,218,20)+txt('↑ 独立卡框',1120,259,20)+txt('↑ 窗口遮罩',1120,300,20)+txt('↑ 已确认插画',1120,341,20)+txt('贴图画布 960 × 1280',1120,408,19)+txt('保留源图透明外边',1120,445,18);
 sheet+='<path d="M34 589h1432" stroke="#AAB69D"/>'+txt('1080p · 实际144 × 192',34,633,22)+image(renders[144],34,657,144,192)+image(fs.readFileSync(back),199,657,144,192);
 sheet+=txt('720p · 实际96 × 128',430,633,22)+image(renders[96],430,657,96,128)+image(fs.readFileSync(back),546,657,96,128);
 sheet+=txt('小尺寸采用效果摘要“6 伤害”',758,691,21)+txt('完整句子与词条由详情区展示',758,730,21)+txt('字体为本机预览字体，尚未作为发行字体包收录',758,779,17)+txt('两张独立图均无卡名、类型或数值烘焙',758,820,17);
 await sharp(Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="920">${sheet}</svg>`)).png().toFile(path.join(out,'review.png'));
 // Deep/light checker checks expose incorrect transparency without modifying artwork.
 for(const bg of ['#172D23','#EDE8DC'])await sharp({create:{width:640,height:430,channels:4,background:bg}}).composite([{input:await sharp(frame).resize(300,400).toBuffer(),left:10,top:15},{input:await sharp(back).resize(300,400).toBuffer(),left:330,top:15}]).png().toFile(path.join(out,bg==='#172D23'?'alpha-dark.png':'alpha-light.png'));
 const alpha=(x,y)=>raw[(y*W+x)*4+3];if(alpha(480,550)!==0||alpha(0,0)!==0||alpha(500,185)<250||alpha(480,930)<250)throw Error('Alpha checks failed');
 const rawBack=await sharp(back).ensureAlpha().raw().toBuffer();if(rawBack[(640*W+480)*4+3]<250||rawBack[3]!==0)throw Error('Back alpha checks failed');
 fs.writeFileSync(path.join(out,'assets.json'),JSON.stringify({batch:'card-production-'+revision,date:'2026-10-11',status:'pending-review',approvedDirection:'C02',assets,reused:revision==='c04'?['cardback_universal_ornate_c03']:[],helpers:[{path:path.relative(root,maskPath).replaceAll('\\','/'),role:'Derived illustration-window mask, same 960x1280 origin'}],previewFont:'System Microsoft YaHei/SimSun; no font redistributed'},null,2));
 fs.writeFileSync(path.join(out,'validation.json'),JSON.stringify({sourceCanvas:[1086,1448],exportCanvas:[W,H],ratio:'3:4 exact canvas',window:win,frameAlphaSamples:{outside:alpha(0,0),window:alpha(480,550),title:alpha(500,185),effect:alpha(480,930)},backAlphaSamples:{outside:rawBack[3],center:rawBack[(640*W+480)*4+3]},checks:['No source overwrite','Uniform downsampling only','Enclosed actual alpha opening','Original approved illustration unchanged','Separate text render at each size','144x192 and 96x128 review','Deep/light alpha boards'],requiresUserApproval:true,requiresEngineValidation:true},null,2));
 console.log(JSON.stringify({assets:assets.map(a=>a.id),window:win,out},null,2));
}
main().catch(e=>{console.error(e);process.exitCode=1});
