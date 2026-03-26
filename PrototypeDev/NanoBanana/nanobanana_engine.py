import base64
import requests
import re
from pathlib import Path

NanoTOKEN='sk-Z09Qf00CSEme9kUy3Osfvt9UHpRttlEpOVCj6dwaMfmSidQm'
APIURL="https://528ai.cc/v1/chat/completions"
class NanobananaEngine:
    def __init__(self, model="gemini-3.1-flash-image-preview", token=NanoTOKEN):
        self.api_url = "https://528ai.cc/v1/chat/completions"
        self.model = model
        self.token = token

    def generate(self, prompt, input_image=None, output_path="output.png",
                 aspect_ratio="16:9", image_size="2K"):
        """
        生成图片
        :param prompt: 文本提示
        :param input_image: 单张参考图路径 或 多张参考图路径列表（最多14张）
        :param output_path: 输出路径
        :param aspect_ratio: 宽高比，支持 16:9, 9:16, 1:1, 4:3, 3:4 等
        :param image_size: 分辨率，支持 0.5K, 1K, 2K, 4K
        """
        content = [{"type": "text", "text": prompt}]

        # 支持单张或多张参考图
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

        print("⏳ 生成中...")
        resp = requests.post(self.api_url, headers=headers, json=payload, timeout=300)
        resp.raise_for_status()
        result = resp.json()

        content = result["choices"][0]["message"]["content"]

        match = re.search(r"data:image/\w+;base64,([A-Za-z0-9+/=]+)", content)
        if match:
            img_data = base64.b64decode(match.group(1))
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(img_data)
            print(f"✅ 图片已保存到 {output_path}")
            return output_path
        else:
            print("📝 返回内容（非图片）：")
            print(content[:500])
            return None
