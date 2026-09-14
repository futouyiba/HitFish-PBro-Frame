# P哥 Frame × FCF Semantic Alignment R0

> **Scope：**只处理第一张横向主图。P哥 Frame 是 Communication Coordinate System；Simplified Production V0 / 0.3.4 是 Semantic / Production Coordinate System。Base 图不修改，本页与 Overlay 只做桥接。
>
> **Status：**WORKING ALIGNMENT / NOT PROMOTED。Terminology Bridge 是当前共同语言候选，不通过本文件修改 FCF Current。

## Authority / Rebase

本轮按以下路径 fresh-read：

1. FCF Router → Project State Current → Design Branch Index → Simplified Production V0 Working Main；
2. 《中鱼机制 0.3.4｜逻辑框架升级（中间对齐骨架）》；
3. 《0.3.4 Logic Ownership Checkpoint R0｜FishMode 去留裁决 × FishGroup 职责 × Bake / Response / Quality 独立 Program × Preset / Binding Boundary》（WORKING / NOT PROMOTED）；
4. 《0.3.4 Authoring Representation Checkpoint R0｜Bass 样板、四执行面聚类与 Resolver 边界》（WORKING / NOT PROMOTED）；
5. 《Fish Logic Discovery & Template Census Method R0》；
6. PBro Frame 当前 Data Contract / Bake Pipeline，仅作 **Reference / Comparison**，不取得 Simplified V0 Authority；
7. 《Base Opportunity × Total Supply Closure Plan R0》继续独立处理 D01。

关键状态边界：0.3.4 主文档仍保留 `FishGroup + FishMode` 历史工作表述；本 Alignment 根据本轮进一步语义澄清，先建立一个更低歧义的共同语言候选，不把 Terminology Bridge 自动解释成 Promotion。

---

## 1. P哥 Frame Terminology Bridge

编号与 `overlay-spec.json` 一致。看图上的 Pxx，可以直接在本表找到同一编号。

| 编号 | P哥原词 | Stable ID | Candidate 术语 | 中文一句话定义 | 为什么更好 | 与当前 FCF 的关系 |
| --- | --- | --- | --- | --- | --- | --- |
| P01 | 基础品质配置 | `P_BASE_039` | **FishQuality 基础定义 / Base Quality Config** | 定义鱼的品质 / 体型桶及其基础生成范围、基础倾向。 | 保留“品质是独立轴”，避免把体型差异混进模式身份。 | **B**：与当前 `FishQuality` 基本一致，但当前另有独立 Quality Selection Surface。 |
| P02 | 基础环境亲和配置 | `P_BASE_001` | **空间机会画像（Spatial Opportunity Profile）** | 描述某 Species 在不同空间条件下，相对自身基准机会的空间形状 / 系数。 | 把“总体机会基准”和“更喜欢哪里”拆开。 | **B**：对应当前 `SpatialOpportunityProfile`；与 Base / Total Supply 的精确关系仍由 D01 专项闭合。 |
| P03 | 鱼习性配置 | `P_BASE_087` | **中鱼习性模式（Engagement Mode）** | 同一鱼种在特定条件下可被激活 / 分配份额的一套中鱼逻辑配置身份；可以只改变参数，也可以切换一个或多个 Surface Program。 | `习性` 太宽，`Group` 更像在描述一群鱼本身；`Mode` 更准确表达“可切换的逻辑 / 配置形态”，又通过 `Engagement` 把范围限制在中鱼机制。 | **B**：吸收原 FishGroup 的业务身份与原 FishMode 的有效逻辑绑定职责；以后共同语言不再需要同时保留 `FishGroup + FishMode` 两层。 |
| P04 | 习性响应判断机制 | `P_BASE_042` | **响应程序（Response Program）** | Response Surface 上实际被 Engagement Mode 绑定、版本化并执行的一份逻辑资产；实现可以是手写程序、DSL 编译结果或 Hybrid。 | P图这里描述的是“实际做判定的机制”，Program 比 Template 更贴近 Runtime / Production 身份，也不预设底层 Representation。 | **B**：多个 Engagement Mode 可以直接共享同一个 Response Program；多个不同 Program 还可以进一步归属于同一个 Logic Template / Program Family。 |
| P05 | 诱鱼呈现库 | `P_BASE_026` | **诱鱼呈现（Presentation Definition → Presentation Signals）** | Authoring 侧定义饵与操作会形成什么呈现；Runtime 侧解析成鱼侧逻辑可读取的 typed Presentation Signals。 | 避免“库”同时指配置资产和运行时输入。 | **B/C**：高层一致；`Bait / Technique / Player Motion → Canonical Presentation Facts` 的完整上游合同仍是 Open。 |
| P06 | 鱼位置权重 | `P_BASE_034` | **环境权重（EnvironmentWeight） / 局部机会强度（LocalOpportunityIntensity）** | Bake 在某条件组 / 空间索引下，为某 Species × Engagement Mode 给出的局部环境机会强度。 | 两个词在这里表达同一个量：它是烘焙结果，不是最终中鱼概率。 | **A/B**：本 Alignment 将二者视作同义语义；不再把 Runtime Exposure 接入后的结果另称 EnvironmentWeight。 |
| P07 | 鱼诱鱼响应权重 | `P_BASE_030` | **响应权重（Response Weight）** | 在当前 Presentation 下，该 Engagement Mode 对本次呈现产生的响应强度 / 适配结果。 | 明确回答“当前呈现对这类鱼有多有效”。 | **B**：与当前 `Response / ResponseWeight` 高层一致。 |
| P08 | 中鱼总权重 | `P_BASE_021` | **候选选择权重（SelectionWeight）** | 进入 Round Table / Selection Pool 的最终候选权重。 | 直接对应 Runtime Consumer，避免“总权重”与场景总量 / Total Supply 混淆。 | **A**：高层角色与当前 `SelectionWeight` 基本一致；场景归一化 / Total Supply 仍是独立 D01。 |

