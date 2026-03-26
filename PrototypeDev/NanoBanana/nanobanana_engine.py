import base64
import requests
import re
from pathlib import Path


class NanobananaEngine:
    def __init__(self, model="[A]gemini-3-pro-image-preview", token="sk-jscqrhYiCx2JDdHYyLyWjApzVtFPhM4CcOTjzQ89sthUTxn7"):
        self.api_url = "https://api.mmw.ink/v1/chat/completions"
        self.model = model
        self.token = token

    def generate(self, prompt, input_image=None, output_path="output.png"):
        content = [{"type": "text", "text": prompt}]

        if input_image:
            with open(input_image, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode("utf-8")
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{img_b64}"}
            })

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": content}],
            "stream": False
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
