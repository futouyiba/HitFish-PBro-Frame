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
5. 《Mechanism Simplification Delta R0》（WORKING / NOT PROMOTED）。

关键状态边界：0.3.4 主文档仍保留 `FishGroup + FishMode` 的正式工作表述；最新 Logic Ownership Checkpoint 的更强候选是 **FishGroup 直接承担业务习性身份 + 独立 Bake / Response / Quality Surface Program，不再 materialize FishMode Runtime Identity**。因此本 Alignment 不把后者伪装成已 Promotion Current。

---

## 1. P哥 Frame Terminology Bridge

编号与 `overlay-spec.json` 一致。看图上的 Pxx，可以直接在本表找到同一编号。

| 编号 | P哥原词 | Stable ID | Candidate 术语 | 中文一句话定义 | 为什么更好 | 与当前 FCF 的关系 |
| --- | --- | --- | --- | --- | --- | --- |
| P01 | 基础品质配置 | `P_BASE_039` | **FishQuality 基础定义 / Base Quality Config** | 定义鱼的品质/体型桶及其基础生成范围、基础倾向。 | 保留“品质是独立轴”，避免把体型差异混进习性身份。 | **B**：与当前 `FishQuality` 基本一致，但当前另有独立 Quality Selection Surface。 |
| P02 | 基础环境亲和配置 | `P_BASE_001` | **空间机会画像（Spatial Opportunity Profile）** | 描述某 Species 在不同空间条件下，相对自身基准机会的无量纲空间形状/系数。 | 把“鱼整体稀有度”与“更喜欢哪里”拆开，Authoring / Runtime 边界清楚。 | **B**：对应当前 `SpatialOpportunityProfile`；编译后的局部值另称 `LocalOpportunityIntensity`。 |
| P03 | 鱼习性配置 | `P_BASE_087` | **中鱼习性群（Engagement Group）** *Candidate* | 同一鱼种内，在有意义时间窗口中共享主要中鱼因果路径的一群鱼；承载业务习性身份与逻辑绑定。 | “习性”过宽、`Group` 过泛；`Engagement Group` 明确范围只到中鱼机制，同时不承诺额外 Runtime Mode 层。 | **C**：正式 0.3.4 当前仍叫 `FishGroup`；最新 Logic Ownership Working 倾向由 FishGroup 直接承担该身份。**暂不采用 Engagement Mode**。 |
| P04 | 习性响应判断机制 | `P_BASE_042` | **响应逻辑模板（Response Logic Template）** *Candidate* | 可被多个习性群复用的一套 Response 控制流结构；具体绑定执行资产仍是 `Response Program`。 | 能表达“结构复用”，同时不把 Template、Program Instance 和 FishGroup Identity 混成一层。 | **C**：当前 FCF 已区分 `LogicTemplate / Program Family` 与实际 `ResponseProgramRef`；P图此节点尚未明确自己是哪一层。 |
| P05 | 诱鱼呈现库 | `P_BASE_026` | **诱鱼呈现（Presentation Definition → Presentation Signals）** | Authoring 侧定义饵与操作会形成什么呈现；Runtime 侧解析成鱼可读取的 typed Presentation Signals。 | 避免“库”同时指配置资产和运行时输入；能直接接 Response Contract。 | **B/C**：高层一致；`Bait / Technique / Player Motion → Canonical Presentation Facts` 的完整上游合同仍是 Open。 |
| P06 | 鱼位置权重 | `P_BASE_034` | **局部机会强度（Local Opportunity Intensity）** | 某 Species / Candidate 在当前局部空间中、进入当前机会池之前的空间机会强度。 | 比“位置权重”更明确它是机会强度，不等于最终中鱼概率。 | **C**：当前 FCF 还区分 `LocalOpportunityIntensity` 与包含必要 Exposure/Access 后的 `EnvironmentWeight`，P图边界需要补最小运行语义。 |
| P07 | 鱼诱鱼响应权重 | `P_BASE_030` | **响应权重（Response Weight）** | 在空间机会已成立后，当前 Presentation 对该 Candidate 的响应强度/适配结果。 | 明确回答“愿不愿开始互动”，不重新解释鱼在哪里。 | **B**：与当前 `Response / ResponseWeight` 基本一致，当前 FCF 对 Stage Ownership 更严格。 |
| P08 | 中鱼总权重 | `P_BASE_021` | **候选选择权重（SelectionWeight）** | 进入 Round Table / Selection Pool 的最终候选权重。 | 直接对应 Runtime Consumer，避免“总权重”与场景总量/总供给混淆。 | **A**：高层角色与当前 `SelectionWeight` 基本一致；但“场景归一化总量”是独立 D01，不在本术语行里闭合。 |

### 术语裁决：为什么 P03 暂不叫 Engagement Mode

Prompt 中的 `Engagement Mode` 是合理候选，但 fresh rebase 后不宜直接确认：

- `Mode` 会承诺一个可独立切换、可被 Runtime materialize 的离散模式身份；
- 最新 Logic Ownership Working Checkpoint 恰恰在做职责分流：习性身份 → FishGroup；具体算法 → typed Surface Program；常见组合 → 一次性 Logic Preset；
- 分流后 `FishMode` 暂时没有剩余的独立信息，因此当前更低承诺的共同语言是 **Engagement Group**。

如果后续出现严格跨 Surface Bundle invariant，或确实需要一个独立 Runtime mode identity，再 reopen `Engagement Mode / LogicProfile`，而不是现在先把它写进共同语言。

