"""
小说转视频完整工作流
运行：python main.py
"""
import os
import sys
import json
import logging
from pathlib import Path

# 配置
LLM_MODEL = "gemini-3.1-flash-lite"
LLM_API_KEY = "sk-poe-X5GOUooMd-EndZvgIs_4OjN2m34OUWJDLLE5FBT9-Cw"
NOVEL_PATH = "novels.txt"
OUTPUT_DIR = "output"
COSYVOICE_MODEL = r'C:\Users\pc\PycharmProjects\TOOL\Pictory\pretrained_models\Fun-CosyVoice3-0.5B'
REF_AUDIO = r'C:\Users\pc\PycharmProjects\TOOL\Pictory\output_audio_20_30.mp3'
REF_DIR = r'C:\Users\pc\PycharmProjects\TOOL\Pictory\PrototypeDev\小说配插画\ref'

CHARACTER_IMAGES = {
    "林知命": os.path.join(REF_DIR, "林知命.png"),
    "姚静": os.path.join(REF_DIR, "姚静.png"),
    "董建": os.path.join(REF_DIR, "董建.png"),
}

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
京都动画风格：
- 精致细腻的作画，人物五官唯美，眼睛刻画深邃有神
- 色彩明亮饱和，光影层次丰富，画面通透干净
- 背景环境写实精细，细节丰富，有电影质感
- 注重人物微表情、眼神、肢体语言的细腻刻画
- 构图讲究，画面有呼吸感，情绪表达克制而有力
"""
}

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(OUTPUT_DIR, 'pipeline.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """检查依赖"""
    logger.info("检查依赖...")
    
    # 检查CosyVoice模型
    if not os.path.exists(COSYVOICE_MODEL):
        raise FileNotFoundError(f"CosyVoice模型不存在: {COSYVOICE_MODEL}")
    
    # 检查参考音频
    if not os.path.exists(REF_AUDIO):
        raise FileNotFoundError(f"参考音频不存在: {REF_AUDIO}")
    
    # 检查ffmpeg
    import subprocess
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except:
        raise RuntimeError("ffmpeg未安装或不在PATH中")
    
    logger.info("✅ 依赖检查通过")

class ProgressManager:
    """进度管理器 - 支持断点续传"""
    def __init__(self, progress_file):
        self.progress_file = progress_file
        self.state = self.load()
    
    def load(self):
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "grid_generated": False,
            "grid_split": False,
            "hd_scenes": [],
            "audio_scenes": [],
            "video_generated": False
        }
    
    def save(self):
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)
    
    def mark_grid_done(self):
        self.state["grid_generated"] = True
        self.state["grid_split"] = True
        self.save()
    
    def mark_hd_done(self, scene_id):
        if scene_id not in self.state["hd_scenes"]:
            self.state["hd_scenes"].append(scene_id)
        self.save()
    
    def mark_audio_done(self, scene_id):
        if scene_id not in self.state["audio_scenes"]:
            self.state["audio_scenes"].append(scene_id)
        self.save()
    
    def is_hd_done(self, scene_id):
        return scene_id in self.state["hd_scenes"]
    
    def is_audio_done(self, scene_id):
        return scene_id in self.state["audio_scenes"]

def step1_generate_grid(novel_text, progress):
    """步骤1: 生成16宫格"""
    if progress.state["grid_generated"]:
        logger.info("⏭️ 16宫格已生成，跳过")
        return
    
    logger.info("=" * 60)
    logger.info("[1/5] 生成16宫格")
    logger.info("=" * 60)
    
    from llm_engine import LLMEngine
    from story_grid_generator import generate_story_prompt
    from nanobanana_engine import NanobananaEngine
    from grid_splitter import smart_split_grid
    
    llm = LLMEngine(model=LLM_MODEL, api_key=LLM_API_KEY)
    
    logger.info("生成故事prompt...")
    story_prompt, scenes_json = generate_story_prompt(
        llm, novel_text,
        GLOBAL_SETTINGS["character_card"],
        GLOBAL_SETTINGS["art_style"]
    )
    
    # 保存JSON和prompt
    with open(os.path.join(OUTPUT_DIR, "scenes_raw.json"), "w", encoding="utf-8") as f:
        json.dump(scenes_json, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(OUTPUT_DIR, "final_prompt.txt"), "w", encoding="utf-8") as f:
        f.write(story_prompt)
    
    # 收集参考图
    ref_images = []
    if os.path.exists(REF_DIR):
        for filename in os.listdir(REF_DIR):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                ref_images.append(os.path.join(REF_DIR, filename))
    
    logger.info(f"生成16宫格图（参考图: {len(ref_images)}张）...")
    nano = NanobananaEngine()
    grid_output = os.path.join(OUTPUT_DIR, "grid_16.png")
    
    nano.generate(
        prompt=story_prompt,
        input_image=ref_images if ref_images else None,
        output_path=grid_output,
        aspect_ratio="16:9",
        image_size="1K"
    )
    
    logger.info("拆分16宫格...")
    scenes_dir = os.path.join(OUTPUT_DIR, "scenes")
    smart_split_grid(grid_output, scenes_dir, rows=4, cols=4)
    
    # 保存scene_mapping
    mapping = {}
    for i, scene in enumerate(scenes_json):
        scene_file = f"scene_{i+1:02d}.png"
        mapping[scene_file] = {
            "scene_id": scene["scene_id"],
            "characters": scene["characters"],
            "shot_type": scene["shot_type"],
            "novel_start": scene["novel_start"],
            "novel_end": scene["novel_end"],
            "description": scene["description"]
        }
    
    with open(os.path.join(OUTPUT_DIR, "scene_mapping.json"), "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    
    progress.mark_grid_done()
    logger.info("✅ 16宫格生成完成")

def step2_enhance_scenes(progress):
    """步骤2: HD升级所有场景"""
    logger.info("=" * 60)
    logger.info("[2/5] HD升级场景")
    logger.info("=" * 60)
    
    from nanobanana_engine import NanobananaEngine
    from llm_engine import LLMEngine
    
    with open(os.path.join(OUTPUT_DIR, "scene_mapping.json"), "r", encoding="utf-8") as f:
        mapping = json.load(f)
    
    scenes_dir = os.path.join(OUTPUT_DIR, "scenes")
    hd_dir = os.path.join(OUTPUT_DIR, "scenes_hd")
    os.makedirs(hd_dir, exist_ok=True)
    
    nano = NanobananaEngine()
    llm = LLMEngine(model=LLM_MODEL, api_key=LLM_API_KEY)
    
    for scene_file, meta in sorted(mapping.items(), key=lambda x: x[1]["scene_id"]):
        scene_id = meta["scene_id"]
        
        if progress.is_hd_done(scene_id):
            logger.info(f"⏭️ Scene {scene_id:02d} HD已完成，跳过")
            continue
        
        logger.info(f"处理 Scene {scene_id:02d}...")
        
        # 构建参考图列表
        scene_path = os.path.join(scenes_dir, scene_file)
        ref_images = [scene_path]
        
        # 动态加载角色参考图
        for char_name in meta['characters'].split(','):
            char_name = char_name.strip()
            if char_name in CHARACTER_IMAGES and os.path.exists(CHARACTER_IMAGES[char_name]):
                ref_images.append(CHARACTER_IMAGES[char_name])
        
        # 生成简单prompt
        prompt = f"京都动画风格，{meta['description']}，精致细腻，光影丰富"
        
        hd_path = os.path.join(hd_dir, scene_file)
        
        try:
            nano.generate(
                prompt=prompt,
                input_image=ref_images,
                output_path=hd_path,
                aspect_ratio="16:9",
                image_size="2K"
            )
            progress.mark_hd_done(scene_id)
            logger.info(f"✅ Scene {scene_id:02d} HD完成")
        except Exception as e:
            logger.error(f"❌ Scene {scene_id:02d} HD失败（已重试5次）: {e}")
            raise RuntimeError(f"Scene {scene_id:02d} HD升级失败，停止工作流")
    
    logger.info("✅ 所有场景HD升级完成")

def step3_generate_audio(novel_text, progress):
    """步骤3: 生成音频"""
    logger.info("=" * 60)
    logger.info("[3/5] 生成音频")
    logger.info("=" * 60)

    # 添加Matcha-TTS路径
    matcha_path = r'C:\Users\pc\PycharmProjects\TOOL\Pictory\third_party\Matcha-TTS'
    if matcha_path not in sys.path:
        sys.path.insert(0, matcha_path)

    from cosyvoice.cli.cosyvoice import AutoModel
    import torchaudio
    
    with open(os.path.join(OUTPUT_DIR, "scene_mapping.json"), "r", encoding="utf-8") as f:
        mapping = json.load(f)
    
    audio_dir = os.path.join(OUTPUT_DIR, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    
    # 提取句区
    sorted_scenes = sorted(mapping.items(), key=lambda x: x[1]["scene_id"])
    segments = {}
    
    for i, (scene_file, scene_data) in enumerate(sorted_scenes):
        start_key = scene_data["novel_start"]
        start_idx = novel_text.find(start_key)
        
        if i < len(sorted_scenes) - 1:
            end_key = sorted_scenes[i + 1][1]["novel_start"]
            end_idx = novel_text.find(end_key, start_idx)
            segment = novel_text[start_idx:end_idx].strip() if end_idx != -1 else novel_text[start_idx:].strip()
        else:
            segment = novel_text[start_idx:].strip()
        
        segments[scene_file] = segment
    
    # 初始化CosyVoice
    logger.info("加载CosyVoice模型...")
    cosyvoice = AutoModel(model_dir=COSYVOICE_MODEL)
    
    for scene_file, scene_data in sorted_scenes:
        scene_id = scene_data["scene_id"]
        
        if progress.is_audio_done(scene_id):
            logger.info(f"⏭️ Scene {scene_id:02d} 音频已完成，跳过")
            continue
        
        segment_text = segments.get(scene_file, "")
        if not segment_text:
            logger.warning(f"⚠️ Scene {scene_id:02d} 无文本，跳过")
            continue
        
        logger.info(f"生成 Scene {scene_id:02d} 音频...")
        
        instruct = "You are a helpful assistant. 请以一个民间说书人的口吻说<|endofprompt|>"
        audio_segments = []
        
        for output in cosyvoice.inference_instruct2(segment_text, instruct, REF_AUDIO, stream=False):
            audio_segments.append(output['tts_speech'])
        
        if audio_segments:
            import torch
            merged = torch.cat(audio_segments, dim=1) if len(audio_segments) > 1 else audio_segments[0]
            output_file = os.path.join(audio_dir, f"scene_{scene_id:02d}_audio.wav")
            torchaudio.save(output_file, merged, cosyvoice.sample_rate)
            progress.mark_audio_done(scene_id)
            logger.info(f"✅ Scene {scene_id:02d} 音频完成")
    
    logger.info("✅ 所有音频生成完成")

def step4_compose_video(progress):
    """步骤4: 合成视频"""
    logger.info("=" * 60)
    logger.info("[4/5] 合成视频")
    logger.info("=" * 60)

    import subprocess
    import json as json_lib
    
    with open(os.path.join(OUTPUT_DIR, "scene_mapping.json"), "r", encoding="utf-8") as f:
        mapping = json.load(f)
    
    hd_dir = os.path.join(OUTPUT_DIR, "scenes_hd")
    audio_dir = os.path.join(OUTPUT_DIR, "audio")
    temp_dir = os.path.join(OUTPUT_DIR, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    sorted_scenes = sorted(mapping.items(), key=lambda x: x[1]["scene_id"])
    video_parts = []
    
    for scene_file, scene_data in sorted_scenes:
        scene_id = scene_data["scene_id"]
        image_path = os.path.join(hd_dir, scene_file)
        audio_path = os.path.join(audio_dir, f"scene_{scene_id:02d}_audio.wav")
        
        if not os.path.exists(audio_path):
            logger.warning(f"⚠️ Scene {scene_id:02d} 音频不存在，跳过")
            continue

        # 使用ffprobe获取音频时长
        probe_cmd = [
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'json', audio_path
        ]
        result = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
        duration = float(json_lib.loads(result.stdout)['format']['duration'])
        
        # 生成视频片段
        video_part = os.path.join(temp_dir, f"part_{scene_id:02d}.mp4")
        cmd = [
            'ffmpeg', '-y', '-loop', '1', '-i', image_path,
            '-i', audio_path, '-c:v', 'libx264', '-tune', 'stillimage',
            '-c:a', 'aac', '-b:a', '192k', '-pix_fmt', 'yuv420p',
            '-shortest', '-t', str(duration), '-r', '30', video_part
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        video_parts.append(video_part)
        logger.info(f"✅ Scene {scene_id:02d} 视频片段完成 ({duration:.2f}s)")
    
    # 合并所有片段
    logger.info("合并所有视频片段...")
    concat_file = os.path.join(temp_dir, "concat.txt")
    with open(concat_file, 'w') as f:
        for part in video_parts:
            f.write(f"file '{os.path.abspath(part)}'\n")
    
    final_video = os.path.join(OUTPUT_DIR, "final_video.mp4")
    cmd = ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_file, '-c', 'copy', final_video]
    subprocess.run(cmd, check=True, capture_output=True)
    
    logger.info(f"✅ 视频合成完成: {final_video}")

def main():
    """主流程入口"""
    try:
        # 创建输出目录
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # 检查依赖
        check_dependencies()
        
        # 读取小说
        logger.info(f"读取小说: {NOVEL_PATH}")
        with open(NOVEL_PATH, 'r', encoding='utf-8') as f:
            novel_text = f.read()
        
        # 初始化进度管理
        progress = ProgressManager(os.path.join(OUTPUT_DIR, "progress.json"))
        
        # 执行流程
        step1_generate_grid(novel_text, progress)
        step2_enhance_scenes(progress)
        step3_generate_audio(novel_text, progress)
        step4_compose_video(progress)
        
        logger.info("=" * 60)
        logger.info("🎉 完整工作流执行成功！")
        logger.info(f"最终视频: {os.path.join(OUTPUT_DIR, 'final_video.mp4')}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ 工作流失败: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
