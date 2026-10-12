# Skeptic 派发模板优化 · 设计文档

> 日期:2026-06-21 · 关联技能:`find-bugs`(`SKILL.md`)· 优化对象:第 54-71 行 "Skeptic dispatch prompt"
>
> 修订记录:初稿经独立审查 agent("子弹")挑刺,修复 8 项问题(五问逐字、absence 类举证出路、复述因果诚实化、格式对齐、at-a-glance 职责、防滥用、Candidate 块、token 估算)。

---

## 1. 背景与痛点

`find-bugs` 技能的核心机制是"两层对抗式过滤":提出候选 bug → 派一个**完全不知情的 fresh skeptic** 逐条反驳 → 反驳不倒且主 Agent 一眼认同才算确认,预期砍掉一半候选。

当前 skeptic 派发模板(2026-06-21 已落地的 P0 版本)虽然补上了派发说明,但存在一个未解决的痛点:

**skeptic 容易走过场** —— 它读了一堆要求,实际反驳时却敷衍作答,没真正逐条读代码取证,随口就给 confirmed/rejected。

定位到两个让 skeptic 能糊弄的真漏洞(初稿列了三个,审查指出第三个"裁决太轻"部分夸大,见下):

1. **举证无门槛**:原文第 64 行 "Answer each, with the line you read as proof" 是软性要求,没硬性规定贴代码原文,也没要行号,它可以空口说"我读了,没问题"
2. **无法证明真读了**:原文第 56 行虽写 "Independently read the cited lines yourself",但只是指令、无验证机制,它可以照抄候选描述措辞,根本没独立读代码

> **关于第三个"漏洞"的诚实订正**(审查指出):原文第 71 行已要求 "one-line reason **citing which question killed or confirmed it**"——即"裁决指向具体问题"的约束本就存在。本次只是在它基础上加"行号/条目"粒度,**不是从无到有**。初稿把它描述成"裁决太轻"忽略了既有约束,此处订正。

## 2. 目标与非目标

### 目标
让一个想糊弄的 skeptic "交不出差" —— 它必须真去读代码、给出可核验的取证、指明靠哪一条得出裁决,否则给不出有效作答。

### 非目标(划清边界)
- **不碰五问内容**(代码事实/设计边界/独立还是派生/部署现实/严重性)—— 打磨报告已验证自洽;本次五问**逐字照抄原文**(见 §6 骨架)
- **不碰两层过滤机制**(fresh skeptic + at-a-glance);**不重构 at-a-glance 的既有职责**
- **不改默认立场** —— 保持"砍半"承诺,**不搞"默认驳回"**(会系统性误杀真 bug)
- **不加打分机制**(同行 bug-hunt 的路子,过度工程)
- **不加自动重派循环**(判无效后由主 Agent 决定,非无限循环)

## 3. 方案选择

| 方案 | 做法 | 取舍 |
|---|---|---|
| A 强制举证 | 每问给可核验取证,裁决指向具体条目 | 直接堵敷衍;需处理 absence 类问题 |
| B 默认驳回 | skeptic 默认 rejected,只有铁证才 confirmed | 对糊弄最狠;**但误杀真 bug,违背"砍半"承诺** ✗ |
| C 两阶段禁跳步 | 阶段1只许取证不许结论,阶段2才裁决 | 堵跳步;弱 runtime 难遵循多阶段 |

**选定:A。** 吸收 C 的"裁决必须指向具体条目"思想(本就接近原文已有约束,只加粒度),但不采用 C 的多阶段结构(弱 runtime 难遵循)。不选 B 是因违背产品承诺。

**A 的关键适配(审查驱动的核心修正)**:不是所有五问都有"单行代码"可贴——Q2(找"无 by design 信号")、Q3(可达性,常跨文件)、Q4(查默认配置/dormant)的正解本就是 **absence**(没找到东西)。若一刀切逼贴行号,skeptic 要么伪造一行,要么该问被判无效,而裁决又要求指向某条 → **系统性误杀这类真实发现**。因此 A 的举证要求分两种模式(见 §4 段②)。

## 4. 具体设计:三段式模板

### 段① 开工前复述
- skeptic 先用自己话 1-2 句复述这个 bug 候选在说什么
- **禁止照抄候选描述的措辞**
- **诚实定位**:复述只能证明 skeptic 读了候选描述、理解了它在说什么;**它不证明 skeptic 独立读了代码**。独立读码的诚实性靠段②的可核验取证承担(段②取证可伪造的残余风险见 §5)
- 复述不出/照抄 → 判未履行职责,作答无效

