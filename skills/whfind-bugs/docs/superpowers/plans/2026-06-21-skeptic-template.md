# Skeptic 派发模板优化 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 `find-bugs` 技能的 skeptic 派发模板从"软性举证"升级为"三段式硬约束 + 双模式取证 + 防滥用",堵住 skeptic 走过场的两个真漏洞。

**Architecture:** 只替换 `SKILL.md` 第 56-71 行那段 skeptic dispatch prompt 为三段式模板(STEP 1 复述 / STEP 2 五问双模式取证 / STEP 3 裁决指向 + 防滥用兜底)。五问文字逐字保留原文单行结构,改动全在外围指令。另在打磨报告改一行标注。

**Tech Stack:** Markdown 技能文档;无代码、无测试框架。验证用 spec §7 的 dry_run 三场景复核 + 逐字对照原文(本项目非 git 仓库,commit 步骤跳过并如实标注)。

**Spec:** `docs/superpowers/specs/2026-06-21-skeptic-template-design.md`

---

## 文件结构

| 文件 | 操作 | 职责 |
|---|---|---|
| `SKILL.md` 第 56-71 行 | Modify | skeptic 派发 prompt 模板本体——本次唯一核心改动 |
| `find-bugs-打磨报告.md` | Modify(一行) | 把"实测表现"短板的"模板致派发跑偏"标注更新为"已用举证门槛加固(待真实 subagent 验证)" |

不改:frontmatter、license、runtime 表、Loop 图、四要素、两层原因、quick-ref 表、Common Mistakes、Red Flags、五问内容本身。

---

### Task 1: 替换 SKILL.md 的 skeptic 派发模板为三段式

**Files:**
- Modify: `SKILL.md:56-71`(替换整段 prompt 正文;第 54-55 行的标题与小节名不动)

- [ ] **Step 1: 用 Edit 替换第 56-71 行**

`old_string`(逐字,从第 56 行 `> You are a fresh skeptic` 到第 71 行 `...killed or confirmed it.`):

```
> You are a fresh skeptic who has not seen any prior analysis. Your ONLY job is to REFUTE this bug candidate. Default to "it's not a real/major bug" unless the code forces you otherwise. Independently read the cited lines yourself — do not trust the description.
>
> Candidate:
> - Location: <file + lines>
> - Phenomenon: <what the code does>
> - Claimed impact: <consequence>
> - Evidence: <code path>
>
> Answer each, with the line you read as proof:
> 1. **Code facts** — did the proposer misread? (e.g. "overwrite" vs "merge", "never passed" vs "passed with default")
> 2. **Design boundary** — is there an explicit "by design" signal? Search comments, docstrings, sibling paths that DO the safe version. If the team clearly knows how to do X and does it elsewhere, that's evidence of a boundary, not a bug.
> 3. **Independent or derived?** — reachable on its own, or only as a consequence of another bug? A bug needing "zero auth + attacker changes config" is a footnote on the auth bug.
> 4. **Deployment reality** — does default config make this dormant? Feature/dependency on by default? Single-process or multi-worker? Existing locks serialize the path? Test covering it? Dormant-by-default ≠ major.
> 5. **Severity honesty** — even if real: data loss / hard failure / core-feature-broken = major; theoretical / low-probability / cosmetic = downgrade.
>
> Return: **confirmed / rejected / downgraded** + one-line reason citing which question killed or confirmed it.
```

`new_string`(三段式;**五问五条保持原文逐字单行,只改外围指令**):

```
> You are a fresh skeptic who has not seen any prior analysis. Your ONLY job is to REFUTE this bug candidate. Default to "it's not a real/major bug" unless the code forces you otherwise. Independently read the cited lines yourself — do not trust the description.
>
> Candidate:
> - Location: <file + lines>
> - Phenomenon: <what the code does>
> - Claimed impact: <consequence>
> - Evidence: <code path>
>
> Do the three steps below in order. Skip or hand-wave any → your answer is invalid.
>
> STEP 1 — Restate (proves you read the candidate): in your own words, 1-2 sentences on what the bug is. Do NOT copy the candidate's wording. (This proves you read the description; independent code-reading is proven by STEP 2's evidence.)
>
> STEP 2 — Answer each of the five questions with CHECKABLE evidence. Bare assertion (no quote AND no search-scope stated) = that question is invalid.
>   - For questions with a single-line answer: quote the line you read + line number.
>   - For absence / search / cross-file answers: state the scope you searched + what you found or did not find.
>   1. **Code facts** — did the proposer misread? (e.g. "overwrite" vs "merge", "never passed" vs "passed with default")
>   2. **Design boundary** — is there an explicit "by design" signal? Search comments, docstrings, sibling paths that DO the safe version. If the team clearly knows how to do X and does it elsewhere, that's evidence of a boundary, not a bug.
>   3. **Independent or derived?** — reachable on its own, or only as a consequence of another bug? A bug needing "zero auth + attacker changes config" is a footnote on the auth bug.
>   4. **Deployment reality** — does default config make this dormant? Feature/dependency on by default? Single-process or multi-worker? Existing locks serialize the path? Test covering it? Dormant-by-default ≠ major.
>   5. **Severity honesty** — even if real: data loss / hard failure / core-feature-broken = major; theoretical / low-probability / cosmetic = downgrade.
>
> STEP 3 — Verdict (must point to a specific STEP 2 question + its evidence; can't = invalid): confirmed / rejected / downgraded + which STEP 2 question & evidence decided it.
>
> Non-compliant answer (no restatement / bare-assertion evidence / verdict points to nothing) = you did not do your job; the answer is invalid. The main agent MUST re-dispatch a skeptic for any invalid answer and may NOT silently keep a candidate on an invalid verdict.
```

