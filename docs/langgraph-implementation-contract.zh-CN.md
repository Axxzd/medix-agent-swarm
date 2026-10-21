# LangGraph 实施契约 v1.1（已对齐 + 已评审）

## 目的

本文档是将 `medix-agent-swarm` 重写为工业级 LangGraph 系统的实施契约。\
所有编码必须遵循本契约。任何行为变更必须先获得明确批准并先更新契约。

## 范围

- 项目：`medix-agent-swarm`
- 编排：`LangGraph`
- 质量目标：可靠性、安全性、可审计性、可恢复性、可测试性

## 不可协商的架构规则

1. 混合类型模型：\
   - 图运行态状态：`TypedDict + Annotated reducers`\
   - 外部边界（API/工具/契约/结果）：`Pydantic`
2. 节点函数只返回状态 patch。
3. 路由必须显式、确定、且有优先级顺序。
4. 安全策略必须由代码强制（非仅提示词）。
5. 人工审核是一级能力（`interrupt`、队列、决策、超时、恢复/重开）。
6. 所有关键迁移必须产出 trace/log/audit 证据。

## 规范节点名与路径

高风险推理主路径仅使用真实节点名：

`triage -> diagnostic -> research -> synthesize -> safety_review -> final_response`

`diagnostic_research` 在本契约中不是实际节点名。\
如果出现，仅作为上述节点链的文档别名。

## 图边表（规范）

1. `intake -> triage_precheck`
2. 若 `emergency_precheck_hit == true`，`triage_precheck -> final_response`
3. 若 `intent_status != resolved`，`triage_precheck -> clarify_intent`
4. 若 `intent_type == medical_info` 且无 `symptom_entities`，`triage_precheck -> consultation`
5. 其他情况，`triage_precheck -> triage`

6. 若 `risk_level == emergency`，`triage -> final_response`
7. 若 `risk_level in {low, medium}`，`triage -> consultation`
8. 若 `risk_level == high`，`triage -> diagnostic`

9. 若 `next_action == finalize`，`consultation -> final_response`
10. 若 `next_action == escalate_diagnostic`，`consultation -> diagnostic`
11. 若 `next_action == request_clarification`，`consultation -> clarify_intent`

12. `diagnostic -> research`
13. `research -> synthesize`
14. `synthesize -> safety_review`
15. 若安全通过，`safety_review -> final_response`
16. 若严重度策略要求，`safety_review -> human_review`

17. 若 `review_decision == approve_continue`，`human_review -> triage`
18. 若 `review_decision == safe_close`，`human_review -> final_response`

## 意图与澄清契约

1. 非急症专业推理前，必须先完成意图解析。
2. 阈值：
   - `intent_confidence_resolved = 0.80`
   - `intent_confidence_ambiguous = 0.60`
3. `max_clarification_rounds = 3`
4. 下列场景均计入澄清轮次：
   - 意图门控触发澄清
   - consultation 阶段触发澄清
5. 到达最大轮次且仍未解析，路由到 `human_review`。

## 急诊契约与引用例外

1. 一旦判定为急诊，响应不得被运行时检索阻塞。
2. 急诊路径使用预批准静态急诊模板。
3. 急诊路由与措辞在审计中引用内部规则 ID。
4. 面向用户的急诊输出可不附运行时 citation。
5. 可选附带预加载可信安全来源的静态 citation。

## 分诊契约

1. 规则优先进行风险评估。
2. 仅对灰区风险进行 LLM 精细化判断。
3. 命中高风险急诊规则时绕过 LLM，立即升级路由。

## 咨询与升级契约

1. `consultation` 处理非急症 `low/medium`。
2. 中风险默认保守（更倾向升级）。
3. `consultation` 的 `next_action` 仅允许：
   - `finalize`
   - `escalate_diagnostic`
   - `request_clarification`

## 诊断/研究/综合契约

1. `diagnostic`：只做鉴别分析，不给确定性诊断，不给剂量指令。
2. `research`：只做证据检索/汇总，并附来源元数据。
3. `synthesize`：如证据冲突，默认更保守/更高风险指引，并标注冲突说明。

## 安全审查契约

违规严重度策略：

1. `high`：立即 `human_review`
2. `medium`：自动改写一次并复检，仍失败则 `human_review`
3. `low`：告警后放行

高严重度包括：

1. 确定性诊断陈述
2. 具体药物剂量/频次建议
3. 急诊降级措辞
4. 特殊人群（孕妇/儿童/老年）用药建议

## 引用策略

必须引用的类别：

1. 医疗结论
2. 数值阈值
3. 分诊决策

可选引用：

