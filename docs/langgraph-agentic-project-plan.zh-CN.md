# 工业级 LangGraph Agentic 项目规划

## 目标

本文档定义了将当前医疗助手项目重写为工业级 LangGraph Agentic 应用的目标架构。

目标系统应满足：

- 以工作流驱动，而不是自由形态的 Agent Loop 驱动。
- 在图状态、任务、工具、输出边界上具备强类型约束。
- 通过检查点与任务生命周期管理实现可恢复性。
- 通过结构化追踪、图事件、安全决策与最终引用实现可审计性。
- 通过工程约束默认安全，特别覆盖医疗分诊、诊断、用药、隐私与人工升级。
- 通过单元测试、图测试、集成测试、安全测试与评测回归实现可验证性。

## 架构原则

1. 编排归工作流负责。\
   LangGraph 图负责执行路径、分支、重试、检查点、中断与收敛行为。

2. 推理归 Agent 负责。\
   Agent 用于图节点内部的有界推理，不负责整个应用生命周期决策。

3. 外部动作归工具负责。\
   检索、搜索、数据库、文件系统、浏览器等副作用操作通过类型化工具契约执行。

4. 安全归 Guardrails 负责。\
   安全规则必须落实为代码策略、权限检查、沙箱限制与输出审查，而不仅是提示词。

5. 恢复归持久化负责。\
   任务状态、线程状态、检查点与回放数据必须是一等公民。

6. 诊断归可观测性负责。\
   每次图运行必须产出 trace_id、节点 span、工具调用、模型使用、延迟、成本、安全决策与审计记录。

7. 质量门禁归评测负责。\
   回归样例、安全样例、工具调用断言必须纳入发布流程。

## 目标项目结构

```text
langgraph-agentic-app/
├─ apps/
│  ├─ api/
│  │  ├─ main.py
│  │  ├─ deps.py
│  │  ├─ schemas.py
│  │  └─ routes/
│  │     ├─ tasks.py
│  │     ├─ threads.py
│  │     └─ approvals.py
│  ├─ worker/
│  │  ├─ main.py
│  │  ├─ runner.py
│  │  └─ lifecycle.py
│  └─ cli/
│     ├─ main.py
│     ├─ run.py
│     ├─ replay.py
│     └─ debug_node.py
├─ src/
│  ├─ graphs/
│  │  ├─ base.py
│  │  ├─ registry.py
│  │  ├─ versions.py
│  │  └─ medical_consultation/
│  │     ├─ graph.py
│  │     ├─ state.py
│  │     ├─ routing.py
│  │     └─ nodes/
│  │        ├─ intake.py
│  │        ├─ triage.py
│  │        ├─ retrieve.py
│  │        ├─ consultation.py
│  │        ├─ diagnostic.py
│  │        ├─ research.py
│  │        ├─ synthesize.py
│  │        ├─ safety_review.py
│  │        ├─ final_response.py
│  │        └─ error_handler.py
│  ├─ nodes/
│  │  └─ common/
│  │     ├─ model_call.py
│  │     ├─ tool_call.py
│  │     ├─ human_interrupt.py
│  │     └─ retry.py
│  ├─ state/
│  │  ├─ reducers.py
│  │  ├─ serializers.py
│  │  └─ migrations.py
│  ├─ contracts/
│  │  ├─ tasks.py
│  │  ├─ graph_events.py
│  │  ├─ tools.py
│  │  ├─ approvals.py
│  │  └─ outputs.py
│  ├─ tools/
│  │  ├─ base.py
│  │  ├─ registry.py
│  │  ├─ knowledge_search.py
│  │  ├─ guideline_search.py
│  │  ├─ risk_score.py
│  │  ├─ icd_lookup.py
│  │  └─ web_search.py
│  ├─ models/
│  │  ├─ client.py
│  │  ├─ providers.py
│  │  ├─ routing.py
│  │  └─ prompts.py
│  ├─ retrieval/
│  │  ├─ embeddings.py
│  │  ├─ vector_store.py
│  │  ├─ document_loader.py
│  │  ├─ chunking.py
│  │  ├─ reranker.py
│  │  └─ citations.py
│  ├─ persistence/
│  │  ├─ checkpointers.py
│  │  ├─ stores.py
│  │  ├─ threads.py
│  │  └─ replay.py
│  ├─ memory/
│  │  ├─ short_term.py
│  │  ├─ long_term.py
│  │  ├─ retrieval.py
│  │  └─ compaction.py
│  ├─ human_in_the_loop/
│  │  ├─ interrupts.py
│  │  ├─ approvals.py
│  │  ├─ review_queue.py
│  │  └─ resume.py
│  ├─ guardrails/
│  │  ├─ permissions.py
│  │  ├─ sandbox.py
│  │  ├─ medical_policy.py
│  │  ├─ output_policy.py
│  │  ├─ secrets.py
│  │  └─ audit.py
│  ├─ tasks/
│  │  ├─ model.py
│  │  ├─ store.py
│  │  ├─ claim.py
│  │  └─ lifecycle.py
│  ├─ workspaces/
│  │  ├─ manager.py
│  │  ├─ sandbox.py
│  │  ├─ locks.py
│  │  └─ cleanup.py
│  ├─ observability/
│  │  ├─ tracing.py
│  │  ├─ metrics.py
│  │  ├─ logging.py
│  │  ├─ langsmith.py
│  │  ├─ cost.py
│  │  └─ audit_log.py
│  ├─ evals/
│  │  ├─ runner.py
│  │  ├─ graders.py
│  │  ├─ graph_regression.py
│  │  └─ tool_assertions.py
│  └─ config/
│     ├─ settings.py
│     ├─ graph_versions.py
│     ├─ environments.py
│     └─ feature_flags.py
├─ prompts/
│  ├─ registry.yaml
│  └─ medical_consultation/
│     ├─ consultation.md
│     ├─ diagnostic.md
│     ├─ research.md
│     ├─ synthesize.md
│     └─ safety_review.md
├─ evals/
│  ├─ datasets/
│  ├─ golden/
│  ├─ red_team/
│  └─ scenarios/
├─ tests/
│  ├─ unit/
│  ├─ graph/
│  ├─ integration/
│  ├─ safety/
│  └─ fixtures/
├─ docs/
├─ migrations/
├─ scripts/
├─ pyproject.toml
├─ .env.example
└─ README.md
```

