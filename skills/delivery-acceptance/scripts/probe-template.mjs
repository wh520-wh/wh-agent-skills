// 边界探针起手模板（通用版）
//
// 用法（两种）：
//   1. 内联（推荐，临时性）：
//      node --input-type=module -e '<把下面 import + 断言粘进去>'
//   2. 落文件（要复用/归档时）：cp 此模板到项目临时目录，改 import 与用例后跑。
//
// 探针的目的：把"疑似 bug"变成"确认 bug"或"排除"。每个疑点一个探针，给 yes/no。
// 跑完即可删，不要污染项目；若要归档证据，把输出粘进验收报告。

import assert from "node:assert/strict";
// 按实际项目改 import 路径：
// import { targetFunction } from "./src/core/target.mjs";

// 探针套路（通用，按项目实际改输入与断言）：

// === 探针 1：边界输入（计划测试没覆盖的中间态）===
// 例：验证某解析函数对"只给部分字段"是否误判
// const r = targetFunction({ only: "partial" });
// console.log("部分输入 结果:", r.someFlag, "(预期 false)");
// assert.equal(r.someFlag, false, "部分输入不应判为有效");

// === 探针 2：状态序列（倒退/乱序后，基准是否被污染）===
// 例：构造倒退序列，看后续判断是否相对正确基准
// const seq = [make(3), make(1), make(2)];
// console.log("乱序序列:", JSON.stringify(check(seq).violations));

// === 探针 3：畸形透传（旧数据/外部污染是否一路透传到下游）===
// 构造畸形字段，喂下游，看不崩 + 看是否被静默降级

// === 探针 4：空值/非法输入（null / undefined / 空串 / 超大数字）===
// const r = targetFunction(null);
// console.log("null 输入:", r);  // 期望不崩 + 合理降级

// === 探针 5：重复输入（同 key 多次是否重复累加/重复比较）===

// === 探针 6：依赖方向（grep 核查无循环依赖，在 shell 里跑）===
//   grep -n "import" src/core/A.mjs  →  A 依赖谁
//   grep -c "A" src/core/B.mjs       →  B 是否反向依赖 A

console.log("探针模板：取消上方注释，按实际项目改 import 与用例后跑。");