1. 通用建议
2. `safe_close` 终止响应

必需引用缺失时：

1. 降级为“证据不足”表述
2. 至少归类 `medium` 严重度
3. 若改写仍失败，升级人工审核

Citation 模型约束：

1. `published_date` 可选
2. `excerpt <= 300 chars`
3. 必须包含 `source_type`、`title`、`url or document_id`、`retrieved_at`、`evidence_quality`

`claim_citation_map` 策略：

1. 仅内部审计使用
2. 默认不通过公开 API 返回

## 状态 Schema 契约（最低要求）

最小状态字段包括：

- `user_id`, `task_id`, `thread_id`, `trace_id`, `graph_name`, `graph_version`
- `raw_user_input`, `normalized_question`
- `intent_type`, `intent_confidence`, `intent_status`, `missing_required_slots`
- `clarification_rounds`, `clarification_history`
- `symptom_entities`, `emergency_precheck_hit`, `risk_level`
- `next_action`, `graph_status`, `end_reason`
- `diagnostic_result`, `research_evidence`, `synthesized_answer`
- `citations`, `safety_violations`, `audit_events`, `error_metadata`

## Reducer 策略契约

覆盖写（overwrite）字段：

- `risk_level`, `intent_status`, `next_action`, `graph_status`, `end_reason`

追加（append）字段：

- `messages`, `clarification_history`, `audit_events`, `trace_events`, `safety_violations`

去重（dedup）字段：

- `citations`（按 `citation_id` 或稳定 hash）
- `research_evidence`（按 evidence ID/hash）

## 审计与副作用边界

1. 节点不得直接写审计数据库。
2. 节点通过状态 patch 输出 `audit_event`。
3. 运行时钩子/中间件在节点成功/失败边界持久化审计事件。
4. 该规则是单测隔离与可重放确定性的强制要求。

## 人工介入超时契约（HITL）

LangGraph `interrupt` 会暂停并无限等待恢复，除非外部处理。\
因此超时必须由 worker/watchdog 外部强制，而不是依赖 interrupt 本身。

超时流程：

1. 将 review ticket 标记为 `timed_out`
2. 追加审计事件
3. 将任务 `end_reason = safe_close_timeout`
4. 由运行时（worker/watchdog）物化 `final_response`，而不是继续执行中断图
5. 关闭原任务路径

超时后晚到审批：

1. 不可恢复原任务
2. 必须走 `force_reopen`

人工审核 ticket 创建契约：

1. 按 `(task_id, interrupt_point, reason)` 幂等创建
2. `interrupt()` 前禁止非幂等副作用
3. 若 ticket 已存在，复用 ticket_id，避免重复入队

## 任务生命周期契约

状态集合：

- `pending`, `claimed`, `running`, `interrupted`, `completed`, `failed`, `cancelled`

状态迁移表：

1. `pending -> claimed | cancelled`
2. `claimed -> running | failed | pending`
3. `running -> interrupted | completed | failed | cancelled`
4. `interrupted -> running | completed | failed | cancelled`
5. `completed -> terminal`
6. `failed -> terminal`
7. `cancelled -> terminal`

结束原因：

- `emergency`
- `safe_close_timeout`
- `safe_close_human`
- `normal_finalize`
- `cancelled_by_user`
- `failed_runtime`

执行超时：

- 自动执行 `execution_timeout_seconds = 120`
- `interrupted` 等待期不计入执行超时

取消行为：

1. `pending`：立即取消
2. `claimed/running`：设置 `cancellation_requested = true`，worker 在每个 node/tool 调用前检查
3. `interrupted`：取消任务并关闭 review ticket
4. 终态：拒绝取消

## 强制重开（Force Reopen）契约

1. 原超时任务保持不可变终态。
2. `force_reopen` 创建新任务并包含：
   - `parent_task_id`
   - `reopen_reason`
3. 重开任务复用原 `thread_id`。
4. 重开任务在同一 `thread_id` 下使用新 `task_id` 建立新的检查点链。
5. 重开执行从 `triage` 启动。

## API 契约（v1）

公开异步流程：

1. `POST /tasks` -> `202 Accepted`
2. `GET /tasks/{task_id}`
3. `GET /tasks/{task_id}/result`
4. `POST /tasks/{task_id}/cancel`

HITL 必需 API：

1. `POST /review-tickets/{ticket_id}/decision`
2. `POST /tasks/{task_id}/force-reopen`
3. `GET /review-tickets`
4. `GET /review-tickets/{ticket_id}`

v1 不使用 webhook，仅轮询。

## 持久化与恢复契约

