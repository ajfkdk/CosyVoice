from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


SEPARATOR_HEIGHT = 40   # 分隔条高度（像素）
SEPARATOR_COLOR = (255, 255, 255)
TEXT_COLOR = (80, 80, 80)
FONT_SIZE = 20
MAX_WIDTH = 768          # 统一缩放到此宽度


def _load_and_resize(img_path: str, width: int) -> Image.Image:
    img = Image.open(img_path).convert("RGB")
    ratio = width / img.width
    new_h = int(img.height * ratio)
    return img.resize((width, new_h), Image.LANCZOS)


def _make_separator(width: int, label: str) -> Image.Image:
    sep = Image.new("RGB", (width, SEPARATOR_HEIGHT), SEPARATOR_COLOR)
    draw = ImageDraw.Draw(sep)
    try:
        font = ImageFont.truetype("msyh.ttc", FONT_SIZE)
    except Exception:
        font = ImageFont.load_default()
    draw.text((10, (SEPARATOR_HEIGHT - FONT_SIZE) // 2), label, fill=TEXT_COLOR, font=font)
    return sep


class CharacterReference:
    """单个角色的参考图条目"""
    def __init__(self, name: str, image_path: str):
        self.name = name
        self.image_path = image_path


class ReferenceImageManager:
    """
    管理角色参考图集合 + 上一帧场景图。
    调用 build_reference() 生成合并后的单张参考图。
    """

    def __init__(self):
        self._characters: list[CharacterReference] = []
        self._last_scene_path: str | None = None

    def add_character(self, name: str, image_path: str):
        """添加或更新角色参考图"""
        for c in self._characters:
            if c.name == name:
                c.image_path = image_path
                return
        self._characters.append(CharacterReference(name, image_path))

    def update_last_scene(self, image_path: str | None):
        """更新上一帧场景图"""
        self._last_scene_path = image_path

    def has_any_reference(self) -> bool:
        return bool(self._characters) or self._last_scene_path is not None

    def build_reference(self, output_path: str,
                         active_characters: list[str] | None = None) -> tuple[str | None, str]:
        """
        将活跃角色参考图 + 上一帧场景原图垂直拼接为一张参考图。
        active_characters: 当前场景出现的角色名列表，None 表示全部注入。
        返回 (合并图路径 or None, 参考图结构说明文字)
        """
        blocks: list[Image.Image] = []
        labels: list[str] = []

        for char in self._characters:
            if active_characters is not None and char.name not in active_characters:
                continue
            if not Path(char.image_path).exists():
                continue
            sep = _make_separator(MAX_WIDTH, f"角色参考：{char.name}")
            img = _load_and_resize(char.image_path, MAX_WIDTH)
            blocks.append(sep)
            blocks.append(img)
            labels.append(f"角色参考：{char.name}")

        if self._last_scene_path and Path(self._last_scene_path).exists():
            sep = _make_separator(MAX_WIDTH, "上一场景参考")
            img = _load_and_resize(self._last_scene_path, MAX_WIDTH)
            blocks.append(sep)
            blocks.append(img)
            labels.append("上一场景参考")

        if not blocks:
            return None, ""

        total_height = sum(b.height for b in blocks)
        merged = Image.new("RGB", (MAX_WIDTH, total_height), SEPARATOR_COLOR)
        y = 0
        for b in blocks:
            merged.paste(b, (0, y))
            y += b.height

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        merged.save(output_path)

        ref_hint = "【参考图说明】\n本图从上到下依次包含：" + "、".join(labels) + "。\n⚠️ 重要：参考图中的白色分隔条和文字标签（如"角色参考：XXX"）仅用于标注，不要画入最终插画中。请严格参照各角色参考图中的人物外貌、发型、服装风格来绘制对应角色，上一场景参考用于保持构图和环境色调连贯。"
        return output_path, ref_hint
