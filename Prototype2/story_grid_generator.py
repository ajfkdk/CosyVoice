from llm_engine import LLMEngine
import json
import re

MIYAZAKI_SYSTEM = """你是京都动画社的灵魂画手，擅长将小说章节转化为16格连贯叙事画面。

镜头类型分配（16格必须包含）：
- 【事件格】6-7格：情节推进，有明确动作和事件
- 【过渡格】3-4格：情绪缓冲，环境、背影、细节特写
- 【特写格】3-4格：纯粹的表情/眼神/手部特写
- 【留白格】2-3格：安静时刻，人物静止或环境空镜

⚠️ 【事件格】额外要求（必须填写以下三个字段）：
- action_subject: 动作的执行者（谁在做）
- action_verb: 核心动作（做什么），可以同义替换但必须符合原文逻辑
- action_target: 动作的接受者/对象（对谁做/对什么做），如果没有明确对象则填"无"

输出格式：JSON数组，每个场景包含：
{"scene_id": 1, "characters": "林知命", "shot_type": "事件格", "novel_start": "夜色已深", "novel_end": "面无表情的西装大汉", "description": "昏暗仓库内，三个男人被吊在天花板下", "action_subject": "林知命", "action_verb": "审问", "action_target": "三个被吊的人"}
"""

def generate_story_prompt(llm: LLMEngine, novel_text: str, character_card: str, art_style: str):
    user_prompt = f"""请将以下小说章节转化为16格连贯叙事画面，输出JSON数组。

【角色设定】
{character_card}

【美术风格】
{art_style}

【小说原文】
{novel_text}

⚠️ 【事件格】必须填写动作三要素：action_subject, action_verb, action_target
其他镜头类型这三个字段填null

输出格式：纯JSON数组，不要任何其他文字。
"""
    
    json_response = llm.chat(user_prompt, system=MIYAZAKI_SYSTEM)
    json_text = re.sub(r'^```json\s*', '', json_response.strip())
    json_text = re.sub(r'\s*```$', '', json_text)
    
    scenes = json.loads(json_text)
    
    scene_descriptions = []
    for scene in scenes:
        if scene['shot_type'] == "事件格" and scene.get('action_subject'):
            if scene.get('action_target') and scene['action_target'] != "无":
                action_desc = f"{scene['action_subject']}对{scene['action_target']}{scene['action_verb']}"
            else:
                action_desc = f"{scene['action_subject']}{scene['action_verb']}"
            desc = f"[{scene['characters']}]【{scene['shot_type']}】《{scene['novel_start']}》{action_desc}，{scene['description']}"
        else:
            desc = f"[{scene['characters']}]【{scene['shot_type']}】《{scene['novel_start']}》{scene['description']}"
        scene_descriptions.append(desc)
    
    narrative_prompt = "。".join(scene_descriptions) + "。"
    final_prompt = f"""{narrative_prompt}

⚠️ 重要布局要求：
- 生成4x4标准网格布局（16个格子）
- 每个格子大小完全相等
- 格子之间用纯黑色分隔线（RGB: 0,0,0），线宽3-5像素
- 整体画面比例16:9
- 画面中不要出现任何文字、对话框、字幕、标题、标签"""
    
    return final_prompt, scenes