## Python 文件职责

### `apps/api`

| 文件 | 职责 |
| --- | --- |
| `apps/api/main.py` | FastAPI 入口。创建应用、注册路由、中间件、生命周期钩子与健康检查。 |
| `apps/api/deps.py` | API 依赖注入。向路由注入 settings、task store、graph registry、审批服务与认证上下文。 |
| `apps/api/schemas.py` | API 请求/响应结构定义。将 HTTP 契约与内部图状态解耦。 |
| `apps/api/routes/tasks.py` | 任务接口。创建图任务、查询状态、读取结果、取消任务。 |
| `apps/api/routes/threads.py` | 线程/检查点接口。查询线程历史、检查点、回放元数据与执行事件。 |
| `apps/api/routes/approvals.py` | 人工审批接口。提交审批决策、拒绝不安全动作、恢复被中断图执行。 |

### `apps/worker`

| 文件 | 职责 |
| --- | --- |
| `apps/worker/main.py` | Worker 进程入口。加载配置、初始化依赖并启动运行时。 |
| `apps/worker/runner.py` | 任务执行器。领取任务、解析图版本、执行编译后的 LangGraph、持久化结果并处理图级失败。 |
| `apps/worker/lifecycle.py` | Worker 生命周期管理。处理启动、停止、心跳、租约续期、优雅取消。 |

### `apps/cli`

| 文件 | 职责 |
| --- | --- |
| `apps/cli/main.py` | CLI 入口。注册本地图执行、回放、单节点调试命令。 |
| `apps/cli/run.py` | 本地图运行器。无需 API/队列即可用本地 payload 执行指定图。 |
| `apps/cli/replay.py` | 检查点回放命令。根据持久化检查点重建图状态并回放执行。 |
| `apps/cli/debug_node.py` | 单节点调试器。用 state fixture 运行单个节点并输出状态 patch。 |

### `src/graphs`

| 文件 | 职责 |
| --- | --- |
| `src/graphs/base.py` | 图工厂通用能力。依赖注入、checkpointer 接线、图配置与 compile 参数管理。 |
| `src/graphs/registry.py` | 图注册表。维护图名+版本到编译图定义的映射与查询能力。 |
| `src/graphs/versions.py` | 图版本元数据。定义支持版本、兼容规则与弃用策略。 |

### `src/graphs/medical_consultation`

