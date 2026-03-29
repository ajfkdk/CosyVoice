"""
1Prompt1Story - 16宫格故事生成器
核心：一个prompt生成16个连贯场景，保持角色和风格一致性
"""
from llm_engine import LLMEngine


MIYAZAKI_SYSTEM = """你是京都动画社的灵魂画手，擅长将小说章节转化为16格连贯叙事画面。

⚠️ 核心原则：你画的不是"事件流水账"，而是"情感节奏"。

镜头类型分配（16格必须包含）：
- 【事件格】6-7格：情节推进，有明确动作和事件
- 【过渡格】3-4格：情绪缓冲，环境、背影、细节特写（无台词）
- 【特写格】3-4格：纯粹的表情/眼神/手部特写，极简背景
- 【留白格】2-3格：安静时刻，人物静止或环境空镜，给读者呼吸空间

强制规则：
1. 暴力/冲突场景后必须紧跟1格【过渡格】（如：夜路背影、车内发呆）
2. 情感高潮场景必须有1格【特写格】（如：眼神、握紧的手）
3. 每4-5格必须有1格非事件格（过渡/特写/留白）
4. 重场戏描述要极简：越重要越克制，只写核心视觉元素

⚠️ 描述铁律（违反即为失败）：
1. 绝对不添加原文不存在的动作或道具（如原文没有"敲扶手"就不能写，没有"皮鞋"就不能写）
2. 用原文的情绪词汇，不用通用审美词（如原文是"冷漠"就写冷漠，不要改成"优雅"）
3. 特写格必须明确：特写什么部位、为什么特写这里、这个特写承载什么叙事信息
4. 描述必须定格在原文段落内的某个画面，不能提前或延后到其他段落的内容

输出格式：JSON数组，每个场景包含：
{
  "scene_id": 1,
  "characters": "林知命",
  "shot_type": "事件格",
  "novel_start": "夜色已深",
  "novel_end": "面无表情的西装大汉",
  "description": "昏暗仓库内，三个男人被吊在天花板下，浑身伤痕，林知命坐在正前方，脸色冷漠",
  "action_subject": "林知命",
  "action_verb": "审问",
  "action_target": "三个被吊的人"
}

⚠️ description写作要求：
- 只描述原文段落内出现的人物、动作、道具、环境
- 直接使用原文的情绪词（冷漠、威严、惨叫、血迹），不要替换成审美词（优雅、唯美、清冷）
- 特写格必须说明特写对象和原因（如"特写林知命的眼睛，冷漠中带着威严"）
- 暴力场景用氛围和情绪表达，避免直接描述伤害细节（如"紧张对峙"而非"拳打脚踢"）
- 15-40字，简洁直接

⚠️ 【事件格】额外要求（必须填写以下三个字段）：
- action_subject: 动作的执行者（谁在做）
- action_verb: 核心动作（做什么），可以同义替换但必须符合原文逻辑
- action_target: 动作的接受者/对象（对谁做/对什么做），如果没有明确对象则填"无"

示例：
- "西装大汉殴打三个被吊的人" → subject: "西装大汉", verb: "殴打", target: "三个被吊的人"
- "董建递烟给林知命" → subject: "董建", verb: "递烟", target: "林知命"
- "林知命抽烟" → subject: "林知命", verb: "抽烟", target: "无"

⚠️ 重要：
- novel_start/novel_end是原文中的关键句（5-15字），标记这个场景对应的小说段落起止位置
- 输出完整的JSON数组，16个元素

京都动画美学：
- 细腻手绘线条，色彩饱和度适中偏暖
- 光影层次丰富，人物五官精致唯美
- 越重要的情绪，画面越安静克制
- ⚠️ 画面中绝对不要出现任何文字、对话框、标题、字幕
"""


