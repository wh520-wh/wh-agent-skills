# agents/

跨 runtime 适配文件。Claude Code 主适配在仓库根 [`SKILL.md`](../SKILL.md) 的 frontmatter。
本目录为其他 Agent 框架提供等效的元数据声明。

## 当前适配状态

| Runtime | 文件 | 状态 | 注 |
|---|---|---|---|
| Claude Code | `../SKILL.md` (frontmatter) | ✅ Primary | 主线适配,所有功能可用 |
| OpenAI / Codex | `openai.yaml` | 🟡 Basic | v0.1.x 提供基础 metadata + policy 声明;v0.2.x 补 tool_use/triggers |
| opencode | — | ⚪ Untested | PR welcome |
| Cursor | — | ⚪ Untested | PR welcome |
| Hermes | — | ⚪ Untested | PR welcome |
| Gemini CLI | — | ⚪ Untested | PR welcome |

## 设计原则

每个适配文件必须保证三件事跨 runtime 一致:

1. **行为契约**——`default_readonly: true` 是硬边界,所有 runtime 都不能绕过。
2. **输出结构**——13 节中文审计报告是 skill 的 deliverable,所有 runtime 都要遵守。
3. **证据规则**——`未验证 / 已验证 / 虚假完成` 等 6 种标签全 runtime 通用,见 [`../references/evidence-grading.md`](../references/evidence-grading.md)。

## 添加新 runtime

如果你想让本 skill 在其他 Agent 框架可用:

1. 拷贝 `openai.yaml` 作为起点
2. 按目标 runtime 的 schema 调整 `interface` / `policy` / `runtime_compatibility` 字段
3. 跑 [`../test-prompts.json`](../test-prompts.json) 里的 3 个测试 prompt,人工核对输出符合 13 节结构
4. 提交 PR,在本表加一行,状态填 `🟢 Tested`

## 为什么 v0.1.x 不强写所有 runtime 适配文件

诚实路线:不熟悉的 runtime schema 强行写出来反而误导用户。等收到对应 runtime 用户的真实反馈再补,避免假阳性"已适配"。
