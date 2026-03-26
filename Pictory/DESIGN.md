# Pictory 小说动态漫画系统 - 设计文档

## 1. 系统概述

将小说文本转换为图文动态漫画的桌面应用，支持章节管理、智能句区切分、AI配音和AI绘图。

## 2. 技术栈

### 前端
- Vue 3 + Vite
- Element Plus (UI组件库)
- Pinia (状态管理)
- Vue Router (路由)

### 后端
- FastAPI (Python Web框架)
- SQLite (数据库)
- SQLAlchemy (ORM)

### 部署
- Web应用（浏览器访问）

### AI引擎
- CosyVoice3 (TTS语音合成，按需加载)
- NanoBanana (图像生成，API调用)
- LLM引擎 (文本处理，API调用)

## 3. 核心功能模块

### 3.1 项目管理
- 创建/删除项目（一个项目=一本小说）
- 项目列表展示
- 项目配置（说书人音频等）

### 3.2 章节管理
- 创建/编辑/删除章节
- 章节列表
- 章节内容输入

### 3.3 句区切分（刘备Agent）
- 输入：章节文本
- 处理：LLM语义分析场景切换
- 规则：同场景合并，超300字自动切分
- 输出：句区列表
- 支持：合并、拆分、拖拽排序

### 3.4 人物资产管理
- 角色列表（含说书人）
- 角色创建：描述→小明Agent→NanoBanana生成三视图
- 说书人：上传参考音频
- 存储：本地文件夹结构

### 3.5 句区编辑
- 音频生成：CosyVoice + 说书人音色
- 图片生成：小乔Agent生成prompt → 选择角色参考图 → 拼接 → NanoBanana生成
- 预览播放

### 3.6 阅读器
- 图文联动播放
- 音频同步
- 交互控制

## 4. 数据库设计

### 4.1 表结构

```sql
-- 项目表
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- 章节表
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    title TEXT,
    content TEXT,
    order_index INTEGER,
    created_at TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- 句区表
CREATE TABLE segments (
    id INTEGER PRIMARY KEY,
    chapter_id INTEGER,
    content TEXT NOT NULL,
    order_index INTEGER,
    audio_path TEXT,
    image_path TEXT,
    image_prompt TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (chapter_id) REFERENCES chapters(id)
);

-- 角色资产表
CREATE TABLE characters (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    name TEXT NOT NULL,
    description TEXT,
    reference_image_path TEXT,
    prompt TEXT,
    is_narrator BOOLEAN DEFAULT 0,
    narrator_audio_path TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

## 5. 目录结构

```
Pictory/
├── backend/                 # FastAPI后端
│   ├── main.py             # 入口
│   ├── models.py           # 数据模型
│   ├── database.py         # 数据库配置
│   ├── routers/            # API路由
│   │   ├── projects.py
│   │   ├── chapters.py
│   │   ├── segments.py
│   │   └── characters.py
│   └── engines/            # AI引擎
│       ├── llm_engine.py
│       ├── tts_engine.py
│       ├── image_engine.py
│       └── agents/
│           ├── liubei.py   # 句区切分
│           ├── xiaoqiao.py # 图片prompt
│           └── xiaoming.py # 角色分析
├── frontend/               # Vue前端
│   ├── src/
│   │   ├── views/         # 页面
│   │   │   ├── ProjectList.vue
│   │   │   ├── ChapterEdit.vue
│   │   │   ├── SegmentEdit.vue
│   │   │   ├── CharacterAssets.vue
│   │   │   └── Reader.vue
│   │   ├── components/    # 组件
│   │   ├── stores/        # Pinia状态
│   │   ├── router/        # 路由
│   │   └── api/           # API调用
│   └── package.json
├── data/                  # 数据目录
│   ├── pictory.db        # SQLite数据库
│   └── assets/           # 资源文件
│       ├── characters/   # 角色资产
│       ├── audio/        # 音频文件
│       └── images/       # 图片文件
└── requirements.txt      # Python依赖
```

## 6. API设计

### 6.1 项目相关
- POST /api/projects - 创建项目
- GET /api/projects - 获取项目列表
- DELETE /api/projects/{id} - 删除项目

### 6.2 章节相关
- POST /api/chapters - 创建章节
- GET /api/chapters?project_id={id} - 获取章节列表
- PUT /api/chapters/{id} - 更新章节
- DELETE /api/chapters/{id} - 删除章节

### 6.3 句区相关
- POST /api/segments/split - 调用刘备Agent切分句区
- GET /api/segments?chapter_id={id} - 获取句区列表
- PUT /api/segments/{id} - 更新句区
- POST /api/segments/merge - 合并句区
- POST /api/segments/reorder - 重排序
- POST /api/segments/{id}/audio - 生成音频
- POST /api/segments/{id}/image - 生成图片

### 6.4 角色资产相关
- POST /api/characters - 创建角色
- GET /api/characters?project_id={id} - 获取角色列表
- POST /api/characters/{id}/generate - 生成角色参考图
- POST /api/characters/narrator/audio - 上传说书人音频

## 7. AI引擎实现

### 7.1 LLM引擎
```python
class LLMEngine:
    def __init__(self, model: str, api_key: str):
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.poe.com/v1"
        )
        self.model = model

    def chat(self, messages: list) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        return response.choices[0].message.content
