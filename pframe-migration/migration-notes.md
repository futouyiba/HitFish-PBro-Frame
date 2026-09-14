# Migration Notes｜飞书主图 → Excalidraw Base（Graphic Migration）

任务：把 P哥 飞书画板《游戏中鱼整个系统的设计》主图（token `DfFRwiueTh2QbdbzS1scoNomnkj`，
docx `ES2Sd89jeoCsiVxqY3WcHbV4n4c`）迁移为 Excalidraw 图形资产。
本文件只记录迁移层面事项，不含任何设计 Review 或语义判断。

## 源数据结构

- 抓取方式：`lark-cli whiteboard +export --output-type raw`（飞书 OpenAPI 原生节点格式），2026-09-14。
- 原始 JSON：`source/feishu-original.json`（132 nodes）；视觉参考：`source/feishu-original-reference.jpg` / `.svg`（仅比对用）。
- 节点构成：`composite_shape`×80（round_rect×79、round_rect2×1）、`connector`×19、`mind_map`×17（1 root + 16 子节点，parent_id 树）、`text_shape`×15（1 个 73 段大文本 + 14 个小标注）、`group`×1（3 子节点）。
- 每节点含 `id/x/y/width/height/angle/z_index/style/text`；connector 含显式 start/end 绑定（目标 id + 分数锚点 position + snap_to）与 turning_points。

## 支持的图元与映射

| 飞书图元 | Excalidraw | 迁移质量 |
|---|---|---|
| composite_shape（round_rect / round_rect2） | `rectangle`（roundness type 3）+ 绑定 `text` | 几何/颜色/字号无损；round_rect2 无对应细分，按圆角矩形处理（o1:15） |
| connector（polyline，显式绑定，单向箭头 start=none / end=line_arrow） | `arrow`（points=起点锚点+拐点+终点锚点；startBinding/endBinding；caption 为绑定 label） | 路径与方向无损；锚点语义见下 |
| mind_map 节点 | `rectangle` + 绑定 `text` | 几何无损；边见「推导项」 |
| text_shape（富文本段落） | 单个多行 `text` | 字节级无损（73 段/空行保留；全部 14 号无混排） |
| group（n1:1） | 子元素 `groupIds:["BASE_GRP_001"]` | 无损（Excalidraw 无独立 group 对象） |
| z-order | elements 数组顺序 | 无损 |

## 无损迁移项

坐标（含负 y，未做平移，映射可逆）、尺寸、z-order、填充色（#f0f4fc / #d4b45b / #d25d5a / #509863 / #fee3e2 / #5178c6）、
边框样式（none / dot→dotted）、字号（14/16/9/48/24）、文本颜色与对齐、文字内容（96 个含文字节点共 1332 字逐字节一致）、
箭头方向（19/19 全部单向）、拐点几何、绑定目标关系（数据层）。

## 近似项（migration approximations）

1. **字体替代**：飞书默认字体 → Excalidraw fontFamily 2（Normal / 系统字体）。中文字形由浏览器回退渲染。
2. **bold 不可表达**：Excalidraw 无 per-element 粗体。z1:1「需求拆解 」为源数据中唯一 bold（白字蓝底），按 normal 迁移。
3. **边框 none → strokeColor transparent**：视觉等价（无描边）；Excalidraw 无"无描边"枚举。
4. **round_rect2 → 圆角矩形**（o1:15）：飞书的两种圆角细分在 Excalidraw 只有 type 3 一种。
5. **思维导图边为推导元素**（16 条 `BASE_ARROW_MM_*`）：飞书 raw 数据中思维导图的边由渲染器自动绘制、无几何数据；
   此处由结构化 `parent_id` 推导为直线（父右边缘中点 → 子左边缘中点，无箭头），非像素猜测。编号 `P_DERIVED_*`，
   可整体删除而不影响任何源对象映射。
6. **caption 位置**：飞书 `caption_position`（沿路径分数，如 0.318）保留在 Layer A；Excalidraw 的箭头 label 默认居中，
   初始放置按该分数插值，编辑后会按 Excalidraw 规则重排。
7. **绑定锚点语义**：飞书分数锚点（position.fx/fy + snap_to）完整保留在 Layer A；Excalidraw binding 使用 focus/gap，
   元素被拖动时按其自身算法重算贴边。初始静态几何与源一致（含 15/19 条带 1–2 个拐点的折线）。
8. **文本框宽高为估算**：Excalidraw 加载后按真实字体重排；估算已按 CJK≈1em / ASCII≈0.6em 计算以贴近原尺寸。
9. **文本行高**：飞书未给行高，统一按 Excalidraw 默认 1.25。

## 原文保留（未修改，仅记录）

- z1:21「环境运算运算因子 」：疑似「运算」重复，原样保留。
- a1:11 / a1:18 / o1:43 的文本为字面 `...`（省略号标注），原样保留。
- 其余文本未做任何措辞修正、术语替换或翻译。

## 工具链备注

- `tools/viewer.html`：本地渲染查看器（React 18 + @excalidraw/excalidraw@0.17.6 UMD，unpkg CDN）。
  启动：仓库根 `npx -y http-server pframe-migration -p 8793 -a 127.0.0.1`，然后访问
  `tools/viewer.html?file=/excalidraw/pframe-base.excalidraw`（或 `pframe-overlay-test.excalidraw`）。
- 本机环境下 `python3 -m http.server`（绑定 0.0.0.0）在应用沙箱内被 macOS 拒绝，改用 npx http-server 绑 127.0.0.1。
- 该 UMD 页面上下文中 `exportToSvg` 返回空 20×20 画布（含官方 `convertToExcalidrawElements` 产出的最小元素同样为空），
  属该上下文的已知问题；交互画布渲染正常。后续如需 SVG 产物，走 node 侧 `@excalidraw/utils` 或 excalidraw.com 打开后导出。
- 确定性：seed/versionNonce 由元素 ID 哈希派生，updated 固定为 2026-09-14T04:00:00Z；重跑转换器输出与落盘文件完全一致
  （`migration-report.json: determinismRegenerationEqualsFile = true`）。

## Overlay Scaffold 验证（非正式 Overlay）

- `excalidraw/pframe-overlay-test.excalidraw` = Base 239 元素（全部 locked）+ `OVR_TEST_*` 4 元素（未锁定）：
  半透明徽标「TEST01」+ 引线箭头 + callout，指向 o1:28「基础环境亲和配置」。
- 合成指针事件实测（2026-09-14）：拖拽 OVR_TEST_RECT_001 位移 (+45,+27) 成功；对 BASE_RECT_001 施加同样拖拽，
  坐标零位移且不可选中。Base locked + Overlay editable 工作方式成立。
- 未制作任何 P01/C01/D01 或术语类正式 Overlay。
