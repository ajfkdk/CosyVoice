import json, uuid, time
from pathlib import Path
from engines.llm_engine import LLMEngine
from engines.nanobanana_engine import NanaBananaEngine
from agents import liu_bei, xiao_ming, xiao_qiao
from db import project_db

llm = LLMEngine()
banana = NanaBananaEngine()


async def handle_liu_bei_parse(project_path: str, payload: dict) -> dict:
    output = await liu_bei.run(llm, payload)
    chapter_id = payload["chapter_id"]
    zones_created = []

    for i, z in enumerate(output["zones"]):
        zone = project_db.create_zone(project_path, chapter_id, {
            "order_index": payload["base_order"] + i,
            "text_content": z["text"],
            "start_char_index": payload["base_offset"] + z["start_char_offset"],
            "end_char_index": payload["base_offset"] + z["end_char_offset"],
            "scene_id": z["scene_id"],
            "emotion_primary": z["emotion_primary"],
            "emotion_intensity": z["emotion_intensity"],
            "characters_present": z.get("characters_present", []),
        })
        zones_created.append(zone["id"])

    project_db.update_chapter(project_path, chapter_id, parse_status="completed")
    return {"zones_created": zones_created}


async def handle_xiao_ming_extract(project_path: str, payload: dict) -> dict:
    output = await xiao_ming.run(llm, payload)
    character_id = payload["character_id"]
    variant_id = str(uuid.uuid4())
    now = int(time.time() * 1000)

    with project_db.get_conn(project_path) as conn:
        conn.execute(
            "UPDATE characters SET personality_tags=?, color_tendency=? WHERE id=?",
            [
                json.dumps(output["personality_tags"], ensure_ascii=False),
                output["color_tendency"],
                character_id,
            ]
        )
        conn.execute(
            "INSERT INTO character_variants(id,character_id,variant_name,"
            "prompt_positive,prompt_negative,trigger_words,appearance_summary,"
            "gen_status,created_at) VALUES (?,?,?,?,?,?,?,?,?)",
            (
                variant_id, character_id, "默认版本",
                output["three_view_prompts"]["front"]["positive"],
                output["three_view_prompts"]["front"]["negative"],
                json.dumps(output.get("trigger_words", []), ensure_ascii=False),
                output["appearance_summary"],
                "pending", now,
            )
        )
    return {"variant_id": variant_id, "output": output}


async def handle_three_view_generate(project_path: str, payload: dict) -> dict:
    variant_id = payload["variant_id"]
    view = payload["view"]
    prompt_pos = payload["prompt_positive"]
    ref_images = payload.get("reference_images", [])

    full_prompt = f"{prompt_pos}, {view} view, full body, white background, character sheet"
    img_bytes = await banana.generate(full_prompt, ref_images or None)

    save_dir = Path(project_path) / "assets" / "characters" / variant_id
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / f"{view}.png"
    save_path.write_bytes(img_bytes)

    col = f"{view}_image_path"
    with project_db.get_conn(project_path) as conn:
        conn.execute(
            f"UPDATE character_variants SET {col}=?, gen_status=? WHERE id=?",
            [str(save_path), "completed", variant_id]
        )
    return {"path": str(save_path)}


async def handle_xiao_qiao_prompt(project_path: str, payload: dict) -> dict:
    output = await xiao_qiao.run(llm, payload)
    zone_id = payload["zone_id"]
    with project_db.get_conn(project_path) as conn:
        conn.execute(
            "UPDATE zones SET prompt_positive=?, prompt_negative=? WHERE id=?",
            [output.get("positive", ""), output.get("negative", ""), zone_id]
        )
    return {"prompt": output}


async def handle_nanobanana_generate(project_path: str, payload: dict) -> dict:
    zone_id = payload["zone_id"]
    prompt_pos = payload["prompt_positive"]
    prompt_neg = payload.get("prompt_negative", "")
    ref_images = payload.get("reference_images", [])

    img_bytes = await banana.generate(prompt_pos, ref_images or None)

    save_dir = Path(project_path) / "assets" / "images"
    save_dir.mkdir(parents=True, exist_ok=True)
    asset_id = str(uuid.uuid4())
    save_path = save_dir / f"{zone_id}_{asset_id}.png"
    save_path.write_bytes(img_bytes)

    now = int(time.time() * 1000)
    with project_db.get_conn(project_path) as conn:
        conn.execute(
            "INSERT INTO image_assets(id,zone_id,file_path,prompt_positive,"
            "prompt_negative,reference_images,created_at) VALUES (?,?,?,?,?,?,?)",
            (asset_id, zone_id, str(save_path), prompt_pos, prompt_neg,
             json.dumps(ref_images), now)
        )
        conn.execute(
            "UPDATE zones SET image_asset_id=? WHERE id=?",
            [asset_id, zone_id]
        )
    return {"asset_id": asset_id, "path": str(save_path)}


HANDLERS = {
    "liu_bei_parse": handle_liu_bei_parse,
    "xiao_ming_extract": handle_xiao_ming_extract,
    "three_view_generate": handle_three_view_generate,
    "xiao_qiao_prompt": handle_xiao_qiao_prompt,
    "nanobanana_generate": handle_nanobanana_generate,
}
