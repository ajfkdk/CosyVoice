GLOBAL_DB_DDL = """
CREATE TABLE IF NOT EXISTS projects (
    id           TEXT PRIMARY KEY,
    name         TEXT NOT NULL,
    path         TEXT NOT NULL UNIQUE,
    created_at   INTEGER NOT NULL,
    updated_at   INTEGER NOT NULL
);
"""

PROJECT_DB_DDL = """
CREATE TABLE IF NOT EXISTS chapters (
    id            TEXT PRIMARY KEY,
    project_id    TEXT NOT NULL,
    title         TEXT NOT NULL,
    order_index   INTEGER NOT NULL,
    raw_text      TEXT NOT NULL DEFAULT '',
    parse_status  TEXT NOT NULL DEFAULT 'idle',
    created_at    INTEGER NOT NULL,
    updated_at    INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS zones (
    id                  TEXT PRIMARY KEY,
    chapter_id          TEXT NOT NULL,
    order_index         INTEGER NOT NULL,
    text_content        TEXT NOT NULL,
    start_char_index    INTEGER NOT NULL DEFAULT 0,
    end_char_index      INTEGER NOT NULL DEFAULT 0,
    scene_id            TEXT,
    emotion_primary     TEXT NOT NULL DEFAULT '平静',
    emotion_intensity   REAL NOT NULL DEFAULT 0.5,
    characters_present  TEXT NOT NULL DEFAULT '[]',
    audio_asset_id      TEXT,
    image_asset_id      TEXT,
    duration_ms         INTEGER,
    prompt_positive     TEXT NOT NULL DEFAULT '',
    prompt_negative     TEXT NOT NULL DEFAULT '',
    created_at          INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS characters (
    id                  TEXT PRIMARY KEY,
    project_id          TEXT NOT NULL,
    name                TEXT NOT NULL,
    raw_description     TEXT NOT NULL DEFAULT '',
    personality_tags    TEXT NOT NULL DEFAULT '[]',
    color_tendency      TEXT NOT NULL DEFAULT '',
    created_at          INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS character_variants (
    id                      TEXT PRIMARY KEY,
    character_id            TEXT NOT NULL,
    variant_name            TEXT NOT NULL,
    prompt_positive         TEXT NOT NULL DEFAULT '',
    prompt_negative         TEXT NOT NULL DEFAULT '',
    trigger_words           TEXT NOT NULL DEFAULT '[]',
    appearance_summary      TEXT NOT NULL DEFAULT '',
    reference_images        TEXT NOT NULL DEFAULT '[]',
    active_from_chapter     INTEGER,
    active_until_chapter    INTEGER,
    front_image_path        TEXT,
    side_image_path         TEXT,
    back_image_path         TEXT,
    gen_status              TEXT NOT NULL DEFAULT 'idle',
    created_at              INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS audio_assets (
    id              TEXT PRIMARY KEY,
    zone_id         TEXT NOT NULL,
    file_path       TEXT NOT NULL,
    duration_ms     INTEGER NOT NULL,
    emotion_params  TEXT NOT NULL DEFAULT '{}',
    created_at      INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS image_assets (
    id                  TEXT PRIMARY KEY,
    zone_id             TEXT NOT NULL,
    file_path           TEXT NOT NULL,
    prompt_positive     TEXT NOT NULL DEFAULT '',
    prompt_negative     TEXT NOT NULL DEFAULT '',
    reference_images    TEXT NOT NULL DEFAULT '[]',
    generation_params   TEXT NOT NULL DEFAULT '{}',
    created_at          INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
    id              TEXT PRIMARY KEY,
    type            TEXT NOT NULL,
    payload         TEXT NOT NULL DEFAULT '{}',
    status          TEXT NOT NULL DEFAULT 'pending',
    retry_count     INTEGER NOT NULL DEFAULT 0,
    max_retries     INTEGER NOT NULL DEFAULT 3,
    error_message   TEXT,
    result          TEXT,
    reference_id    TEXT NOT NULL,
    reference_type  TEXT NOT NULL,
    created_at      INTEGER NOT NULL,
    updated_at      INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_reference ON tasks(reference_id);
"""
