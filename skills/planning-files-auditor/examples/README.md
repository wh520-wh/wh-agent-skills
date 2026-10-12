# Examples

本目录是 planning-files-auditor 的使用示例。

## 文件说明

| 文件 | 用途 |
|---|---|
| [`../assets/sample-task-plan.md`](../assets/sample-task-plan.md) | 一个**故意包含虚假完成**的 `task_plan.md` 示例，模拟 AI 跑完任务后的"声称完成"状态 |
| [`../assets/audit-output-example.md`](../assets/audit-output-example.md) | 用本 skill 审计 `sample-task-plan.md` 的**预期输出**，展示完整的 13 节审计报告结构 |

## 怎么用这两个示例

### 1. 理解本 skill 的能力

如果你 30 秒内想知道"这 skill 到底能干嘛"，按这个顺序看：

1. `sample-task-plan.md`——看一个"假装完成"的规划文件
2. `audit-output-example.md`——看本 skill 怎么把虚假完成揪出来

### 2. 调试你的审计调用

如果你在本 skill 中遇到问题（比如输出不符合预期），可以：

1. 把 `sample-task-plan.md` 当作"已知输入"
2. 跑一次 audit
3. 对比你的输出和 `audit-output-example.md`
4. 差异点就是 skill 没正常工作的部分

### 3. 作为本 skill 自身的"自审"素材

`audit-output-example.md` 也展示了本 skill **自身的输出格式**，可以作为单元测试 fixture（如果将来要加自动化测试的话）。

## 跑一次实战

1. 把 `sample-task-plan.md` 复制到你的项目根目录（作为 `task_plan.md`）
2. 在 Claude Code 中调用本 skill：
   > /planning-files-auditor
3. 对比 skill 的输出和 `audit-output-example.md`
4. 两者应该**结构上完全一致**（13 节），但具体核验结果会因你项目里的真实证据不同而不同