1. 数据栈：`SQLAlchemy 2.x + Alembic`
2. Checkpointer 后端：
   - dev 默认 `sqlite`
   - prod 强制 `postgres`
3. 生产环境启动 fail-fast 条件：
   - 缺少 `llm_api_key`
   - 缺少 `db_url`
   - checkpointer 后端不是 `postgres`
4. 崩溃恢复：
   - `claim_lease_seconds = 30`
   - `heartbeat_every_seconds = 10`
   - `max_retries = 2`（`max_total_attempts = 3`）
5. 被重新认领任务从最新 durable checkpoint 恢复。
6. 任务重认领必须产出审计事件。
7. 状态迁移失败：
   - 设置 `error_code = state_migration_failed`
   - 安全失败退出

最小数据库 schema 契约：

1. 必需表：
   - `tasks`
   - `task_events`
   - `review_tickets`
   - `checkpoints`
   - `audit_events`
2. `tasks` 最小列：
   - `task_id`, `parent_task_id`, `thread_id`, `user_id`
   - `graph_name`, `graph_version`, `status`, `end_reason`
   - `payload_encrypted`, `payload_hash`
   - `created_at`, `updated_at`
3. `review_tickets` 最小列：
   - `ticket_id`, `task_id`, `thread_id`, `status`, `priority`
   - `reason`, `reviewer_id`, `expires_at`, `created_at`, `updated_at`

## 幂等契约

1. 幂等键：`(user_id, graph_name, graph_version, payload_hash)`
2. 时间窗：`60s`
3. 仅复用活跃任务状态：
   - `pending|claimed|running|interrupted`
4. 与终态命中时必须新建任务。

## 工具运行时契约

1. 工具接口必须是 async-only。
2. 统一返回包：`ToolResult(status, data, error_code, error_message, meta)`
3. 权限拒绝返回 `status = denied`（不抛异常）。
4. 未知工具：
   - `status = error`
   - `error_code = tool_not_found`
5. 超时：
   - `status = timeout`
   - `error_code = tool_timeout`
6. 超时仅重试一次：
   - base delay `300ms`
   - backoff factor `2.0`
   - max delay `2000ms`
   - jitter `+/-20%`

## PHI/PII 契约

1. Trace 与 metrics 禁止包含原始 PHI/PII。
2. 原始医疗输入在 payload/checkpoint 中必须静态加密。
3. 审计日志仅保留最小必要上下文（可脱敏时必须脱敏）。
4. 审核员访问原文需 RBAC 保护，且仅经 review UI/API。
5. 写结构化日志与审核队列摘要前必须执行脱敏策略。

## 可观测性契约

1. 生产默认日志级别：`INFO`
2. 指标后端风格：Prometheus
3. 禁止高基数标签：
   - `user_id`, `thread_id`, `task_id`
4. 指标仅使用低基数标签（graph/node/status/tool）
5. 高粒度排障使用 trace/log，不进入高基数字段

## 评测与 CI 门禁

阻断阈值：

1. 急诊漏判容忍度 = `0`
2. 高严重度安全违规容忍度 = `0`
3. 若 `intent_status != resolved`，diagnostic/research 工具调用必须为 `0`
4. 急诊路径必须断言：`no retrieval`、`no diagnostic`、`no research`

评测样例族必须包含：

1. 急症症状样例
2. 意图歧义样例
3. 高风险非急症样例
4. 剂量拒答样例
5. 孕妇/儿童/老年样例
6. 引用缺失样例
7. 急诊降级对抗样例
8. 路由回归快照

医疗证据来源策略：

默认允许：

1. 政府/公共卫生机构
2. 公认临床指南组织
3. 同行评审医学文献
4. 系统所有者批准的机构级医学参考

默认禁止：

1. 论坛
2. 营销页面
3. 未验证博客
4. 无医学权威的 SEO 内容

## 配置优先级契约

配置读取顺序：

1. environment variables
2. `.env`
3. 代码默认值

## 实施顺序（更新版）

1. `src/config`
2. `src/contracts`
3. `src/graphs/medical_consultation/state.py`
4. `src/graphs/medical_consultation/routing.py`
5. 路由回归测试
6. 任务生命周期状态机测试
7. 核心节点（`intake/triage/consultation/diagnostic/research/synthesize/safety_review/final_response`）
8. `src/tools` 基础层 + registry
9. `src/persistence`
10. HITL 超时 watchdog + reopen 流
11. `src/guardrails`
12. `apps/api` + `apps/worker`
13. `src/observability`
14. `src/evals` + CI gates

## 变更控制

任何实现不得偏离本契约，除非同时满足：

1. 用户明确批准该行为变更；并且
2. 本文件先被更新。
