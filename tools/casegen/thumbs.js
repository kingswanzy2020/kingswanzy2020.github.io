const { chromium } = require('playwright');
(async () => {
  const site = require('path').resolve(__dirname, '../..') + '/';
  const slugs = process.argv.slice(3); const outdir = process.argv[2];
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1300, height: 900 }, deviceScaleFactor: 1 });
  for (const s of slugs) {
    await p.goto('file://' + site + s + '/index.html'); await p.waitForTimeout(400);
    await (await p.$('.fig-scroll svg')).screenshot({ path: `${outdir}/${s}.png` });
  }
  await b.close();
})();
