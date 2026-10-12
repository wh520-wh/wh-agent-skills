<div align="center">

# Prune-cc — 安全卸载 Claude Code 插件 / 技能

> *「删之前先查清它藏在哪几处、是谁装的——别把你自己写的技能连坐删掉。」*

[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-Prune--cc-blueviolet)](SKILL.md)
[![Claude Code](https://img.shields.io/badge/Runtime-Claude%20Code%20only-informational)](https://docs.claude.com/en/docs/claude-code)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**把「删一个插件」从一次 `rm -rf` 的赌博，变成先调查、确认来源、再动手的可回溯流程。**

[它解决什么问题](#它解决什么问题) · [效果示例](#效果示例) · [快速开始](#快速开始) · [触发方式](#触发方式) · [它和同类有什么不同](#它和同类有什么不同) · [安全边界](#安全边界)

</div>

---

## 它解决什么问题

事情是这样的。你装了一堆 Claude Code 插件和技能，某天想删掉其中一个，跟 Agent 说「把那个 xxx 删了」。它 `rm -rf` 掉一个文件夹，告诉你「删好了」。

结果呢——

- **删了一半**：同一个逻辑插件，Claude Code 其实存在**最多四个地方**（cache、marketplace 源、`settings.json` 注册、`settings.local.json` 启用标记）。清一处，其余三处还在，下个项目照样把它加载回来。
- **删错了对象**：`tdd`、`diagnosing-bugs`、`handoff` 这些技能名，**好几个互不相关的来源都在用**。凭名字删，删掉的可能是另一个源的、甚至是你自己写的那个。
- **连坐删**：`~/.agents/skills/` 是**多来源共享**的文件夹——你自己的 `luban`、`ppt-master` 和别人的技能挤在一起。谁要是 `rm -rf ~/.agents/skills/` 图省事，你的东西一起没。

普通做法之所以不行，是因为它**先删再说**。Prune-cc 换了个顺序：**先调查（只读，不删）→ 确认来源 → 来源不明就停下来问你 → 确认后按序删 → 删完验证目标没了、你的东西还在。** 删得干净，也删得对。

## 效果示例

对 Agent 说「删掉 obsidian-vault」，它不会立刻动手，而是先跑一遍只读调查，把真实情况摆给你看：

```text
调查结果（未删除任何东西）：
  ~/.agents/skills/ 磁盘上有 10 个技能，manifest 只追踪其中 6 个
  目标 obsidian-vault → .skill-lock.json 记录 source = mattpocock/skills  ✓ 来源明确

  ⚠ 但检测到：你机器上 obsidian-vault 是真实目录，且你日常在用 Obsidian。
    另有 4 个技能（arkts-syntax-assistant / karpathy-guidelines /
    netease-uu-booster / planning-files-auditor）manifest 查无记录
    —— 大概率是你自己装的，本次不会碰。

  请确认：obsidian-vault 你要删，还是保留？
```

> 这段来自本机真实文件系统的调查回放。真正让删除变安全的，是「删之前把上面这些查清楚」——`mattpocock/skills` 这一批共九个技能被删掉，唯独 `obsidian-vault` 因为你在用而保留，正是靠这一步问出来的。

## 快速开始

> **说明**：Prune-cc 是一套让 Claude Code 安全执行删除的**方法论技能**，靠的是本地文件系统命令（`test -L`、`readlink`、JSON 精确编辑），不走 `npx` 安装生态。用你现有的技能安装方式把本仓库放进 `~/.claude/skills/Prune-cc/`（或作为 marketplace 插件安装）即可。

装好后，直接对 Claude Code 说：

```text
帮我把 <插件或技能名> 全局删干净，别删到我自己的东西
```

它会自动进入「先调查后删除」流程。

## 触发方式

Agent 听到这些话会启用本技能（中英文都触发）：

- 「卸载 / 删除 / 清理 / 清除 / 干掉 / 抹掉 xxx 插件」
- 「把 xxx skill 删干净」「全局删除，所有项目都别再加载」
- “uninstall / remove / delete / prune / clean up / wipe / get rid of the xxx plugin”
- 「我之前装的那个东西，帮我弄掉」

## 它会交付什么

| 阶段 | 交付物 |
|---|---|
| 调查（只读） | 一份「目标藏在哪几处 + 来源是谁 + 哪些是你自有」的清单，一个文件都没删 |
| 删除 | 按序清理配置 → 链接 → 真实文件夹 → manifest 记录，每步说明动了什么 |
| 验证 | 确认目标已消失、受保护技能仍在的核对结果 |
| 报告 | 删了什么、**特意保留了什么及原因**、以及重启 Claude Code 才彻底生效的提醒 |

## 它和同类有什么不同

| 维度 | 常见做法 | Prune-cc |
|---|---|---|
| 动作顺序 | 先 `rm -rf` 再说 | 先只读调查、确认来源，再删 |
| 存储位置 | 删一个文件夹 | 覆盖插件的四处 / 技能的三处存储，一处不漏 |
| 同名冲突 | 凭文件夹名删 | 用 `.skill-lock.json` 的 `source` 字段确认来源 |
| 来源不明时 | 猜 | 停下来问你，绝不猜 |
| 你的自有技能 | 可能连坐 | manifest 查无记录 = 默认视为你的，先问再说 |

（讲差异，不评判同类——很多同类工具主打安装或管理，删除本就不是它们的重点。）

## 安全边界

- **Phase 1 全程只读**，不含任何 `rm`；调查没做完不删东西。
- **绝不 `rm -rf ~/.agents/skills/` 整个删**——那是多来源共享目录。
- **绝不凭文件夹名删**——先确认 `source`。
- **来源不明、或 manifest 查无此项，一律停下来问你**，不擅自判断。
- **编辑 `settings.json` / `.skill-lock.json` 只做精确的键删除**，保证 JSON 仍合法，不碰无关配置。
- **Windows 上若文件被占用**（Claude Code 正在运行导致 symlink 锁定），会请你先完全退出再重试，**不擅自 kill 进程**。

## 文件结构

```
Prune-cc/
├── SKILL.md      # 技能正文：两种存储模型 + 调查/删除/验证/报告四阶段流程（Agent 读这个）
└── README.md     # 你正在看的这份：面向人的说明
```

> 路线图（尚未入库）：`scripts/investigate.sh`（把 Phase 1 调查固化成可复现脚本，也是天然的展示产物）、`examples/`（真实删除案例回放）、demo GIF。

## 验证与测试

装好后，用一句会触发误删风险的话验收：

```text
删掉 tdd 这个技能
```

**合格表现**：Agent 不直接删，而是先查 `tdd` 在你机器上有几个来源、分别是谁的，若存在同名或来源不明，先把情况列给你、请你确认——而不是删掉第一个匹配到的文件夹。

## 致谢

方法论来自一次真实踩坑：删除 `mattpocock/skills` 的技能时，`obsidian-vault` 同批安装但用户日常在用，只有「停下来问」才避免了误删。Claude Code 的存储机制参考[官方文档](https://docs.claude.com/en/docs/claude-code)。

## License

[MIT](LICENSE)

---

<div align="center">

*先查清，再动手——删得干净，也删得对。*

</div>
