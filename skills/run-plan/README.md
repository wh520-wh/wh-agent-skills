# run-plan

> 把 plan 丢给它就能去干别的：kickoff 一次问清，之后全流程无人值守——加载计划 → 执行任务 → 审查 → 修复 → 分支收尾

`run-plan` 是一个 Claude Code / Codex skill，专门用于**执行已有的实现计划（markdown 文件）**。你写好 plan，调用 `/run-plan`，它接管从执行到收尾的完整流程。**执行期间只在真正不可逆的岔路口才回来问你**，其余判断自己拍板、记进决策日志。

## 为什么需要这个 skill

执行一个实现计划，通常要跨多个 skill：执行、任务审查、修复循环、最终审查、分支收尾、代码审查……手动串联既繁琐又容易漏环节。

`run-plan` 把这些流程**合成一个 skill**——一次调用，全流程自动走完。kickoff 时你只回答三个问题（执行模式、收尾动作、要不要代码审查），剩下交给它。

## 核心亮点

- **🌙 kickoff 之后不打断你**：执行、复审、修复循环里的所有判断（比如「先堵上还是根治」）都由模型自己拍板，不会每次都回来问你。这个 skill 的初衷就是把计划文件交出去、跑几个小时不用盯
- **📝 决策日志代替提问**：每条自主判断都写进 `decisions.md`（选了什么、放弃了什么、为什么、怎么回滚），跑完你翻一遍就知道它替你决定了什么
- **🛑 只有三类硬刹车会停下**：会根本性改变项目的操作、无法回滚且后果不可计量的操作、计划整体失效。其余一律自主
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
Step 0  Kickoff（唯一提问点）：一次问清 执行模式 + 收尾动作 + 是否代码审查
Step 1  加载 plan + 模型判断要不要建 worktree（大且危险才建）
Step 2  执行任务 ← 从这里开始不再提问
        ├─ 子代理模式：逐任务 dispatch subagent + task review + fix loop
        └─ 内联模式：单 session 逐步执行
Step 3  最终整体审查（子代理模式）
Step 4  分支收尾：验证测试 → 执行 kickoff 预设的动作 → 清理
Step 5  按 kickoff 的预设置决定是否跑代码审查

硬刹车：只有这三种会停下来问你
  ├─ 会根本性改变项目的操作：换架构 / 换栈 / 破坏公共接口 / 撕掉计划外的大量既有工作
  ├─ 无法回滚且后果不可计量：删改数据、force push 共享分支、发布部署、对外发消息、花钱
  └─ 计划整体失效：过期、与现有代码不符、达不到目标（单个步骤写错不算，那是记进日志的偏差）
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

skill 会先一次性问清三件事（执行模式、收尾动作、要不要代码审查），然后就一路跑到底。

### 示例

```
/run-plan docs/plans/2026-07-27-add-auth.md
```

skill 启动后：

1. 读取这个 plan 做批判性审查（只有计划整体失效才会来问你；单个步骤写错它自己改，并记进日志）
2. 一次问清：子代理还是内联、收尾动作选哪个、要不要代码审查
3. 按你选的模式执行所有任务，中途的判断自己拍板并写进 `decisions.md`
4. 验证测试后直接执行你预设的收尾动作（merge / PR / keep / discard）
5. 按预设置决定是否走代码审查

## 文件结构

```
run-plan/
├── SKILL.md                  # 主文件（合成 5 个 skill 的逻辑 + 零打断执行契约）
├── implementer-prompt.md      # 子代理模式：implementer subagent 的 prompt 模板
├── task-reviewer-prompt.md    # 子代理模式：任务审查 subagent 的 prompt 模板
├── re-review-prompt.md        # 子代理模式：修复后再审查的 prompt 模板
├── code-reviewer.md           # 最终代码审查 subagent 的 prompt 模板
├── agents/
│   └── openai.yaml            # Codex 清单（policy.allow_implicit_invocation: false）
└── scripts/
    ├── sdd-workspace          # 解析 plan 的工作区目录（存 ledger / brief / report / decisions）
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

在上述整合之外，本仓库自己加了一条**零打断执行契约**（Hard Brakes / 决策日志 / 计划与评审冲突的裁决规则 / 最小改动优先的修复取向），这是上游没有的部分——目的就是让这个 skill 能真正无人值守地跑完一个计划，而不是每遇到一个岔路就停下来问你。

## License

MIT
