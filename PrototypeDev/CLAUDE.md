# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个基于AI的小说自动配插画系统，包含两个核心功能：
1. **小说配插画** (`小说配插画/`) - 将小说文本自动切分场景并生成对应插画
2. **1Prompt1Story** (`小说配插画/main_grid.py`) - 生成16宫格故事板
3. **NanoBanana引擎** (`NanoBanana/`) - 图像生成引擎封装

## 运行命令

### 小说配插画系统
```bash
cd 小说配插画
python main.py
```

### 16宫格故事板生成
```bash
cd 小说配插画
python main_grid.py
```

### 生成角色参考图
```bash
cd NanoBanana
python generate_character.py
```

## 核心架构

### 小说配插画流程 (main.py)
```
小说文本
  → [text_splitter] LLM语义切分为多个画面单元
  → [scene_describer] 生成插画描述（注入角色卡+美术风格）
  → [illustrator] 调用Nanobanana生成插图
  → output/ 目录输出
```

**关键特性：**
- 自动检测场景中出现的角色，加载对应参考图
- 将上一场景图作为参考图传入，保持视觉连贯性
- 支持最多14张参考图同时输入
- 429限流自动重试机制（指数退避）

### 1Prompt1Story流程 (main_grid.py)
```
小说文本
  → [story_grid_generator] 提炼16个关键画面为单个prompt
  → [NanobananaEngine] 一次性生成16宫格图
  → output_grid/ 目录输出
```

### 模块职责

- **llm_engine.py** - LLM引擎封装，基于Poe OpenAI兼容API
- **text_splitter.py** - AI语义切分，按场景/时间/人物/情绪转折点切分
- **scene_describer.py** - 场景描述生成，融合角色卡和美术风格
- **illustrator.py** - Nanobanana绘图封装，含重试逻辑
- **nanobanana_engine.py** - 图像生成API封装（528ai.cc）
- **reference_manager.py** - 角色参考图管理
- **story_grid_generator.py** - 16宫格prompt生成

## 配置说明

### API配置
所有API密钥和模型配置硬编码在各main文件顶部的配置区：
- `LLM_MODEL` - LLM模型名称（如 "gpt-5.4-mini"）
- `LLM_API_KEY` - Poe API密钥
- `NanoTOKEN` - Nanobanana API密钥（在nanobanana_engine.py中）

### 角色配置
在main.py中配置：
```python
CHARACTER_IMAGES = {
    "角色名": "参考图路径",
}

GLOBAL_SETTINGS = {
    "character_card": "角色外貌、性格、服装描述",
    "art_style": "美术风格描述"
}
```

### 美术风格
- **小说配插画**: 京都动画（Kyoto Animation）风格
- **16宫格**: 宫崎骏手绘风格
- 画面比例: 16:9横屏，2K分辨率

## 重要约定

1. **参考图处理**: 参考图中的白色分隔条、文字标签不应被画入最终插画
2. **角色一致性**: 通过角色卡和参考图保证跨场景角色外貌一致
3. **场景连贯性**: 将上一场景图作为参考传入下一场景
4. **切分原则**: 场景变化、时间跳跃、人物变化、情绪转折点必须切分
5. **限流处理**: 遇到429错误自动重试，最多3次，指数退避

## 依赖
```
openai
requests
Pillow
```

## 输出目录
- `output/` - 小说配插画输出（scene_XX.png + scene_XX_desc.txt）
- `output_grid/` - 16宫格输出（story_grid_16.png + story_prompt.txt）
