const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const base=process.env.GRAPH_TEST_BASE||'http://127.0.0.1:8772/';
const output=process.env.GRAPH_TEST_OUTPUT||'/tmp/pibs-document-studio';fs.mkdirSync(output,{recursive:true});
const fixture=JSON.parse(fs.readFileSync('site/document-studio/examples/organization-chart.json'));
const programs=JSON.parse(fs.readFileSync('site/document-studio/templates/programs.json')).programs;
const KEY='pibs-document-studio-v1';
const edit=(page,parts)=>page.locator('[data-edit-path='+JSON.stringify(JSON.stringify(parts))+']');
const input=(page,parts)=>page.locator('[data-input-path='+JSON.stringify(JSON.stringify(parts))+']');
const section=(page,parts)=>page.locator('section[data-field-path='+JSON.stringify(JSON.stringify(parts))+']');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.BROWSER_EXECUTABLE,args:['--no-sandbox']});
 try{
  const context=await browser.newContext({viewport:{width:1550,height:1050}}),page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base+'document-studio/',{waitUntil:'domcontentloaded'});await page.waitForSelector('[data-edit-path]');
  assert.match(await page.locator('#document-title').innerText(),/Info Source/);assert.equal(await page.locator('#dataset-nav').count(),0);assert.ok(!(await page.locator('#paper').innerText()).includes('infosource'));
  assert.match(await page.locator('.locked-content').first().innerText(),/Info Source describes/);
  await edit(page,['payload','institution_name','en']).fill('Example Department');await edit(page,['payload','institution_name','fr']).fill('Ministère exemple');
  await page.waitForTimeout(250);await page.reload();await page.waitForSelector('[data-edit-path]');assert.equal(await edit(page,['payload','institution_name','fr']).innerText(),'Ministère exemple');
  const [draft]=await Promise.all([page.waitForEvent('download'),page.locator('#draft-download').click()]);await draft.saveAs(output+'/bilingual.draft.md');assert.ok(fs.readFileSync(output+'/bilingual.draft.md','utf8').includes('Ministère exemple'));
  await page.locator('#ready-download').click();await page.waitForSelector('#review-dialog[open]');assert.ok(await page.locator('#issues li').count());await page.locator('#review-dialog [data-close]').click();
  await page.locator('#outline button').filter({hasText:'Institution-specific programs'}).click();
  await section(page,['payload','institution_specific']).locator('.repeat-heading button').click();await page.locator('[data-template-id="program"]').click();
  const programPath=['payload','institution_specific',0];await edit(page,[...programPath,'title','en']).fill('Example program');await edit(page,[...programPath,'title','fr']).fill('Programme exemple');await input(page,[...programPath,'program_id']).fill('DEMO-01');
  const description=edit(page,[...programPath,'description','en']);await description.fill('A formatted program description.');await description.focus();await description.press('Control+A');await page.locator('[data-command="bold"]').click();assert.ok(await description.locator('b,strong').count());
  await section(page,[...programPath,'classes']).locator('.repeat-heading button').click();await page.locator('[data-template-id="standard-cor-930"]').click();
  const corPath=[...programPath,'classes',0];assert.match(await edit(page,[...corPath,'description','fr']).innerText(),/./);
  await section(page,[...corPath,'pibs']).locator('.repeat-heading button').click();await page.locator('[data-template-id="standard-pib-psu-901"]').click();
  assert.ok((await page.locator('#breadcrumbs button').count())>=5);assert.equal(await input(page,[...corPath,'pibs',0,'bank_number']).inputValue(),'PSU 901');
  await page.getByRole('button',{name:'← Back to parent section',exact:true}).click();assert.ok(await section(page,[...corPath,'pibs']).locator('.repeat-item').count());
  // Import the complete fictional chart, then exercise its real authoring controls.
  await page.locator('#open-file').setInputFiles('site/document-studio/examples/organization-chart.json');await page.waitForFunction(()=>document.getElementById('document-title').textContent.includes('Fictional organization'));
  assert.equal(await page.locator('.chart-node').count(),3);assert.equal(await page.locator('.chart-canvas path').count(),2);assert.ok((await page.locator('.chart-node').last().innerText()).includes('EXAMPLE-01'));
  await page.locator('.chart-node').filter({hasText:'Sam Example'}).click();const personPath=['payload','people',2];
  assert.equal(await input(page,[...personPath,'classification_group']).inputValue(),'EX');assert.equal(await input(page,[...personPath,'classification_level']).inputValue(),'03');
  const assignments=section(page,[...personPath,'programs']);await assignments.locator('.item-actions button[aria-label^="Remove item"]').click();
  await page.locator('#ready-download').click();await page.waitForSelector('#review-dialog[open]');assert.match(await page.locator('#issues').innerText(),/at least 1/);await page.locator('#review-dialog [data-close]').click();
  const programIndex=programs.findIndex(p=>p.owner_org==='cic'&&p.program_id==='BGD02');assert.ok(programIndex>=0);await assignments.locator('.program-picker select').selectOption('inventory:'+programIndex);await assignments.getByRole('button',{name:'Assign selected program',exact:true}).click();assert.equal(await page.locator('#issue-count').innerText(),'0');
  const [ready]=await Promise.all([page.waitForEvent('download'),page.locator('#ready-download').click()]);await ready.saveAs(output+'/organization-chart.md');assert.match(fs.readFileSync(output+'/organization-chart.md','utf8'),/BGD02/);
  await page.locator('#outline button').filter({hasText:'People and reporting lines'}).click();await page.screenshot({path:output+'/organization-chart-desktop.png',fullPage:true});
  await page.locator('.chart-node').filter({hasText:'Morgan Example'}).click();await input(page,['payload','people',0,'reports_to']).selectOption(fixture.payload.people[2].id);assert.notEqual(await page.locator('#issue-count').innerText(),'0');await input(page,['payload','people',0,'reports_to']).selectOption('');assert.equal(await page.locator('#issue-count').innerText(),'0');
  // Source form sections and repeated-table columns are editable through the same interface.
  for(const id of ['pib_submission','pia_web_summary','privacy_checklist','privacy_impact_assessment','privacy_protocol']){
   await page.locator('#new-document').click();await page.locator('[data-template-id="'+id+'"]').click();assert.equal(await page.locator('#app-error').isHidden(),true,id);assert.ok((await page.locator('#outline button').count())>=1);
   if(id==='privacy_impact_assessment'){
    await page.locator('#outline button').filter({hasText:'4. Handling of personal information'}).click();
    // Locate the 13-column handling table using the generated schema metadata.
    const add=page.locator('.repeat-section .repeat-heading button').first();await add.click();assert.equal(await page.locator('#paper .bilingual-field').count(),13);
   }
  }
  await page.locator('#open-file').setInputFiles(output+'/organization-chart.md');await page.waitForFunction(()=>document.getElementById('document-title').textContent.includes('Fictional organization'));
  await page.locator('#language').click();await page.locator('#outline button').filter({hasText:'Personnes et liens hiérarchiques'}).click();assert.match(await page.locator('#paper').innerText(),/Chaîne de commandement/);assert.match(await page.locator('#paper').innerText(),/Programme/);
  await page.setViewportSize({width:390,height:844});await page.locator('#toggle-outline').click();assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await page.screenshot({path:output+'/organization-chart-mobile-fr.png',fullPage:true});
  const before=await page.locator('#document-title').innerText();await page.locator('#open-file').setInputFiles({name:'bad.md',mimeType:'text/markdown',buffer:Buffer.from('Unstructured text')});assert.equal(await page.locator('#document-title').innerText(),before);assert.match(await page.locator('#app-error').innerText(),/Le fichier n’a pas été ouvert/);
  const unusualId=structuredClone(fixture);unusualId.document_id='__proto__';await page.locator('#open-file').setInputFiles({name:'literal-id.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(unusualId))});await page.waitForTimeout(250);assert.ok(await page.evaluate(key=>Object.hasOwn(JSON.parse(localStorage.getItem(key)).documents,'__proto__'),KEY));
  assert.deepEqual(errors,[]);
  const recovery=await context.newPage();await recovery.addInitScript(({key})=>localStorage.setItem(key,'{"version":"old","documents":{"preserve":"content"}}'),{key:KEY});await recovery.goto(base+'document-studio/');await recovery.waitForSelector('[data-edit-path]');assert.equal(await recovery.locator('#recover-drafts').isVisible(),true);assert.ok((await recovery.evaluate(key=>localStorage.getItem(key),KEY)).includes('preserve'));
  console.log('Passed Document Studio: bilingual visual editing/autosave, nested standard templates, five forms, 13-column repeated table, enforced program assignments, reporting-cycle checks, Markdown downloads/import, French mobile and recovery.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
