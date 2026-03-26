import json
from llm_engine import LLMEngine


SPLIT_SYSTEM = """你是一个专业的小说分镜师。
你的任务是分析小说文本，将其切分为适合配插图的「画面单元」。

切分原则（参考漫画分镜理论）：
1. 场景变化（地点切换）→ 必须切分
2. 时间跳跃（时间推移明显）→ 必须切分
3. 人物变化（新人物登场或退场）→ 建议切分
4. 情绪/动作转折点（高潮、冲突、关键行动）→ 必须切分
5. 过于短小的段落（少于30字）→ 合并到相邻单元

输出格式必须是合法的 JSON 数组，每个元素包含：
- index: 序号（从1开始）
- text: 该画面单元的原文内容
- scene_tag: 简短场景标签（如"山顶对峙"、"客栈夜谈"）

只输出 JSON，不要任何额外说明。
"""


def split_novel(llm: LLMEngine, novel_text: str) -> list[dict]:
    prompt = f"请对以下小说文本进行分镜切分：\n\n{novel_text}"
    raw = llm.chat(prompt, system=SPLIT_SYSTEM)

    # 提取 JSON 部分（防止模型输出多余内容）
    start = raw.find("[")
    end = raw.rfind("]") + 1
    if start == -1 or end == 0:
        raise ValueError(f"LLM 未返回合法 JSON，原始内容：\n{raw}")

    scenes = json.loads(raw[start:end])
    return scenes
