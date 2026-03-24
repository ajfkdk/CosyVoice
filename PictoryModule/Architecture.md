*Thinking...*

> The user wants me to redesign the architecture based on the API examples provided, and give a step-by-step implementation plan that Claude Code can follow. Let me analyze:
> 
> 1. **NanoBanana Engine**: Takes model name + token, sends image + text prompt, gets back an image (multimodal image generation/editing)
>    - API URL: `https://api.mmw.ink/v1/chat/completions`
>    - Uses base64 encoded images
>    - Returns base64 encoded image (in markdown format or raw)
> 
> 2. **LLM Engine**: Takes model name + token, standard OpenAI-compatible chat completions
>    - API URL: `https://api.poe.com/v1`
>    - Standard OpenAI client
> 
> So I need to abstract these into two separate engine classes, then redesign the full architecture around them and create a step-by-step implementation plan. The engine layer will have an `LLMEngine` wrapping the OpenAI client pointed at Poe, and a `NanoBananaEngine` handling image generation with optional reference images. Then I'll build the agent layer on top using the LLM engine.
> 
> For the agents, I'm looking at `LiuBeiAgent` for zone parsing, `XiaoMingAgent` for character extraction and prompt generation, and `XiaoQiaoAgent` for scene synthesis. The image generation will handle three-view character generation and scene images through the NanoBanana engine, and I still need to figure out where CosyVoice fits into the audio generation pipeline.
> 
> The key realization is that both APIs are OpenAI-compatible, so I can build both engines using the same Python client library but with different base URLs—Poe at `https://api.poe.com/v1` and NanaBanana at `https://api.mmw.ink/v1`. NanaBanana has special handling for multimodal messages with base64-encoded images and returns images in markdown format, so I'll need to account for that in the engine implementation.
> 
> Designing the full project structure now with concrete file paths and module organization...
> 
> Setting up the engine abstractions with async LLM calls to Poe API and image generation through the custom endpoint...

# NovaManga 架构设计文档 v2（可落地版）

## 一、引擎层抽象

这是整个系统最底层的两块基石，所有 Agent 都建立在这上面。

### LLMEngine

```python
# backend/engines/llm_engine.py
import json, re
import openai

class LLMEngine:
    # 硬编码，原型阶段不配置
    _MODEL   = "gpt-5.4-mini"
    _API_KEY = "sk-YOUR_POE_KEY"
    _BASE_URL = "https://api.poe.com/v1"

    def __init__(self):
        self._client = openai.AsyncOpenAI(
            api_key=self._API_KEY,
            base_url=self._BASE_URL,
        )

    async def complete(self, messages: list[dict], system: str | None = None) -> str:
        if system:
            messages = [{"role": "system", "content": system}] + messages
        resp = await self._client.chat.completions.create(
            model=self._MODEL, messages=messages
        )
        return resp.choices[0].message.content

    async def complete_json(self, messages: list[dict], system: str | None = None) -> dict:
        raw = await self.complete(messages, system)
        # 剥离 markdown 代码块
        raw = re.sub(r"^```(?:json)?\n?", "", raw.strip())
        raw = re.sub(r"\n?```$", "", raw)
        return json.loads(raw)
```

### NanaBananaEngine

```python
# backend/engines/nanobanana_engine.py
import base64, re
from pathlib import Path
import httpx

