import openai


class LLMEngine:
    def __init__(self, model: str, api_key: str, base_url: str = "https://api.poe.com/v1"):
        self.model = model
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

    def chat(self, prompt: str, system: str = None) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        return response.choices[0].message.content
