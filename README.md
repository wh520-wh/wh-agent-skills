# WH Agent Skills

个人 Agent 技能集合，涵盖架构分析、计划执行、缺陷调查、交付验收、GitHub 发布、内容整理与游戏模组开发。

所有技能统一保存在 `skills/` 中，可以按需要选择安装和使用。各技能沿用原有定义、触发条件、工具依赖和使用边界。

## 安装

通过 [Skills CLI](https://github.com/vercel-labs/skills) 查看并选择需要的技能：

```sh
npx skills add wh520-wh/wh-agent-skills --list
npx skills add wh520-wh/wh-agent-skills
```

只安装指定技能：

```sh
npx skills add wh520-wh/wh-agent-skills --skill run-plan
```

也可以克隆本仓库，再将对应的完整技能目录放入所使用 Agent 的技能目录。请保留技能目录中的脚本、参考资料和素材。

## 技能目录

| 技能 | 用途 | 使用条件 |
|---|---|---|
| [first-principles-architecture](skills/first-principles-architecture) | 从目标出发审视架构、计划与重构方向 | 显式调用 |
| [run-plan](skills/run-plan) | 执行已有实施计划，完成任务审查、修复与分支收尾 | 需要已有计划；支持子代理或内联模式 |
| [whfind-bugs](skills/whfind-bugs) | 提出缺陷候选，通过独立反驳筛选确认问题 | 专项缺陷调查 |
| [delivery-acceptance](skills/delivery-acceptance) | 按计划、源码、测试与边界探针验收交付 | 需要实施计划 |
| [planning-files-auditor](skills/planning-files-auditor) | 核验规划文件中的完成声明 | 对应 task_plan.md、findings.md、progress.md |
| [Togithub](skills/Togithub) | 扫描、清理并发布项目到 GitHub | 依赖 GitHub CLI；清理与发布沿用原授权规则 |
| [later](skills/later) | 延迟执行一次任务 | Claude Code 专用定时工具 |
| [Prune-cc](skills/Prune-cc) | 调查并卸载技能、插件与市场安装 | Claude Code 专用 |
| [videounderstand](skills/videounderstand) | 将本地教程视频整理成图文流程或 DOCX/PDF 手册 | 需要相应视频与文档工具 |
| [create-mods](skills/create-mods) | 核验真实 API 并开发 Minecraft 模组 | Minecraft 1.20.1 + Forge 47.x |
| [create-oxygennotincluded-mod](skills/create-oxygennotincluded-mod) | 用缺氧开发经验补齐模组的系统关联、美术与验证 | Oxygen Not Included 模组项目 |

## 使用

根据任务选择对应技能。各技能的完整使用方式见其 `SKILL.md`，配套说明见各目录中的 `README.md`（如有）。

例如：

- 用 first-principles-architecture 审视这个重构方案。
- 用 run-plan 执行已有的实施计划。
- 用 delivery-acceptance 验收这次计划交付。
- 用 videounderstand 将本地教程视频整理成图文手册。

`Togithub`、`Prune-cc` 等名称保留原始大小写。本次整理保留各技能的全部原文件，因此子目录中的部分历史安装地址仍指向原独立仓库；安装时请使用本页的新仓库地址。

## 仓库结构

```text
wh-agent-skills/
├── README.md
├── LICENSE
├── SOURCES.json
└── skills/
    └── <skill-name>/
        ├── SKILL.md
        ├── LICENSE
        └── 原仓库的配套文件
```

## 来源与许可证

各技能由原独立仓库迁入，源仓库、默认分支和迁移时的提交记录见 [SOURCES.json](SOURCES.json)。迁入技能的默认分支 Git 历史保留在本仓库的提交历史中，文件内容按迁移时的源版本完整保留。

本仓库采用 [MIT](LICENSE) 许可证。各技能保留自己的 LICENSE 和来源说明，原有版权与第三方说明继续适用。