class NanaBananaEngine:
    # 硬编码，原型阶段不配置
    _MODEL   = "[A]gemini-3-pro-image-preview"
    _API_KEY = "sk-YOUR_MMW_KEY"
    _API_URL = "https://api.mmw.ink/v1/chat/completions"

    async def generate(
        self,
        prompt: str,
        reference_images: list[str] | None = None,  # 本地文件绝对路径列表
    ) -> bytes:
        """
        输入：文本 prompt + 可选参考图路径列表
        输出：生成图片的 bytes
        """
        content: list[dict] = [{"type": "text", "text": prompt}]

        for path in (reference_images or []):
            data = Path(path).read_bytes()
            ext  = Path(path).suffix.lstrip(".") or "png"
            b64  = base64.b64encode(data).decode()
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/{ext};base64,{b64}"}
            })

        payload = {
            "model": self._MODEL,
            "messages": [{"role": "user", "content": content}],
        }
        headers = {
            "Authorization": f"Bearer {self._API_KEY}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(self._API_URL, headers=headers, json=payload)
            resp.raise_for_status()

        content_str = resp.json()["choices"][0]["message"]["content"]
        match = re.search(r"data:image/\w+;base64,([A-Za-z0-9+/=]+)", content_str)
        if not match:
            raise ValueError(f"NanaBanana 未返回图片，原始内容: {content_str[:300]}")
        return base64.b64decode(match.group(1))
```

---

## 二、完整目录结构

```
novamanga/
├── backend/
│   ├── main.py
│   ├── config.py                    # workspace 路径、并发度等常量
│   ├── engines/
│   │   ├── __init__.py
│   │   ├── llm_engine.py            # LLMEngine
│   │   └── nanobanana_engine.py     # NanaBananaEngine
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── liu_bei.py               # 句区切分 Agent
│   │   ├── xiao_ming.py             # 角色提取 + 三视图 Prompt Agent
│   │   └── xiao_qiao.py             # 场景 Prompt 合成 Agent
│   ├── db/
│   │   ├── __init__.py
│   │   ├── global_db.py             # projects.db 操作
│   │   ├── project_db.py            # project.db 操作（per-project）
│   │   └── schema.py                # 建表 SQL，两个数据库的 DDL 都在此
│   ├── services/
│   │   ├── __init__.py
│   │   ├── task_runner.py           # 后台任务队列（asyncio，并发度=3）
│   │   ├── task_handlers.py         # 每种 task_type 的具体执行函数
│   │   └── sse_manager.py           # SSE 订阅/推送管理
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── projects.py
│   │   ├── chapters.py
│   │   ├── zones.py
│   │   ├── characters.py
│   │   └── sse.py
│   └── requirements.txt
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── api/
│       │   └── client.ts            # axios 实例 + 所有 API 函数
│       ├── stores/
│       │   ├── projectStore.ts      # Zustand
│       │   ├── taskStore.ts         # Zustand，由 SSE 驱动
│       │   └── assetStore.ts        # Zustand
│       ├── hooks/
│       │   ├── useSSE.ts            # EventSource 管理
│       │   └── useTaskStatus.ts     # 订阅某个 reference_id 的任务状态
│       ├── pages/
│       │   ├── ProjectList.tsx
│       │   ├── ProjectDashboard.tsx
│       │   ├── ChapterEditor.tsx
│       │   ├── ZoneEditor.tsx
│       │   ├── CharacterAssets.tsx
│       │   └── Timeline.tsx
│       └── components/
│           ├── ZoneCard.tsx
│           ├── TaskBadge.tsx
│           ├── CharacterModal.tsx
│           ├── AudioPlayer.tsx
│           └── ImageViewer.tsx
├── start.sh                         # 一键启动：后端 + 前端
└── README.md
```

---

## 三、数据库模式（完整 DDL）

```python
# backend/db/schema.py

GLOBAL_DB_DDL = """
CREATE TABLE IF NOT EXISTS projects (
    id           TEXT PRIMARY KEY,
    name         TEXT NOT NULL,
    path         TEXT NOT NULL UNIQUE,   -- 项目目录绝对路径
    created_at   INTEGER NOT NULL,
    updated_at   INTEGER NOT NULL
);
"""

PROJECT_DB_DDL = """
CREATE TABLE IF NOT EXISTS chapters (
    id            TEXT PRIMARY KEY,
    project_id    TEXT NOT NULL,
    title         TEXT NOT NULL,
    order_index   INTEGER NOT NULL,
    raw_text      TEXT NOT NULL DEFAULT '',
    parse_status  TEXT NOT NULL DEFAULT 'idle',
    created_at    INTEGER NOT NULL,
    updated_at    INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS zones (
    id                  TEXT PRIMARY KEY,
    chapter_id          TEXT NOT NULL,
    order_index         INTEGER NOT NULL,
    text_content        TEXT NOT NULL,
    start_char_index    INTEGER NOT NULL DEFAULT 0,
    end_char_index      INTEGER NOT NULL DEFAULT 0,
    scene_id            TEXT,
    emotion_primary     TEXT NOT NULL DEFAULT '平静',
    emotion_intensity   REAL NOT NULL DEFAULT 0.5,
    characters_present  TEXT NOT NULL DEFAULT '[]',  -- JSON 数组: variant_id[]
    audio_asset_id      TEXT,
    image_asset_id      TEXT,
    duration_ms         INTEGER,
    created_at          INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS characters (
    id                  TEXT PRIMARY KEY,
    project_id          TEXT NOT NULL,
    name                TEXT NOT NULL,
    raw_description     TEXT NOT NULL DEFAULT '',
    personality_tags    TEXT NOT NULL DEFAULT '[]',
    color_tendency      TEXT NOT NULL DEFAULT '',
    created_at          INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS character_variants (
    id                      TEXT PRIMARY KEY,
    character_id            TEXT NOT NULL,
    variant_name            TEXT NOT NULL,
    prompt_positive         TEXT NOT NULL DEFAULT '',
    prompt_negative         TEXT NOT NULL DEFAULT '',
    trigger_words           TEXT NOT NULL DEFAULT '[]',
    appearance_summary      TEXT NOT NULL DEFAULT '',
    reference_images        TEXT NOT NULL DEFAULT '[]',  -- JSON 数组: 本地路径[]
    active_from_chapter     INTEGER,
    active_until_chapter    INTEGER,
    front_image_path        TEXT,
    side_image_path         TEXT,
    back_image_path         TEXT,
    gen_status              TEXT NOT NULL DEFAULT 'idle',
    created_at              INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS audio_assets (
    id              TEXT PRIMARY KEY,
    zone_id         TEXT NOT NULL,
    file_path       TEXT NOT NULL,
    duration_ms     INTEGER NOT NULL,
    emotion_params  TEXT NOT NULL DEFAULT '{}',  -- JSON: {speed,pitch,emotion,style}
    created_at      INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS image_assets (
    id                  TEXT PRIMARY KEY,
    zone_id             TEXT NOT NULL,
    file_path           TEXT NOT NULL,
    prompt_positive     TEXT NOT NULL DEFAULT '',
    prompt_negative     TEXT NOT NULL DEFAULT '',
    reference_images    TEXT NOT NULL DEFAULT '[]',
    generation_params   TEXT NOT NULL DEFAULT '{}',
    created_at          INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
    id              TEXT PRIMARY KEY,
    type            TEXT NOT NULL,
    payload         TEXT NOT NULL DEFAULT '{}',
    status          TEXT NOT NULL DEFAULT 'pending',
    retry_count     INTEGER NOT NULL DEFAULT 0,
    max_retries     INTEGER NOT NULL DEFAULT 3,
    error_message   TEXT,
    result          TEXT,
    reference_id    TEXT NOT NULL,
    reference_type  TEXT NOT NULL,
    created_at      INTEGER NOT NULL,
    updated_at      INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_reference ON tasks(reference_id);
"""
```

---

## 四、Agent 实现规范

### LiuBeiAgent

```python
# backend/agents/liu_bei.py

SYSTEM_PROMPT = """
你是刘备，专职小说文本的分镜切分。
你的任务是将输入文本切分为若干"句区"，每个句区是一个画面单元。
切分原则：
1. 每个句区对应一个独立的视觉场景或情绪单元，约 30~120 字
2. 对话与旁白尽量不混合在同一句区
3. 相同场景的连续句区使用相同的 scene_id（自定义字符串，如 "scene_001"）
4. 情绪标签从以下选择：悲痛、紧张、欢快、平静、愤怒、恐惧、温柔、震撼
5. intensity 为 0.0~1.0 的浮点数
6. characters_present 填写出现的角色名字（字符串，非 ID）
7. estimated_duration_s 为朗读该句区的估算秒数

严格返回 JSON，不要有任何其他文字。
"""

INPUT_TEMPLATE = """
当前文本块：
{block_text}

前置上下文（前一块末尾）：
{overlap_prev}

后置上下文（后一块开头）：
{overlap_next}
"""

OUTPUT_SCHEMA = {
    "zones": [
        {
            "text": "str",
            "start_char_offset": "int",
            "end_char_offset": "int",
            "scene_id": "str",
            "emotion_primary": "str",
            "emotion_intensity": "float",
            "characters_present": ["str"],
            "estimated_duration_s": "float"
        }
    ],
    "dedup_boundary_start": "int"
}
```

### XiaoMingAgent

```python
# backend/agents/xiao_ming.py

SYSTEM_PROMPT = """
你是小明，专职从小说描述中提取角色信息，并生成用于图像生成的 Prompt。
输入：角色名 + 原始描述文本
输出：结构化角色信息 + 三视图的图像生成 Prompt

Prompt 编写规则（用于 gemini-3-pro-image-preview 模型）：
1. positive 按 角色特征 → 服饰 → 表情/动作 → 背景 → 风格 顺序编写
2. 用英文逗号分隔的标签形式
3. 三视图分别加 front view / side view / back view 标签
4. negative 包含防混淆词：multiple people, crowd, deformed, blurry

严格返回 JSON，不要有任何其他文字。
"""
```

### XiaoQiaoAgent

```python
# backend/agents/xiao_qiao.py

SYSTEM_PROMPT = """
你是小乔，专职将小说句区合成为场景图像生成 Prompt。
你会收到：句区文本、情绪标签、场景上下文、以及出现的角色 Prompt 信息。
你的工作是将这些信息融合为一个连贯的图像生成 Prompt。

输出规则：
1. positive 顺序：主体角色 → 动作/表情 → 场景背景 → 光线氛围 → 画风
2. 根据 emotion_intensity 调整画面戏剧程度（0.8以上需要强烈光影对比）
3. 将角色的 trigger_words 嵌入 positive 中，权重高于场景描述
4. 用英文逗号分隔的标签形式

严格返回 JSON，不要有任何其他文字。
"""
```

---

## 五、Claude Code 分步实施计划

以下是 Claude Code 可以逐步执行的精确任务序列，每步均可独立运行验证。

---

### Phase 1：项目脚手架与引擎层

**Task 1.1 — 初始化后端**

```bash
# 创建目录结构
mkdir -p novamanga/backend/{engines,agents,db,services,routers}
cd novamanga/backend
touch engines/__init__.py agents/__init__.py db/__init__.py services/__init__.py routers/__init__.py

# 创建 requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.115.0
uvicorn[standard]==0.30.0
openai==1.40.0
httpx==0.27.0
python-multipart==0.0.9
EOF

pip install -r requirements.txt
```

**Task 1.2 — 实现 LLMEngine，并写单元测试**

创建 `backend/engines/llm_engine.py`（如上方规范）

```python
# 验证脚本 backend/engines/test_llm.py
import asyncio
from llm_engine import LLMEngine

async def main():
    engine = LLMEngine()
    result = await engine.complete_json([
        {"role": "user", "content": '返回 {"status": "ok", "value": 42}'}
    ])
    assert result["status"] == "ok"
    print("✅ LLMEngine 验证通过:", result)

asyncio.run(main())
```

**Task 1.3 — 实现 NanaBananaEngine，并写单元测试**

创建 `backend/engines/nanobanana_engine.py`（如上方规范）

```python
# 验证脚本 backend/engines/test_nanobanana.py
import asyncio
from nanobanana_engine import NanaBananaEngine

async def main():
    engine = NanaBananaEngine()
    img_bytes = await engine.generate("一只可爱的橙色猫咪，坐在窗台上，阳光风格，动漫插画")
    with open("/tmp/test_output.png", "wb") as f:
        f.write(img_bytes)
    print(f"✅ NanaBananaEngine 验证通过，图片大小: {len(img_bytes)} bytes")
    print("图片保存至 /tmp/test_output.png")

asyncio.run(main())
```

---

### Phase 2：数据库层

**Task 2.1 — 实现 schema.py 和数据库初始化**

创建 `backend/db/schema.py`（如上方 DDL）

**Task 2.2 — 实现 global_db.py**

```python
# backend/db/global_db.py
import sqlite3, uuid, time
from pathlib import Path
from .schema import GLOBAL_DB_DDL

GLOBAL_DB_PATH = Path.home() / ".novamanga" / "projects.db"

def get_conn() -> sqlite3.Connection:
    GLOBAL_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(GLOBAL_DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.executescript(GLOBAL_DB_DDL)
    conn.commit()
    return conn

def create_project(name: str, path: str) -> dict:
    with get_conn() as conn:
        pid = str(uuid.uuid4())
        now = int(time.time() * 1000)
        conn.execute(
            "INSERT INTO projects VALUES (?,?,?,?,?)",
            (pid, name, path, now, now)
        )
        return {"id": pid, "name": name, "path": path, "created_at": now, "updated_at": now}

def list_projects() -> list[dict]:
    with get_conn() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM projects ORDER BY updated_at DESC")]

def get_project(pid: str) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM projects WHERE id=?", [pid]).fetchone()
        return dict(row) if row else None
```

**Task 2.3 — 实现 project_db.py**

```python
# backend/db/project_db.py
import sqlite3, uuid, time, json
from pathlib import Path
from .schema import PROJECT_DB_DDL

def get_conn(project_path: str) -> sqlite3.Connection:
    db_path = Path(project_path) / "project.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.executescript(PROJECT_DB_DDL)
    conn.commit()
    return conn

# ── Chapter ──────────────────────────────────
def create_chapter(project_path: str, project_id: str, title: str, order_index: int) -> dict:
    with get_conn(project_path) as conn:
        cid = str(uuid.uuid4())
        now = int(time.time() * 1000)
        conn.execute(
            "INSERT INTO chapters(id,project_id,title,order_index,raw_text,parse_status,created_at,updated_at) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (cid, project_id, title, order_index, '', 'idle', now, now)
        )
        return get_chapter(project_path, cid)

def get_chapter(project_path: str, chapter_id: str) -> dict | None:
    with get_conn(project_path) as conn:
        row = conn.execute("SELECT * FROM chapters WHERE id=?", [chapter_id]).fetchone()
        return dict(row) if row else None

def update_chapter(project_path: str, chapter_id: str, **kwargs) -> dict:
    allowed = {"title", "raw_text", "order_index", "parse_status"}
    fields  = {k: v for k, v in kwargs.items() if k in allowed}
    fields["updated_at"] = int(time.time() * 1000)
    sets  = ", ".join(f"{k}=?" for k in fields)
    vals  = list(fields.values()) + [chapter_id]
    with get_conn(project_path) as conn:
        conn.execute(f"UPDATE chapters SET {sets} WHERE id=?", vals)
    return get_chapter(project_path, chapter_id)

def list_chapters(project_path: str) -> list[dict]:
    with get_conn(project_path) as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM chapters ORDER BY order_index"
        )]

