# 03 · 数据契约与 Schema

> 本文是 [02 架构](02-Production架构设计.md) 的数据层落地：全部配置与产物结构、编辑器创作模型、编译期校验规则。
> Schema 采用 JSON 表示；工程实现可换protobuf/表结构，但字段与语义为契约。
> 更新记录 R1.1（2026-09-10）：并入 06 复核 F2（`AFIT_CAP` veto 动作 + 编译期强制校验）与 F1（priority 域校验）。

---

## 一、空间数据（关卡侧供给）

### 1.1 SpatialTarget（空间目标 = 结构区 × 水层带）

```json
{
  "targetId": "L1-GRASS-EAST-03-M",
  "zoneId": "L1-GRASS-EAST-03",
  "layer": "MIDDLE",                    // SURFACE|UPPER|MIDDLE|LOWER|BOTTOM
  "structureTags": ["GRASS_EDGE"],       // 多标签，继承自对话（非单枚举）
  "attributes": {                        // 连续属性，环境管线与模板读取
    "depthM": 2.5, "flowType": "SLACK", "flowSpeed": 0.2,
    "cover": 0.8, "bottomType": "SILT", "openness": 0.3,
    "shade": 0.4                         // 静态遮蔽基线；动态光照来自环境管线
  },
  "capacity": 12.0,                      // 可钓点数 / 面积归一承载量，归一化权重用
  "connectivity": ["L1-GRASS-EAST-03-L", "L1-DROP-07-M"]  // 迁移可达邻接
}
```

约定：
- Zone 粒度：20–50m 结构单元；每 Zone 切 3–5 水层带；场景规模 100–500 Target；
- `capacity` 必填且 >0（归一化公平性依赖，继承"按容量加权"结论）；
- 层带与物理深度解耦（FeedingLayer 生态语义 vs Depth 物理值），映射表由关卡配置。

### 1.2 EnvFactSlice（环境事实切片，环境管线产物）

```json
{
  "sliceId": "2026W37-D3-T2",            // 周-日-时段
  "scene": {
    "season": "EARLY_SUMMER", "weather": "CLOUDY",
    "airTempC": 26, "pressureHpa": 1008, "pressureTrend": "FALLING"
  },
  "perTarget": {                          // 稀疏：只列有局部事实的 Target
    "L1-GRASS-EAST-03-M": { "waterTempC": 24.5, "oxygen": 0.62,
      "light": 0.35, "turbidity": 0.4, "foodDensity": 0.7 },
    "L1-DEEP-09-B": { "waterTempC": 19.0, "oxygen": 0.35 }
  },
  "events": { "baitfishSchool": ["L1-OPEN-02-U"], "hatch": [], "fishingPressure": 0.3 },
  "derived": { "heatStressBase": 0.42, "oxygenStressBase": 0.15 }  // 管线预计算的压力基线
}
```

约定：
- **派生与平滑在管线内完成**（moving_average / trend / hysteresis），烘焙内核只读成品事实——继承"时间持续与迟滞不进 DSL/内核"的决定；
- 事件事实（饵鱼群位置、羽化、钓压）由外部状态系统写入，烘焙不管理其演化；
- `weather` 只是因，内核与条件行禁止直接读它（通道纪律）。

---

## 二、模板库（预设，authoring 时被宏复制，D4）

### 2.1 SpaceTemplate（空间模板）

```json
{
  "tplId": "SP_SHALLOW_STRUCTURE",
  "name": "浅水结构驻留",
  "gates": [                              // 硬 Gate 声明
    { "fact": "target.attributes.depthM", "op": "LTE", "value": 6.0 }
  ],
  "coreFactors": [                        // 核心层：几何平均（AND 语义）
    { "field": "structure",  "weight": 1.5, "matcher": { "type": "TAG_LOOKUP",
        "table": { "GRASS_EDGE": 1.0, "WOOD": 1.0, "ROCK": 0.6, "OPEN": 0.15 } } },
    { "field": "layer",      "weight": 1.0, "matcher": { "type": "TAG_LOOKUP",
        "table": { "MIDDLE": 1.0, "LOWER": 1.0, "BOTTOM": 0.7, "SURFACE": 0.2 } } },
    { "field": "flow",       "weight": 0.8, "matcher": { "type": "RANGE_FIT",
        "comfort": [0.0, 0.3], "acceptable": [0.0, 0.6] } }
  ],
  "comfortFactors": [                     // 舒适层：加性、限幅 ±0.3 总钳
    { "field": "cover",      "delta": { "type": "LINEAR_POS", "scale": 0.15 } },
    { "field": "bottomType", "delta": { "type": "TAG_LOOKUP",
        "table": { "SILT": 0.05, "GRAVEL": 0.0, "ROCK": -0.05 } } }
  ]
}
```

