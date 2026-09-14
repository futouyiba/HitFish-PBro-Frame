// node 侧运行 @excalidraw/utils 所需的最小 DOM 环境（配合 tools/render-svg.mjs）。
// 依赖不在本仓库内：默认读 PF_EXCAL_NODE_MODULES（缺省 /tmp/excal-render/node_modules），
// 需含 @excalidraw/utils@0.1.5 与 jsdom（npm i @excalidraw/utils@0.1.5 jsdom）。
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

const MODS = process.env.PF_EXCAL_NODE_MODULES || '/tmp/excal-render/node_modules';
const require2 = createRequire(pathToFileURL(path.join(MODS, 'noop.js')));

const { JSDOM } = require2('jsdom');
const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>', { pretendToBeVisual: true, url: 'https://localhost/' });
for (const k of ['DOMParser', 'XMLSerializer', 'SVGElement', 'HTMLElement', 'Element', 'Node',
                 'getComputedStyle', 'Image', 'KeyboardEvent', 'MouseEvent', 'PointerEvent',
                 'CustomEvent', 'Event', 'FileReader', 'Blob', 'URL', 'FormData']) {
  if (dom.window[k] !== undefined && globalThis[k] === undefined) globalThis[k] = dom.window[k];
}
globalThis.window = dom.window;
globalThis.document = dom.window.document;
try { globalThis.navigator = dom.window.navigator; } catch {}
globalThis.devicePixelRatio = 1;
globalThis.innerWidth = 1024; globalThis.innerHeight = 768;
globalThis.localStorage = { getItem: () => null, setItem: () => {}, removeItem: () => {} };
globalThis.matchMedia ??= () => ({ matches: false, addListener() {}, removeListener() {}, addEventListener() {}, removeEventListener() {} });
globalThis.requestAnimationFrame = (cb) => setTimeout(() => cb(Date.now()), 16);
globalThis.cancelAnimationFrame = clearTimeout;
try { if (!globalThis.crypto?.randomUUID) globalThis.crypto = { getRandomValues: (a) => { for (let i = 0; i < a.length; i++) a[i] = (Math.random() * 256) | 0; return a; }, randomUUID: () => '00000000-0000-4000-8000-000000000000' }; } catch {}
class RO { observe() {} unobserve() {} disconnect() {} }
globalThis.ResizeObserver ??= RO;
globalThis.IntersectionObserver ??= RO;
export { dom, MODS, require2 };
