const fs=require('node:fs'),path=require('node:path'),sharp=require(process.argv[2]);
const root=path.resolve(__dirname,'../../..'),review=path.join(root,'ImageReview'),out=path.join(review,'batches/card-production-c04');
const txt=(s,x,y,n=20,c='#28392F')=>`<text x="${x}" y="${y}" font-family="Microsoft YaHei,sans-serif" font-size="${n}" fill="${c}">${s}</text>`;
const img=(buf,x,y,w,h)=>`<image href="data:image/png;base64,${buf.toString('base64')}" x="${x}" y="${y}" width="${w}" height="${h}"/>`;
(async()=>{
let s='<rect width="1400" height="875" fill="#E8E2D3"/>'+txt('C04 · 缩小底饰，扩大描述区',32,47,30)+txt('描述安全区：600 × 192 → 600 × 280；约增加46% · 卡背保持C03不变',32,85,18);
s+=txt('修改前',32,133,23)+img(fs.readFileSync(path.join(review,'batches/card-production-c03/attack-300.png')),32,155,300,400)+txt('修改后',385,133,23)+img(fs.readFileSync(path.join(out,'attack-300.png')),385,155,300,400);
const frame=path.join(review,'cardframes/border_card_attack_ornate_c04.png'),mask=path.join(out,'illustration-window-mask.png');
const a=JSON.parse(fs.readFileSync(path.join(out,'assets.json'),'utf8')).assets[0],win=a.window;
const art=await sharp(path.join(root,'Assets/UI/cards/card_attack_dushubiji_illustration_v02.png')).resize(win.width,win.height,{fit:'contain',background:'#EDE8DC'}).png().toBuffer();
const fill=await sharp({create:{width:960,height:1280,channels:4,background:{r:0,g:0,b:0,alpha:0}}}).composite([{input:art,left:win.x,top:win.y}]).png().toBuffer();
const clipped=await sharp(fill).composite([{input:mask,blend:'dest-in'}]).png().toBuffer();
const base=await sharp(clipped).composite([{input:frame}]).png().toBuffer();
const samples={};
for(const w of [300,144,96]){
const k=w/960,h=w*4/3,font=w===300?22:w===144?11:8.5,title=w===300?29:w===144?14:10;
const lines=w===300?['配对：8伤害','翻开：标记相邻牌','共鸣']:['配对：8伤害','翻开：标记邻牌','共鸣'];
const overlay=`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}">`+txt('读书笔记',245*k,231*k,title)+lines.map((line,i)=>txt(line,195*k,(922+i*86)*k,font)).join('')+'</svg>';
samples[w]=await sharp(base).resize(w,h).composite([{input:Buffer.from(overlay)}]).png().toBuffer();fs.writeFileSync(path.join(out,'multiline-'+w+'.png'),samples[w]);
}
s+=txt('三行描述排版',740,133,23)+img(samples[300],740,155,300,400)+txt('原卡名与效果独立排字',1080,218,18)+txt('下方留出三行空间',1080,256,18)+txt('山纹移除',1080,321,19)+txt('罗盘缩小并下移',1080,359,19)+txt('保留窄版画底边',1080,397,19);
s+='<path d="M32 590h1336" stroke="#A9B59B"/>'+txt('144 × 192',32,634,21)+img(samples[144],32,655,144,192)+txt('96 × 128',255,634,21)+img(samples[96],255,655,96,128)+txt('小尺寸展示效果摘要，完整规则仍在详情中查看',451,699,20)+txt('本轮仅调整攻击卡框下部；新稿待审，未发布',451,744,20);
await sharp(Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="875">${s}</svg>`)).png().toFile(path.join(out,'comparison.png'));
console.log('C04 before/after and three-line description proof rendered');
})().catch(e=>{console.error(e);process.exitCode=1});
