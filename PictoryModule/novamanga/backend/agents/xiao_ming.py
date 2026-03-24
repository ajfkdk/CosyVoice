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