### 术语裁决：Logic Template 与 Program 必须分开

`Logic Template` 表达的是**可复用控制流结构**；`Program` 表达的是某 Surface 可被绑定、版本化、编译/执行的具体逻辑资产。当前 Working 倾向保持：

```text
FishGroup
├─ BakeProgramRef
├─ ResponseProgramRef
└─ QualitySelectionProgramRef

多个 Program Instance
        ↑
可共享同一 LogicTemplate / Program Family
```

因此 P哥图上的“判定机制”如果表示“大家共用的判定结构”，叫 Logic Template 合适；如果表示“这条鱼/这个 Group 实际绑定的可执行规则”，生产语义应落到 Surface Program。这个区分进入 C01/C02，而不是靠一个新词强行抹平。

---

## 2. Semantic Bridge Matrix｜第一轮初判

分类：`A` 名字不同但本质一致；`B` 本质一致但抽象粒度不同；`C` 高层一致但 Runtime / Production Semantic 还需闭合；`D` 真正机制语义差异。

| P图元素/关系 | Stable ID | 当前 FCF 对应 | 分类 | 第一轮动作 |
| --- | --- | --- | --- | --- |
| 基础品质配置 | `P_BASE_039` | FishQuality Definition + Quality Selection inputs | B | 只做 Terminology Bridge，不进 Delta Overlay。 |
| 基础环境亲和配置 | `P_BASE_001` | SpatialOpportunityProfile | B | 只做 Terminology Bridge。 |
| 鱼习性配置 | `P_BASE_087` | FishGroup；最新 Working 候选为 business habit identity + Surface bindings | C | 记录 C01：Routing / Group Identity / Program Binding 的最小 Contract。 |
| 习性响应判断机制 | `P_BASE_042` | Response LogicTemplate / Response Program | C | 记录 C02：先分清 Template 与 bound Program，不讨论 DSL 实现。 |
| 诱鱼呈现库 | `P_BASE_026` | Presentation Definition / Presentation Signals | B/C | 当前只桥接；上游 Canonical Presentation Facts 合同保持 Open。 |
| 鱼位置权重 | `P_BASE_034` | LocalOpportunityIntensity →（必要 Exposure 后）EnvironmentWeight | C | 记录 C03：把 Bake 后局部机会与 Runtime Exposure 边界说清。 |
| 鱼诱鱼响应权重 | `P_BASE_030` | ResponseWeight | B | 只做 Terminology Bridge。 |
| 中鱼总权重 | `P_BASE_021` | SelectionWeight | A | 只做 Terminology Bridge；不要把它解释成 Total Supply。 |
| 场景归一化 / 总量再分配 | 主要见 `P_BASE_009` 长文本；与初始权重 `P_BASE_051`、最终权重 `P_BASE_021` 相关 | Base Opportunity / Total Supply / Spatial Distribution 专项 | **D01** | **专项处理中，本任务不闭合，不进入第一版 Delta Overlay。** |

---

## 3. First Delta Candidates｜只识别，不在本轮展开

### C01｜“鱼习性”到底是 Group Identity，还是 Runtime Mode

- **P哥当前表达：**鱼习性配置会被点位环境/结构触发，并影响活性、位置与响应。
- **当前 FCF 高层理解：**这里确实需要一个“同鱼种内中鱼习性身份”。
- **最小 Candidate Semantic：**`Group Routing → current Engagement Group/FishGroup → group-local params + typed Surface Program bindings`。
- **本轮 Recommendation：**用 `Engagement Group` 做沟通候选；不新增 `Engagement Mode` Runtime Layer。
- **Status：**C / WORKING，等待后续 Candidate Semantic case 验证。

### C02｜“判定机制”是 Template 还是 Program

- **P哥当前表达：**习性/诱鱼响应存在判定机制。
- **当前 FCF 高层理解：**可复用逻辑结构与实际绑定执行资产必须分层。
- **最小 Candidate Semantic：**多个 `Response Program` 可以共享同一 `Response Logic Template`；FishGroup 绑定 Program，不直接绑定抽象 Template。
- **本轮 Recommendation：**Terminology 用 `Logic Template` 解释复用层；Production Contract 保留 `Surface Program` 身份。
- **Status：**C / WORKING。

### C03｜“鱼位置权重”的阶段边界

- **P哥当前表达：**点位匹配后烘焙出鱼位置权重。
- **当前 FCF 高层理解：**Bake 后的 `LocalOpportunityIntensity` 与 Runtime 的 `ExposureAccess` 不应静默混成同一个概念。
- **最小 Candidate Semantic：**先得到局部机会强度；如果当前 Presentation 的可见/可听/可触达性还依赖 Runtime 条件，再形成最终 `EnvironmentWeight`。
- **Status：**C / WORKING。

### D01｜Total / Normalization vs Base Opportunity

- **Status：**专项处理中。
- **本轮规则：**不自行闭合，不用术语桥把它伪装成 A/B；等专项结论回流后再决定 Delta Card 与 Overlay。

---

## 4. Overlay R0

第一版 Overlay **只放 P01–P08 numberTag**：

- 不放 A/B 一致性徽标；
- 不放 C/D 长气泡；
- 不修改 Base 文本；
- 图上只保存“编号 → stableId → semanticRef”；
- 详细定义只保存在本页。

视觉目标：熟悉 P哥原图的人仍按原阅读路径看图，只在关键对象旁看到少量蓝色 Pxx；需要时再回到本表查共同语言。