### 段② 五问逐条取证(堵"举证无门槛")
五问内容**逐字保留原文**(含所有 e.g. 与 "Dormant-by-default ≠ major" 等句子,见 §6 骨架)。改动只在作答的**取证要求**,分两种模式:

- **模式甲·有单行证据**(适用 Q1 代码事实、Q5 严重性常关联具体行):作答必须**贴实际读到的代码原文 + 行号**
- **模式乙·absence/搜索/跨文件**(适用 Q2 设计边界、Q3 可达性、Q4 部署现实):正解常是"没找到",作答可给**搜索范围 + 未命中结论**作为有效取证(如"已搜遍 X 模块注释与 sibling 路径,均无安全写法 → 非边界";或"默认配置项 Y=off,见 config 默认值 → dormant")

**统一硬约束**:每问必须给出**可核验的取证**(甲:贴行;乙:搜索范围+结论)。纯空口(既不贴行也不说搜索范围)= 该问无效。

### 段③ 裁决(在原文既有"指向具体问题"约束上加粒度)
- 裁决 = `confirmed / rejected / downgraded`
- **必须指明靠段②哪一问、哪条取证得出**(条目即可,甲类带行号、乙类带搜索范围)
- 指不了 = 裁决无效
- 段②有问被判无效(纯空口),该方向就不能作为裁决依据,逼它补全

### 兜底:格式不合规判无效 + 防滥用
- 末尾硬规则:**格式不合规(未复述/取证纯空口/裁决无指向)= skeptic 未履行职责,作答无效**
- **防滥用约束(审查驱动)**:主 Agent(propose 方)有动机把不利的 rejected 以格式瑕疵判"无效"后静默保留候选。故规定——**任何被判格式无效的作答,主 Agent 必须重派一次 skeptic,不得以"无效"为由静默保留候选**。重派后若仍不合规,主 Agent 才可在记录中标注"skeptic 未履职,该候选本轮未获有效反驳"并显式说明,不可默认按 confirmed 处理

## 5. 成本与风险

### 成本(token 估算,审查要求补全)
- **输入侧**:模板从约 18 行增至约 30-34 行(涨幅约 70%)。这是 skeptic prompt 的**每次输入固定增量**。以单次输入增量约 250-350 token 估
- **输出侧**:复述 1-2 句 + 五问取证(甲类贴行/乙类搜索范围,约 5-15 行)+ 裁决引用,单次约多 200-400 token
- **"10 个 skeptic"假设来源**:打磨报告第 82 行"一次 hunt 派 10 个 skeptic"为示例量级,非实测;实际随候选数而定
- 合计:一次 hunt 假设 10 次调用 → 输入侧多约 2.5-3.5k + 输出侧多约 2-4k = 约 4.5-7.5k token 增量。**可接受**(为质量付的成本,本来就要砍半)

### 风险与兜底
| 风险 | 兜底 | 残余 |
|---|---|---|
| skeptic 硬编假代码引用糊弄(甲类) | 主 Agent 复核时可**重读该行抽查**验真 | 抽查能挡部分,非全部;**残余风险如实标注**,不宣称已消除 |
| 弱 runtime 不遵循取证格式 | "格式不合规=无效"+ 必须重派规则 | 弱 runtime 可能反复不合规,靠主 Agent 显式标注兜底 |
| 过度较真误杀真 bug | A 不改默认立场;举证门槛≠提高驳回门槛;absence 类有模式乙出路 | 不引入系统性误杀 |
| propose 方滥用"无效"保留候选 | 判无效必须重派,不得静默保留 | 重派后仍不合规才显式标注 |

**at-a-glance 职责的诚实说明(审查驱动)**:at-a-glance 在原文(第 77 行)被定义为"过滤过度谨慎 skeptic 保留下来的边角项"的一眼认同闸。**本次不改变它的既有职责**——它不强制逐行核验引用真假。新增的"引用验真"是主 Agent 在复核时**可选的抽查动作**(怀疑伪造时重读该行),不是 at-a-glance 的强制职责。若要强制逐行验真,需另设机制(超出本轮范围,记为残余)。

## 6. 改动范围与落地

### 改动范围
**只改 `SKILL.md` 第 54-71 行 "Skeptic dispatch prompt" 模板**。其余不动:Loop 图、四要素、两层原因、五问内容、quick-ref 表、Common Mistakes、Red Flags、frontmatter、license、runtime 表。

### 改写后模板(英文,与全文一致;五问逐字照抄原文)

