"""
1Prompt1Story - 16宫格故事生成器
核心：一个prompt生成16个连贯场景，保持角色和风格一致性
"""
from llm_engine import LLMEngine


MIYAZAKI_SYSTEM = """你是京都动画社的灵魂画手，擅长将小说章节转化为16格连贯叙事画面。

关键要求：
1. 输出16个简洁的场景描述，每个场景1-2句话
2. 每个场景前用方括号标注出现的角色：[角色1，角色2]
3. 用"接着"、"然后"、"此时"等词串联，形成连贯故事流
4. 每个场景用句号分隔，保持简洁明确
5. 描述要具体可视化：人物动作、表情、环境、光线、构图
6. ⚠️ 重要：这是小说插画，画面中不要出现任何文字、字幕、对话框、标题

京都动画的美学原则：
- 细腻柔和的手绘线条，色彩饱和度适中偏暖
- 光影层次丰富，人物五官精致唯美
- 人物姿态和眼神传达细腻情绪
- 构图有空气感和留白，背景环境写实精细
- 画面具有电影质感和情绪氛围
- 镜头语言服务情绪：特写表现紧张，中景表现关系

输出格式示例：
[角色A，角色B]。[场景1简洁描述]。接着，[角色A]。[场景2]。然后，[角色B，角色C]。[场景3]。此时，[角色A]。[场景4]...

每个场景控制在20-40字，总共16个场景。
"""


def generate_story_prompt(llm: LLMEngine, novel_text: str, character_card: str,
                          art_style: str) -> str:
    """
    生成1Prompt1Story的连贯叙事prompt
    """
    user_prompt = f"""请将以下小说章节转化为16格连贯叙事画面：

【角色设定】
{character_card}

【美术风格】
{art_style}

【小说原文】
{novel_text}

请用连贯的叙述性语言输出16个场景，形成一个完整的故事流。
格式：[角色身份]。[场景1]。接着，[场景2]。然后，[场景3]...
"""

    story_prompt = llm.chat(user_prompt, system=MIYAZAKI_SYSTEM)

    # 添加16宫格布局要求
    final_prompt = f"""{story_prompt.strip()}

⚠️ 重要布局要求：
- 生成4x4标准网格布局（16个格子）
- 每个格子大小完全相等
- 格子之间用纯黑色分隔线（RGB: 0,0,0），线宽3-5像素
- 分隔线必须笔直、清晰、连贯
- 整体画面比例16:9"""

    return final_prompt


def split_story_scenes(story_prompt: str) -> list[str]:
    """
    将连贯叙事prompt拆分为16个场景（用于生成16宫格）
    """
    # 按句号分割，保留前16个场景
    scenes = [s.strip() for s in story_prompt.split('。') if s.strip()]
    return scenes[:16]
