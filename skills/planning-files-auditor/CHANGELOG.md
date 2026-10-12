# Changelog

本项目的所有重要变更都会记录在此文件。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/),
版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [Unreleased]

## [0.1.0] - 2026-06-17

> 代码定型于 2026-06-09,GitHub release tag 与公开发布于 2026-06-17 完成。

### Added
- 首次开源发布
- 完整的 13 节审计报告结构
- 严格的证据分级(强/中/弱/无)
- 6 种核验结果标签(已验证/基本验证/部分验证/未验证/被反驳/虚假完成)
- 4 种问题标签(虚假完成/目标漂移/未验证/部分实现/占位实现/测试不足)
- 默认只读硬边界
- 隐私保护:审计时只读、不会自动写文件
- `.claude-plugin/marketplace.json` 支持 `npx skills add` 一键安装
- 完整的 `assets/` 示例和 `examples/` 使用说明
- SKILL.md "兼容性"段,声明对 `planning-with-files` v3.0.x – v3.1.x 字段兼容范围

### Fixed
- README "不适用场景"段 `[code-review](...)` 占位符链接(改为描述性说明,消除死链)

[Unreleased]: https://github.com/wh520-wh/planning-files-auditor/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/wh520-wh/planning-files-auditor/releases/tag/v0.1.0