Matcher 类型全集（继承对话的算法分类，L0）：`TAG_LOOKUP / RANGE_FIT(comfort,acceptable,curve) / CURVE(points) / MONO_POS / MONO_NEG / PRESSURE(trigger) / RELIEF(fields)`。`RELIEF` 型实现动态空间响应：读取 `derived.heatStressBase` 等压力，输出 `lerp(1, relief, pressure)` 进 comfort 层。

### 2.2 FeedingTemplate（摄食模板）

```json
{
  "tplId": "FT_AMBUSH_ENGULF",
  "name": "伏击吞食",
  "targetFood": ["FISH_S", "CRAYFISH", "FROG"],
  "senses": { "vision": 0.6, "lateral": 0.8, "smell": 0.3 },   // 感知权重
  "approach": "AMBUSH_BURST",
  "action": "ENGULF",
  "attackInvest": {
    "approachDistM": 1.5, "chaseDistM": 4.0, "leaveStructureM": 3.0,
    "reattack": 0.4, "patience": 0.5
  },
  "baitAffinity": {                       // BaitMatch 的鱼侧输入（运行时）
    "profileByType": { "SOFT_PLASTIC": 1.0, "CRANK": 0.8, "JIG": 1.1, "FLOAT_FLY": 0.4 },
    "sizeRangeCm": [4, 18], "colorTilt": { "NATURAL": 0.1, "FLASHY": -0.1 },
    "speedPref": [0.2, 0.8],              // PresentationMatch 输入
    "pauseLove": 0.7, "trajectory": { "STEADY": 0.6, "TwitchPause": 1.0, "BOTTOM_DIE": 0.8 }
  },
  "stateProjection": {                    // D5：四态的表现差异（供 APP/FishAI 展示层）
    "ACTIVE":  { "radiusScale": 1.4, "reattackBonus": 0.2 },
    "NORMAL":  { "radiusScale": 1.0, "reattackBonus": 0.0 },
    "OPPORTUNISTIC": { "radiusScale": 0.6, "requireHighMatch": true },
    "SUPPRESSED":  { "radiusScale": 0.2, "requireContact": true }
  }
}
```

### 2.3 ConditionRow（条件行 = L1 规则的全部表达力）

```json
{
  "rowId": "R-heat-shallow",
  "comment": "高温时压制阳性浅水、抬升遮蔽舒适度",
  "when": { "fact": "derived.heatStressBase", "op": "GT", "value": 0.35 },
  "effect": {
    "channel": "PFIT",                    // SUPPLY|SCOPE|PFIT|AFIT（D2）
    "targetField": "comfort.shadeRelief",
    "action": "ADD_DELTA",                // ADD_DELTA|MUL|CLAMP_LO|CLAMP_HI|AFIT_CAP|GATE_FAIL|FORCE_SHARE|SCOPE_SET
    "value": { "type": "PRESSURE_SCALE", "scale": 0.3 },
    "cap": 0.3
  },
  "priority": 10,                         // 同通道冲突时的静态序（编译期排序，无运行期自由顺序）
  "conflictWith": ["R-cold-shallow"],
  "missingDataPolicy": "USE_DEFAULT:0",   // ERROR|SKIP|USE_DEFAULT:x（显式，绝不静默=1）
  "traceTemplate": "HEAT_STRESS_SHALLOW_SUPPRESS"
}
```

**表达力上限即此**：条件（单事实比较 + 可选 AND 两个）→ 对四通道之一的限幅动作。无变量、无顺序自由、无跨行读取、无 Early Return（Gate 是唯一短路）。超出此表达力的需求 = 新增 Matcher 类型走框架扩展，不走规则书写。

**F2 veto 包络（公式层的一票否决）**：`A = min( clamp01(aBase + Σ AFIT_delta行), Π AFIT_cap行 )`。加性增量允许正负抵消（黄昏 +0.25 + 食物 +0.2 可抵掉严重缺氧 −0.4），因此否决必须结构化：
- `AFIT_CAP` 行进入乘性上限连乘组；模板库内置**标准 veto 包**（严重缺氧 cap 0.15 / 超出摄食适温 cap 0.2 / 极端流速 cap 0.25，数值待 05 模拟校准），宏复制时默认带入（D4 机制天然支持"默认带包"）；
- 编译期强制：凡生存 Gate 含溶氧/温度/流速的鱼种，AFIT 必须存在对应 `AFIT_CAP` 行——靠结构不靠自觉。