def generate_story_prompt(llm: LLMEngine, novel_text: str, character_card: str,
                          art_style: str) -> tuple[str, list[dict]]:
    """
    生成1Prompt1Story的连贯叙事prompt
    返回：(最终prompt字符串, 场景JSON数组)
    """
    import json
    import re

    user_prompt = f"""请将以下小说章节转化为16格连贯叙事画面，输出JSON数组。

【角色设定】
{character_card}

【美术风格】
{art_style}

【小说原文】
{novel_text}

⚠️ 镜头分配要求：
- 必须包含3-4格【过渡格】：环境、背影、细节，无对话
- 必须包含3-4格【特写格】：表情、眼神、手部特写
- 必须包含2-3格【留白格】：安静时刻，给读者呼吸空间
- 冲突场景后必须紧跟过渡格
- 情感高潮场景必须极简克制

⚠️ description核心要求：
1. 只写原文段落内存在的内容，不添加任何原文没有的动作、道具、环境细节
2. 直接使用原文的情绪词汇（如"冷漠"、"威严"、"惨叫"），不要替换成通用审美词（如"优雅"、"唯美"）
3. 特写格必须明确：特写什么、为什么特写（承载什么叙事信息）
4. 捕捉原文段落的气质（压迫、冷硬、危险），不要自动美化

⚠️ 【事件格】必须填写动作三要素：
- action_subject: 谁在做动作
- action_verb: 做什么动作（可同义替换，但必须符合原文逻辑）
- action_target: 对谁/对什么做（没有明确对象则填"无"）
- 其他镜头类型（特写格/过渡格/留白格）这三个字段填null

输出格式：纯JSON数组，不要任何其他文字。示例：
[
  {{"scene_id": 1, "characters": "林知命", "shot_type": "事件格", "novel_start": "夜色已深", "novel_end": "面无表情的西装大汉", "description": "昏黄仓库里，吊灯摇晃，林知命坐在椅上审讯", "action_subject": "林知命", "action_verb": "审讯", "action_target": "三个被吊的人"}},
  {{"scene_id": 2, "characters": "无", "shot_type": "过渡格", "novel_start": "地面上早充斥着", "novel_end": "血迹", "description": "血迹斑驳的水泥地，靴尖停在血泊边", "action_subject": null, "action_verb": null, "action_target": null}}
]
"""

    json_response = llm.chat(user_prompt, system=MIYAZAKI_SYSTEM)

    # 提取JSON（去除可能的markdown代码块标记）
    json_text = json_response.strip()
    json_text = re.sub(r'^```json\s*', '', json_text)
    json_text = re.sub(r'\s*```$', '', json_text)

    # 解析JSON
    try:
        scenes = json.loads(json_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM输出的JSON格式错误: {e}\n原始输出:\n{json_response}")

    # 拼接成连贯叙事prompt
    scene_descriptions = []
    for scene in scenes:
        # 事件格：使用结构化字段生成更清晰的描述
        if scene['shot_type'] == "事件格" and scene.get('action_subject'):
            if scene.get('action_target') and scene['action_target'] != "无":
                action_desc = f"{scene['action_subject']}对{scene['action_target']}{scene['action_verb']}"
            else:
                action_desc = f"{scene['action_subject']}{scene['action_verb']}"
            desc = f"[{scene['characters']}]【{scene['shot_type']}】《{scene['novel_start']}》{action_desc}，{scene['description']}"
        else:
            # 其他镜头类型：保持原有格式
            desc = f"[{scene['characters']}]【{scene['shot_type']}】《{scene['novel_start']}》{scene['description']}"
        scene_descriptions.append(desc)

    narrative_prompt = "。".join(scene_descriptions) + "。"

    # 添加16宫格布局要求
    final_prompt = f"""{narrative_prompt}

⚠️ 重要布局要求：
- 生成4x4标准网格布局（16个格子）
- 每个格子大小完全相等
- 格子之间用纯黑色分隔线（RGB: 0,0,0），线宽3-5像素
- 分隔线必须笔直、清晰、连贯
- 整体画面比例16:9

⚠️ 绝对禁止：
- 画面中不要出现任何文字、对话框、字幕、标题、标签
- 不要在格子内添加场景编号或说明文字
- 这是纯视觉叙事，只用画面讲故事"""

    return final_prompt, scenes


def split_story_scenes(story_prompt: str) -> list[str]:
    """
    将连贯叙事prompt拆分为16个场景（用于生成16宫格）
    """
    # 按句号分割，保留前16个场景
    scenes = [s.strip() for s in story_prompt.split('。') if s.strip()]
    return scenes[:16]
