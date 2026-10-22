// Review board from unchanged native icon assets. No new icon designs.
const fs=require('node:fs'),path=require('node:path'),sharp=require(process.argv[2]);
const root=path.resolve(__dirname,'../../..'),out=path.join(root,'ImageReview/batches/etching-b01');
const assets=JSON.parse(fs.readFileSync(path.join(out,'assets.json'),'utf8')).assets.filter(a=>a.category==='icons');
if(assets.length!==15) throw Error('Expected 15 B01 icons');
const groups=[['type','卡牌类型'],['status','状态效果'],['intent','敌人意图']];
let s='<rect width="1280" height="690" fill="#E8E3D7"/><g font-family="Microsoft YaHei, sans-serif" fill="#283330"><text x="34" y="49" font-size="28">B01 · 战斗图标审阅</text><text x="34" y="80" font-size="16">每项并列显示 48 px 与 32 px；本轮只审图形与辨识度</text>';
groups.forEach(([key,label],row)=>{
 const y=113+row*188;s+=`<text x="34" y="${y+22}" font-size="21">${label}</text>`;
 assets.filter(a=>a.id.startsWith('icon_'+key+'_')).forEach((a,i)=>{
  const x=34+i*205,href='data:image/png;base64,'+fs.readFileSync(path.join(root,'ImageReview',a.png)).toString('base64');
  s+=`<rect x="${x}" y="${y+38}" width="190" height="124" rx="4" fill="#F1EDE2" stroke="#C9CCBC"/><image href="${href}" x="${x+40}" y="${y+55}" width="48" height="48"/><image href="${href}" x="${x+113}" y="${y+63}" width="32" height="32"/><text x="${x+95}" y="${y+140}" text-anchor="middle" font-size="18">${a.name}</text>`;
 });
});
s+='</g>';
sharp(Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="690">${s}</svg>`)).png().toFile(path.join(out,'review_icons_2026-10-07.png')).then(()=>console.log('15 unchanged icons rendered for review')).catch(e=>{console.error(e);process.exitCode=1});
