# delivery-acceptance (YANSHOU · 验收)

> 程序员说“做完了、测试全绿”时，用这个 skill 做对抗性验收：按计划对账、审代码、跑真实测试、写边界探针，最后给出可合并判断。

## 什么时候用

- 验收一次已经执行完的 implementation plan。
- 合并前核实“计划完成度 / 代码质量 / Bug 风险”。
- 用户说 `/delivery-acceptance`、`/YANSHOU`、`验收一下 docs/.../plan.md`。

## 输出契约

报告是 report，不是 plan；修完的事写进报告，不补写事后 TDD 计划。

| 场景 | 输出 |
|---|---|
| 无问题 | `docs/superpowers/reports/<plan-slug>-acceptance-report.md` |
| 有问题，已顺手修复 | 只写 acceptance report，记录修复摘要 + 复验证据 |
| 有问题，先不修复 | acceptance report + `docs/superpowers/plans/<plan-slug>-fix-plan.md` |
| 问题太大/高风险 | 停下问用户，按选择修复或写 fix plan |

不要把验收结论放进 `plans/`。

## 开局必须问

拿到计划路径后，必须先问用户：

1. 发现问题后是顺手修复、先不修复写 fix plan，还是逐项确认？
2. 如果允许修复，是否允许 commit？
3. 标准验收还是快速浅验？
4. 是否追加性能、安全、文档完整性、可访问性等维度？

不要 auto-resolve，不要按默认推荐值继续。

## 使用示例

```text
/delivery-acceptance docs/superpowers/plans/2026-06-20-example.md
```

合格执行应当：先问开局决策，跑真实测试，写边界探针，报告落到 `reports/`，只有存在未修复工作时才写 `fix-plan.md`。

## 文件结构

```text
delivery-acceptance/
  SKILL.md
  references/
    acceptance-dimensions.md
    report-template.md
    polish-plan-format.md
    dispatch-fix-subagent.md
  scripts/
    probe-template.mjs
```

## 核心原则

- Evidence before assertions。
- report 放结论，plan 只放未来要执行的工作。
- 标准验收必须跑测试和边界探针。
- 修复策略由用户开局决定。