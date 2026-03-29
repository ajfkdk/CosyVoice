import base64
import requests
import re
import time
from pathlib import Path

NanoTOKEN='sk-wLxCvAqR3oYP1AjmaMalHgrK04o2pDINdA732Euuix1r72FU'
APIURL="https://yinli.one/v1/chat/completions"
NANOMODEL="gemini-3-pro-image-preview"

class NanobananaEngine:
    def __init__(self, model=NANOMODEL, token=NanoTOKEN, max_retries=5):
        self.api_url = APIURL
        self.model = model
        self.token = token
        self.max_retries = max_retries

    def generate(self, prompt, input_image=None, output_path="output.png",
                 aspect_ratio="16:9", image_size="2K"):
        """生成图片，带重试机制"""
        for attempt in range(1, self.max_retries + 1):
            try:
                return self._generate_once(prompt, input_image, output_path, aspect_ratio, image_size)
            except Exception as e:
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt
                    print(f"⚠️ 生成失败 (尝试 {attempt}/{self.max_retries}): {e}")
                    print(f"   等待 {wait_time}秒后重试...")
                    time.sleep(wait_time)
                else:
                    print(f"❌ 生成失败，已重试 {self.max_retries} 次: {e}")
                    raise

    def _generate_once(self, prompt, input_image, output_path, aspect_ratio, image_size):
        content = [{"type": "text", "text": prompt}]

        images = [input_image] if isinstance(input_image, str) else (input_image or [])
        for img_path in images:
            if img_path:
                with open(img_path, "rb") as f:
                    img_b64 = base64.b64encode(f.read()).decode("utf-8")
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{img_b64}"}
                })

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": content}],
            "stream": False,
            "aspectRatio": aspect_ratio,
            "imageSize": image_size
        }

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        resp = requests.post(self.api_url, headers=headers, json=payload, timeout=300, verify=False)
        resp.raise_for_status()
        result = resp.json()

        content = result["choices"][0]["message"]["content"]

        match = re.search(r"data:image/\w+;base64,([A-Za-z0-9+/=]+)", content)
        if match:
            img_data = base64.b64decode(match.group(1))
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(img_data)
            return output_path
        else:
            raise Exception(f"未返回图片数据: {content[:200]}")