---

## 三、鱼种档案 FishProfile（authoring；宏复制产物 = ResolvedProfile）

```json
{
  "fishId": "largemouth_bass",
  "familyMacro": "FM_BASS_V3",            // D4：仅作复制来源标记，运行时无继承
  "provenanceNote": "copied 2026-09-10; modified: temperature, modes[1].priority",
  "base": {
    "survivalGates": [
      { "fact": "waterTempC", "op": "BETWEEN", "value": [2, 36] },
      { "fact": "oxygen",     "op": "GTE", "value": 0.25 },
      { "fact": "salinity",   "op": "LT",  "value": 3 }
    ],
    "basePop": 100.0,                     // 本场景基础投放（Supply 基线，地图层可覆盖）
    "supplyClamp": [0.2, 2.0],
    "activityGamma": 1.0                  // ActivityMod = A^γ
  },
  "modes": [
    { "roleId": "MAIN", "priority": 1.0, "mixability": 1.0, "inertiaHint": null,
      "spaceTpl": "SP_SHALLOW_STRUCTURE", "feedingTpl": "FT_AMBUSH_ENGULF",
      "aBase": 0.55,
      "conditionRows": ["R-dusk-boost", "R-cold-dormant"] },
    { "roleId": "SUB", "id": "open_chase", "priority": 0.9, "mixability": 0.8,
      "spaceTpl": "SP_OPEN_FOLLOW", "feedingTpl": "FT_ACTIVE_CHASE", "aBase": 0.6,
      "conditionRows": ["R-baitfish-window"] },          // SCOPE 行：饵鱼群出现→Scope 上升
    { "roleId": "LIFECYCLE", "id": "spawn_guard", "priority": 1.2, "mixability": 1.0,
      "spaceTpl": "SP_SPAWN_SHALLOW", "feedingTpl": "FT_DEFENSIVE_STRIKE", "aBase": 0.35,
      "conditionRows": ["R-spawn-season"] },             // FORCE_SHARE: 产卵季钉 0.25 份额
    { "roleId": "AVOID", "priority": 1.5, "mixability": 1.0,
      "spaceTpl": "SP_REFUGE_DEEP_SHADE_O2", "feedingTpl": "FT_NONE", "aBase": 0.05,
      "conditionRows": ["R-heat-pressure", "R-oxygen-pressure"] }
  ],
  "qualities": [                           // D7：体型轴恢复
    { "q": "SMALL",  "share": 0.60, "weightKg": [0.3, 1.0], "lengthCm": [20, 32] },
    { "q": "MEDIUM", "share": 0.30, "weightKg": [1.0, 2.5], "lengthCm": [32, 45],
      "pOverrides": [ { "channel": "PFIT", "field": "core.structure.WOOD", "delta": 0.2 } ] },
    { "q": "TROPHY", "share": 0.10, "weightKg": [2.5, 6.0], "lengthCm": [45, 65],
      "pOverrides": [ { "channel": "PFIT", "field": "core.layer.BOTTOM", "delta": 0.25 },
                      { "channel": "AFIT", "field": "aBase", "delta": -0.10 } ] }
  ],
  "display": { "stateThresholds": { "family": "WARM_PREDATOR",
      "cut": [0.25, 0.45, 0.75] } }        // D5：仅投影用
}
```

**ResolvedProfile**：编辑器保存时宏展开的纯平铺结构（模式×模板参数×条件行内联，字段级 provenance）。**CompiledProfile**：按通道预分组、常量折叠、按 priority 静态排序后的运行时形态（数组化、无字符串查找）。三者关系：

```text
FishProfile(authoring, 带宏标记) → Resolve(展开+溯源) → ResolvedProfile(平铺)
                                   → Validate(静态检查) → Compile → CompiledProfile(版本化)
```

---

## 四、烘焙产物 BakeArtifact