```
> You are a fresh skeptic who has not seen any prior analysis. Your ONLY job is to
> REFUTE this bug candidate. Default to "it's not a real/major bug" unless the code
> forces you otherwise. Independently read the cited lines yourself — do not trust the
> description.
>
> Candidate:
> - Location: <file + lines>
> - Phenomenon: <what the code does>
> - Claimed impact: <consequence>
> - Evidence: <code path>
>
> Do the three steps below in order. Skip or hand-wave any → your answer is invalid.
>
> STEP 1 — Restate (proves you read the candidate): in your own words, 1-2 sentences on
> what the bug is. Do NOT copy the candidate's wording. (This proves you read the
> description; independent code-reading is proven by STEP 2's evidence.)
>
> STEP 2 — Answer each of the five questions with CHECKABLE evidence. Bare assertion
> (no quote AND no search-scope stated) = that question is invalid.
>   - For questions with a single-line answer: quote the line you read + line number.
>   - For absence / search / cross-file answers: state the scope you searched + what you
>     found or did not find.
>   1. **Code facts** — did the proposer misread? (e.g. "overwrite" vs "merge", "never
>      passed" vs "passed with default")
>   2. **Design boundary** — is there an explicit "by design" signal? Search comments,
>      docstrings, sibling paths that DO the safe version. If the team clearly knows how
>      to do X and does it elsewhere, that's evidence of a boundary, not a bug.
>   3. **Independent or derived?** — reachable on its own, or only as a consequence of
>      another bug? A bug needing "zero auth + attacker changes config" is a footnote on
>      the auth bug.
>   4. **Deployment reality** — does default config make this dormant? Feature/dependency
>      on by default? Single-process or multi-worker? Existing locks serialize the path?
>      Test covering it? Dormant-by-default ≠ major.
>   5. **Severity honesty** — even if real: data loss / hard failure / core-feature-broken
>      = major; theoretical / low-probability / cosmetic = downgrade.
>
> STEP 3 — Verdict (must point to a specific STEP 2 question + its evidence; can't =
> invalid): confirmed / rejected / downgraded + which STEP 2 question & evidence decided it.
>
> Non-compliant answer (no restatement / bare-assertion evidence / verdict points to
> nothing) = you did not do your job; the answer is invalid. The main agent MUST re-dispatch
> a skeptic for any invalid answer and may NOT silently keep a candidate on an invalid
> verdict.
```

### Candidate 块
**保留不变**(Location/Phenomenon/Claimed impact/Evidence 四要素),见骨架。

### 关键决策
1. 语言保持英文(与全文一致)
2. 五问文字**逐字照抄原文**(含所有 e.g.、"Dormant-by-default ≠ major."、"even if real:" 等),已在骨架中核验
3. 新增硬约束:复述要求、双模式取证要求、裁决指向要求、末尾"格式不合规=无效 + 必须重派"
4. 三件套格式以**英文骨架(§6)为落地准**,§4 中文描述为说明

### 落地动作
1. Edit `SKILL.md` 第 54-71 行(替换为 §6 骨架)
2. 更新 `find-bugs-打磨报告.md`:把"实测表现"短板里"模板致派发跑偏"标注为"已用举证门槛加固(待真实 subagent 验证)"
3. dry_run 三场景复核,标注 dry_run

## 7. 验证方式

find-bugs 无真实运行数据,**只能 dry_run**(如实标注)。改完后用打磨报告里 3 个测试场景复核:

| 测试场景 | 主导问 | absence/单行 | 改动后是否回归 |
|---|---|---|---|
| ① 并发 TOCTOU 但默认单 worker | Q4 部署现实 | absence 类(查默认配置) | 走模式乙,过滤方向不变 ✓ |
| ② key=None 但 sibling 都这么调 | Q2 设计边界 | absence 类(搜 sibling) | 走模式乙 ✓ |
| ③ 无认证+改配置致 RCE | Q3 可达性 | 跨文件/absence | 走模式乙 ✓ |

五问文字逐字不变,过滤方向由五问本身保证;新增的是"双模式取证门槛",不影响五问判定方向。可信度仍限于 dry_run,真实 subagent 实跑留待下一轮(用户提供代码库后)。

## 8. 出师状态

- 改动面:单文件单段(SKILL.md 第 54-71 行)+ 打磨报告一行标注
- 不碰方法论核心(Loop/五问内容/两层/redflags)
- 不重构 at-a-glance 既有职责
- 不新增文件/目录;不发布、不 merge、不打 tag
- 残余风险(如实):skeptic 甲类伪造代码引用只能靠主 Agent 抽查验真,非强制逐行核验