# ── Zone ─────────────────────────────────────
def create_zone(project_path: str, chapter_id: str, data: dict) -> dict:
    with get_conn(project_path) as conn:
        zid = str(uuid.uuid4())
        now = int(time.time() * 1000)
        conn.execute(
            "INSERT INTO zones(id,chapter_id,order_index,text_content,"
            "start_char_index,end_char_index,scene_id,emotion_primary,"
            "emotion_intensity,characters_present,created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                zid, chapter_id,
                data.get("order_index", 0),
                data["text_content"],
                data.get("start_char_index", 0),
                data.get("end_char_index", 0),
                data.get("scene_id"),
                data.get("emotion_primary", "平静"),
                data.get("emotion_intensity", 0.5),
                json.dumps(data.get("characters_present", []), ensure_ascii=False),
                now,
            )
        )
        return get_zone(project_path, zid)

def get_zone(project_path: str, zone_id: str) -> dict | None:
    with get_conn(project_path) as conn:
        row = conn.execute("SELECT * FROM zones WHERE id=?", [zone_id]).fetchone()
        return dict(row) if row else None

def list_zones(project_path: str, chapter_id: str) -> list[dict]:
    with get_conn(project_path) as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM zones WHERE chapter_id=? ORDER BY order_index",
            [chapter_id]
        )]

