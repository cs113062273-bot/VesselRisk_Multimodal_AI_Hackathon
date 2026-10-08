// A repeatable first-visit walkthrough, not a timed usability study.
import {createRequire} from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'..');
const require=createRequire(path.join(root,'web/package.json'));
const {chromium,expect}=require('@playwright/test');
const phase=process.argv[2];
if(!['before','after'].includes(phase))throw Error('Use before or after');
const output=path.join(root,'review/first-30-seconds',phase);
fs.mkdirSync(output,{recursive:true});
const browser=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const errors=[];const records=[];
try{
for(const [width,height] of [[1440,1000],[1920,1080]]){
 const page=await browser.newPage({viewport:{width,height}});
 page.on('pageerror',e=>errors.push(e.message));
 const capture=async(state)=>{
  await page.evaluate(()=>scrollTo({top:0,behavior:'instant'}));
  await page.screenshot({path:path.join(output,`${width}-${state}.png`),animations:'disabled'});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  records.push({width,height,state});
 };
 await page.goto(process.env.DEMO_URL||'http://127.0.0.1:3001');
 await expect(page.getByRole('button',{name:'Predict coronary risk',exact:true})).toBeEnabled({timeout:90000});
 await expect(page.getByText(/FPS · live/)).toBeVisible({timeout:30000});
 await capture('01-ready');
 await page.getByRole('button',{name:'Predict coronary risk',exact:true}).click();
 await expect(page.getByText(/held-out demonstration/)).toBeVisible({timeout:90000});
 await capture('02-prediction');
 await page.getByRole('button',{name:'Select LCX in 3D'}).click();
 await page.getByRole('button',{name:'X-ray',exact:true}).click();
 await expect(page.getByRole('heading',{name:'Left circumflex',exact:true})).toBeVisible();
 await capture('03-linked-lcx');
 await page.getByRole('button',{name:'Evidence Lab',exact:true}).click();
 await capture('04-evidence');
 await page.close();
}
expect(errors).toEqual([]);
fs.writeFileSync(path.join(output,'index.json'),JSON.stringify({phase,records,errors},null,2));
console.log(`${phase}: 8 first-visit screenshots; no page errors or horizontal overflow.`);
}finally{await browser.close();}
