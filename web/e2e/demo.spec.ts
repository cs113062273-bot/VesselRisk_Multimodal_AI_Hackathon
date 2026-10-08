import { test, expect } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';

test('real prediction → coronary anatomy → local explanation → evidence → patient edit',async({page})=>{
  const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('/');
  await expect(page.getByRole('heading',{name:'Coronary risk, made visible.'})).toBeVisible();
  await page.getByRole('button',{name:'Predict coronary risk',exact:true}).click();
  await expect(page.getByText(/held-out demonstration ·/)).toBeVisible();
  await expect(page.getByRole('heading',{name:'Left anterior descending',exact:true})).toBeVisible();
  await expect(page.locator('canvas')).toBeVisible();
  await expect(page.getByText('63 anatomical structures')).toBeVisible();
  await expect(page.getByRole('button',{name:'Select LAD in 3D'})).toBeVisible();
  await expect(page.locator('.orientation')).toContainText('RESET VIEW');
  await expect(page.locator('.color-key')).toContainText('30–<60%');
  const outDir=path.resolve('../demo/screenshots');fs.mkdirSync(outDir,{recursive:true});
  await page.screenshot({path:path.join(outDir,'patient-workspace.png'),fullPage:true});
  await page.locator('.heart-viewer').screenshot({path:path.join(outDir,'coronary-anatomy.png')});
  // Vessel selection routes to the corresponding independently trained explanation.
  await page.getByRole('button',{name:'Select LCX in 3D'}).click();
  await expect(page.getByRole('heading',{name:'Left circumflex',exact:true})).toBeVisible();
  await page.getByRole('button',{name:'X-ray',exact:true}).click();
  await expect(page.getByRole('button',{name:'X-ray',exact:true})).toHaveAttribute('aria-pressed','true');
  await page.getByRole('button',{name:'Vessels only',exact:true}).click();
  await page.getByRole('button',{name:'Vessels only',exact:true}).click();
  await page.getByRole('button',{name:'X-ray',exact:true}).click();
  await page.getByRole('button',{name:'Reveal recorded outcomes'}).click();
  await expect(page.locator('.recorded-outcomes')).toBeVisible();
  await page.getByRole('button',{name:'Evidence Lab',exact:true}).click();
  await expect(page.getByRole('heading',{name:'Every claim, inspectable.'})).toBeVisible();
  await page.getByRole('tab',{name:'CAD',exact:true}).click();
  await expect(page.locator('.auc-feature')).toContainText('0.925');
  await page.screenshot({path:path.join(outDir,'evidence-validation.png'),fullPage:true});
  await page.getByRole('tab',{name:'LCX',exact:true}).click();
  await expect(page.locator('.research-thresholds')).toContainText('0.840');
  await expect(page.locator('.research-thresholds')).toContainText('93 / 19');
  await page.getByRole('tab',{name:'RCA',exact:true}).click();
  await expect(page.locator('.research-thresholds')).toContainText('0.868');
  await page.getByRole('tab',{name:'Robustness',exact:true}).click();
  await expect(page.getByRole('heading',{name:'Where the model failed'})).toBeVisible();
  await page.getByRole('tab',{name:'Data & provenance',exact:true}).click();
  await expect(page.getByText('Guard runs before all preprocessing')).toBeVisible();
  await page.screenshot({path:path.join(outDir,'leakage-provenance.png'),fullPage:true});
  await page.getByRole('button',{name:'Patient workspace',exact:true}).click();
  await page.getByLabel('Age',{exact:true}).fill('85');
  await expect(page.getByText('Showing the previous result · predict to apply edited inputs')).toBeVisible();
  await expect(page.getByRole('button',{name:'Export case',exact:true})).toBeDisabled();
  await page.getByRole('button',{name:'Predict coronary risk',exact:true}).click();
  await expect(page.getByText(/held-out sensitivity ·/)).toBeVisible();
  await expect(page.getByRole('button',{name:'Reveal recorded outcomes'})).toHaveCount(0);
  const download=page.waitForEvent('download');await page.getByRole('button',{name:'Export case',exact:true}).click();
  const exported=await download;
  expect(exported.suggestedFilename()).toBe('vesselrisk-patient-evidence.json');
  const exportedCase=JSON.parse(fs.readFileSync((await exported.path())!,'utf8'));
  for(const t of ['CAD','LAD','LCX','RCA']){
    expect(exportedCase.targets[t].model_reference.artifact_file).toBe(`${t}.joblib`);
    expect(exportedCase.targets[t].model_reference.member).toMatch(/^folds\[\d+\]\.model$/);
  }
  expect(errors).toEqual([]);
});

test('mobile input, working 3D and evidence without horizontal overflow',async({page})=>{
  await page.setViewportSize({width:390,height:844});await page.goto('/');
  await page.getByRole('button',{name:'Predict coronary risk',exact:true}).click();
  await expect(page.getByText(/held-out demonstration ·/)).toBeVisible();
  await page.locator('.heart-viewer').scrollIntoViewIfNeeded();
  await expect(page.locator('canvas')).toBeVisible();
  const outDir=path.resolve('../demo/screenshots');fs.mkdirSync(outDir,{recursive:true});
  await page.screenshot({path:path.join(outDir,'mobile-workspace.png'),fullPage:true});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
  await page.getByRole('button',{name:'Evidence Lab',exact:true}).click();
  await expect(page.getByRole('heading',{name:'Every claim, inspectable.'})).toBeVisible();
  await page.getByRole('tab',{name:'LCX',exact:true}).click();
  await expect(page.locator('.research-thresholds')).toContainText('0.840');
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
});
