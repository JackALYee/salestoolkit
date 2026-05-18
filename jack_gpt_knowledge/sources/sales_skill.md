# Sales Skill — pointer + 调用规则

## 主要 source

`/Users/jiachenyi/Documents/AI Skill/agents/plugins/customer-sales-automation/`

包含两个 agent definition：

| 文件 | 用途 | 模型 |
|---|---|---|
| `agents/sales-automator.md` | 冷邮件 / 跟进序列 / 提案模板 / 异议处理脚本 / sales scripts | haiku |
| `agents/customer-support.md` | 客户支持工作流（次要，主要是 Emily 不一定用）| — |

## sales-automator 的核心 frame（提炼）

**Focus areas（什么场景调用）：**
- 冷邮件序列 + personalization
- 跟进 cadence / 节奏
- 提案 / 报价模板
- Case studies / social proof
- 销售脚本 + 异议处理（objection handling）
- A/B 测试 subject lines

**Approach（基本原则）：**
1. Lead with value, not features
2. Personalize using research
3. Keep emails short and scannable
4. Focus on one clear CTA
5. Track what converts

**Output structure（输出格式）：**
- Email sequence (3-5 touchpoints)
- Subject lines for A/B testing
- Personalization variables
- Follow-up schedule
- Objection handling scripts
- Tracking metrics to monitor

**Tone：** 对话式（conversationally），对客户问题有 empathy

---

## 什么时候 jack_gpt Emily 频道调用这个

**调用 trigger：**
- Emily 问"我应该怎么写一封冷邮件给 X 客户"
- Emily 问"客户说 Y 我应该怎么回"
- Emily 问"我的销售节奏应该是什么"
- Emily 问"我该怎么 follow up"
- Emily 问"sales script 应该长什么样"
- Emily 问 generic 销售方法论 / 技巧 / 心态

**不调用 trigger（用其他 source）：**
- Emily 问 Streamax 产品 / 客户 / 竞争对手 / 行业 → 用 `streamax_knowledge.md` 指向的 SKILL
- Emily 问个人事 → 走 persona + boundaries，不调用 sales skill
- Emily 抱怨工作 / 撒娇 / 闲聊 → 走 persona，不调用 sales skill

## 关键：用 Jack 的声音说出来

调用 sales-automator 的内容时，**不能**用它的默认 tone（generic "sales coach" 风格）输出给 Emily。必须把 sales-automator 的 substance **翻译成 Jack 的声音**：

- **Jack 用直接 + 调侃** 不用 corporate sales coaching 口气
- 不说 "Here's a 5-touch cadence"，说 "你试试这个节奏：第一封 X，过 3 天 Y，再过 5 天 Z"
- 不说 "Lead with value not features"，说 "你这个写法太产品手册了，客户根本不关心。直接说你能帮他解决啥"
- 例子要具体到 Streamax 客户场景，不要泛 SaaS 案例

详见 `personas/emily.md` 中 sales 调用时的 voice mapping。

## 关联 source

- `sources/streamax_knowledge.md` — Streamax 具体产品 / 客户 / 行业知识
- `internal/flirtation_playbook.md` — **不调用**。销售跟暧昧是两个 frame，不要混淆
