# ⏰ /later — Claude Code 的闹钟

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)
![One-shot](https://img.shields.io/badge/trigger-one--shot-orange)
![No loop](https://img.shields.io/badge/no--loop-no--wait-green)

> 告诉 Claude「N 小时后帮我做某事」——到点自动跑一次，跑完销毁。
>
> A one-shot alarm for Claude Code: schedule a task N hours ahead, it runs once at the scheduled time, then self-destructs.

---

## 一眼看完

```text
你      /later 4小时后 审查 docs/plans/auth.md 的实施完成度

Claude   ⏰ 闹钟已定
         📅 今天 23:47（4 小时后）跑一次
         🎯 审查 docs/plans/auth.md 的实施完成度
         🔁 不循环   ⚡ 不立刻跑   🗑️ 跑完自动销毁
         ⚠️ 开着 Claude Code 才跑，关了就丢

…4 小时后，Claude 自动醒来，开始审查…
```

一行命令，把「稍后再做」这件事交给 Claude 的闹钟。

---

## 这能干嘛

让你离开电脑后，Claude 在到点时替你把活干了。

- 🌙 **睡前定一个**：「6 小时后检查昨晚的构建是不是过了，红测列给我」——睡醒直接看结果
- 🚀 **跑长任务时**：「30 分钟后看看 dist 里的 exe 是不是还是旧的」
- 📅 **过几天再查**：「2 天后看看那个 PR 合了没」
- 🤖 **统一入口**：所有「过段时间再让 Claude 做某事」的需求，一行说完，不用去凑 `/loop`

**一句话：你先忙别的，到点 Claude 替你干。**

---

## 跟 `/loop` 有什么不一样

|                | `/loop`        | `/later`           |
| -------------- | -------------- | ------------------ |
| 立刻跑         | ✅              | ❌                  |
| 循环           | ✅ 每 N 分钟    | ❌ 一次性           |
| 触发时间       | 最近的整点      | 真的「N 小时后」    |
| 跑完           | 继续           | 自动销毁            |

要「每隔 30 分钟跑一次」用 `/loop`；要「4 小时后跑一次就完事」用 `/later`。

---

## 快速安装

```bash
git clone https://github.com/wh520-wh/later-skill ~/.claude/skills/later
```

重启 Claude Code，输入 `/later` 即可。

> 装在用户级 `~/.claude/skills/later/`，对所有项目生效。

---

## 怎么用

```
/later <相对时间> <任务指令>
```

**时间写法很宽容**，下面都认：

- `4小时后` / `4小时以后` / `4h后` / `四小时后`
- `30分钟后` / `30分后` / `30m后`
- `2天后` / `2d后`
- 说秒？向上取整到 1 分钟（cron 最小粒度），并告诉你取整了

**示例**：

```
/later 4小时后 审查 docs/plans/xxx.md 的实施完成度，对照 reviews/xxx-review.md
/later 30分钟后 跑 npm test，把失败的红测列给我
/later 2天后 检查 dist-desktop 里的 exe 是不是还是旧的
```

**中途管理**：

- 问「定了哪些」→ 列出所有闹钟
- 说「取消那个」→ 删掉指定闹钟

---

## 特性 & 限制

✅ **相对时间**：4 小时后、30 分钟后、2 天后，中文数字也认
✅ **一次性**：跑完自动销毁，不留垃圾
✅ **可查可取消**：随时问「定了哪些」、随时取消
✅ **自包含检查**：任务太空泛（只有「审查一下」没具体对象）会提醒你补全，不硬定

⚠️ **开着才跑**：基于 Claude Code 的 session 机制，关了 Claude Code 闹钟就丢（不 durable）。想让 Claude 半夜替你干活，得让它开着。
❌ **不支持绝对时间**：「明天 9 点」「今晚」不行，只认「从现在起 N 小时后」
❌ **不循环**：要循环用 `/loop`

---

## 它是怎么工作的

基于 Claude Code CLI 自带的 cron 机制（一次性、session-only）。到点会触发一个**全新的对话轮**，执行你给的指令——所以指令必须自带一切（文件路径、对照依据、要做什么），现在的上下文到点早不在了。

不依赖外部服务，不常驻进程，轻量到整个 skill 就一个文件。

---

## License

[MIT](./LICENSE)
