# Common Failure Modes

> Extracted from SKILL.md '## 常见失败模式' section for reference (loaded on demand).


- 规划文件说已完成，但实现文件缺失。
- `progress.md` 声称测试通过，但没有命令输出或测试文件支持。
- 实现只覆盖 happy path。
- UI/API 集成仍是 stub、mock 或硬编码。
- 仍存在 TODO、占位、假数据或临时值。
- 新代码绕开既有架构模式。
- 构建/测试脚本被不必要地改动。
- 测试存在，但只验证 mock 或表面渲染。
- 任务目标在实现过程中漂移。
- 审计者开始修复，而不是审计。

