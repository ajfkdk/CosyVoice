# 小说自动配插画系统

## 项目结构

```
小说配插画/
├── main.py            # 主流程入口，配置区在顶部
├── llm_engine.py      # LLM 引擎（基于 Poe OpenAI 兼容 API）
├── text_splitter.py   # 文本语义切分（AI 自动识别分镜节点）
├── scene_describer.py # 场景描述生成（注入角色卡 + 美术风格）
├── illustrator.py     # Nanobanana 绘图封装（复用 ../NanoBanana/）
└── output/            # 输出目录（自动创建）
    ├── scene_01.png
    ├── scene_01_desc.txt
    └── ...
```

## 核心流程

```
小说文本
   ↓
[text_splitter]  LLM 语义切分 → 多个画面单元（含场景标签）
   ↓
[scene_describer] 逐场景生成插画描述（注入角色卡 + 美术风格）
   ↓
[illustrator]    调用 Nanobanana 生成插图
   ↓
output/ 目录（每场景一张图 + 一份描述文本）
```

## 使用方法

1. 打开 `main.py`，修改配置区：
   - `LLM_API_KEY`：填入你的 Poe API Key
   - `GLOBAL_SETTINGS`：填入你的角色设定和美术风格
   - `SAMPLE_NOVEL`：替换为你的小说文本

2. 运行：
   ```bash
   python main.py
   ```

## 依赖

```
openai
requests
```