def update_zone(project_path: str, zone_id: str, **kwargs) -> dict:
    allowed = {"order_index", "text_content", "emotion_primary",
               "emotion_intensity", "audio_asset_id", "image_asset_id", "duration_ms"}
    fields  = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        return get_zone(project_path, zone_id)
    sets = ", ".join(f"{k}=?" for k in fields)
    vals = list(fields.values()) + [zone_id]
    with get_conn(project_path) as conn:
        conn.execute(f"UPDATE zones SET {sets} WHERE id=?", vals)
    return get_zone(project_path, zone_id)

# ── Task ─────────────────────────────────────
def enqueue_task(project_path: str, task_type: str, payload: dict,
                 reference_id: str, reference_type: str, max_retries: int = 3) -> dict:
    with get_conn(project_path) as conn:
        tid = str(uuid.uuid4())
        now = int(time.time() * 1000)
        conn.execute(
            "INSERT INTO tasks(id,type,payload,status,retry_count,max_retries,"
            "reference_id,reference_type,created_at,updated_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (tid, task_type, json.dumps(payload), 'pending', 0, max_retries,
             reference_id, reference_type, now, now)
        )
        return get_task(project_path, tid)

def get_task(project_path: str, task_id: str) -> dict | None:
    with get_conn(project_path) as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id=?", [task_id]).fetchone()
        return dict(row) if row else None

def fetch_pending_tasks(project_path: str, limit: int = 10) -> list[dict]:
    with get_conn(project_path) as conn:
        rows = conn.execute(
            "SELECT * FROM tasks WHERE status='pending' ORDER BY created_at LIMIT ?",
            [limit]
        ).fetchall()
        return [dict(r) for r in rows]

def update_task(project_path: str, task_id: str, **kwargs) -> dict:
    allowed = {"status", "retry_count", "error_message", "result"}
    fields  = {k: v for k, v in kwargs.items() if k in allowed}
    fields["updated_at"] = int(time.time() * 1000)
    sets = ", ".join(f"{k}=?" for k in fields)
    vals = list(fields.values()) + [task_id]
    with get_conn(project_path) as conn:
        conn.execute(f"UPDATE tasks SET {sets} WHERE id=?", vals)
    return get_task(project_path, task_id)
```

---

### Phase 3：任务队列与 SSE 推送

**Task 3.1 — 实现 SSEManager**

```python
# backend/services/sse_manager.py
import asyncio
from collections import defaultdict

class SSEManager:
    def __init__(self):
        # { reference_id: { client_id: asyncio.Queue } }
        self._subs: dict[str, dict[str, asyncio.Queue]] = defaultdict(dict)

    def subscribe(self, client_id: str, reference_ids: list[str]) -> dict[str, asyncio.Queue]:
        queues = {}
        for rid in reference_ids:
            q = asyncio.Queue()
            self._subs[rid][client_id] = q
            queues[rid] = q
        return queues

    def unsubscribe(self, client_id: str, reference_ids: list[str]):
        for rid in reference_ids:
            self._subs[rid].pop(client_id, None)

    def broadcast(self, reference_id: str, event: dict):
        for q in list(self._subs.get(reference_id, {}).values()):
            q.put_nowait(event)

sse_manager = SSEManager()  # 全局单例
```

**Task 3.2 — 实现 TaskRunner**

```python
# backend/services/task_runner.py
import asyncio, json, time
from db import project_db
from .sse_manager import sse_manager

RETRY_DELAYS = [2, 8, 30]   # 指数退避（秒）

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
                # 立即标记为 processing，防止重复拾取
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
                result  = await handler(self.project_path, json.loads(task["payload"]))
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

# 全局实例字典，key = project_path
_runners: dict[str, TaskRunner] = {}

def get_runner(project_path: str) -> TaskRunner:
    if project_path not in _runners:
        _runners[project_path] = TaskRunner(project_path)
    return _runners[project_path]
