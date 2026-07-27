# run-plan

> 一个 skill 跑完整个 plan 执行流程：加载计划 → 执行任务 → 审查 → 分支收尾 → 可选代码审查

`run-plan` 是一个 Claude Code / Codex skill，专门用于**执行已有的实现计划（markdown 文件）**。你写好 plan，调用 `/run-plan`，它接管从执行到收尾的完整流程。

## 为什么需要这个 skill

执行一个实现计划，通常要跨多个 skill：执行、任务审查、修复循环、最终审查、分支收尾、代码审查……手动串联既繁琐又容易漏环节。

`run-plan` 把这些流程**合成一个 skill**——一次调用，全流程自动走完。你只需选执行模式，剩下交给它。

## 核心亮点

- **🧩 一个 skill 代替五个**：整合 `subagent-driven-development` + `executing-plans` + `finishing-a-development-branch` + `requesting-code-review` + `using-git-worktrees` 的逻辑，不再跨 skill 串联
- **🔀 两种执行模式自选**：子代理模式（复杂 plan，质量优先）或内联模式（简单 plan，速度优先）
- **🛡️ 模型自判 worktree**：大且危险的工作自动建隔离工作区，小改动直接干，不用你操心
- **🔐 仅主动触发**：模型不会自动调用，只在你 `/run-plan` 时触发，**不占用对话开始时的上下文**
- **✅ 完整工作流**：加载 → 执行 → 任务审查 → 最终整体审查 → 分支收尾（merge/PR/keep/discard）→ 可选代码审查

## 两种模式怎么选

| 模式 | 适用场景 | 工作方式 | 特点 |
|---|---|---|---|
| **子代理模式** | 复杂、多任务、风险高的 plan | 每个任务 dispatch 一个独立 subagent 实现，task reviewer 审查，fix loop 修复，最终整体审查 | context 隔离，审查严格，质量高但慢 |
| **内联模式** | 简单、小改动、快速验证的 plan | 单 session 内逐步执行 plan 的每个 step | 快，但无 context 隔离 |

## 完整工作流

```
Step 0  问你选子代理 / 内联模式
Step 1  加载 plan + 模型判断要不要建 worktree（大且危险才建）
Step 2  执行任务
        ├─ 子代理模式：逐任务 dispatch subagent + task review + fix loop
        └─ 内联模式：单 session 逐步执行
Step 3  最终整体审查（子代理模式）
Step 4  分支收尾：验证测试 → 4 选项（merge / PR / keep / discard）→ 执行 → 清理
Step 5  问你要不要代码审查（你同意才走）
```

## 安装

### Claude Code

```bash
cp -r run-plan ~/.claude/skills/
```

### Codex

```bash
cp -r run-plan ~/.codex/skills/
```

Codex 的 `agents/openai.yaml` 已配置 `policy.allow_implicit_invocation: false`（仅主动触发）。

## 使用

在 Claude Code 或 Codex 中输入：

```
/run-plan <plan-file-path>
```

skill 会先问你选子代理模式还是内联模式，然后执行计划。

### 示例

```
/run-plan docs/plans/2026-07-27-add-auth.md
```

skill 启动后：

1. 读取这个 plan，批判性审查，有疑问先问你
2. 问你选子代理还是内联模式
3. 按你选的模式执行所有任务
4. 执行完验证测试，问你 merge / PR / keep / discard
5. 问你要不要走代码审查

## 文件结构

```
run-plan/
├── SKILL.md                  # 主文件（合成 5 个 skill 的逻辑）
├── implementer-prompt.md      # 子代理模式：implementer subagent 的 prompt 模板
├── task-reviewer-prompt.md    # 子代理模式：任务审查 subagent 的 prompt 模板
├── re-review-prompt.md        # 子代理模式：修复后再审查的 prompt 模板
├── code-reviewer.md           # 最终代码审查 subagent 的 prompt 模板
└── scripts/
    ├── sdd-workspace          # 解析 plan 的工作区目录（存 ledger/brief/report）
    ├── task-brief             # 从 plan 提取单个任务的完整文本
    └── review-package         # 生成 review 用的 diff 包
```

## 致谢

本 skill 整合自 [superpowers](https://github.com/obra/superpowers) 体系的多个 skill：

- [`subagent-driven-development`](https://github.com/obra/superpowers) — 子代理执行流程
- [`executing-plans`](https://github.com/obra/superpowers) — 内联执行流程
- [`finishing-a-development-branch`](https://github.com/obra/superpowers) — 分支收尾
- [`requesting-code-review`](https://github.com/obra/superpowers) — 代码审查
- [`using-git-worktrees`](https://github.com/obra/superpowers) — worktree 隔离

## License

MIT
