# 真实闭环案例：混合粒度日期误报（B1）

> ✅ **本文件是 `delivery-acceptance` skill 的一次真实验收闭环产物（已脱敏）。** 项目名、提交哈希已中性化，但决策链、探针证据、契约保护逻辑、测试增长数字（731→733）均为真实运行结果，非虚构。它展示 skill 的"必跑探针 + 保护既有契约 + 闭环修复"三件套在真实 bug 上如何落地。
>
> 脱敏说明：原项目名、真实 commit hash 已替换为占位；文件路径 `src/core/timeline-check.mjs`、函数名 `checkTimeline`/`parseDateRaw` 为通用模式，保留以保持技术可读性。

---

## 背景：这次验收在干什么

某项目交付了一份"故事时间线检查"功能（Part A，8 个 feat 提交 + 1 个 fix 提交，**731 测试全绿**）。delivery-acceptance 以独立验收师傅视角做第二次验收，发现一个隐藏 bug：

> **B1：日期混合粒度比较产生假倒退。** 当故事里先出现"2021年3月15日"（日粒度）、再出现"2021年3月"（月粒度）时，检查器误报"时间倒退"。但"2021年3月"可能指 3 月任意一天（含 15 日之后），并非确定倒退 → **误报**，违反计划原则 A3「宁缺毋滥」。

这个 bug **只读代码 + 跑既有测试永远挖不出来**——既有 731 测试全绿，恰恰因为没人喂过"月粒度跟在同月日粒度后面"这种中间态。必须写探针才能暴露。

---

## 探针证据（修复前）

```
ch3=2021年3月15日, ch5=2021年3月  => violations: 1 [{"type":"time_reversal","ch":5,"prior":3}]   ← 误报
parseDateRaw("2021年3月") => {"comparable":true,"value":20210300}                               ← 契约保留，不动
```

探针把"疑似 bug"变成了"确认 bug"——这是 delivery-acceptance 的硬要求，不允许停留在"我觉得这里有风险"。

---

## 关键决策：保护既有契约（skill 原则 #6）

这里有一次**真实的工程纪律考验**。修 B1 有两条路：

| 方案 | 做法 | 后果 |
|------|------|------|
| ❌ 改契约 | 把 `comparable` 从「有年且(有月或日)」收紧成「必须年月日齐全」 | 能消误报，但**波及所有消费方**（render/fact-check/迁移），破坏 `:155` 测试。历史上真有人这么试过，被 revert 回退。 |
| ✅ 保护契约 | `comparable` 语义**一字不改**，只在 `checkTimeline` 比较处按"双方最粗公共粒度"对齐 | 消误报 + 保覆盖，改动局部化，零回归。 |

**delivery-acceptance 选了第二条**——并在 polish 计划里显式声明"本 Fix 不改 `parseDateRaw`/`comparable` 语义，不触及渲染、fact-check 等消费方，改动仅限 `checkTimeline` 内部"。

> 这就是 skill 的真实增量价值所在：**不在"能不能发现 bug"（有经验的无 skill agent 也能发现），而在"修复时守住工程纪律、不随手改已被评审过的契约"。** baseline（无 skill）修同一个 bug 时，直接改了 `comparable` 契约，波及所有消费方却不自知。

---

## TDD 闭环（先失败测试 → 改实现 → 跑绿）

### Step 1 失败测试（追加到 `tests/timeline-check.test.mjs`）

```js
test("checkTimeline: 月粒度与日粒度混比不误报倒退（B1）", () => {
  // 同年同月：日粒度在前、月粒度在后；月粒度可能落在该月任意一天，不应判倒退
  const { violations } = checkTimeline([
    an(3, "scene", { type: "date", raw: "2021年3月15日" }),
    an(5, "scene", { type: "date", raw: "2021年3月" })
  ]);
  assert.equal(violations.length, 0);
});

test("checkTimeline: 月粒度之间真实倒退仍报（防过度收窄）", () => {
  // 行为锁定：修复不得把月粒度日期整体踢出裁决（否则与"粒度足够"意图相悖）
  const { violations } = checkTimeline([
    an(3, "scene", { type: "date", raw: "2021年3月" }),
    an(5, "scene", { type: "date", raw: "2021年2月" })
  ]);
  assert.equal(violations.length, 1);
  assert.equal(violations[0].type, "time_reversal");
});
```

> 注意第二条测试：它不是修 B1 本身，而是**防过度收窄**——锁定"月粒度之间真实倒退仍要报"，防止未来有人把修复做成"月粒度整体踢出裁决"。这是 skill 教的"修 bug 时同时锁定正反两面行为"。

### Step 2 跑红

`node --test tests/timeline-check.test.mjs` → 第一条 FAIL（`violations.length` 实测 1，预期 0）。第二条当前已绿（行为锁定）。

### Step 3 实现（按粒度对齐，契约不变）

改动仅限 `checkTimeline` 内 `date_regression` 循环——双方均有日 → 比完整 `value`；任一为月粒度 → 只比年月（`Math.floor(value/100)`）。`parseDateRaw`/`comparable` 一字未改。

### Step 4 跑绿 + 全量回归

```bash
node --test tests/*.test.mjs tests/app-shell/*.test.mjs
```

**Expected: 全绿（既有 731 + 本次新增 2 条 = 733 全通过）。✅ 实测通过。**

---

## 闭环结论

| 维度 | 结果 |
|------|------|
| 探针挖出隐藏 bug | ✅ B1（混合粒度误报），既有 731 测试挖不到 |
| 保护既有契约 | ✅ `comparable` 语义不变，对比 baseline 的改契约做法 |
| TDD 红绿 | ✅ 先失败测试→跑红→改实现→跑绿 |
| 全量回归 | ✅ 731 → 733 全绿，零回归 |
| 可合并 | ✅ 通过 |

这就是 delivery-acceptance 一次完整验收闭环的真实形态：**探针证明交付有假 → 写 TDD 改进计划 → 派子代理修复（守住契约）→ 复审全绿 → 可合并。**