```

**Task 3.3 — 实现 task_handlers.py**

```python
# backend/services/task_handlers.py
"""
每个 handler 签名：async def handler(project_path: str, payload: dict) -> dict
"""
import json, uuid, time
from pathlib import Path
from engines.llm_engine import LLMEngine
from engines.nanobanana_engine import NanaBananaEngine
from agents import liu_bei, xiao_ming, xiao_qiao
from db import project_db

llm    = LLMEngine()
banana = NanaBananaEngine()

# ── 刘备：句区切分 ────────────────────────────
async def handle_liu_bei_parse(project_path: str, payload: dict) -> dict:
    output   = await liu_bei.run(llm, payload)
    chapter_id = payload["chapter_id"]
    zones_created = []

    for i, z in enumerate(output["zones"]):
        zone = project_db.create_zone(project_path, chapter_id, {
            "order_index": payload["base_order"] + i,
            "text_content": z["text"],
            "start_char_index": payload["base_offset"] + z["start_char_offset"],
            "end_char_index": payload["base_offset"] + z["end_char_offset"],
            "scene_id": z["scene_id"],
            "emotion_primary": z["emotion_primary"],
            "emotion_intensity": z["emotion_intensity"],
            "characters_present": z.get("characters_present", []),
        })
        zones_created.append(zone["id"])

    project_db.update_chapter(project_path, chapter_id, parse_status="completed")
    return {"zones_created": zones_created}


# ── 小明：角色提取 + 三视图 Prompt ──────────────
async def handle_xiao_ming_extract(project_path: str, payload: dict) -> dict:
    output      = await xiao_ming.run(llm, payload)
    character_id = payload["character_id"]
    variant_id   = str(uuid.uuid4())
    now          = int(time.time() * 1000)

    with project_db.get_conn(project_path) as conn:
        conn.execute(
            "UPDATE characters SET personality_tags=?, color_tendency=? WHERE id=?",
            [
                json.dumps(output["personality_tags"], ensure_ascii=False),
                output["color_tendency"],
                character_id,
            ]
        )
        conn.execute(
            "INSERT INTO character_variants(id,character_id,variant_name,"
            "prompt_positive,prompt_negative,trigger_words,appearance_summary,"
            "gen_status,created_at) VALUES (?,?,?,?,?,?,?,?,?)",
            (
                variant_id, character_id, "默认版本",
                output["three_view_prompts"]["front"]["positive"],
                output["three_view_prompts"]["front"]["negative"],
                json.dumps(output.get("trigger_words", []), ensure_ascii=False),
                output["appearance_summary"],
                "pending", now,
            )
        )
    return {"variant_id": variant_id, "output": output}


# ── 三视图图片生成 ─────────────────────────────
async def handle_three_view_generate(project_path: str, payload: dict) -> dict:
    variant_id = payload["variant_id"]
    view       = payload["view"]        # "front" | "side" | "back"
    prompt_pos = payload["prompt_positive"]
    ref_images = payload.get("reference_images", [])

    full_prompt = f"{prompt_pos}, {view} view, full body, white background, character sheet"
    img_bytes   = await banana.generate(full_prompt, ref_images or None)

    save_dir  = Path(project_path) / "assets" / "characters" / variant_id
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / f"{view}.png"
    save_path.write_bytes(img_bytes)

    col = f"{view}_image_path"
    with project_db.get_conn(project_path) as conn:
        conn.execute(
            f"UPDATE character_variants SET {col}=?, gen_status=? WHERE id=?",
            [str(save_path), "completed", variant_id]
        )
    return {"path": str(save_path)}


# ── 小乔：场景 Prompt ──────────────────────────
async def handle_xiao_qiao_prompt(project_path: str, payload: dict) -> dict:
    output  = await xiao_qiao.run(llm, payload)
    zone_id = payload["zone_id"]
    with project_db.get_conn(project_path) as conn:
        conn.execute(
            "UPDATE zones SET emotion_primary=? WHERE id=?",
            [payload.get("emotion_primary", "平静"), zone_id]
        )
    return {"prompt": output}


# ── NanaBanana：场景图片生成 ───────────────────
async def handle_nanobanana_generate(project_path: str, payload: dict) -> dict:
    zone_id     = payload["zone_id"]
    prompt_pos  = payload["prompt_positive"]
    prompt_neg  = payload.get("prompt_negative", "")
    ref_images  = payload.get("reference_images", [])

    full_prompt = prompt_pos
    img_bytes   = await banana.generate(full_prompt, ref_images or None)

    save_dir  = Path(project_path) / "assets" / "images"
    save_dir.mkdir(parents=True, exist_ok=True)
    asset_id  = str(uuid.uuid4())
    save_path = save_dir / f"{zone_id}_{asset_id}.png"
    save_path.write_bytes(img_bytes)

    now = int(time.time() * 1000)
    with project_db.get_conn(project_path) as conn:
        conn.execute(
            "INSERT INTO image_assets(id,zone_id,file_path,prompt_positive,"
            "prompt_negative,reference_images,created_at) VALUES (?,?,?,?,?,?,?)",
            (asset_id, zone_id, str(save_path), prompt_pos, prompt_neg,
             json.dumps(ref_images), now)
        )
        conn.execute(
            "UPDATE zones SET image_asset_id=? WHERE id=?",
            [asset_id, zone_id]
        )
    return {"asset_id": asset_id, "path": str(save_path)}


HANDLERS = {
    "liu_bei_parse":        handle_liu_bei_parse,
    "xiao_ming_extract":    handle_xiao_ming_extract,
    "three_view_generate":  handle_three_view_generate,
    "xiao_qiao_prompt":     handle_xiao_qiao_prompt,
    "nanobanana_generate":  handle_nanobanana_generate,
}
```

---

### Phase 4：Agent 实现

**Task 4.1 — 实现 liu_bei.py**

```python
# backend/agents/liu_bei.py
import json
from engines.llm_engine import LLMEngine

