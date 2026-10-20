// 需求评审版截图（云端可用，Playwright + Chromium）：把 推送系统后台集成需求/需求评审版_原型/<名>.html 里的 .shot 元素
// 按 2 倍像素截成 推送系统后台集成需求/需求评审版_图/<名>.jpg（质量 90）。
// 用法：node _scripts/pl_评审版截图.mjs [名 …]      不给名则截全部；名不带 .html
// 页面宽 1280；每个原型页面自己 <link> 原型样式.css 或评审版图表样式，路径相对 需求评审版_原型/。
import { createRequire } from 'module';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
const require = createRequire(import.meta.url);
let pw;
try { pw = require('playwright'); } catch { pw = require('/opt/node22/lib/node_modules/playwright'); }
const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const SRC = path.join(ROOT, '推送系统后台集成需求/需求评审版_原型');
const OUT = path.join(ROOT, '推送系统后台集成需求/需求评审版_图');
let names = process.argv.slice(2);
if (!names.length) names = fs.readdirSync(SRC).filter(f => f.endsWith('.html') && !f.startsWith('_')).map(f => f.slice(0, -5));
const browser = await pw.chromium.launch({ executablePath: fs.existsSync('/opt/pw-browsers/chromium') ? undefined : undefined });
const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 2 });
for (const n of names) {
  const page = await ctx.newPage();
  await page.goto('file://' + path.join(SRC, n + '.html'));
  await page.evaluate(() => document.fonts.ready);
  const el = await page.$('.shot');
  if (!el) { console.log('✘', n, '没有 .shot 元素'); await page.close(); continue; }
  await el.screenshot({ path: path.join(OUT, n + '.jpg'), type: 'jpeg', quality: 90 });
  const b = await el.boundingBox();
  console.log('✔', n, Math.round(b.width) + '×' + Math.round(b.height));
  await page.close();
}
await browser.close();
