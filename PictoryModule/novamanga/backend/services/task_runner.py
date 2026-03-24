import asyncio, json
from db import project_db
from .sse_manager import sse_manager

RETRY_DELAYS = [2, 8, 30]


class TaskRunner:
    def __init__(self, project_path: str, concurrency: int = 3):
        self.project_path = project_path
        self._sem = asyncio.Semaphore(concurrency)
        self._running = False

    async def start(self):
        self._running = True
        while self._running:
            tasks = project_db.fetch_pending_tasks(self.project_path, limit=10)
            for t in tasks:
                project_db.update_task(self.project_path, t["id"], status="processing")
                asyncio.create_task(self._execute(t))
            await asyncio.sleep(0.5)

    async def _execute(self, task: dict):
        from .task_handlers import HANDLERS
        async with self._sem:
            sse_manager.broadcast(task["reference_id"], {
                "task_id": task["id"], "type": task["type"], "status": "processing"
            })
            try:
                handler = HANDLERS[task["type"]]
                result = await handler(self.project_path, json.loads(task["payload"]))
                project_db.update_task(
                    self.project_path, task["id"],
                    status="completed", result=json.dumps(result, ensure_ascii=False)
                )
                sse_manager.broadcast(task["reference_id"], {
                    "task_id": task["id"], "type": task["type"],
                    "status": "completed", "result": result
                })
            except Exception as e:
                rc = task["retry_count"] + 1
                if rc <= task["max_retries"]:
                    delay = RETRY_DELAYS[min(rc - 1, len(RETRY_DELAYS) - 1)]
                    project_db.update_task(
                        self.project_path, task["id"],
                        status="pending", retry_count=rc,
                        error_message=f"retry {rc}: {str(e)}"
                    )
                    await asyncio.sleep(delay)
                else:
                    project_db.update_task(
                        self.project_path, task["id"],
                        status="failed", error_message=str(e)
                    )
                    sse_manager.broadcast(task["reference_id"], {
                        "task_id": task["id"], "type": task["type"],
                        "status": "failed", "error": str(e)
                    })


_runners: dict[str, TaskRunner] = {}


def get_runner(project_path: str) -> TaskRunner:
    if project_path not in _runners:
        _runners[project_path] = TaskRunner(project_path)
    return _runners[project_path]
