import sys
import os
import time
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'NanoBanana'))

from nanobanana_engine import NanobananaEngine


class Illustrator:
    def __init__(self, nano_model: str = "[A]gemini-3-pro-image-preview",
                 nano_token: str = "sk-jscqrhYiCx2JDdHYyLyWjApzVtFPhM4CcOTjzQ89sthUTxn7",
                 max_retries: int = 3, retry_base_wait: int = 30):
        self.engine = NanobananaEngine(model=nano_model, token=nano_token)
        self.max_retries = max_retries
        self.retry_base_wait = retry_base_wait

    def draw(self, description: str, output_path: str,
             reference_images: list[str] | None = None) -> str | None:
        """
        生成插画
        :param description: 场景描述
        :param output_path: 输出路径
        :param reference_images: 参考图列表（最多14张）
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                return self.engine.generate(
                    prompt=description,
                    input_image=reference_images,
                    output_path=output_path,
                    aspect_ratio="16:9",
                    image_size="2K"
                )
            except requests.exceptions.HTTPError as e:
                if e.response is not None and e.response.status_code == 429:
                    wait = self.retry_base_wait * attempt
                    print(f"   ⏳ 429 限流，{wait}秒后重试（第{attempt}/{self.max_retries}次）...")
                    time.sleep(wait)
                else:
                    raise
        print(f"   ❌ 重试{self.max_retries}次后仍失败，跳过此场景")
        return None
