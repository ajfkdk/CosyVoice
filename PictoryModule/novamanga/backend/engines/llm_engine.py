import json, re
import openai


class LLMEngine:
    _MODEL = "gpt-4o-mini"
    _API_KEY = "sk-poe-6WlZk7uNMWw0r9o6LrFP2nGm1jj1fBFMvzH5ChKOP_8"
    _BASE_URL = "https://api.poe.com/v1"

    def __init__(self):
        self._client = openai.AsyncOpenAI(
            api_key=self._API_KEY,
            base_url=self._BASE_URL,
        )

    async def complete(self, messages: list[dict], system: str | None = None) -> str:
        if system:
            messages = [{"role": "system", "content": system}] + messages
        resp = await self._client.chat.completions.create(
            model=self._MODEL, messages=messages
        )
        return resp.choices[0].message.content

    async def complete_json(self, messages: list[dict], system: str | None = None) -> dict:
        raw = await self.complete(messages, system)
        raw = re.sub(r"^```(?:json)?\n?", "", raw.strip())
        raw = re.sub(r"\n?```$", "", raw)
        return json.loads(raw)
