# Pictory 实现计划

## 概述
将小说转换为动态漫画的Web应用，分3个阶段实现核心功能。

## Phase 1: 基础架构与核心流程

### 1.1 后端基础搭建
**目标**: 搭建FastAPI + SQLite基础框架

**文件**:
- `backend/main.py` - FastAPI入口
- `backend/database.py` - SQLite配置
- `backend/models.py` - SQLAlchemy模型
- `backend/requirements.txt` - Python依赖

**实现**:
1. 创建FastAPI应用，配置CORS
2. 配置SQLite数据库连接
3. 定义4个数据模型：Project, Chapter, Segment, Character
4. 创建数据库表

**验证**: 启动后端，访问 http://localhost:8000/docs 查看API文档

### 1.2 项目管理API
**目标**: 实现项目CRUD接口

**文件**:
- `backend/routers/projects.py`

**接口**:
- POST /api/projects - 创建项目
- GET /api/projects - 获取项目列表
- GET /api/projects/{id} - 获取项目详情
- DELETE /api/projects/{id} - 删除项目

**验证**: 使用Playwright测试API

### 1.3 章节管理API
**目标**: 实现章节CRUD接口

**文件**:
- `backend/routers/chapters.py`

**接口**:
- POST /api/chapters - 创建章节
- GET /api/chapters?project_id={id} - 获取章节列表
- PUT /api/chapters/{id} - 更新章节
- DELETE /api/chapters/{id} - 删除章节

**验证**: 使用Playwright测试API

### 1.4 LLM引擎实现
**目标**: 封装LLM调用

**文件**:
- `backend/engines/llm_engine.py`
- `backend/config.json` - 配置文件

**实现**:
```python
class LLMEngine:
    def __init__(self, model, api_key, base_url)
    def chat(self, messages) -> str
```

**验证**: 单元测试调用

### 1.5 刘备Agent实现
**目标**: 实现句区切分Agent

**文件**:
- `backend/engines/agents/liubei.py`

**实现**:
- 定义system prompt
- 调用LLM进行场景分析
- 返回句区列表JSON

**验证**: 输入测试章节，检查切分结果

### 1.6 句区切分API
**目标**: 实现句区相关接口

**文件**:
- `backend/routers/segments.py`

**接口**:
- POST /api/segments/split - 切分句区
- GET /api/segments?chapter_id={id} - 获取句区列表
- PUT /api/segments/{id} - 更新句区
- POST /api/segments/merge - 合并句区
- PUT /api/segments/reorder - 重排序

**验证**: 使用Playwright测试切分流程

## Phase 2: AI生成功能

### 2.1 CosyVoice引擎实现
**目标**: 封装TTS调用，支持按需加载

**文件**:
- `backend/engines/tts_engine.py`

**实现**:
```python
class CosyVoiceEngine:
    def load() - 加载模型
    def unload() - 卸载模型
    def generate(text, ref_audio, instruct) -> bytes
```

**验证**: 生成测试音频

### 2.2 音频生成API
**目标**: 实现音频生成接口

**文件**:
- `backend/routers/segments.py` (扩展)

**接口**:
- POST /api/segments/{id}/audio - 生成音频

**实现**:
1. 接收句区ID和说书人音频路径
2. 调用CosyVoice生成
3. 保存音频文件
4. 更新数据库路径

**验证**: 使用Playwright测试生成流程

### 2.3 NanoBanana引擎实现
**目标**: 封装图片生成API

**文件**:
- `backend/engines/image_engine.py`

**实现**:
```python
class NanoBananaEngine:
    def generate(prompt, ref_image_path) -> bytes
    def merge_character_images(image_paths, names) -> bytes
```

**验证**: 生成测试图片

### 2.4 小乔Agent实现
**目标**: 实现图片prompt生成

**文件**:
- `backend/engines/agents/xiaoqiao.py`

**实现**:
- 定义system prompt
- 根据句区内容生成场景描述
- 如有角色参考图，补充角色信息

**验证**: 输入测试句区，检查prompt质量

### 2.5 图片生成API
**目标**: 实现图片生成接口

**文件**:
- `backend/routers/segments.py` (扩展)

