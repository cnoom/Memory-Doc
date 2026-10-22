const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),sharp=require(process.argv[2]);
const root=path.resolve(__dirname,'../../..'),dir=path.join(root,'ImageReview/batches/card-rarity-r02'),W=960,H=1280;
async function main(){const assets=[],layers=[];let labels='';
for(const [i,type,rarity,name]of [[0,'skill','uncommon','技能 · 罕见'],[1,'skill','rare','技能 · 稀有'],[2,'ability','uncommon','能力 · 罕见'],[3,'ability','rare','能力 · 稀有']]){
 const id=`border_card_${type}_${rarity}_r02`,dst=rarity==='common'?path.join(root,'Assets/UI/cardframes/border_card_attack_ornate_c04.png'):path.join(root,'ImageReview/cardframes',id+'.png');
 if(rarity!=='common'){const src=path.join(dir,'sources',type+'-'+rarity+'.png'),m=await sharp(src).metadata();if(!m.hasAlpha||m.width*4!==m.height*3)throw Error('Source geometry');await sharp(src).resize(W,H).png().toFile(dst);}
 const raw=await sharp(dst).ensureAlpha().raw().toBuffer(),alpha=(x,y)=>raw[(y*W+x)*4+3];if(alpha(480,550)>5||alpha(0,0)!==0||alpha(480,930)<250)throw Error('Alpha invalid');
 const seen=new Uint8Array(W*H),queue=[550*W+480];seen[queue[0]]=1;let l=W,t=H,r=0,b=0;
 for(let n=0;n<queue.length;n++){const k=queue[n],x=k%W,y=Math.floor(k/W);l=Math.min(l,x);r=Math.max(r,x);t=Math.min(t,y);b=Math.max(b,y);for(const [nx,ny]of [[x-1,y],[x+1,y],[x,y-1],[x,y+1]]){if(nx<0||ny<0||nx>=W||ny>=H)continue;const z=ny*W+nx;if(!seen[z]&&alpha(nx,ny)<128){seen[z]=1;queue.push(z);}}}
 if(l<80||r>880||t<200||b>850)throw Error('Window not enclosed');
 const mask=Buffer.alloc(W*H*4);for(let y=t;y<=b;y++)for(let x=l;x<=r;x++){let k=(y*W+x)*4;mask[k]=mask[k+1]=mask[k+2]=255;mask[k+3]=255-alpha(x,y);}
 const maskpath=path.join(dir,type+'-'+rarity+'-window-mask.png');await sharp(mask,{raw:{width:W,height:H,channels:4}}).png().toFile(maskpath);
 if(rarity!=='common')assets.push({id,category:'cardframes',png:'cardframes/'+id+'.png',rarity,type,width:W,height:H,status:'pending-review',productionEligible:false,sha256:crypto.createHash('sha256').update(fs.readFileSync(dst)).digest('hex'),window:{x:l,y:t,width:r-l+1,height:b-t+1},windowMask:path.relative(root,maskpath).replaceAll('\\','/'),textSafe:{title:{x:235,y:153,width:545,height:107},effect:{x:180,y:858,width:600,height:280}},scaling:'uniform-only'});
 const insert=await sharp(path.join(root,type==='skill'?'Assets/UI/cards/card_skill_sudu_etching_d01.png':'Assets/UI/cards/card_ability_quanshenguanzhu_etching_d01.png')).resize(r-l+1,b-t+1,{fit:'contain',background:'#EDE8DC'}).toBuffer();
 const base=await sharp({create:{width:W,height:H,channels:4,background:{r:0,g:0,b:0,alpha:0}}}).composite([{input:insert,left:l,top:t}]).png().toBuffer();
 const clipped=await sharp(base).composite([{input:maskpath,blend:'dest-in'}]).png().toBuffer();
 const full=await sharp(clipped).composite([{input:dst}]).png().toBuffer();
 const x=25+i*330;labels+=`<text x="${x}" y="105">${name}</text>`;
 layers.push({input:await sharp(full).resize(300,400).toBuffer(),left:x,top:125});
 layers.push({input:await sharp(full).resize(144,192).toBuffer(),left:x,top:555});
 layers.push({input:await sharp(full).resize(96,128).toBuffer(),left:x+170,top:555});
 fs.writeFileSync(path.join(dir,type+'-'+rarity+'-framed.png'),full);
}
let svg=`<svg xmlns="http://www.w3.org/2000/svg" width="1340" height="790"><rect width="1340" height="790" fill="#dcd9cc"/><g font-family="Microsoft YaHei" fill="#26382c"><text x="30" y="40" font-size="27">R02 · 技能与能力稀有度卡框</text><text x="30" y="70" font-size="17">类型色带与稀有度边框分开 · 插画仅作对比，不改变实际稀有度 · 下排144 / 96像素</text><g font-size="23">${labels}</g></g></svg>`;
await sharp(Buffer.from(svg)).composite(layers).png().toFile(path.join(dir,'review.png'));
fs.writeFileSync(path.join(dir,'assets.json'),JSON.stringify({batch:'card-rarity-r02',status:'pending-review',assets,reused:[]},null,2));console.log(JSON.stringify(assets.map(a=>({id:a.id,window:a.window}))));}
main().catch(e=>{console.error(e);process.exitCode=1});