| 文件 | 职责 |
| --- | --- |
| `src/graphs/medical_consultation/graph.py` | 医疗咨询 `StateGraph` 定义。注册节点、条件边、错误路径、中断点并编译。 |
| `src/graphs/medical_consultation/state.py` | 医疗咨询图状态模式。定义问题、患者上下文、风险等级、证据、引用、最终答案等字段。 |
| `src/graphs/medical_consultation/routing.py` | 医疗咨询路由函数。决定急诊路径、普通咨询、复杂诊断、研究、安全审查或终止。 |
| `.../nodes/intake.py` | 入口节点。归一化输入、校验必填上下文、提取患者字段、初始化图元数据。 |
| `.../nodes/triage.py` | 分诊节点。识别急症症状、判定风险等级、决定是否强制急诊指引。 |
| `.../nodes/retrieve.py` | 检索节点。获取知识库、指南、线程记忆与长期记忆片段。 |
| `.../nodes/consultation.py` | 咨询推理节点。为非急症低/中风险问题生成一般健康建议。 |
| `.../nodes/diagnostic.py` | 诊断推理节点。执行症状模式与鉴别分析，不给出确定性诊断。 |
| `.../nodes/research.py` | 证据研究节点。汇总检索证据并输出可引用结论。 |
| `.../nodes/synthesize.py` | 综合节点。融合咨询、诊断、研究产出形成候选答复。 |
| `.../nodes/safety_review.py` | 安全审查节点。对诊断、用药、隐私、引用进行政策审查。 |
| `.../nodes/final_response.py` | 最终输出节点。生成用户答案、引用、免责声明、后续建议与审计摘要。 |
| `.../nodes/error_handler.py` | 错误处理节点。将可恢复错误转换为安全答复并记录失败元数据。 |

### `src/nodes/common`

| 文件 | 职责 |
| --- | --- |
| `src/nodes/common/model_call.py` | 模型调用通用封装。统一 tracing、超时、重试、schema 解析与成本记录。 |
| `src/nodes/common/tool_call.py` | 工具调用通用封装。执行权限校验、输入输出 schema 校验、审计事件记录。 |
| `src/nodes/common/human_interrupt.py` | 人工中断通用封装。创建审批/澄清/审查型 LangGraph interrupt。 |
| `src/nodes/common/retry.py` | 重试与回退通用封装。执行有界重试并产出回退状态 patch。 |

### `src/state`

| 文件 | 职责 |
| --- | --- |
| `src/state/reducers.py` | 通用 reducer。定义 append、merge、去重、last-write-wins 行为。 |
| `src/state/serializers.py` | 状态序列化。图状态与持久化格式互转。 |
| `src/state/migrations.py` | 状态迁移。将旧检查点状态升级到当前 schema。 |

### `src/contracts`

| 文件 | 职责 |
| --- | --- |
| `src/contracts/tasks.py` | 任务契约。定义任务创建、状态、结果、取消模型。 |
| `src/contracts/graph_events.py` | 图事件契约。定义节点开始/完成、工具调用、模型调用、中断、恢复、失败、完成事件。 |
| `src/contracts/tools.py` | 工具契约。定义输入输出模型、权限元数据、失败模型与结果包装。 |
| `src/contracts/approvals.py` | 审批契约。定义审批请求、审批决策、审查员元数据与恢复 payload。 |
| `src/contracts/outputs.py` | 输出契约。定义最终答案、引用、免责声明、安全警示等结构化响应。 |

### `src/tools`

| 文件 | 职责 |
| --- | --- |
| `src/tools/base.py` | 工具协议与元数据。定义调用接口、输入输出 schema、超时、副作用等级、权限要求。 |
| `src/tools/registry.py` | 工具注册表。注册工具、按名/版本解析工具、校验节点是否可调用。 |
| `src/tools/knowledge_search.py` | 医疗知识检索工具。查询策展知识库并返回排序证据片段。 |
| `src/tools/guideline_search.py` | 临床指南检索工具。返回带来源元数据与时效信息的指南段落。 |
| `src/tools/risk_score.py` | 风险评分工具。执行规则分诊并可选模型辅助分类。 |
| `src/tools/icd_lookup.py` | ICD 编码查询工具。检索 ICD 代码与疾病分类元数据。 |
| `src/tools/web_search.py` | 外部检索工具。执行受控网络/文献检索，带来源过滤、超时与引用元数据。 |

### `src/models`

| 文件 | 职责 |
| --- | --- |
| `src/models/client.py` | 统一模型客户端接口。提供 chat、结构化输出、embedding、streaming 与可取消调用。 |
| `src/models/providers.py` | 供应商适配层。封装 OpenAI 兼容与本地/其他 provider 客户端。 |
| `src/models/routing.py` | 模型路由策略。按任务类型、风险等级、成本预算、时延目标与回退策略选模。 |
| `src/models/prompts.py` | 提示词加载。读取 `prompts/`、注入变量、校验版本并绑定输出 schema。 |

### `src/retrieval`

