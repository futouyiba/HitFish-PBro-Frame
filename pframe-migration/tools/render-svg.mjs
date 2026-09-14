// 离线渲染 .excalidraw 场景为 SVG（node + @excalidraw/utils + jsdom，无需浏览器）。
// 依赖：npm i @excalidraw/utils@0.1.5 jsdom
// 用法：node tools/render-svg.mjs <scene.excalidraw> <out.svg> [width]
//
// 已知坑（2026-09-14 实测）：
// 1. exportToSvg 签名是 { data: {...scene}, config }（README 的平铺签名已过时）。
// 2. 不加 skipInliningFonts 会走 WASM 字体子集路径，jsdom 下崩溃。
// 3. utils 0.1.5 经 jsdom 序列化会给 <svg> 写两个 xmlns——重复属性是非法 XML，
//    <img> 严格解码直接失败，宽松渲染器会画出粉色错误占位。此处后处理去重。
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { MODS } from './jsdom-globals.mjs';

const [,, inPath, outPath, widthArg] = process.argv;
const WIDTH = Number(widthArg || 1600);

const { exportToSvg } = await import(pathToFileURL(path.join(MODS, '@excalidraw/utils/dist/prod/index.js')).href);
const scene = JSON.parse(fs.readFileSync(inPath, 'utf8'));

const svg = await exportToSvg({
  data: { ...scene, appState: { ...scene.appState, exportBackground: true, viewBackgroundColor: '#ffffff' }, files: {} },
  config: { padding: 10, skipInliningFonts: true },
});

let out = new (globalThis.XMLSerializer)().serializeToString(svg);
const dup = ' xmlns="http://www.w3.org/2000/svg"';
const first = out.indexOf(dup);
if (first !== -1) {
  const rest = out.slice(first + dup.length);
  out = out.slice(0, first + dup.length) + rest.split(dup).join('');
}
const sw = Number(svg.getAttribute('width')) || WIDTH;
const sh = Number(svg.getAttribute('height')) || 1;
out = out.replace(/(<svg[^>]*?)width="[0-9.]+"\s+height="[0-9.]+"/,
  `$1width="${WIDTH}" height="${(sh * WIDTH / sw).toFixed(1)}"`);
fs.writeFileSync(outPath, out, 'utf8');
console.log(`wrote ${outPath} (${(out.length / 1024).toFixed(1)} KB)`);