---

## 1.1 P03 术语裁决｜Engagement Mode > Engagement Group

当前推荐正式共同语言：

```text
中鱼习性模式（Engagement Mode）
代码字段可短写 engageMode / engagementMode
```

核心原因不是名称偏好，而是这个对象回答的是：

> **当前这部分鱼使用哪一种中鱼逻辑配置形态？**

而不是：

> **这是不是一群具有长期群体身份的鱼？**

当前最小 Contract：

```text
Species
  ↓
Mode Routing / Share Resolution
  ↓
Engagement Mode
  ├─ Mode-local Parameters
  ├─ BakeProgramRef
  ├─ ResponseProgramRef
  ├─ QualitySelectionProgramRef（如需要）
  └─ 其它该 Mode 真正拥有的薄配置
```

创建新的 Engagement Mode 的准入可以有两种：

```text
A. 逻辑不变，但一组参数形成稳定、可辨识的中鱼形态
B. 一个或多个 Surface 的 Program / Program binding 真正变化
```

因此 **Program 是否变化不是 Mode 的必要条件**；只改参数也可以形成 Mode。反过来，一个天气 / 光照等动态事实如果只连续修改当前 Mode 的参数，而没有形成值得独立命名、分配 share、调试和 Authoring 的离散形态，也不应该自动升成 Mode。

`ModeShare` 只表示在当前 Condition Group / Scope 下，各 Engagement Mode 的相对份额；有 share 不等于这个对象必须叫 Group。

这也解释为什么 `Mode` 比 `Group` 更稳：Normal Feeding、Guarding、Cold-Slow、Forage-Coupled Feeding 等对象，语义中心都是“中鱼逻辑处于哪种形态”，而不是稳定 population cohort。此前 Bass 研究也反复出现“现实 Story 很多，但只有部分值得升成 Mode”的准入问题。

---

## 1.2 P04 术语裁决｜P图上的“判定机制”优先映射 Program，不映射 Template

必须保留两个层次，但不要让 P图同时承担两个词：

```text
LogicTemplate / Program Family
= 一类可复用的程序结构 / 控制流骨架（结构等价族，Census / Authoring 层）

Surface Program｜中鱼执行面逻辑程序
= 某个 Surface 上实际可被 Mode 绑定、版本化、编译和执行的逻辑资产
```

