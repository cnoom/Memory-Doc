const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const sharp=require(process.argv[2]),root=path.resolve(__dirname,'../../..');
const dir=path.join(root,'ImageReview/batches/card-production-c05'),W=960,H=1280;
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
async function main(){
const assets=[],layers=[];
const types=[['skill','技能'],['ability','能力'],['curse','诅咒']];
for(let i=0;i<types.length;i++){
 const [type,label]=types[i],id=`border_card_${type}_ornate_c05`,src=path.join(dir,'sources',type+'.png'),dst=path.join(root,'ImageReview/cardframes',id+'.png');
 const m=await sharp(src).metadata();if(!m.hasAlpha||Math.abs(m.width/m.height-.75)>.01)throw Error('Source alpha/aspect invalid');
 await sharp(src).resize(W,H,{fit:'contain',background:{r:0,g:0,b:0,alpha:0}}).png().toFile(dst);
 const raw=await sharp(dst).ensureAlpha().raw().toBuffer(),alpha=(x,y)=>raw[(y*W+x)*4+3];
 if(alpha(0,0)!==0||alpha(480,550)>5||alpha(480,930)<250)throw Error(type+' alpha invalid');
 const seen=new Uint8Array(W*H),queue=[550*W+480];seen[queue[0]]=1;let l=W,t=H,r=0,b=0;
 for(let n=0;n<queue.length;n++){const p=queue[n],x=p%W,y=Math.floor(p/W);l=Math.min(l,x);r=Math.max(r,x);t=Math.min(t,y);b=Math.max(b,y);for(const [nx,ny]of [[x-1,y],[x+1,y],[x,y-1],[x,y+1]]){if(nx<0||ny<0||nx>=W||ny>=H)continue;const k=ny*W+nx;if(!seen[k]&&alpha(nx,ny)<128){seen[k]=1;queue.push(k);}}}
 if(l<80||r>880||t<200||b>850||queue.length<200000)throw Error(type+' opening invalid');
 const mask=Buffer.alloc(W*H*4);for(let y=t;y<=b;y++)for(let x=l;x<=r;x++){const k=(y*W+x)*4;mask[k]=mask[k+1]=mask[k+2]=255;mask[k+3]=255-alpha(x,y);}
 const mp=path.join(dir,type+'-window-mask.png');await sharp(mask,{raw:{width:W,height:H,channels:4}}).png().toFile(mp);
 const a={id,category:'cardframes',png:'cardframes/'+id+'.png',status:'pending-review',productionEligible:false,width:W,height:H,scaling:'uniform-only',textBaked:false,sourceResolution:[m.width,m.height],sha256:hash(dst),sourceSha256:hash(src),window:{x:l,y:t,width:r-l+1,height:b-t+1},windowMask:path.relative(root,mp).replaceAll('\\','/'),textSafe:{title:{x:235,y:153,width:545,height:107},effect:{x:180,y:858,width:600,height:280}}};assets.push(a);
 const x=30+i*390;
 layers.push({input:await sharp(dst).resize(300,400).png().toBuffer(),left:x,top:95});
 for(const [w,top]of [[144,540],[96,765]])layers.push({input:await sharp(dst).resize(w,w*4/3).png().toBuffer(),left:x,top});
}
let svg='<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="920"><rect width="1200" height="920" fill="#d5d9d0"/><g font-family="Microsoft YaHei" fill="#24362d"><text x="30" y="40" font-size="26">C05 · 三类卡框待审 / 沿用扩大描述区</text>';
types.forEach(([type,label],i)=>{let x=30+i*390;svg+=`<text x="${x}" y="80" font-size="22">${label}</text><text x="${x+165}" y="580" font-size="16">144 × 192</text><text x="${x+115}" y="800" font-size="16">96 × 128</text>`;});svg+='</g></svg>';
await sharp(Buffer.from(svg)).composite(layers).png().toFile(path.join(dir,'review.png'));
fs.writeFileSync(path.join(dir,'assets.json'),JSON.stringify({batch:'card-production-c05',date:'2026-10-11',status:'pending-review',assets},null,2));
console.log(JSON.stringify(assets.map(a=>({id:a.id,window:a.window})),null,2));
}main().catch(e=>{console.error(e);process.exitCode=1});