```json
{
  "bakeRevision": "BK-2026W37-0007",
  "revisions": { "config": "CFG-0.4.2", "rule": "RULE-0.4.2", "environment": "ENV-1.9" },
  "sceneId": "LAKE1", "week": "2026-W37",
  "records": [                            // 列式存储，此处 JSON 示意
    {
      "slice": "2026W37-D3-T2", "fishId": "largemouth_bass", "q": "MEDIUM",
      "targetId": "L1-GRASS-EAST-03-M",
      "envWeight": 3.42,                  // 圆桌直接消费
      "a_selection": 0.71, "a_dominant": 0.68, "dominantModeId": "MAIN",
      "shares": { "MAIN": 0.58, "open_chase": 0.17, "spawn_guard": 0.25, "AVOID": 0.0 },
      "trace": { "topReasons": ["DUSK_WINDOW+0.15","OXYGEN_LOW-0.05"],
                 "supply": 0.9, "fallback": null }
    }
  ],
  "hints": [                              // APPHint 投影（客户端可见的全部）
    { "zone": "L1-GRASS-EAST", "slice": "2026W37-D3-T2",
      "state": "ACTIVE", "recommendTags": ["SOFT_PLASTIC","TwitchPause"] }
  ]
}
```

不变量（进版前强制校验）：
1. `Σ_target envWeight(fish,q,·,slice) == Supply × QualityShare`（容差 1e-4，守恒）；
2. `Σ_m shares == 1`；`a_selection ∈ [0,1]`；`a_dominant ∈ [0,1]`；`dominantModeId` 必须存在；`envWeight ≥ 0`；
3. 无 NaN/Inf；无 `fallback != null` 超过阈值（默认 0.5% 记录）的批次否则 Bake 失败；
4. `records` 的 revision 四元组一致。

## 五、运行时 API（服务端）

```text
EvaluateCast(session, sceneId, slice, baitPosM, layerGuessM, baitDesc, presentationStats, seed)
  → { selection: {fishId, q} | NONE,
      weightDetail: { envWeight, activityMod, baitMatch, presentationMatch, distanceMatch },
      traceId }                            // traceId + revisions + seed = 完整回放键
```

- `ResolveTarget`：饵位置 → (zone, layerBand)；v1 最近带，v2 双带线性插值（记录进决策日志）；
- 调用方：旧实时中鱼入口；P0 期三 Match 由旧饵/手法适配替代（同接口注入），P1 期切换。

## 六、编译期校验清单（全部静态，失败即阻止进版）

| 类别 | 检查 |
|---|---|
| 引用 | 模板/条件行/事实路径存在；matcher 参数完备 |
| 数值 | 权重>0；RANGE_FIT 的 comfort⊂acceptable；supplyClamp 下界<上界；share≥0；**priority ∈ [0.5, 2.0]（F1：幂归一对量纲敏感）** |
| 通道纪律 | 同 (fish, 事实, 通道, 目标字段) 只有一行生效（conflictWith 覆盖或 priority 唯一）；天气事实直接引用→拒绝 |
| Gate | 生存 Gate 与空间 Gate 不重复登记同一事实；Gate 不进 comfort 层 |
| 守恒 | qualities.share 总和=1；每 Target capacity>0 |
| 模式 | 必须且仅有一个 `FALLBACK`；其余行为模式（含 MAIN/AVOID/LIFECYCLE）可选；LIFECYCLE 的 FORCE_SHARE 总和 ≤ 0.6 |
| 投影 | stateThresholds 单调递增 |
| MissingDataPolicy | 每行显式；涉及 Gate 的事实只允许 ERROR |
| Veto（F2） | 凡生存 Gate 含溶氧/温度/流速的鱼种，AFIT 必须存在对应 `AFIT_CAP` 行；标准 veto 包随宏复制默认带入 |
## Reviewer R1 强制契约补充

- `modes` 必须恰好包含一个 `id=FALLBACK`；Scope 全零只指向该模式。
- `qualities[].share >= 0` 且总和为 1；`mixability >= 0`；`tau > 0`。
- Bake 产物同时保存 `a_selection`、`a_dominant` 和 `dominantModeId`。
- `EnvironmentRevision` 必须包含事实 DAG 版本和 EMA 初始状态哈希。

### R1 数值与版本硬校验

- `mixability >= 0`；`tau > 0`（建议 `0.5 <= tau <= 3`，超出需显式豁免）。
- `qualities[].share >= 0` 且总和为 1（允许误差 1e-6）。
- `modes` 恰好一个 `id=FALLBACK`。
- `EnvironmentRevision` 含事实 DAG/hash 与 EMA 初始状态 hash。