```

### 7.2 NanoBanana引擎
```python
class NanoBananaEngine:
    def __init__(self, api_key: str):
        self.api_url = "https://api.mmw.ink/v1/chat/completions"
        self.api_key = api_key
        self.model = "[A]gemini-3-pro-image-preview"

    def generate(self, prompt: str, ref_image_path: str = None) -> bytes:
        # 实现图片生成逻辑
        pass
```

### 7.3 CosyVoice引擎
```python
class CosyVoiceEngine:
    def __init__(self):
        self.model = None
        self.loaded = False

    def load(self):
        if not self.loaded:
            self.model = AutoModel(model_dir='pretrained_models/Fun-CosyVoice3-0.5B')
            self.loaded = True

    def unload(self):
        self.model = None
        self.loaded = False

    def generate(self, text: str, ref_audio: str, instruct: str = None) -> bytes:
        self.load()
        # 实现音频生成逻辑
        pass
```

## 8. Agent实现

### 8.1 刘备Agent（句区切分）
```python
LIUBEI_PROMPT = """你是句区切分专家刘备。
任务：将章节文本切分为合适的句区。
规则：
1. 同一场景的内容合并为一个句区
2. 场景判断依据：地点变化、时间跳跃、视角转换
3. 单个句区不超过300字，超过则切分
4. 输出JSON格式：[{"content": "句区内容", "scene": "场景描述"}]
"""

class LiubeiAgent:
    def __init__(self, llm_engine: LLMEngine):
        self.llm = llm_engine

    def split_segments(self, chapter_text: str) -> list:
        messages = [
            {"role": "system", "content": LIUBEI_PROMPT},
            {"role": "user", "content": chapter_text}
        ]
        result = self.llm.chat(messages)
        return json.loads(result)
```

### 8.2 小乔Agent（图片prompt生成）
```python
XIAOQIAO_PROMPT = """你是图片prompt生成专家小乔。
任务：为句区生成NanoBanana专用的图片生成prompt。
要求：
1. 描述场景、氛围、构图
2. 如果有参考图角色，说明"图中的{角色名}是主角"
3. 风格：漫画风格、动态感
4. 输出纯prompt文本
"""

class XiaoqiaoAgent:
    def __init__(self, llm_engine: LLMEngine):
        self.llm = llm_engine

    def generate_prompt(self, segment_text: str, characters: list = None) -> str:
        # 实现prompt生成
        pass
```

### 8.3 小明Agent（角色分析）
```python
XIAOMING_PROMPT = """你是角色分析专家小明。
任务：从角色描述中提取关键信息，生成NanoBanana三视图prompt。
输出格式：
{
  "name": "角色名",
  "appearance": "外貌特征",
  "clothing": "服装描述",
  "prompt": "三视图生成prompt"
}
"""

class XiaomingAgent:
    def __init__(self, llm_engine: LLMEngine):
        self.llm = llm_engine

    def analyze_character(self, description: str) -> dict:
        # 实现角色分析
        pass
```

## 9. 前端页面流程

### 9.1 项目列表页
- 显示所有项目卡片
- 点击"新建项目"弹窗输入名称
- 点击项目进入章节列表

### 9.2 章节列表页
- 显示章节列表
- 点击"创建章节"进入章节编辑页
- 点击章节进入句区列表

### 9.3 章节编辑页
- 左侧：文本输入框（半屏）
- 右侧：句区列表（可滚动）
- 点击"开始检测"调用刘备Agent
- 支持句区合并、拆分、排序
- 双击句区进入句区编辑页

### 9.4 句区编辑页
- 顶部：句区文本显示
- 音频区：生成按钮 + 进度条 + 播放器
- 图片区：生成prompt按钮 + 选择角色 + 生成按钮 + 预览

### 9.5 角色资产页
- 瀑布流显示角色卡片
- 说书人卡片（固定）：上传音频
- 角色卡片：图片 + 名字
- 新建角色：输入描述 → 生成

### 9.6 阅读器页
- 图片展示区
- 音频播放控制
- 上一句/下一句切换

## 10. 实现优先级

### Phase 1: 核心流程（MVP）
1. 项目/章节CRUD
2. 刘备Agent句区切分
3. 基础UI框架

### Phase 2: AI生成
4. CosyVoice音频生成
5. 小乔Agent + NanoBanana图片生成
6. 角色资产管理

### Phase 3: 完善功能
7. 句区编辑（合并/拆分/排序）
8. 阅读器
9. 部署优化

## 11. 技术难点

### 11.1 CosyVoice按需加载
- 问题：模型加载慢，占用内存大
- 方案：首次生成时加载，生成完成后延迟卸载（5分钟无操作）

### 11.2 多角色参考图拼接
- 问题：NanoBanana只支持单图上传
- 方案：PIL拼接多张图，添加角色名标注，压缩分辨率

### 11.3 句区切分准确性
- 问题：LLM切分可能不准确
- 方案：提供手动编辑功能（合并/拆分/排序）

## 12. 配置管理

创建 `config.json`:
```json
{
  "llm": {
    "model": "gpt-5.4-mini",
    "api_key": "YOUR_POE_API_KEY",
    "base_url": "https://api.poe.com/v1"
  },
  "nanobanana": {
    "model": "[A]gemini-3-pro-image-preview",
    "api_key": "sk-xxxx",
    "api_url": "https://api.mmw.ink/v1/chat/completions"
  },
  "cosyvoice": {
    "model_dir": "../pretrained_models/Fun-CosyVoice3-0.5B",
    "auto_unload_minutes": 5
  }
}
```
