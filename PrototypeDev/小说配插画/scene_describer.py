from llm_engine import LLMEngine


DESCRIBE_SYSTEM = """你是一个专业的插画导演，擅长将小说场景转化为详细的插画描述。

你的描述将直接用于 AI 绘画生成插图，描述需要：
1. 自然语言描述，清晰具体，不需要 Stable Diffusion 风格的关键词堆砌
2. 描述视角：明确是全景/中景/近景/特写
3. 描述内容包含：人物（外貌、表情、姿势、服装）、环境（地点、光线、天气、氛围）、构图重点
4. 自动融入「全局设定」中的角色外貌，保证跨图一致性
5. 描述长度：100-200字，精炼但完整
6. 美术风格必须是京都动画（Kyoto Animation）风格：细腻柔和的手绘线条，色彩饱和度适中偏暖，
   光影层次丰富，人物五官精致唯美，背景环境写实精细，整体画面具有电影质感和情绪氛围
7. 画面比例：16:9横屏构图，适合电影级叙事画面

⚠️ 关键要求：
- 如果提供了参考图，参考图中的白色分隔条、文字标签（如"角色参考：XXX"、"上一场景参考"）仅用于标注说明，绝对不要将这些标注元素画入最终插画
- 只参考图片内容本身（人物外貌、场景构图、色调氛围），不要复制参考图的排版结构

只输出插画描述文字，不要编号、不要标题、不要额外说明。
"""


def describe_scene(llm: LLMEngine, scene: dict, global_settings: dict) -> str:
    character_card = global_settings.get("character_card", "")
    art_style = global_settings.get("art_style", "")

    prompt = f"""请根据以下信息，生成一段插画描述：

【全局角色设定】
{character_card}

【美术风格】
京都动画（Kyoto Animation）风格。{art_style}

【当前场景原文】
{scene['text']}

【场景标签】
{scene['scene_tag']}

请生成适合 AI 绘画的插画描述。"""

    description = llm.chat(prompt, system=DESCRIBE_SYSTEM)
    return description.strip()
