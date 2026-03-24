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
        f"- {c['name']}: trigger={c.get('trigger_words', [])}, 外貌={c.get('appearance_summary', '')}"
        for c in payload.get("character_variants", [])
    )
    user_msg = f"""
句区文本：{payload['zone_text']}
情绪：{payload['emotion_primary']}（强度 {payload.get('emotion_intensity', 0.5)}）
场景上下文：{payload.get('scene_context', '')}
出现角色：
{chars_info}
"""
    return await llm.complete_json(
        [{"role": "user", "content": user_msg}],
        system=SYSTEM
    )
