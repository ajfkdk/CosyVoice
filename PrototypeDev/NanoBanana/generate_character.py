from nanobanana_engine import NanobananaEngine

prompt = """
京都动画风格角色头像参考表。
单张白底图中包含：正面头像、左侧面头像、右侧面头像，三图横向并排排列。
角色特征：中年男性，林知命的心腹手下，面相沉稳,早年当兵脸有刀疤
图面顶部标注加粗角色名"董建"
整体排版整洁专业，参考京都动画作画规范。线条干净精致，仅展示头颈部。
"""

full_prompt = f"{prompt}\n\n"

engine = NanobananaEngine()
engine.generate(full_prompt, output_path="董建.png")
