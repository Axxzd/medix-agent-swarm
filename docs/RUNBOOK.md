# Medix Agent Swarm 运行文档

## 1. 当前状态

- 当前为开发原型，功能边界见项目根目录 README。
- 新鲜测试结果和旧测试归档说明见 [VERIFICATION.md](VERIFICATION.md)。
- 当前本地运行推荐使用**单进程开发栈**（API + Worker 共享同一内存 runtime）。

## 2. 环境准备

在项目根目录执行：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

在 `.env` 中配置自己的服务密钥、接口地址和可用模型，切勿提交真实密钥。测试无需真实密钥。建议 Python 3.12，也可使用已安装依赖的 Conda 环境。

可选检查：

```powershell
python -c "from apps.api.main import app; print(app.title)"
```

## 3. 一键启动本地栈（推荐）

```powershell
.venv\Scripts\Activate.ps1
python scripts/run_dev_stack.py --host 127.0.0.1 --port 8000
```

启动后服务地址：

- API: `http://127.0.0.1:8000`
- FastAPI 文档: `http://127.0.0.1:8000/docs`

## 3.1 终端问答（与 API/Worker 行为一致）

`run_terminal_chat.py` 现在是 API 客户端，执行路径与 `run_dev_stack.py` 一致。\
请先启动本地栈（或指向远端 API）：

```powershell
.venv\Scripts\Activate.ps1
python scripts/run_dev_stack.py --host 127.0.0.1 --port 8000
```

再开一个终端执行：

```powershell
.venv\Scripts\Activate.ps1
python scripts/run_terminal_chat.py --api-base-url http://127.0.0.1:8000
```

单次问答模式：

```powershell
python scripts/run_terminal_chat.py --api-base-url http://127.0.0.1:8000 --once "持续高热三天，伴明显呼吸急促"
```

## 4. API 快速验证（PowerShell）

### 4.1 提交任务

```powershell
$body = @{
  user_id = "u1"
  graph_name = "medical_consultation"
  graph_version = "v1"
  payload = @{
    question = "持续高热三天，伴明显呼吸急促"
  }
} | ConvertTo-Json -Depth 5

$create = Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/tasks" -ContentType "application/json" -Body $body
$create
```

返回里会有 `task_id`。

### 4.2 查询状态

```powershell
$taskId = $create.task_id
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/tasks/$taskId"
```

### 4.3 获取结果

```powershell
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/tasks/$taskId/result"
```

## 5. 运行测试

完整当前测试集（旧版缺失模块的测试原文保留在 `archive/legacy-tests/`）：

```powershell
.venv\Scripts\Activate.ps1
$env:PYTHONIOENCODING='utf-8'
python -m pytest -q
```

## 6. 常见问题

### 6.1 端口占用

改端口启动：

```powershell
python scripts/run_dev_stack.py --port 8010
```

### 6.2 conda run 编码异常

如果选择 Conda 而非 `.venv`，先激活自己的 Conda 环境再直接执行命令。

### 6.3 API 启动了但任务不完成

请确认你使用的是 `scripts/run_dev_stack.py`。\
当前实现中，若把 API 和 Worker 分别以两个独立进程启动，它们不会共享内存 runtime。