SYSTEM = """
你是刘备，专职小说文本的分镜切分。将输入文本切分为若干"句区"，每个句区是一个画面单元。

切分原则：
1. 每个句区约 30~120 字，对应一个独立视觉画面
2. 对话与旁白尽量不混合在同一句区
3. 相同场景的连续句区使用相同 scene_id（如 "s001"）
4. emotion_primary 从以下选择：悲痛、紧张、欢快、平静、愤怒、恐惧、温柔、震撼
5. emotion_intensity 为 0.0~1.0
6. characters_present 填写出现的角色姓名列表
7. estimated_duration_s 为估算朗读秒数

严格返回如下 JSON，不要有任何其他文字：
{
  "zones": [
    {
      "text": "...",
      "start_char_offset": 0,
      "end_char_offset": 50,
      "scene_id": "s001",
      "emotion_primary": "平静",
      "emotion_intensity": 0.5,
      "characters_present": ["角色名"],
      "estimated_duration_s": 5.0
    }
  ],
  "dedup_boundary_start": 0
}
"""

async def run(llm: LLMEngine, payload: dict) -> dict:
    user_msg = f"""
当前文本块：
{payload['block_text']}

前置上下文：
{payload.get('overlap_prev', '')}

后置上下文：
{payload.get('overlap_next', '')}
"""
    return await llm.complete_json(
        [{"role": "user", "content": user_msg}],
        system=SYSTEM
    )
```

**Task 4.2 — 实现 xiao_ming.py**

```python
# backend/agents/xiao_ming.py
from engines.llm_engine import LLMEngine

SYSTEM = """
你是小明，从小说描述中提取角色信息并生成图像 Prompt。

输出格式（严格 JSON，无其他文字）：
{
  "personality_tags": ["标签1", "标签2"],
  "color_tendency": "暖色系，赤红与金黄",
  "appearance_summary": "简洁的外貌总结",
  "trigger_words": ["trigger1", "trigger2"],
  "three_view_prompts": {
    "front": {"positive": "英文逗号分隔的正向标签", "negative": "英文负向标签"},
    "side":  {"positive": "...", "negative": "..."},
    "back":  {"positive": "...", "negative": "..."}
  }
}
"""

async def run(llm: LLMEngine, payload: dict) -> dict:
    user_msg = f"角色名：{payload['character_name']}\n\n原始描述：\n{payload['raw_description']}"
    return await llm.complete_json(
        [{"role": "user", "content": user_msg}],
        system=SYSTEM
    )
```

**Task 4.3 — 实现 xiao_qiao.py**

```python
# backend/agents/xiao_qiao.py
from engines.llm_engine import LLMEngine

SYSTEM = """
你是小乔，将小说句区信息合成为场景图像生成 Prompt。

规则：
1. positive 顺序：主体角色 → 动作表情 → 场景背景 → 光线氛围 → 画风
2. emotion_intensity > 0.7 时加入强烈光影词汇（如 dramatic lighting, intense shadows）
3. 将角色 trigger_words 放在 positive 最前面

输出格式（严格 JSON）：
{
  "positive": "英文逗号分隔的正向标签",
  "negative": "英文逗号分隔的负向标签",
  "reference_image_paths": []
}
"""

async def run(llm: LLMEngine, payload: dict) -> dict:
    chars_info = "\n".join(
        f"- {c['name']}: trigger={c['trigger_words']}, 外貌={c['appearance_summary']}"
        for c in payload.get("character_variants", [])
    )
    user_msg = f"""
句区文本：{payload['zone_text']}
情绪：{payload['emotion_primary']}（强度 {payload['emotion_intensity']}）
场景上下文：{payload.get('scene_context', '')}
出现角色：
{chars_info}
"""
    return await llm.complete_json(
        [{"role": "user", "content": user_msg}],
        system=SYSTEM
    )
```

---

### Phase 5：FastAPI 主程序与路由

**Task 5.1 — 实现 main.py**

```python
# backend/main.py
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from services.task_runner import get_runner
from routers import projects, chapters, zones, characters, sse

