import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'NanoBanana'))

from llm_engine import LLMEngine
from story_grid_generator import generate_story_prompt
import json

LLM_MODEL = "gemini-3.1-flash-lite"
LLM_API_KEY = "sk-poe-X5GOUooMd-EndZvgIs_4OjN2m34OUWJDLLE5FBT9-Cw"

GLOBAL_SETTINGS = {
    "character_card": """
男主角：林知命
- 28岁，英俊成熟，面容冷漠带威严，眼神深邃有杀意
- 身材挺拔，常穿深色西装
- 表面懦弱是伪装，内里隐忍的枭雄

女主角：姚静
- 绝色美女，身高一米七，体型完美，柔顺长发
- 商业女强人，冷静克制，情绪极少外露
- 居家穿丝质睡衣，出行着职业装

配角：董建
- 中年男性，林知命心腹，面相沉稳
""",
    "art_style": """
宫崎骏手绘风格：
- 细腻柔和的线条，色彩饱和度适中偏暖
- 光影层次丰富，人物五官精致唯美
- 背景环境写实精细，画面有电影质感和情绪氛围
- 注重人物姿态、眼神、肢体语言传达情绪
- 构图有呼吸感和空气感，避免呆板居中
"""
}

SAMPLE_NOVEL = """
第一章 我们离婚吧
    夜色已深。
    海峡市郊区某仓库内。
    阵阵惨叫声从仓库中传出。
    三个男人被人捆绑住双手吊在仓库的天花板下，他们光着身子，浑身上下都是伤痕。
    在他们的边上，是几个面无表情的西装大汉。
    "我招，我都招，我所做的一切都是大少爷安排的！"
    "二少爷，绕了我们吧，我们不敢了！"
    那被绑着的几个人对着他们正前方的人苦苦哀求着。
    有谁能想到，这几个帮林氏集团原董事长林知行做过许多见不得光的事情的狠人，此时竟然如此可怜。
    "为什么非要我动粗你们才肯招呢？"
    林知命有些无奈的说道，他就坐在这三个人的正前方位置，翘着二郎腿，脸色冷漠之中略微带着一股威严。
    年纪二十八的林知命脸上，是与他这个年纪不相符的成熟感。
    这样一个林知命，早已经颠覆面前三人的认知。
    在今天之前，他们一直以为，这个长得好看的不像话的林家二少爷，是一个懦弱无能的软蛋。
    事实上，整个海峡市许多人也都认为林知命是个软蛋，是一个打不还手骂不还口的懦夫。
    有谁能想到，就是这样一个懦夫，亲手将他的大哥，林氏集团的董事长林知行送进了大牢，同时，还让整个林氏集团变得风雨飘摇，面临破产。
    "人都是贱骨头，不把骨头打断不行。"站在林知命旁边的一个中年人说道。
    "董建，你好狠毒！咱们可都是大少爷的手下！"三人中的一个激动的叫道。
    "那就把骨头打断吧，我希望能得到一些更有价值的东西。"林知命微笑着说道。
    于是，几个西装大汉再一次拿起了家伙，开始往那三个人身上招呼。
"""

print("测试结构化prompt生成...")
llm = LLMEngine(model=LLM_MODEL, api_key=LLM_API_KEY)

story_prompt, scenes_json = generate_story_prompt(
    llm, SAMPLE_NOVEL,
    GLOBAL_SETTINGS["character_card"],
    GLOBAL_SETTINGS["art_style"]
)

# 保存JSON
with open("test_scenes.json", "w", encoding="utf-8") as f:
    json.dump(scenes_json, f, ensure_ascii=False, indent=2)

print("\n生成的场景JSON已保存到 test_scenes.json")
print("\n前3个场景预览：")
for i, scene in enumerate(scenes_json[:3]):
    print(f"\n场景{i+1}:")
    print(f"  类型: {scene['shot_type']}")
    print(f"  描述: {scene['description']}")
    if scene['shot_type'] == "事件格":
        print(f"  主体: {scene.get('action_subject', 'N/A')}")
        print(f"  动作: {scene.get('action_verb', 'N/A')}")
        print(f"  对象: {scene.get('action_target', 'N/A')}")
