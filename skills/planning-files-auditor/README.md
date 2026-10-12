# Planning Files Auditor

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](./CHANGELOG.md)
[![Skills Standard](https://img.shields.io/badge/Agent%20Skills-compatible-blueviolet)](http://agentskills.io)
[![Install via npx skills](https://img.shields.io/badge/install-npx%20skills-blueviolet)](https://skills.sh)
[![planning-with-files-zh](https://img.shields.io/badge/audits-planning--with--files--zh%20v3.0.x--v3.1.x-green)](https://github.com/OthmanAdi/planning-with-files)

> **AI 说完成了，我看证据。**
>
> `planning-with-files-zh` 的官方质检岗——揪出 AI 自己声称 “已完成” 但代码里查不到证据的虚假完成。

## 看一眼输出长什么样

跑完后,本 skill 给你一份 13 节标准化报告。第 1 节"总体结论"长这样:

> ## 1. 总体结论
>
> - 结论:**失败**
> - 真实完成度估计:55%
> - 代码质量评分:6/10
> - planning-with-files-zh 使用评分:7/10
> - 审计置信度:中
> - 交付决定:**不可交付**——存在 P0 安全风险
> - 主要结论:3 个阶段虚假完成,1 个阶段部分实现,集成测试完全未做;rate-limit 中间件未接入构成 P0 风险。

完整 13 节示例输出 → [`assets/audit-output-example.md`](./assets/audit-output-example.md)

## 这是什么

当一个 AI（或人）跑完一个 planning-with-files-zh 任务后，它会在 `progress.md` 里写"已完成"、"测试通过"、"已部署"等声明。本 skill 把这些声明当作**待核验的声明**，通过读取真实项目证据（源码、`git status`、`git diff`、测试输出、构建日志等）来验证它们是否真的完成。

它特别擅长揪出这些"虚假完成"模式：

- 规划文件说"已实现 X"，但代码里没有 X
- `progress.md` 写"测试通过"，但没有任何命令输出或测试文件
- 实现只覆盖了 happy path，边界情况是 stub/mock
- 任务目标在执行过程中悄悄漂移了
- AI 自我审计时，自己的记忆被当成证据

## 适用场景

- AI 跑完多步任务后，**你**想知道"它是不是真的做完了"——但又不想自己重新核验
- 前一会话做了一件事，这次会话需要**继承**前一会话的产出——担心是虚假完成
- **多 AI 协作**（一个写、一个审）场景下的"审计"角色
- **CI/CD 集成**：在 merge 之前自动跑一遍审计，防止 AI 写"已完成"骗过 review

## 不适用场景

- 没有 planning-with-files-zh 产出的任务（要先有 `task_plan.md` / `findings.md` / `progress.md`）
- 实时监控 AI 执行过程（这是另外的 skill）
- 代码 review(这是另一类 skill 的活儿;本 skill 只审“声称完成是否属实”,不做代码风格/正确性 review)

## 安装

### 方式一：`npx skills add`（推荐）

```bash
npx skills add https://github.com/wh520-wh/planning-files-auditor --skill planning-files-auditor --agent claude-code -g -y
```

### 方式二：手动安装

将 `SKILL.md`、`agents/openai.yaml` 复制到你的 `~/.claude（或.codex）/skills/planning-files-auditor/` 目录即可。

## 使用方法

安装后，在 Claude Code 中：

> 审计我当前项目的 planning-with-files-zh 任务

或者直接调用：

> /planning-files-auditor

skill 会自动：

1. 找到当前项目中的 `task_plan.md` / `findings.md` / `progress.md`
2. 读取所有声称完成的内容
3. 收集项目证据（源码、git、测试、日志）
4. 输出 13 节标准化审计报告（见下方"输出格式"）

如果找不到规划文件，skill 会询问你具体路径。

## 输出格式

skill 强制使用以下 13 节结构（见 `SKILL.md` 完整定义）：

1. 总体结论
2. 重建的任务目标
3. 规划文件审查
4. 阶段完成度审查
5. 声明核验
6. 代码质量审查
7. 按严重程度分类的问题
8. 虚假完成和未验证工作
9. 初步修复计划
10. 缺失测试和验证
11. 交付决定
12. 评分卡
13. 给原执行者的修复提示词

每个声明的核验结果只能用：`已验证` / `基本验证` / `部分验证` / `未验证` / `被反驳` / `虚假完成`。

## 核心原则

- **默认只读**：skill 只读文件、做分析、给报告，**不会修改任何文件**
- **证据 > 声明**：自我记忆不算证据；只有源码、命令输出、git diff 才算
- **保守评分**：宁可低估完成度，也不放过虚假完成
- **人机分工**：skill 出报告 + 修复提案 + 修复提示词，**最终修复由原执行者做**

## 隐私与安全

- 本 skill 在你的本地环境运行，**不会上传任何文件到外部服务**
- 审计报告里出现的所有文件路径、用户名、commit 信息都来自你**主动提供给 skill**的内容
- 默认不读 `.env`、不读 `~/.ssh/`、不读任何明显敏感路径——但你仍然应该在审计前先 review 一遍项目里有没有敏感信息
- skill 自身的隐私策略：见本仓库 [LICENSE](./LICENSE) 和源码

## 反馈与贡献

发现问题或有改进建议？欢迎开 [Issue](../../issues) 或 [PR](../../pulls)。

特别欢迎：

- 新的"虚假完成模式"案例（让 skill 的检测更准）
- 不同语言项目的核验规则
- 评分算法的改进

## License

MIT — 详见 [LICENSE](./LICENSE)。

## 关联项目

- **planning-with-files-zh** — 本 skill 的唯一审计对象（专门为它设计）
- [agentskills.io](http://agentskills.io) — Agent Skills 标准规范
