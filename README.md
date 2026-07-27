# run-plan

一个 Claude Code / Codex skill，用于执行已有的实现计划（markdown 文件）。一个 skill 覆盖完整工作流：加载计划 → 执行 → 审查 → 分支收尾 → 可选代码审查。

## 特性

- **两种执行模式**：子代理模式（逐任务 dispatch subagent + review + fix loop）和内联模式（单 session 逐步执行）
- **模型自判 worktree**：大且危险的工作自动创建隔离 worktree，小且安全的不用
- **完整工作流**：加载计划 → 执行任务 → 任务审查 → 最终整体审查 → 分支收尾（merge/PR/keep/discard）→ 可选代码审查
- **仅主动触发**：模型不自动调用，只在你 `/run-plan` 时触发，不占用对话开始时的上下文

## 使用

在 Claude Code 或 Codex 中输入：

```
/run-plan <plan-file-path>
```

skill 会先问你选子代理模式还是内联模式，然后执行计划。

### 两种模式怎么选

| 模式 | 适用场景 | 特点 |
|---|---|---|
| 子代理模式 | 复杂、多任务、风险高的 plan | 每任务隔离 context，review 严格，质量高但慢 |
| 内联模式 | 简单、小改动、快速验证的 plan | 单 session 执行，快但不隔离 |

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

## 文件结构

```
run-plan/
  SKILL.md                 # 主文件（合成 5 个 skill 的逻辑）
  implementer-prompt.md     # 子代理模式 implementer 模板
  task-reviewer-prompt.md   # 任务审查模板
  re-review-prompt.md       # 修复后再审查模板
  code-reviewer.md          # 代码审查模板
  scripts/
    sdd-workspace           # 解析 plan 工作区目录
    task-brief              # 提取单任务文本
    review-package          # 生成 review diff 包
```

## 致谢

本 skill 整合自 [superpowers](https://github.com/obra/superpowers) 体系的多个 skill：

- `subagent-driven-development` - 子代理执行流程
- `executing-plans` - 内联执行流程
- `finishing-a-development-branch` - 分支收尾
- `requesting-code-review` - 代码审查
- `using-git-worktrees` - worktree 隔离

## License

MIT
