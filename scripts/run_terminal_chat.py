from __future__ import annotations

import argparse
import time
from typing import Any

import httpx

TERMINAL_TASK_STATUSES = {"completed", "failed", "cancelled"}


class ApiChatClient:
    def __init__(self, *, base_url: str, request_timeout_seconds: float) -> None:
        self.base_url = base_url.rstrip("/")
        # `trust_env=False` avoids accidentally routing localhost traffic
        # through system/company proxies, which often causes 502 errors.
        self._client = httpx.Client(timeout=request_timeout_seconds, trust_env=False)

    def close(self) -> None:
        self._client.close()

    def submit_question(self, question: str) -> dict[str, Any]:
        response = self._client.post(
            f"{self.base_url}/tasks",
            json={
                "user_id": "terminal_user",
                "graph_name": "medical_consultation",
                "graph_version": "v1",
                "payload": {"question": question},
            },
        )
        response.raise_for_status()
        return dict(response.json())

    def get_task_status(self, task_id: str) -> dict[str, Any]:
        response = self._client.get(f"{self.base_url}/tasks/{task_id}")
        response.raise_for_status()
        return dict(response.json())

    def get_task_result(self, task_id: str) -> dict[str, Any]:
        response = self._client.get(f"{self.base_url}/tasks/{task_id}/result")
        response.raise_for_status()
        return dict(response.json())


def run_once(
    *,
    client: ApiChatClient,
    question: str,
    wait_timeout_seconds: float,
    poll_interval_seconds: float,
) -> None:
    created = client.submit_question(question)
    task_id = str(created["task_id"])

    deadline = time.monotonic() + wait_timeout_seconds
    last_status = "pending"

    while time.monotonic() < deadline:
        result_payload = client.get_task_result(task_id)
        status = str(result_payload.get("status", "unknown"))
        last_status = status
        if status in TERMINAL_TASK_STATUSES:
            _print_result(result_payload)
            return
        time.sleep(poll_interval_seconds)

    status_payload = client.get_task_status(task_id)
    print("\n--- 回答 ---")
    print(f"任务超时未完成，请继续轮询。task_id={task_id}")
    print(f"\n[status={status_payload.get('status', last_status)}] [end_reason={status_payload.get('end_reason')}]")


def interactive(*, client: ApiChatClient, wait_timeout_seconds: float, poll_interval_seconds: float) -> None:
    print("Medix Terminal Chat (通过 API/Worker 执行，输入 exit/quit 退出)\n")
    while True:
        question = input("你: ").strip()
        if not question:
            continue
        if question.lower() in {"exit", "quit", "q"}:
            print("已退出。")
            return
        run_once(
            client=client,
            question=question,
            wait_timeout_seconds=wait_timeout_seconds,
            poll_interval_seconds=poll_interval_seconds,
        )
        print()


def _print_result(result_payload: dict[str, Any]) -> None:
    status = str(result_payload.get("status", "unknown"))
    end_reason = result_payload.get("end_reason")
    result = result_payload.get("result")

    answer = "未生成回答。"
    risk = "unknown"
    if isinstance(result, dict):
        answer = str(result.get("answer") or answer)
        risk = str(result.get("risk_level") or risk)

    print("\n--- 回答 ---")
    print(answer)
    print(f"\n[status={status}] [risk_level={risk}] [end_reason={end_reason}]")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run medix terminal chat via API + worker runtime.")
    parser.add_argument("--api-base-url", default="http://127.0.0.1:8000", help="API base URL.")
    parser.add_argument("--once", type=str, default="", help="Single question mode.")
    parser.add_argument("--wait-timeout-seconds", type=float, default=20.0, help="Wait timeout for one question.")
    parser.add_argument("--poll-interval-seconds", type=float, default=0.2, help="Polling interval.")
    parser.add_argument("--request-timeout-seconds", type=float, default=10.0, help="HTTP request timeout.")
    args = parser.parse_args()

    client = ApiChatClient(
        base_url=args.api_base_url,
        request_timeout_seconds=args.request_timeout_seconds,
    )
    try:
        if args.once:
            run_once(
                client=client,
                question=args.once,
                wait_timeout_seconds=args.wait_timeout_seconds,
                poll_interval_seconds=args.poll_interval_seconds,
            )
            return
        interactive(
            client=client,
            wait_timeout_seconds=args.wait_timeout_seconds,
            poll_interval_seconds=args.poll_interval_seconds,
        )
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text if exc.response is not None else ""
        print(f"API 返回错误：{exc}")
        if detail:
            print(f"响应体：{detail}")
        print(
            "若仍为 502，请检查系统代理并确保 NO_PROXY 包含 127.0.0.1,localhost。"
        )
    except httpx.HTTPError as exc:
        print(f"连接 API 失败：{exc}")
        print(
            f"请先启动服务：python scripts/run_dev_stack.py --host 127.0.0.1 --port 8000"
            f"\n或通过 --api-base-url 指定可用地址。"
        )
    finally:
        client.close()


if __name__ == "__main__":
    main()