app = FastAPI(title="NovaManga API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router,   prefix="/api")
app.include_router(chapters.router,   prefix="/api")
app.include_router(zones.router,      prefix="/api")
app.include_router(characters.router, prefix="/api")
app.include_router(sse.router,        prefix="/api")

# 静态文件：前端 build 和项目资产
app.mount("/assets", StaticFiles(directory="/"), name="assets")

@app.on_event("startup")
async def startup():
    # 启动时为已有项目恢复 TaskRunner
    from db.global_db import list_projects
    for p in list_projects():
        runner = get_runner(p["path"])
        asyncio.create_task(runner.start())

@app.get("/health")
async def health():
    return {"status": "ok"}
```

**Task 5.2 — 实现各路由**

```python
# backend/routers/projects.py
import asyncio
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import global_db, project_db
from services.task_runner import get_runner

router = APIRouter()

class CreateProjectReq(BaseModel):
    name: str
    path: str   # 用户选择的目录绝对路径

@router.post("/projects")
async def create_project(req: CreateProjectReq):
    p = global_db.create_project(req.name, req.path)
    # 初始化 project.db
    project_db.get_conn(req.path).close()
    # 启动 TaskRunner
    runner = get_runner(req.path)
    asyncio.create_task(runner.start())
    return p

@router.get("/projects")
async def list_projects():
    return global_db.list_projects()

@router.get("/projects/{pid}")
async def get_project(pid: str):
    p = global_db.get_project(pid)
    if not p:
        raise HTTPException(404)
    return p
```

```python
# backend/routers/chapters.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import global_db, project_db
from services.task_runner import get_runner

router = APIRouter()

class CreateChapterReq(BaseModel):
    title: str
    order_index: int = 0

class UpdateChapterReq(BaseModel):
    title: str | None = None
    raw_text: str | None = None
    order_index: int | None = None

@router.post("/projects/{pid}/chapters")
async def create_chapter(pid: str, req: CreateChapterReq):
    p = global_db.get_project(pid)
    if not p:
        raise HTTPException(404)
    return project_db.create_chapter(p["path"], pid, req.title, req.order_index)

@router.get("/projects/{pid}/chapters")
async def list_chapters(pid: str):
    p = global_db.get_project(pid)
    if not p:
        raise HTTPException(404)
    return project_db.list_chapters(p["path"])

@router.put("/chapters/{cid}")
async def update_chapter(cid: str, req: UpdateChapterReq, project_path: str):
    # project_path 作为 query param 传入（临时方案，原型阶段可接受）
    kwargs = {k: v for k, v in req.dict().items() if v is not None}
    return project_db.update_chapter(project_path, cid, **kwargs)

@router.post("/chapters/{cid}/parse")
async def parse_chapter(cid: str, project_path: str):
    """触发刘备 Agent，按 Block 分块入队"""
    chapter = project_db.get_chapter(project_path, cid)
    if not chapter:
        raise HTTPException(404)

    raw_text = chapter["raw_text"]
    if not raw_text.strip():
        raise HTTPException(400, "章节内容为空")

    # 按自然段切分为 ~1000 字的 Block
    blocks    = _split_blocks(raw_text, max_chars=1000)
    task_ids  = []
    base_order = 0

    for i, (block_text, base_offset) in enumerate(blocks):
        prev_text = blocks[i - 1][0][-100:] if i > 0 else ""
        next_text = blocks[i + 1][0][:100] if i < len(blocks) - 1 else ""

        task = project_db.enqueue_task(
            project_path, "liu_bei_parse",
            {
                "chapter_id": cid,
                "block_text": block_text,
                "overlap_prev": prev_text,
                "overlap_next": next_text,
                "base_offset": base_offset,
                "base_order": base_order,
            },
            reference_id=cid,
            reference_type="chapter"
        )
        task_ids.append(task["id"])
        base_order += 50   # 预留足够的 order_index 间隔

    project_db.update_chapter(project_path, cid, parse_status="processing")
    return {"task_ids": task_ids}

def _split_blocks(text: str, max_chars: int) -> list[tuple[str, int]]:
    """返回 [(block_text, start_offset), ...]"""
    paragraphs = text.split("\n")
    blocks, current, offset, current_offset = [], [], 0, 0

    for para in paragraphs:
        if sum(len(p) for p in current) + len(para) > max_chars and current:
            block_text = "\n".join(current)
            blocks.append((block_text, current_offset))
            current_offset = offset
            current = []
        current.append(para)
        offset += len(para) + 1  # +1 for \n

    if current:
        blocks.append(("\n".join(current), current_offset))
    return blocks
```

```python
# backend/routers/sse.py
import asyncio, json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from services.sse_manager import sse_manager
import uuid

router = APIRouter()

@router.get("/sse/subscribe")
async def subscribe(reference_ids: str):
    """
    reference_ids: 逗号分隔的 ID 列表
    返回 Server-Sent Events 流
    """
    rid_list  = [r.strip() for r in reference_ids.split(",") if r.strip()]
    client_id = str(uuid.uuid4())
    queues    = sse_manager.subscribe(client_id, rid_list)

    async def event_stream():
        try:
            yield "data: {\"type\":\"connected\"}\n\n"
            while True:
                # 轮询所有订阅队列
                for rid, q in queues.items():
                    try:
                        event = q.get_nowait()
                        event["reference_id"] = rid
                        yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
                    except asyncio.QueueEmpty:
                        pass
                await asyncio.sleep(0.1)
        finally:
            sse_manager.unsubscribe(client_id, rid_list)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )
```

---

### Phase 6：前端脚手架

**Task 6.1 — 初始化前端**

```bash
cd novamanga
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install zustand axios react-router-dom
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

**Task 6.2 — 实现 API 客户端**

```typescript
// frontend/src/api/client.ts
import axios from "axios";

const api = axios.create({ baseURL: "http://localhost:8000/api" });

export const projectsAPI = {
  list:   ()              => api.get("/projects").then(r => r.data),
  create: (name: string, path: string) =>
    api.post("/projects", { name, path }).then(r => r.data),
  get:    (pid: string)   => api.get(`/projects/${pid}`).then(r => r.data),
};

export const chaptersAPI = {
  list:   (pid: string, projectPath: string) =>
    api.get(`/projects/${pid}/chapters`, { params: { project_path: projectPath } }).then(r => r.data),
  create: (pid: string, title: string, orderIndex = 0) =>
    api.post(`/projects/${pid}/chapters`, { title, order_index: orderIndex }).then(r => r.data),
  update: (cid: string, projectPath: string, data: Record<string, unknown>) =>
    api.put(`/chapters/${cid}`, data, { params: { project_path: projectPath } }).then(r => r.data),
  parse:  (cid: string, projectPath: string) =>
    api.post(`/chapters/${cid}/parse`, null, { params: { project_path: projectPath } }).then(r => r.data),
  zones:  (cid: string, projectPath: string) =>
    api.get(`/chapters/${cid}/zones`, { params: { project_path: projectPath } }).then(r => r.data),
};

export const zonesAPI = {
  update:          (zid: string, projectPath: string, data: Record<string, unknown>) =>
    api.put(`/zones/${zid}`, data, { params: { project_path: projectPath } }).then(r => r.data),
  generatePrompt:  (zid: string, projectPath: string) =>
    api.post(`/zones/${zid}/prompt/generate`, null, { params: { project_path: projectPath } }).then(r => r.data),
  generateImage:   (zid: string, projectPath: string, promptData?: Record<string, unknown>) =>
    api.post(`/zones/${zid}/image/generate`, promptData || {}, { params: { project_path: projectPath } }).then(r => r.data),
};

export const charactersAPI = {
  list:   (pid: string, projectPath: string) =>
    api.get(`/projects/${pid}/characters`, { params: { project_path: projectPath } }).then(r => r.data),
  create: (pid: string, projectPath: string, name: string, rawDescription: string) =>
    api.post(`/projects/${pid}/characters`, { name, raw_description: rawDescription }, {
      params: { project_path: projectPath }
    }).then(r => r.data),
};

export default api;
```

**Task 6.3 — 实现 useSSE Hook**

