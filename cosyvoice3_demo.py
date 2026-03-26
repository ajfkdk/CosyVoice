import sys
sys.path.append('third_party/Matcha-TTS')
from cosyvoice.cli.cosyvoice import AutoModel
import torchaudio


class CosyVoice3Demo:
    def __init__(self):
        self.model_dir = 'pretrained_models/Fun-CosyVoice3-0.5B'
        self.cosyvoice = AutoModel(model_dir=self.model_dir)
        self.prompt_audio = './asset/zero_shot_prompt.wav'
        self.prompt_text = '希望你以后能够做的比我还好呦。'
        self.ref_audio = r'C:\Users\pc\PycharmProjects\TOOL\Pictory\output_audio_20_30.mp3'  # 统一的参考音频
        print(f"✅ 模型加载成功: {self.model_dir}")

    def play_1_basic_zero_shot(self):
        """玩法1: 基础音色克隆"""
        print("\n🎯 玩法1: 基础音色克隆")
        text = '，陈小姐这回真哭了。这一段情节其实大家都知道个大概，但是现在让陈小姐亲口说出来，还带有如此多的细节，真让人感慨不已,........。'
        prompt = 'You are a helpful assistant.<|endofprompt|>'
        ref_audio = r'C:\Users\pc\PycharmProjects\TOOL\Pictory\output_audio_20_30.mp3'

        for i, j in enumerate(self.cosyvoice.inference_zero_shot(
            text, prompt, ref_audio, stream=False
        )):
            output = f'output/1_basic_zero_shot_{i}.wav'
            torchaudio.save(output, j['tts_speech'], self.cosyvoice.sample_rate)
            print(f"✅ 生成: {output}")

    def play_2_breath_control(self):
        """玩法2: 呼吸控制 - 自然停顿"""
        print("\n🎯 玩法2: 呼吸控制")
        text = 'You are a helpful assistant.<|endofprompt|>[breath]陈小姐这回真哭了。[breath]这一段情节其实大家都知道个大概，[breath]但是现在让陈小姐亲口说出来，[breath]还带有如此多的细节，[breath]真让人感慨不已。[breath]'
        ref_audio = r'C:\Users\pc\PycharmProjects\TOOL\Pictory\output_audio_20_30.mp3'

        for i, j in enumerate(self.cosyvoice.inference_cross_lingual(
            text, ref_audio, stream=False
        )):
            output = f'output/2_breath_control_{i}.wav'
            torchaudio.save(output, j['tts_speech'], self.cosyvoice.sample_rate)
            print(f"✅ 生成: {output}")

    def play_3_cantonese(self):
        """玩法3: 粤语合成"""
        print("\n🎯 玩法3: 粤语合成")
        text = '陈小姐这回真哭了。这一段情节其实大家都知道个大概，但是现在让陈小姐亲口说出来，还带有如此多的细节，真让人感慨不已。'
        instruct = 'You are a helpful assistant. 请用广东话表达。<|endofprompt|>'
        ref_audio = r'C:\Users\pc\PycharmProjects\TOOL\Pictory\output_audio_20_30.mp3'

        for i, j in enumerate(self.cosyvoice.inference_instruct2(
            text, instruct, ref_audio, stream=False
        )):
            output = f'output/3_cantonese_{i}.wav'
            torchaudio.save(output, j['tts_speech'], self.cosyvoice.sample_rate)
            print(f"✅ 生成: {output}")

    def play_4_speed_control(self):
        """玩法4: 语速控制 - 快速"""
        print("\n🎯 玩法4: 语速控制")
        text = '陈小姐这回真哭了。这一段情节其实大家都知道个大概，但是现在让陈小姐亲口说出来，还带有如此多的细节，真让人感慨不已。'
        instruct = 'You are a helpful assistant. 请用尽可能快地语速说一句话。<|endofprompt|>'
        ref_audio = r'C:\Users\pc\PycharmProjects\TOOL\Pictory\output_audio_20_30.mp3'

        for i, j in enumerate(self.cosyvoice.inference_instruct2(
            text, instruct, ref_audio, stream=False
        )):
            output = f'output/4_fast_speed_{i}.wav'
            torchaudio.save(output, j['tts_speech'], self.cosyvoice.sample_rate)
            print(f"✅ 生成: {output}")

    def play_5_hotfix_pronunciation(self):
        """玩法5: 多音字修正"""
        print("\n🎯 玩法5: 多音字修正")
        text = '高管也通过电话、短信、微信等方式对报道[j][ǐ]予好评。'
        prompt = f'You are a helpful assistant.<|endofprompt|>{self.prompt_text}'

        for i, j in enumerate(self.cosyvoice.inference_zero_shot(
            text, prompt, self.prompt_audio, stream=False
        )):
            output = f'output/5_hotfix_{i}.wav'
            torchaudio.save(output, j['tts_speech'], self.cosyvoice.sample_rate)
            print(f"✅ 生成: {output}")

    def play_6_japanese(self):
        """玩法6: 日语合成 (片假名)"""
        print("\n🎯 玩法6: 日语合成")
        text = 'You are a helpful assistant.<|endofprompt|>レキシ テキ セカイ ニ オイ テ ワ、カコ ワ タンニ スギサッ タ モノ デ ワ ナイ。'

        for i, j in enumerate(self.cosyvoice.inference_cross_lingual(
            text, self.prompt_audio, stream=False
        )):
            output = f'output/6_japanese_{i}.wav'
            torchaudio.save(output, j['tts_speech'], self.cosyvoice.sample_rate)
            print(f"✅ 生成: {output}")

    def play_7_slow_speed(self):
        """玩法7: 慢速语速"""
        print("\n🎯 玩法7: 慢速语速")
        text = '陈小姐这回真哭了。这一段情节其实大家都知道个大概，但是现在让陈小姐亲口说出来，还带有如此多的细节，真让人感慨不已。'
        instruct = 'You are a helpful assistant. 请用缓慢的语速说这句话。<|endofprompt|>'
        ref_audio = r'C:\Users\pc\PycharmProjects\TOOL\Pictory\output_audio_20_30.mp3'

        for i, j in enumerate(self.cosyvoice.inference_instruct2(
            text, instruct, ref_audio, stream=False
        )):
            output = f'output/7_slow_speed_{i}.wav'
            torchaudio.save(output, j['tts_speech'], self.cosyvoice.sample_rate)
            print(f"✅ 生成: {output}")

    def play_8_sichuan_dialect(self):
        """玩法8: 四川话"""
        print("\n🎯 玩法8: 四川话")
        text = '陈小姐这回真哭了。这一段情节其实大家都知道个大概，但是现在让陈小姐亲口说出来，还带有如此多的细节，真让人感慨不已。'
        instruct = 'You are a helpful assistant. 请用四川话表达。<|endofprompt|>'
        ref_audio = r'C:\Users\pc\PycharmProjects\TOOL\Pictory\output_audio_20_30.mp3'

        for i, j in enumerate(self.cosyvoice.inference_instruct2(
            text, instruct, ref_audio, stream=False
        )):
            output = f'output/8_sichuan_{i}.wav'
            torchaudio.save(output, j['tts_speech'], self.cosyvoice.sample_rate)
            print(f"✅ 生成: {output}")

    def play_9_emotion_happy(self):
        """玩法9: 情感控制 - 悲伤"""
        print("\n🎯 玩法9: 情感控制 - 悲伤")
        text = '陈小姐这回真哭了。这一段情节其实大家都知道个大概，但是现在让陈小姐亲口说出来，还带有如此多的细节，真让人感慨不已。'
        instruct = 'You are a helpful assistant. 请用悲伤哭泣的语气说这句话。<|endofprompt|>'
        ref_audio = r'C:\Users\pc\PycharmProjects\TOOL\Pictory\output_audio_20_30.mp3'

        for i, j in enumerate(self.cosyvoice.inference_instruct2(
            text, instruct, ref_audio, stream=False
        )):
            output = f'output/9_emotion_sad_{i}.wav'
            torchaudio.save(output, j['tts_speech'], self.cosyvoice.sample_rate)
            print(f"✅ 生成: {output}")

    def play_10_english(self):
        """玩法10: 英文合成"""
        print("\n🎯 玩法10: 英文合成")
        text = 'You are a helpful assistant.<|endofprompt|>Hello, this is a test of English speech synthesis using CosyVoice3.'

        for i, j in enumerate(self.cosyvoice.inference_cross_lingual(
            text, self.prompt_audio, stream=False
        )):
            output = f'output/10_english_{i}.wav'
            torchaudio.save(output, j['tts_speech'], self.cosyvoice.sample_rate)
            print(f"✅ 生成: {output}")

    def play_11_xiangsheng_tone(self):
        """玩法11: 讲相声的语气"""
        print("\n🎯 玩法11: 讲相声的语气")
        text = '个律师在一起强奸案的法庭辩护中的奇遇。大约四个月前，陈小姐在半夜回到自己的公寓里遭到一个预先埋伏的歹徒的攻击和强奸。在整个强奸过程中陈小姐被蒙上了双眼，自始至终都未能见到强暴犯的长相。但她却清晰地记住了罪犯的声音。从陪审团的身体语言反应出的情况来估计，如不出意外，这个案子被告方是必输无疑了'
        instruct = 'You are a helpful assistant. 请用讲相声的幽默诙谐语气说这段话。<|endofprompt|>'
        ref_audio = r'C:\Users\pc\PycharmProjects\TOOL\Pictory\output_audio_20_30.mp3'

        for i, j in enumerate(self.cosyvoice.inference_instruct2(
            text, instruct, ref_audio, stream=False
        )):
            output = f'output/11_xiangsheng_{i}.wav'
            torchaudio.save(output, j['tts_speech'], self.cosyvoice.sample_rate)
            print(f"✅ 生成: {output}")

    def play_12_flirty_tone(self):
        """玩法12: 勾引的语气"""
        print("\n🎯 玩法12: 勾引的语气")
        text = '个律师在一起强奸案的法庭辩护中的奇遇。大约四个月前，陈小姐在半夜回到自己的公寓里遭到一个预先埋伏的歹徒的攻击和强奸。在整个强奸过程中陈小姐被蒙上了双眼，自始至终都未能见到强暴犯的长相。但她却清晰地记住了罪犯的声音。从陪审团的身体语言反应出的情况来估计，如不出意外，这个案子被告方是必输无疑了'
        instruct = 'You are a helpful assistant. 请用妩媚撩人的语气说这段话。<|endofprompt|>'
        ref_audio = r'C:\Users\pc\PycharmProjects\TOOL\Pictory\output_audio_20_30.mp3'

        for i, j in enumerate(self.cosyvoice.inference_instruct2(
            text, instruct, ref_audio, stream=False
        )):
            output = f'output/12_flirty_{i}.wav'
            torchaudio.save(output, j['tts_speech'], self.cosyvoice.sample_rate)
            print(f"✅ 生成: {output}")

    def play_13_complain_tone(self):
        """玩法13: 和男朋友吐槽的语气"""
        print("\n🎯 玩法13: 和男朋友吐槽的语气")
        text = '个律师在一起强奸案的法庭辩护中的奇遇。大约四个月前，陈小姐在半夜回到自己的公寓里遭到一个预先埋伏的歹徒的攻击和强奸。在整个强奸过程中陈小姐被蒙上了双眼，自始至终都未能见到强暴犯的长相。但她却清晰地记住了罪犯的声音。从陪审团的身体语言反应出的情况来估计，如不出意外，这个案子被告方是必输无疑了'
        instruct = 'You are a helpful assistant. 请用向男朋友抱怨吐槽的语气说这段话。<|endofprompt|>'
        ref_audio = r'C:\Users\pc\PycharmProjects\TOOL\Pictory\output_audio_20_30.mp3'

        for i, j in enumerate(self.cosyvoice.inference_instruct2(
            text, instruct, ref_audio, stream=False
        )):
            output = f'output/13_complain_{i}.wav'
            torchaudio.save(output, j['tts_speech'], self.cosyvoice.sample_rate)
            print(f"✅ 生成: {output}")

    def play_14_whisper_tone(self):
        """玩法14: 同事之间悄悄话的语气"""
        print("\n🎯 玩法14: 同事之间悄悄话的语气")
        text = '个律师在一起强奸案的法庭辩护中的奇遇。大约四个月前，陈小姐在半夜回到自己的公寓里遭到一个预先埋伏的歹徒的攻击和强奸。在整个强奸过程中陈小姐被蒙上了双眼，自始至终都未能见到强暴犯的长相。但她却清晰地记住了罪犯的声音。从陪审团的身体语言反应出的情况来估计，如不出意外，这个案子被告方是必输无疑了'
        instruct = 'You are a helpful assistant. 请用在嘈杂环境中大声说话的方式说这段话。<|endofprompt|>'
        ref_audio = r'C:\Users\pc\PycharmProjects\TOOL\Pictory\output_audio_20_30.mp3'

        for i, j in enumerate(self.cosyvoice.inference_instruct2(
            text, instruct, ref_audio, stream=False
        )):
            output = f'output/14_whisper_{i}.wav'
            torchaudio.save(output, j['tts_speech'], self.cosyvoice.sample_rate)
            print(f"✅ 生成: {output}")


def main():
    import os
    os.makedirs('output', exist_ok=True)

    demo = CosyVoice3Demo()

    print("\n" + "="*50)
    print("CosyVoice3 玩法演示")
    print("="*50)

    # 取消注释想要运行的玩法
    # demo.play_1_basic_zero_shot()      # 基础音色克隆
    # demo.play_2_breath_control()     # 呼吸控制
    # demo.play_3_cantonese()          # 粤语
    # demo.play_4_speed_control()      # 快速语速
    # demo.play_5_hotfix_pronunciation() # 多音字修正
    # demo.play_6_japanese()           # 日语
    # demo.play_7_slow_speed()         # 慢速语速
    # demo.play_8_sichuan_dialect()    # 四川话
    # demo.play_9_emotion_happy()      # 情感控制
    # demo.play_10_english()           # 英文
    # demo.play_11_xiangsheng_tone()   # 讲相声语气
    # demo.play_12_flirty_tone()       # 勾引语气
    # demo.play_13_complain_tone()     # 吐槽语气
    demo.play_14_whisper_tone()      # 悄悄话语气

    print("\n✅ 所有任务完成！")


if __name__ == '__main__':
    main()

