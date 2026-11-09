-- ContextMap schema for Neon (Postgres 16)

CREATE TABLE IF NOT EXISTS experiments (
    id            BIGSERIAL PRIMARY KEY,
    name          TEXT NOT NULL,
    model_id      TEXT NOT NULL,
    is_baseline   BOOLEAN NOT NULL DEFAULT FALSE,
    seed          INTEGER NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    notes         TEXT
);

CREATE TABLE IF NOT EXISTS test_cases (
    id                BIGSERIAL PRIMARY KEY,
    split             TEXT NOT NULL CHECK (split IN ('eval', 'capability', 'train')),
    length_bucket     TEXT,
    doc_tokens        INTEGER NOT NULL,
    needle_pos_pct    SMALLINT,
    question          TEXT NOT NULL,
    expected_answer   TEXT NOT NULL,
    document_path     TEXT NOT NULL,
    UNIQUE (split, document_path)
);

CREATE TABLE IF NOT EXISTS results (
    id                BIGSERIAL PRIMARY KEY,
    experiment_id     BIGINT NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    test_case_id      BIGINT NOT NULL REFERENCES test_cases(id) ON DELETE CASCADE,
    model_output      TEXT NOT NULL,
    is_correct        BOOLEAN NOT NULL,
    latency_ms        INTEGER,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (experiment_id, test_case_id)
);

CREATE INDEX IF NOT EXISTS idx_results_exp ON results(experiment_id);
CREATE INDEX IF NOT EXISTS idx_cases_bucket ON test_cases(length_bucket, needle_pos_pct);
