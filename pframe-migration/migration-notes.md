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
  `tools/viewer.html?file=/pframe-base.excalidraw`（或 `/pframe-working.excalidraw`）。
- 本机环境下 `python3 -m http.server`（绑定 0.0.0.0）在应用沙箱内被 macOS 拒绝，改用 npx http-server 绑 127.0.0.1。
- 该 UMD 页面上下文中 `exportToSvg` 返回空 20×20 画布（含官方 `convertToExcalidrawElements` 产出的最小元素同样为空），
  属该上下文的已知问题；交互画布渲染正常。SVG 产物已改走 node 侧：`tools/render-svg.mjs`（@excalidraw/utils@0.1.5 + jsdom，
  依赖目录由 PF_EXCAL_NODE_MODULES 指定，缺省 /tmp/excal-render/node_modules）。
- viewer 的 `scrollToContent(null)` 在 0.17.6 UMD 会抛 `isDeleted` TypeError，已移除；整幅适配改由 `?fit=1`
  参数在挂载时按内容包围盒计算 zoom/scroll 注入 initialData。
- 确定性：seed/versionNonce 由元素 ID 哈希派生，updated 固定为 2026-09-14T04:00:00Z；重跑转换器输出与落盘文件完全一致
  （`migration-report.json: determinismRegenerationEqualsFile = true`）。

## Overlay Scaffold 验证（非正式 Overlay）

- 初版验证文件 `pframe-overlay-test.excalidraw` 已在 2026-09-14 重组中移除，由 **`pframe-working.excalidraw`** 接替：
  `tools/build_working.py` 读取 `overlay-spec.json`（当前仅含 TEST01 scaffold 项）+ base 生成，机制不变。
- working = Base 239 元素（原样前缀、全部 locked）+ `OVR_TEST01_*` 4 元素（未锁定）：
  半透明徽标「TEST01」+ 引线箭头 + callout，指向 o1:28「基础环境亲和配置」（P_BASE_001）。
- 合成指针事件实测（2026-09-14，初版文件）：拖拽 OVR 徽标位移 (+45,+27) 成功；对 BASE_RECT_001 施加同样拖拽，
  坐标零位移且不可选中。重组后以渲染像素级复检（徽标琥珀色像素 25998，4 个 OVR 元素未锁定）。
- 未制作任何 P01/C01/D01 或术语类正式 Overlay。

## 2026-09-14 结构重组（收敛工作面）

依据上游建议，工作集拍平到 `pframe-migration/` 根，五个文件：

| 文件 | 角色 |
|---|---|
| `pframe-base.excalidraw` | P哥第一张图，锁定，只读（自 `excalidraw/` 移入，内容字节不变） |
| `element-map.json` | 稳定ID ↔ 原图 element ID（自 `metadata/pframe-element-map.json` 改名移入） |
| `overlay-spec.json` | Overlay 标注要求（scaffold，待迁入对话结论） |
| `pframe-working.excalidraw` | base + overlay-spec 生成（`tools/build_working.py`） |
| `alignment.md` | Terminology Bridge / Semantic Bridge Matrix / Delta Cards（第一阶段 Markdown 承载，空底座） |

溯源层不动：`source/`（飞书 raw + 视觉参考）、`normalized/`（Layer A 中间层）、`tools/`（确定性 converter）、
`metadata/`（migration-report + 视觉证据截图）。`to_excalidraw.py` 的 `--overlay-test` 模式已移除（职责并入 build_working.py）。
重组后复检：base 重生成字节一致、报告 0 警告、unmapped=0。

## 2026-09-14 视觉回读补强（离线渲染链路）

背景：compare.html 右栏原先放的是 viewer 交互页截图（含 HUD/工具栏 UI），与左栏纯画布导出不可比。本次建立
**离线 SVG 渲染链路**并出具新证据：

- `tools/render-svg.mjs`：node 侧 @excalidraw/utils 渲染（不走浏览器）。实测坑：① README 平铺签名已过时，
  实际为 `{data, config}`；② 必须 `skipInliningFonts`（否则走 WASM 字体子集在 jsdom 下崩溃）；
  ③ utils 0.1.5 经 jsdom 序列化会给 `<svg>` 写两个 xmlns，重复属性属非法 XML——`<img>` 严格解码直接失败，
  宽松渲染器（chrome/qlmanage）画出统一粉色 (255,221,221) 错误占位。已后处理去重，产物通过 XML well-formed 校验。
- 新证据：`metadata/visual-evidence-base-render.svg`（矢量原件）+ `.png`（1600 宽栅格，headless Chrome）。
  颜色核对：#f0f4fc/#d4b45b/#d25d5a/#fee3e2 全部按源比例出现，无粉色残留。