- [ ] **Step 2: 逐字核对五问未变**

人工核对 `new_string` 里五问(1-5)与 `old_string` 里五问**逐字一致**(含所有 e.g.、"Dormant-by-default ≠ major."、"even if real:"、"is a footnote on the auth bug."、"evidence of a boundary, not a bug.")。五问原为单行,新模板里也为单行(仅缩进对齐),未折行改字。

Expected: 五问五个句子零改动。

- [ ] **Step 3: 验证 Edit 成功**

读 `SKILL.md` 第 54-75 行,确认:
- 第 54-55 行标题 `### Skeptic dispatch prompt (copy verbatim)` 与空行仍在
- 新模板三段(STEP 1/2/3)+ 末尾防滥用句已就位
- 五问文字与原文一致

Expected: 文件结构完整,无截断、无重复。

- [ ] **Step 4: dry_run 三场景复核(标注 dry_run)**

按 spec §7 表逐场景确认过滤方向不变:

| 场景 | 主导问 | 模式 | 预期 |
|---|---|---|---|
| ① 并发 TOCTOU 但默认单 worker | Q4 部署现实 | 乙(absence:查默认配置) | 走模式乙,过滤方向不变 ✓ |
| ② key=None 但 sibling 都这么调 | Q2 设计边界 | 乙(absence:搜 sibling) | 走模式乙 ✓ |
| ③ 无认证+改配置致 RCE | Q3 可达性 | 乙(跨文件/absence) | 走模式乙 ✓ |

逐条口述:五问文字未变 → 判定方向由五问本身保证 → 新增的"双模式取证门槛"不影响判定方向,只影响"作答是否被采纳为有效"。

Expected: 三个场景过滤结论与打磨报告原表一致(① downgrade / ② reject / ③ ②降为①footnote)。

- [ ] **Step 5: Commit(跳过,如实标注)**

本项目非 git 仓库,无 commit。如实记录:改动已直接写入 `SKILL.md`,未提交版本控制。

---

### Task 2: 更新打磨报告的实测表现标注

**Files:**
- Modify: `find-bugs-打磨报告.md`(实测表现行)

- [ ] **Step 1: 定位"实测表现"行**

读 `find-bugs-打磨报告.md`,找到九维评分表里"实测表现"那一行(第 82 行附近),其"最大短板"列当前为:

```
未真实subagent实跑,缺模板致派发可能跑偏
```

- [ ] **Step 2: 用 Edit 更新标注**

`old_string`:
```
| 实测表现 | 23 | 16 | dry_run三场景过滤指令齐全自洽(dry_run标注) | 未真实subagent实跑,缺模板致派发可能跑偏 | P1 |
```

`new_string`:
```
| 实测表现 | 23 | 16 | dry_run三场景过滤指令齐全自洽(dry_run标注);模板已用举证门槛加固(三段式+双模式取证+防滥用) | 未真实subagent实跑,模板加固待真实验证 | P1 |
```

- [ ] **Step 3: 验证标注更新**

读该行,确认更新生效、表格其余行未被波及。

Expected: 仅此一行改动。

- [ ] **Step 4: Commit(跳过,如实标注)**

非 git 仓库,无 commit。如实记录。

---

## Self-Review

**1. Spec coverage:**
- spec §4 三段式(复述/双模式取证/裁决指向)→ Task 1 Step 1 new_string 全覆盖 ✓
- spec §4 兜底"格式不合规=无效 + 必须重派"防滥用 → Task 1 new_string 末尾句 ✓
- spec §6 五问逐字照抄 + Candidate 块保留 → Task 1 new_string(Candidate 块原样保留、五问逐字)+ Step 2 逐字核对 ✓
- spec §6 at-a-glance 不重构 → 计划文件结构表与 Task 范围均声明不动 ✓
- spec 落地动作2(打磨报告标注)→ Task 2 ✓
- spec 落地动作3(dry_run 三场景)→ Task 1 Step 4 ✓

**2. Placeholder scan:** 无 TBD/TODO;new_string 为成品全文;old_string 为精确逐字。✓

**3. 一致性:**
- 五问文字在 old/new 两处、spec §6 骨架、Task 1 Step 1 三处一致(均逐字原文)✓
- "必须重派"约束在 spec §4/§5 与 Task 1 new_string 末尾一致 ✓
- 子弹提示1(防滥用次级条款落地点):核心防滥用"必重派、不得静默保留"已落地进 54-71 行 prompt;次级条款"重派后仍不合规怎么标注"属主 Agent 行为,本计划范围仅改 prompt 与报告一行,次级条款保持为 spec 级指导(spec §4 已述),不额外落地——已与子弹的"非阻断"判定一致 ✓
- 子弹提示2(五问折行):Task 1 new_string 明确保留五问单行结构,Step 2 设逐字核对 ✓

无遗漏。

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-06-21-skeptic-template.md`.
