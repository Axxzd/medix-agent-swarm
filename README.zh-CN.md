# medix-agent-swarm

用于研究医疗咨询任务编排的 Python 原型：包含显式图路由、结构化任务契约、API/Worker、人工复核生命周期组件和回归测试。[English](README.md)

**当前为开发原型，仅供软件研究与教学。** 尚无临床有效性验证，不能用于诊断、治疗或紧急决策。演示与 Issue 请使用合成数据。

## 已有实现

- 自定义 `GraphApp` 执行器，包含输入、预分诊、意图澄清、咨询、研究、综合、安全检查与回答节点。
- FastAPI 任务、线程与审批接口，以及内存任务存储、Worker 重试和租约逻辑。
- Pydantic 任务、输出、引用、工具和复核票据契约。
- 独立的 SQLite 存储、检查点与回放组件，以及人工复核超时/恢复组件。
- 路由、生命周期、API/Worker、输出策略和评估门禁的测试；测试以固定替身代替模型调用。

## 必须了解的实现边界

当前图执行器没有接入 LangGraph SDK；`docs/` 中的 LangGraph 文档是设计方向。研究节点默认返回演示证据，开发 Worker 尚未接入真实检索源，因此默认引用不能当作真实医学证据。

API 与 Worker 需要在同一进程共享内存，重启会丢失 API 任务。SQLite 组件尚未接入 API 主流程，PostgreSQL 后端也未实现。人工复核组件有独立测试，但图中的复核节点默认安全结束，尚无完整的临床人工中断与恢复流程。API 没有身份认证和租户隔离，仅建议绑定本机开发。

软件测试通过只说明对应软件行为通过验证，不代表医学正确性、临床安全、真实用户采用或生产可用。

## 本地启动

使用 Python 3.12，在项目目录执行：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

在本地 `.env` 填写 `MEDIX_LLM_API_KEY`。默认使用 OpenAI 接口；若使用其他兼容服务，须同时设置对应的 `MEDIX_LLM_BASE_URL` 与 `MEDIX_LLM_MODEL_NAME`。模型名称以你的服务实际支持情况为准，真实请求可能产生费用。不要提交 `.env`。

```powershell
python scripts/run_dev_stack.py --host 127.0.0.1 --port 8000
```

打开 <http://127.0.0.1:8000/docs>，再开一个终端进入同一环境执行：

```powershell
python scripts/run_terminal_chat.py --api-base-url http://127.0.0.1:8000
```

Linux/macOS 使用 `. .venv/bin/activate` 和 `cp .env.example .env`，其余命令相同。

## 测试与贡献

```powershell
python -m pytest -q
```

初次审计发现两个旧测试引用目录中不存在的 `swarm`、`knowledge.milvus_kb` 模块，原文件已完整保留到 [archive/legacy-tests](archive/legacy-tests/README.md)。本地测试结果和验证边界见 [VERIFICATION.md](docs/VERIFICATION.md)。GitHub Actions 运行当前 `tests/` 中的完整测试，云端结果见 [CI 实际运行记录](https://github.com/Axxzd/medix-agent-swarm/actions/workflows/tests.yml)。运行说明见 [RUNBOOK](docs/RUNBOOK.md)，贡献步骤见 [CONTRIBUTING](CONTRIBUTING.md)，漏洞报告见 [SECURITY](SECURITY.md)。

许可证：[MIT](LICENSE)，仅覆盖贡献者有权授权的代码，不包含外部医学数据集或模型权重授权。