- 布局比对（60×24 内容包围盒归一占格）：飞书参考 vs 渲染 **pearson 0.81**；大文本区、主流程簇、右侧思维导图树、
  左列长条逐区对位。旧的 `visual-evidence-base-full.jpg`（带 UI 截图）已删除。
- compare.html 增加图片加载回退与"请走本地服务打开"提示；正确打开方式
  `http://localhost:8793/tools/compare.html`（静态预览上下文解析不了 `../` 相对路径，这是"只见两个文字框"的原因）。

## 2026-09-14 Semantic Overlay R1｜P01–P08 Semantic Callout + D01 Delta 标记

- 规格：`overlay-spec.json` v3。P01–P08 由 `numberTag` 升级为 `semanticTag`（小型蓝色标签 `P0x` + 紧邻白底轻量卡片：英文 Contract 名 + 中文一行）。
  内容取自 `alignment.md`，未自行裁决术语。新增 `D01`（amber 小标记，锚 `P_BASE_051`「投鱼初始权重」，卡片「Normalization vs Total Supply / 总量再分配差异待专项」）。
- 渲染：`tools/build_working.py` 增 `semanticTag` 类型（tag 44×20 + 绑定文字 + 卡片 + 卡片文字）。working = 239 Base（锁定未动）+ 36 Overlay。
- 摆放：用一次性避让求解器（网格搜索 + 硬约束：不与实心框/虚线框**边线**/箭头/独立文本/锚点自身节点/其它 Overlay 碰撞）求得各 tag offset；
  长英文名折行收窄卡片。P03/P04/P06 优先求解。
- 校验（对构建产物独立复检）：9 个标记 P01–P08+D01 全部存在；9/9 锚点文本匹配 alignment.md；18 个 tag/card 盒 **0 碰撞**；Base 239 全锁定。
- 说明：P01/P02 卡片落在虚线框内部（仅边线可见，不构成遮挡），P03/P05/P06 的 tag 与锚点间距 4–38px 不等，未追求机械对齐。

## 2026-09-14 Semantic Overlay R1 · MINOR VISUAL TUNE（外部评审：MINOR VISUAL TUNE）

只改三处，语义/术语/anchor identity/Base/第二张图均未动：

1. **P01/P02 移出大框 + 蓝色短 leader**。原卡片位于大虚线框 `o1:41`（BASE_RECT_011）内部，易被误读成 PBro 原生字段。
   大框上方被琥珀标题框「一条鱼的配置」(924,-2135)-(1341,-2053) 占死、左侧到 `a1:1` 文本块只剩 104px 缝隙，
   **唯一可用的框外近邻空白在下方**。两张 tag+card 成对下移到框下缘外 6.2px（P01 tag@(940,-1694)、P02 tag@(1150,-1694)），
   各加一条**蓝色 leader 折线**指回原节点：P01 直线 (1053,-1712)→(1027,-1837)；P02 两段 (1300,-1712)→(1300,-1866)→(1275,-1866)
   （P02 必须走 `o1:28` 与 `o1:29` 之间的空隙，竖直下穿会压到 `o1:32` 的说明文字）。
   两条 leader 只穿虚线边线、不穿实心框/箭头/独立文本。
2. **D01 改为横跨整条权重链的 amber bracket**。原贴在「投鱼初始权重」左侧、像单节点备注。现改为链下方的下沿 bracket
   （x 2004..2648，与链同宽；中线 y=-435，两端上指至 y=-451，距链底 2px），标记与卡片置于 bracket 下方。
   文案收敛为 `D01 / Total Supply / Normalization / 总量 / 归一化 Contract 待专项闭合`，不展开公式。
   **为何走下方**：链上方是箭头栅栏（c1:2 折线在 x=2361 与 x=2588 竖直贯穿 y −533…−622，另有 o1:8 虚线框），
   任何横跨全链的 bracket 放上方都会被压；链下方为空白。
3. **P04 未动**（保持 0,-56）。P03/P05–P08 offset 全部不变。

实现：`tools/build_working.py` 新增 `polyline_element`（anchor 相对折线，用于 leader 与 bracket）与 `deltaSpan` 类型。
`overlay-spec.json` v4：P01/P02 增 `leader`，D01 改 `kind=deltaSpan` + `bracket`。

独立 reviewer 子代理复核：8/8 PASS，未发现反例。其记录的两点存疑：alignment.md §2 将 D01 主要引向 `P_BASE_009`（长文本）
而 spec 锚 `P_BASE_051`（本轮按指示未改 anchor identity）；bracket 与链节点留 2px 不重叠。
视觉回读：渲染 PNG/SVG 中 9 个标记与卡片文案齐全，Base 四色比例不变。