关系方向是**从 Program 反推 Template**，不是从 Template 实例化 Program：

```text
Surface Program A ─┐
Surface Program B ─┼→ 去实例化 / 结构比对（de-instantiation）
Surface Program C ─┘        ↓
              LogicTemplate / Program Family
```

多个 Program 去掉鱼名、参数值、合法 Fact Binding 后，如果 Operator、Gate / Branch、依赖关系、Aggregate 与 Return topology 相同，就归入同一个 LogicTemplate / Program Family。

也就是说：

- **LogicTemplate / Program Family 是 Census / Authoring 层的结构等价族**，不是 Runtime 对象；
- **Runtime（Engagement Mode）绑定的是 `ProgramRef`**；
- **Template 不是 Runtime Binding Identity**。

另有一种更简单的情况——多个 Mode 直接共享同一份通用 Program：

```text
Engagement Mode A ─┐
Engagement Mode B ─┼→ 同一个 ResponseProgramRef
Engagement Mode C ─┘
```

如果所有差异都能通过外部参数输入，那么根本不需要三个 Program Instance；多个 Mode 直接复用同一个通用 Program 即可。此时 Template 与 Program 在生产上几乎“塌缩”为同一份共享资产，这是允许的，不应为了概念完整强行造两层。

因此：

- **P哥图上的“习性响应判断机制” → `Response Program`｜响应逻辑程序；**
- `LogicTemplate / Program Family` 留在 Census / Authoring 层，由 Program 反推，而不是正向下发；
- Engagement Mode **绑定 `ProgramRef`**，不要求 Runtime 去绑定一个抽象 Template；
- Program 的实现方式保持中立：工程手写、DSL 编译、Hybrid 都可以。

---

## 1.3 Bake Output｜C03 收敛为同义命名与产物结构

本轮澄清后，不再使用：

```text
LocalOpportunityIntensity
→ 再经 Runtime Exposure
→ EnvironmentWeight
```

作为两个不同阶段值。

在当前共同语言里：

```text
EnvironmentWeight
≡ LocalOpportunityIntensity
```

都指 **Bake 已经算出的局部环境机会强度**。

一个简化的 Bake Artifact 心智模型可以写成：

```text
ConditionGroup / Spatial Index
  ↓
Species[]
  ↓
EngagementMode[]
  ├─ ModeShare
  ├─ EnvironmentWeight      # = LocalOpportunityIntensity
  └─ FishConditionSnapshot
       ├─ FeedingReadiness
       ├─ FunctionalCapacity
       └─ ...其它鱼侧动态参数
```

`ConditionGroup / Spatial Index` 是共享索引；其下可以查询很多 Species。每个 Species 在当前条件下可以有多个 Engagement Mode share，每个 Mode 有自己的 EnvironmentWeight，并带当前需要的鱼侧动态参数。

如果未来仍保留 Presentation-dependent `ExposureAccess`，它应作为 Runtime Response / Access 语义的一部分或独立乘项处理；**不要把它乘完以后再把结果命名成另一个 EnvironmentWeight**，否则会重新制造同名两阶段量。

---

## 2. Semantic Bridge Matrix｜第一轮修订

分类：`A` 名字不同但本质一致；`B` 本质一致但抽象粒度不同；`C` 高层一致但 Runtime / Production Semantic 还需闭合；`D` 真正机制语义差异。