| 文件 | 职责 |
| --- | --- |
| `src/retrieval/embeddings.py` | Embedding 封装。提供批处理、缓存与 provider 抽象。 |
| `src/retrieval/vector_store.py` | 向量库适配。封装 Milvus/Qdrant/本地向量库操作。 |
| `src/retrieval/document_loader.py` | 文档加载器。读取源文档、抽取元数据、准备入库记录。 |
| `src/retrieval/chunking.py` | 切片策略。按重叠窗口切片并传递元数据。 |
| `src/retrieval/reranker.py` | 重排逻辑。用启发式或模型对检索结果重排。 |
| `src/retrieval/citations.py` | 引用构建器。将检索证据转换为稳定 citation 对象。 |

### `src/persistence`

| 文件 | 职责 |
| --- | --- |
| `src/persistence/checkpointers.py` | LangGraph checkpointer 配置。提供 memory/SQLite/Postgres/Redis 后端实现。 |
| `src/persistence/stores.py` | 存储适配。持久化任务、图事件、线程状态、记忆记录与审计数据。 |
| `src/persistence/threads.py` | 线程管理。创建 thread_id、映射会话与线程、列出检查点历史。 |
| `src/persistence/replay.py` | 回放服务。基于检查点与事件重建图运行用于调试和事故分析。 |

### `src/memory`

| 文件 | 职责 |
| --- | --- |
| `src/memory/short_term.py` | 短期记忆。存储线程级最近消息与图内上下文。 |
| `src/memory/long_term.py` | 长期记忆。在许可条件下存储跨会话摘要与用户长期事实。 |
| `src/memory/retrieval.py` | 记忆检索。带过滤与权限检查检索短期/长期记忆。 |
| `src/memory/compaction.py` | 记忆压缩。执行摘要化、去重、过期清理与压缩。 |

### `src/human_in_the_loop`

| 文件 | 职责 |
| --- | --- |
| `src/human_in_the_loop/interrupts.py` | 中断定义。定义审批、澄清、安全审查触发点。 |
| `src/human_in_the_loop/approvals.py` | 审批服务。应用审批规则、校验决策、记录审批事件。 |
| `src/human_in_the_loop/review_queue.py` | 审核队列。管理待审核项、分配、认领与超时处理。 |
| `src/human_in_the_loop/resume.py` | 恢复服务。将审批决策映射为图恢复命令与状态 patch。 |

### `src/guardrails`

| 文件 | 职责 |
| --- | --- |
| `src/guardrails/permissions.py` | 权限策略。判定图/节点/Agent/用户是否可执行某动作或调用某工具。 |
| `src/guardrails/sandbox.py` | 运行沙箱。限制文件系统、网络、命令执行与工作区访问。 |
| `src/guardrails/medical_policy.py` | 医疗政策。执行急诊升级、禁止确定性诊断、用药边界与不确定性表达规则。 |
| `src/guardrails/output_policy.py` | 输出策略。校验输出格式、免责声明、引用、拒绝措辞与安全表达。 |
| `src/guardrails/secrets.py` | 密钥扫描。检测输入/输出/工具载荷中的 token、密钥、凭据与敏感信息。 |
| `src/guardrails/audit.py` | 安全审计。记录拦截动作、安全警告、策略决策与人工覆盖。 |

### `src/tasks`

| 文件 | 职责 |
| --- | --- |
| `src/tasks/model.py` | 任务领域模型。定义身份、目标图、状态、优先级、线程、用户、时间戳与结果引用。 |
| `src/tasks/store.py` | 任务存储接口。独立于图状态创建/更新/查询任务。 |
| `src/tasks/claim.py` | 任务认领。支持 worker 认领、续租、释放并避免重复执行。 |
| `src/tasks/lifecycle.py` | 任务生命周期。统一 pending/running/paused/failed/cancelled/completed 转换。 |

### `src/workspaces`

| 文件 | 职责 |
| --- | --- |
| `src/workspaces/manager.py` | 工作区管理。创建隔离工作区并映射任务。 |
| `src/workspaces/sandbox.py` | 工作区沙箱。执行文件访问与命令执行策略。 |
| `src/workspaces/locks.py` | 工作区锁。防止并发任务改动同一资源。 |
| `src/workspaces/cleanup.py` | 工作区清理。清理过期文件、陈旧锁与历史工作区。 |

### `src/observability`

| 文件 | 职责 |
| --- | --- |
| `src/observability/tracing.py` | 链路追踪。生成 trace_id、节点 span、工具 span、模型 span 与图级追踪。 |
| `src/observability/metrics.py` | 指标。记录时延、成功率、失败率、工具错误率、排队时间、安全违规数。 |
| `src/observability/logging.py` | 结构化日志。输出 JSON 日志并注入 task_id/thread_id/trace_id/graph/node 信息。 |
| `src/observability/langsmith.py` | LangSmith 集成。开启时上报 LangGraph 与 LLM 追踪。 |
| `src/observability/cost.py` | 成本统计。按任务与用户聚合 token/tool/图运行成本。 |
| `src/observability/audit_log.py` | 用户可见审计日志。存储关键动作、安全决策、引用与最终输出元数据。 |

