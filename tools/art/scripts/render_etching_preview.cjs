// Render the locally authored UI; generated bitmap art is used as unchanged layers.
// Usage: node render_etching_preview.cjs <playwright-module-path>
const { chromium } = require(process.argv[2] || 'playwright');
const path = require('node:path');
const fs = require('node:fs');
const { pathToFileURL } = require('node:url');
const root = path.resolve(__dirname, '../../..');
const out = path.join(root, 'ImageReview/mockups');
const url = pathToFileURL(path.join(out, 'battle-etching-v02/index.html')).href;
(async () => {
 const browser = await chromium.launch({channel:'chrome',headless:true});
 const page = await browser.newPage({viewport:{width:1920,height:1156},deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(url);await page.evaluate(()=>document.fonts.ready);
 await page.locator('.scene').evaluate(async img=>{if(!img.complete)await new Promise(r=>img.onload=r)});
 await page.locator('.card-art img').evaluate(async img=>{if(!img.complete)await new Promise(r=>img.onload=r)});
 const geometry=await page.evaluate(()=>({cards:[...document.querySelectorAll('.card')].map(e=>({w:e.offsetWidth,h:e.offsetHeight,x:e.offsetLeft,y:e.offsetTop})),faces:document.querySelectorAll('.face').length,segments:document.querySelectorAll('.segment').length,lit:document.querySelectorAll('.segment.lit').length,brokenImages:[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src)}));
 if(geometry.cards.length!==16||geometry.faces!==1||geometry.segments!==10||geometry.lit!==1||geometry.cards.some(c=>c.w*4!==c.h*3)||geometry.brokenImages.length)throw Error(JSON.stringify(geometry));
 await page.locator('#stage').screenshot({path:path.join(out,'mockup_s03_etching_v02.png')});
 await page.locator('.card.face').click();await page.locator('#detail').waitFor({state:'visible'});
 await page.locator('#stage').screenshot({path:path.join(out,'mockup_s03_etching_v02_detail.png')});
 await page.keyboard.press('Escape');await page.locator('#detail').waitFor({state:'hidden'});
 await page.locator('#danger').click();
 if(await page.locator('.segment.lit').count()!==9)throw Error('Danger meter must have nine lit segments');
 await page.locator('#stage').screenshot({path:path.join(out,'mockup_s03_etching_v02_danger.png')});
 await page.locator('#normal').click();
 await page.locator('.card[data-slot="0"]').click();
 if(await page.locator('.card.face').count()!==1)throw Error('Hidden card leaked in preview');
 await page.keyboard.press('Escape');await page.locator('.card[data-slot="6"]').blur();
 await page.setViewportSize({width:1280,height:796});await page.mouse.move(0,0);
 await page.locator('#stage').screenshot({path:path.join(out,'mockup_s03_etching_v02_720p.png')});
 const overflow=await page.evaluate(()=>({body:document.documentElement.scrollWidth>innerWidth,compactCard:{w:document.querySelector('.card').offsetWidth,h:document.querySelector('.card').offsetHeight},detail:(()=>{window.preview.toggleDetail(true);const el=document.querySelector('#detail'),r=el.getBoundingClientRect();return {left:r.left,right:r.right,bottom:r.bottom,scrollHeight:el.scrollHeight,clientHeight:el.clientHeight,viewportWidth:innerWidth,viewportHeight:innerHeight}})()}));
 await page.locator('#stage').screenshot({path:path.join(out,'mockup_s03_etching_v02_720p_detail.png')});
 if(errors.length||overflow.body||overflow.detail.right>1280||overflow.detail.bottom>720||overflow.compactCard.w*4!==overflow.compactCard.h*3)throw Error(JSON.stringify({errors,overflow}));
 fs.writeFileSync(path.join(out,'battle-etching-v02/verification.json'),JSON.stringify({geometry,overflow,errors,checks:['16 cards','one face','3:4 exact','10 meter segments','normal 1/10','danger 9/10','detail click and Escape','hidden cards stay hidden','images loaded']},null,2));
 await browser.close();console.log(JSON.stringify({ok:true,out,geometry,overflow},null,2));
})().catch(e=>{console.error(e);process.exitCode=1});