| P图元素/关系 | Stable ID | 当前 FCF 对应 | 分类 | 第一轮动作 |
| --- | --- | --- | --- | --- |
| 基础品质配置 | `P_BASE_039` | FishQuality Definition + Quality Selection inputs | B | Terminology Bridge。 |
| 基础环境亲和配置 | `P_BASE_001` | SpatialOpportunityProfile | B | Terminology Bridge；Base / Supply 关系由 D01 专项处理。 |
| 鱼习性配置 | `P_BASE_087` | **Engagement Mode**：吸收旧 FishGroup identity + 有效 FishMode binding 职责 | B | C01 关闭为 Terminology / Contract consolidation，不做 Delta Overlay。 |
| 习性响应判断机制 | `P_BASE_042` | Response Program；LogicTemplate 位于其上方的复用 / Census 层 | B | C02 关闭为抽象层澄清，不做 Delta Overlay。 |
| 诱鱼呈现库 | `P_BASE_026` | Presentation Definition / Presentation Signals | B/C | 只桥接；Canonical Presentation Facts 仍 Open。 |
| 鱼位置权重 | `P_BASE_034` | EnvironmentWeight ≡ LocalOpportunityIntensity | A/B | C03 关闭；记录 Bake Artifact 结构即可。 |
| 鱼诱鱼响应权重 | `P_BASE_030` | ResponseWeight | B | Terminology Bridge。 |
| 中鱼总权重 | `P_BASE_021` | SelectionWeight | A | Terminology Bridge；不要解释成 Total Supply。 |
| 场景归一化 / 总量再分配 | 主要见 `P_BASE_009` 长文本；与初始权重 `P_BASE_051`、最终权重 `P_BASE_021` 相关 | Base Opportunity / Total Supply / Spatial Distribution 专项 | **D01** | **专项处理中，本任务不闭合。** |

这一轮的结果反而更符合 Alignment 的目标：**大部分差异被证明是 Terminology / Abstraction 差异；当前第一张图里仍明确保留的主要机制 Delta 只有 D01。**

---

## 3. Remaining Delta

### D01｜Total / Normalization vs Base Opportunity

- **Status：**专项处理中。
- **本轮规则：**不自行闭合，不用术语桥把它伪装成 A/B；等待 Base Opportunity × Total Supply 专项结果回流。

**D01 不简化成只属于 `P_BASE_051`。** 三个引用面必须分开写：

| 面 | 指向 | 说明 |
| --- | --- | --- |
| **Semantic Evidence** | `P_BASE_009` | D01 的语义证据来自左上长文本（场景归一 / 总量再分配 vs Base Opportunity / Total Supply）。 |
| **Visual Scope** | `P_BASE_051` → `P_BASE_034` / `P_BASE_030` → `P_BASE_021` | Delta 在图上覆盖的整条底部权重链：投鱼初始权重 × 鱼位置权重 × 鱼诱鱼响应权重 → 中鱼总权重。（此处按 P-tag 语义身份书写；注意链上「鱼位置权重」节点的 stableId 实为 `P_BASE_010`，而 `P_BASE_034` 是 P06 所锚的同名重复对象、位于上方分组内、不在链上。） |
| **Overlay implementation anchor** | `P_BASE_051` | 仅作为 bracket 的坐标起点；**不代表 semantic ownership 属于「投鱼初始权重」**。 |

即：图上 anchor 落在链首只是实现便利；D01 的语义归属是**整条链之上的 Contract 差异**，不是某一个节点。

其它 C01 / C02 / C03 已在本轮收敛为 Terminology / Production-layer mapping，不再需要正式 Delta Card。

---

## 4. Overlay R1（当前）

当前 Overlay 与 `overlay-spec.json` v4 一致：

| 标记 | 类型 | 说明 |
| --- | --- | --- |
| P01–P08 | `semanticTag` | 小型蓝色编号标签 + 紧邻轻量语义卡片（EN Contract 名 + 中文一行）。其中 P01/P02 的卡片移到大虚线框 `o1:41` **外侧**，各带一条蓝色短 leader 指回原节点。 |
| D01 | `deltaSpan` | amber 下沿 bracket **横跨整条底部权重链**，不是单节点备注。 |

- **Base 不改**：`pframe-base.excalidraw` 的 239 个元素保持锁定；Overlay 只在其上叠加 `OVR_*`。
- 不放 A/B 一致性徽标，不放 C/D 长气泡，不修改 Base 文本。
- 图上只保存“编号 → stableId → semanticRef”；详细定义只保存在本页。
- **第一张图不承担第二套架构**：它只做 Terminology / Delta 的桥接标注，不是新的机制图。

视觉目标：熟悉 P哥原图的人仍按原阅读路径看图，只在关键对象旁看到少量蓝色 Pxx 与一张 amber D01 卡片；需要时再回到本表查共同语言。

（历史：R0 只放 P01–P08 `numberTag`、无卡片，已被 R1 取代。）