### `src/evals`

| 文件 | 职责 |
| --- | --- |
| `src/evals/runner.py` | 评测运行器。对指定图版本执行数据集并输出评分报告。 |
| `src/evals/graders.py` | 评分器。评估答案质量、安全行为、引用质量与任务完成度。 |
| `src/evals/graph_regression.py` | 图回归校验。对比路径、节点输出、安全决策与最终回答。 |
| `src/evals/tool_assertions.py` | 工具断言。校验必需工具是否调用、禁用工具是否未调用、入参是否合法。 |

### `src/config`

| 文件 | 职责 |
| --- | --- |
| `src/config/settings.py` | 运行配置。基于 `pydantic-settings` 读取环境变量并暴露类型化设置。 |
| `src/config/graph_versions.py` | 图版本配置。定义默认版本、灰度比例、版本 pin 策略。 |
| `src/config/environments.py` | 环境配置。定义 dev/test/staging/prod 差异。 |
| `src/config/feature_flags.py` | 特性开关。支持节点、工具、模型、策略能力渐进发布。 |

## 非 Python 区域职责

| 路径 | 职责 |
| --- | --- |
| `prompts/registry.yaml` | 提示词注册表：ID、版本、目标节点、负责人、期望输出 schema。 |
| `prompts/medical_consultation/*.md` | 医疗咨询图节点提示词模板。 |
| `evals/datasets/` | 原始评测数据集。 |
| `evals/golden/` | 回归黄金样例。 |
| `evals/red_team/` | 高风险对抗与安全样例。 |
| `evals/scenarios/` | 多步图评测场景定义。 |
| `tests/unit/` | 纯函数、策略、schema、工具、reducer 的单测。 |
| `tests/graph/` | 用 mock 模型/工具依赖执行图测试。 |
| `tests/integration/` | 持久化、检索、记忆、外部适配层集成测试。 |
| `tests/safety/` | 急诊升级、诊断边界、用药边界、隐私泄露安全测试。 |
| `tests/fixtures/` | 共享测试 payload、检查点样例、模型响应、工具输出。 |
| `docs/` | 架构、图设计、状态 schema、工具契约、HITL、持久化、评测、运维文档。 |
| `migrations/` | 数据库与状态存储迁移。 |
| `scripts/` | 离线索引、评测运行、部署冒烟与维护脚本。 |

## 医疗咨询图流程

```text
START
  -> intake
  -> triage
  -> route_after_triage

if emergency:
  -> final_response
  -> END

if normal_consultation:
  -> retrieve
  -> consultation
  -> safety_review
  -> final_response
  -> END

if complex_symptoms:
  -> retrieve
  -> diagnostic
  -> research
  -> synthesize
  -> safety_review
  -> final_response
  -> END

if retrieval_or_model_failure:
  -> error_handler
  -> safety_review
  -> final_response
  -> END
```

## 工业级最小可行切片

第一阶段不必一次性构建所有图和应用，应先验证一条工业级主链路。

优先构建：

1. `apps/api`
2. `apps/worker`
3. `src/graphs/medical_consultation`
4. `src/tools`
5. `src/persistence`
6. `src/guardrails`
7. `src/observability`
8. `tests/graph`
9. `tests/safety`

在首个业务图稳定后再扩展：

1. `apps/web`
2. 多业务图
3. 更高级工作区隔离
4. 完整 LangSmith 仪表盘
5. 大规模评测自动化

## 验收标准

只有当以下条件全部满足时，重写版本才可视为可生产：

1. 用户可通过 API 提交任务并获得 task_id。
2. Worker 可认领任务、运行图、保存检查点并持久化最终结果。
3. 图执行可在中断后从检查点恢复。
4. 急症症状可强制触发安全升级行为。
5. 用药剂量与确定性诊断请求可被拦截或安全改写。
6. 最终医疗回答包含不确定性表达、在使用证据时包含引用、并带免责声明。
7. 每次模型调用、工具调用、节点迁移、安全决策都可通过 `trace_id` 追踪。
8. 单测、图测试、集成测试、安全测试、评测可在 CI 运行。
9. 可通过文档命令与 `.env.example` 在本地启动。
10. 提示词版本、图版本、状态 schema 版本明确且可审计。
