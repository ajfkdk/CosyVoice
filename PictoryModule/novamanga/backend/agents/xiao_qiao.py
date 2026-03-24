from engines.llm_engine import LLMEngine

SYSTEM = """
You are XiaoQiao, an expert at writing Stable Diffusion image generation prompts for comic/manga panels based on Chinese novel scenes.

Rules:
1. Output ENGLISH prompts only, comma-separated tags
2. positive tag order: character trigger words → character appearance & action → facial expression → scene/background → lighting & atmosphere → art style & quality
3. When emotion_intensity > 0.7, add: dramatic lighting, intense shadows, cinematic composition
4. Always end positive with: masterpiece, best quality, highly detailed, cinematic
5. negative always includes: text, watermark, blurry, low quality, deformed, ugly, duplicate
6. Use the full story context to understand the narrative background and make prompts more specific and vivid
7. Scene description must be specific and concrete (e.g. "dark abandoned warehouse with wooden crates, dusty air, single spotlight from above" rather than just "warehouse")
8. Character actions and expressions must match the scene emotion precisely

Output strict JSON only:
{
  "positive": "comma separated english tags",
  "negative": "comma separated english tags",
  "reference_image_paths": []
}
"""


async def run(llm: LLMEngine, payload: dict) -> dict:
    chars_info = "\n".join(
        f"- {c['name']}: trigger_words={c.get('trigger_words', [])}, appearance={c.get('appearance_summary', '')}"
        for c in payload.get("character_variants", [])
    )
    story_context = payload.get("story_context", "")
    scene_context = payload.get("scene_context", "")

    user_msg = f"""
## Full Story Context (for understanding the narrative background):
{story_context or scene_context or "(no context provided)"}

## Current Panel to Generate:
- Scene text: {payload['zone_text']}
- Primary emotion: {payload['emotion_primary']} (intensity: {payload.get('emotion_intensity', 0.5)})
- Characters present:
{chars_info or "  (no named characters in this panel)"}

Generate a detailed, vivid Stable Diffusion prompt for this specific panel based on the full story context above.
"""
    return await llm.complete_json(
        [{"role": "user", "content": user_msg}],
        system=SYSTEM
    )
