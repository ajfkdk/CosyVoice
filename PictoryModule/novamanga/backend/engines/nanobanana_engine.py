import base64, re
from pathlib import Path
import httpx


class NanaBananaEngine:
    _MODEL = "[A]gemini-3-pro-image-preview"
    _API_KEY = "sk-jscqrhYiCx2JDdHYyLyWjApzVtFPhM4CcOTjzQ89sthUTxn7"
    _API_URL = "https://api.mmw.ink/v1/chat/completions"

    async def generate(
        self,
        prompt: str,
        reference_images: list[str] | None = None,
    ) -> bytes:
        content: list[dict] = [{"type": "text", "text": prompt}]

        for path in (reference_images or []):
            data = Path(path).read_bytes()
            ext = Path(path).suffix.lstrip(".") or "png"
            b64 = base64.b64encode(data).decode()
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/{ext};base64,{b64}"}
            })

        payload = {
            "model": self._MODEL,
            "messages": [{"role": "user", "content": content}],
        }
        headers = {
            "Authorization": f"Bearer {self._API_KEY}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(self._API_URL, headers=headers, json=payload)
            resp.raise_for_status()

        content_str = resp.json()["choices"][0]["message"]["content"]
        match = re.search(r"data:image/\w+;base64,([A-Za-z0-9+/=]+)", content_str)
        if not match:
            raise ValueError(f"NanaBanana 未返回图片，原始内容: {content_str[:300]}")
        return base64.b64decode(match.group(1))