```typescript
// frontend/src/hooks/useSSE.ts
import { useEffect, useRef } from "react";
import { useTaskStore } from "../stores/taskStore";

export function useSSE(referenceIds: string[]) {
  const esRef = useRef<EventSource | null>(null);
  const { handleEvent } = useTaskStore();

  useEffect(() => {
    if (referenceIds.length === 0) return;
    const ids = referenceIds.join(",");
    const es  = new EventSource(
      `http://localhost:8000/api/sse/subscribe?reference_ids=${encodeURIComponent(ids)}`
    );
    esRef.current = es;

    es.onmessage = (e) => {
      try {
        const event = JSON.parse(e.data);
        if (event.type !== "connected") {
          handleEvent(event);
        }
      } catch (_) {}
    };

    es.onerror = () => {
      // 浏览器会自动重连，无需手动处理
    };

    return () => {
      es.close();
      esRef.current = null;
    };
  }, [referenceIds.join(",")]);
}
```

**Task 6.4 — 实现 Zustand Stores**

```typescript
// frontend/src/stores/taskStore.ts
import { create } from "zustand";

export interface TaskEvent {
  task_id:      string;
  type:         string;
  status:       "processing" | "completed" | "failed";
  reference_id: string;
  result?:      unknown;
  error?:       string;
}

interface TaskStore {
  tasks:       Record<string, TaskEvent>;   // key = task_id
  byReference: Record<string, string[]>;    // reference_id → task_id[]
  handleEvent: (event: TaskEvent) => void;
  getStatus:   (referenceId: string) => "idle" | "processing" | "completed" | "failed";
}

export const useTaskStore = create<TaskStore>((set, get) => ({
  tasks:       {},
  byReference: {},

  handleEvent: (event) => set((state) => {
    const byRef = { ...state.byReference };
    if (!byRef[event.reference_id]) byRef[event.reference_id] = [];
    if (!byRef[event.reference_id].includes(event.task_id)) {
      byRef[event.reference_id] = [...byRef[event.reference_id], event.task_id];
    }
    return {
      tasks:       { ...state.tasks, [event.task_id]: event },
      byReference: byRef,
    };
  }),

  getStatus: (referenceId) => {
    const { tasks, byReference } = get();
    const taskIds = byReference[referenceId] || [];
    if (taskIds.length === 0) return "idle";
    const statuses = taskIds.map(id => tasks[id]?.status);
    if (statuses.some(s => s === "processing"))  return "processing";
    if (statuses.some(s => s === "failed"))      return "failed";
    if (statuses.every(s => s === "completed"))  return "completed";
    return "idle";
  },
}));
```

---

### Phase 7：前端核心页面

**Task 7.1 — ProjectList.tsx（首页）**

实现项目卡片列表，右上角"新建项目"按钮弹出对话框，填写项目名和本地目录路径（文本输入，不是文件选择器，原型阶段），提交后跳转到 ProjectDashboard。

**Task 7.2 — ChapterEditor.tsx（胶片轨道）**

胶片轨道的卡片宽度由 `duration_ms` 决定，最小 `w-20`（对应 2 秒），每 100ms 增加 1px（用行内 style 实现）。卡片颜色深度由 `emotion_intensity` 驱动：0.2 以下用 `bg-blue-100`，0.5 以上用 `bg-blue-400`，0.8 以上用 `bg-blue-700`。卡片边框状态：无资产虚线、仅音频点划线、仅图片实线浅色、两者齐全实线彩色。

**Task 7.3 — ZoneEditor.tsx（工作台）**

布局：顶部文本区（只读，高度固定），下方左右各 50%。左侧音频区含情感参数滑块（Speed/Pitch/Intensity），右侧图片区含 Prompt 文本框（小乔生成后可手动编辑）。两侧均有"生成"按钮，点击后按钮变为 Spinner，通过 `useSSE` 监听该 `zone_id` 的任务状态，完成后自动刷新内容。

**Task 7.4 — Timeline.tsx（全局预览）**

所有章节的句区横向排列，按 `order_index` 排序，缩略图模式（固定宽高比卡片）。右侧固定面板为播放器，按顺序播放图片（Ken Burns 用 CSS `transition: transform 5s ease`）和音频，图片展示时长等于对应 `duration_ms`。

---

### Phase 8：一键启动

```bash
# start.sh
#!/bin/bash
echo "🚀 启动 NovaManga..."

# 后端
cd backend
pip install -r requirements.txt -q
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "✅ 后端启动 PID=$BACKEND_PID"

# 前端
cd ../frontend
npm install -q
npm run dev &
FRONTEND_PID=$!
echo "✅ 前端启动 PID=$FRONTEND_PID"

echo ""
echo "📖 NovaManga 已启动"
echo "   前端: http://localhost:5173"
echo "   后端: http://localhost:8000"
echo "   API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
```

---

## 六、Claude Code 执行顺序汇总

| 步骤 | 任务 | 验证方式 |
|------|------|---------|
| 1 | 创建目录结构，写 requirements.txt | `ls` 确认结构 |
| 2 | 实现 LLMEngine | `python test_llm.py` 返回 JSON |
| 3 | 实现 NanaBananaEngine | `python test_nanobanana.py` 生成图片 |
| 4 | 实现 schema.py + global_db.py + project_db.py | `python -c "from db import global_db; print(global_db.list_projects())"` |
| 5 | 实现 SSEManager + TaskRunner + task_handlers.py | 单独 `python -c "..."` 测试入队和轮询 |
| 6 | 实现三个 Agent（liu_bei/xiao_ming/xiao_qiao） | 直接 `asyncio.run(agent.run(...))` |
| 7 | 实现所有 routers + main.py | `uvicorn main:app` + curl 测试每条路由 |
| 8 | 前端脚手架 + api/client.ts + stores + hooks | `npm run dev` 能访问首页 |
| 9 | 实现 ProjectList + ProjectDashboard | 能创建项目和章节 |
| 10 | 实现 ChapterEditor（胶片轨道）| 触发刘备，看到句区卡片渲染 |
| 11 | 实现 ZoneEditor | 生成按钮 → Spinner → 结果展示 |
| 12 | 实现 CharacterAssets + Timeline | 完整创作循环闭合 |
| 13 | 整合 start.sh，端到端联调 | 完整走一遍：建项目→导文本→检测→生图→预览 |

每一步在进入下一步之前必须可以独立运行，没有"稍后联调"的侥幸，出错在当步解决。