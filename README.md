# ContextMap

Where does a small model lose the fact in a long document?

ContextMap hides one fact at a set depth inside a document of a set length, asks the model for it, and draws a length x depth accuracy map. A LoRA fine-tune is then measured against the same map.

## Setup

1. Create a Neon project and copy its connection string.
2. `cp .env.example .env` and paste `DATABASE_URL`.
3. Apply the schema: `psql "$DATABASE_URL" -f db/schema.sql`
4. Generate eval cases: `python generator/make_cases.py --split eval --seed 1 --out data/cases_eval.jsonl`
5. Run the scoring tests: `python -m pytest eval/`

## Layout

- `generator/` builds test documents and cases
- `eval/scoring.py` is the single correctness rule, shared by eval and backend
- `db/schema.sql` is the Neon Postgres schema
- `backend/` and `frontend/` come next
