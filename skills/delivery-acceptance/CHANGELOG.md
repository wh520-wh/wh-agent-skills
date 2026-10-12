# 更新日志 / Changelog

本文件记录 delivery-acceptance (YANSHOU · 验收) skill 的演进。格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/)，日期为提交日。

## 2026-06-26

### 新增
- **开局决策改为「AI 预判 + 带「（推荐）」标记的问法」。** AI 先做快速预判（读计划基线 + `git diff --stat` + 涉及文件量级），判断这批交付若发现问题更倾向哪种处理方式；问问题时 A/B/C 选项文字一字不改，只在预判倾向的选项后加「（推荐）」标记并附一句理由。标推荐仍须等用户回答，不自动执行。

### 变更
- 原「不要按推荐默认值继续」一句改清楚：标「（推荐）」只是表达倾向，仍必须等用户回答后再执行。

## 2026-06-23

### 新增
- 给 delivery-acceptance 增加 4 个判断标准，并删除重复契约表述。
- `.gitignore` 排除 `.claude/` 目录（AI 协作痕迹）。
- 将「4 个判断标准 + 删重复契约 + 排除 .claude/」合并入主线。

## 2026-06-20

### 新增
- 初始化仓库：LICENSE + `.gitignore`，按公开标准备齐发布证件。
- README 按 house 模板重写，补充可见产物，去除真实痕迹。
- 补充真实闭环案例 B1；README 删诚实声明、分数推到实测。
- 加社交预览图（social-preview）及生成脚本。
- `.gitignore` 排除 `.gstack/` 目录。

### 变更
- 收窄 `.gitignore`，放行 `examples/` 下的示例报告。
- 收尾打磨：精简 README / SKILL 与 references。
- README 首屏加亮点徽章行 + 对比钩子。
