from nanobanana_engine import NanobananaEngine

prompt = """
根据以下角色描述，为我生成一套完整的角色设定图（Character Design Sheet）：

【角色描述】
配角：董建
- 中年男性，林知命的心腹手下，面相沉稳

设定图需包含：
角色名字（加粗醒目）
三视图（正面、侧面、背面）
表情设定（Expression Sheet）
动作设定（Pose Sheet）
服装设定（Costume Design Sheet）
头身比例参考
风格统一，排版整洁，所有内容集中在同一张图中。
"""

full_prompt = f"{prompt}\n\n"

engine = NanobananaEngine()
engine.generate(full_prompt, output_path="董建.png")