**接口**:
- POST /api/segments/{id}/prompt - 生成prompt
- POST /api/segments/{id}/image - 生成图片

**验证**: 使用Playwright测试生成流程

### 2.6 角色资产管理
**目标**: 实现角色管理功能

**文件**:
- `backend/routers/characters.py`
- `backend/engines/agents/xiaoming.py`

**接口**:
- POST /api/characters - 创建角色
- GET /api/characters?project_id={id} - 获取角色列表
- POST /api/characters/{id}/generate - 生成参考图
- POST /api/characters/narrator/audio - 上传说书人音频

**验证**: 使用Playwright测试角色创建流程

## Phase 3: 前端实现

### 3.1 前端基础搭建
**目标**: 创建Vue 3项目

**文件**:
- `frontend/package.json`
- `frontend/vite.config.js`
- `frontend/src/main.js`
- `frontend/src/App.vue`

**实现**:
1. 初始化Vite + Vue 3项目
2. 安装Element Plus
3. 配置Pinia和Vue Router
4. 配置API基础URL

**验证**: 启动前端，访问 http://localhost:5173

### 3.2 项目列表页
**目标**: 实现项目管理界面

**文件**:
- `frontend/src/views/ProjectList.vue`
- `frontend/src/api/projects.js`

**功能**:
- 显示项目卡片列表
- 新建项目对话框
- 删除项目确认
- 点击进入章节列表

**验证**: 使用Playwright测试UI交互

### 3.3 章节编辑页
**目标**: 实现章节编辑和句区切分

**文件**:
- `frontend/src/views/ChapterEdit.vue`
- `frontend/src/api/chapters.js`
- `frontend/src/api/segments.js`

**布局**:
- 左侧：文本输入框
- 右侧：句区列表（可滚动）
- 底部：开始检测按钮

**功能**:
- 输入章节内容
- 调用刘备Agent切分
- 显示句区列表
- 支持合并/拆分/排序
- 双击进入句区编辑

**验证**: 使用Playwright测试完整流程

### 3.4 句区编辑页
**目标**: 实现音频和图片生成

**文件**:
- `frontend/src/views/SegmentEdit.vue`

**布局**:
- 顶部：句区文本
- 音频区：生成按钮 + 进度 + 播放器
- 图片区：生成prompt + 选择角色 + 生成 + 预览

**功能**:
- 生成音频（显示进度）
- 播放音频
- 生成图片prompt
- 选择角色参考图
- 生成图片
- 预览图片

**验证**: 使用Playwright测试生成流程

### 3.5 角色资产页
**目标**: 实现角色管理界面

**文件**:
- `frontend/src/views/CharacterAssets.vue`
- `frontend/src/api/characters.js`

**布局**:
- 瀑布流显示角色卡片
- 说书人卡片（固定）
- 新建角色按钮

**功能**:
- 显示角色列表
- 上传说书人音频
- 新建角色（输入描述 → 生成）
- 选择角色（用于句区编辑）

**验证**: 使用Playwright测试角色创建

### 3.6 阅读器页
**目标**: 实现图文联动播放

**文件**:
- `frontend/src/views/Reader.vue`

**布局**:
- 图片展示区
- 音频播放控制
- 上一句/下一句按钮

**功能**:
- 显示当前句区图片
- 播放当前句区音频
- 切换句区

**验证**: 使用Playwright测试播放流程

## 关键技术点

### 文件上传处理
- 说书人音频上传
- 角色参考图上传
- 保存到 `data/assets/` 目录

### 进度显示
- 音频生成进度（轮询或WebSocket）
- 图片生成进度

### 错误处理
- API调用失败提示
- 模型加载失败降级
- 文件上传失败重试

## 验证策略

每个功能完成后：
1. 使用Playwright MCP自动测试UI交互
2. 验证API返回数据正确性
3. 检查文件正确保存
4. 测试错误场景处理

## 依赖关系

```
Phase 1 → Phase 2 → Phase 3
  ↓         ↓         ↓
基础架构  AI引擎    前端UI
```

每个Phase内部按顺序实现，Phase之间有依赖关系。
