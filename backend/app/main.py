"""ContextMap API: ingest eval results and serve accuracy maps."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from backend.app.db import get_conn, init_schema
from eval.scoring import is_correct

app = FastAPI(title="ContextMap API", version="0.1.0")


class ExperimentIn(BaseModel):
    name: str
    model_id: str
    seed: int = 42
    is_baseline: bool = False
    notes: str | None = None


class ResultIn(BaseModel):
    test_case_id: int
    model_output: str
    latency_ms: int | None = None


class ResultsIn(BaseModel):
    results: list[ResultIn] = Field(min_length=1, max_length=1000)


@app.on_event("startup")
def startup() -> None:
    init_schema()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/experiments")
def list_experiments() -> list[dict]:
    with get_conn() as conn:
        return conn.execute(
            "SELECT id, name, model_id, is_baseline, seed, created_at FROM experiments ORDER BY id"
        ).fetchall()


@app.post("/experiments", status_code=201)
def create_experiment(body: ExperimentIn) -> dict:
    with get_conn() as conn:
        row = conn.execute(
            """INSERT INTO experiments (name, model_id, is_baseline, seed, notes)
               VALUES (%(name)s, %(model_id)s, %(is_baseline)s, %(seed)s, %(notes)s)
               RETURNING id""",
            body.model_dump(),
        ).fetchone()
        conn.commit()
    return {"id": row["id"]}


@app.post("/experiments/{exp_id}/results")
def ingest_results(exp_id: int, body: ResultsIn) -> dict:
    ids = [r.test_case_id for r in body.results]
    with get_conn() as conn:
        exists = conn.execute("SELECT 1 FROM experiments WHERE id = %s", (exp_id,)).fetchone()
        if not exists:
            raise HTTPException(status_code=404, detail="Experiment not found")

        cases = {
            row["id"]: row["expected_answer"]
            for row in conn.execute(
                "SELECT id, expected_answer FROM test_cases WHERE id = ANY(%s)", (ids,)
            ).fetchall()
        }
        missing = [i for i in ids if i not in cases]
        if missing:
            raise HTTPException(status_code=422, detail={"unknown_test_case_ids": missing[:20]})

        # Correctness is computed here, never trusted from the client.
        for r in body.results:
            correct = is_correct(r.model_output, cases[r.test_case_id])
            conn.execute(
                """INSERT INTO results (experiment_id, test_case_id, model_output, is_correct, latency_ms)
                   VALUES (%s, %s, %s, %s, %s)
                   ON CONFLICT (experiment_id, test_case_id)
                   DO UPDATE SET model_output = EXCLUDED.model_output,
                                 is_correct = EXCLUDED.is_correct,
                                 latency_ms = EXCLUDED.latency_ms""",
                (exp_id, r.test_case_id, r.model_output, correct, r.latency_ms),
            )
        conn.commit()
    return {"ingested": len(body.results)}


@app.get("/experiments/{exp_id}/heatmap")
def heatmap(exp_id: int) -> list[dict]:
    with get_conn() as conn:
        return conn.execute(
            """SELECT t.length_bucket, t.needle_pos_pct,
                      AVG(r.is_correct::int) AS accuracy,
                      COUNT(*) AS n
               FROM results r
               JOIN test_cases t ON t.id = r.test_case_id
               WHERE r.experiment_id = %s AND t.split = 'eval'
               GROUP BY t.length_bucket, t.needle_pos_pct
               ORDER BY t.length_bucket, t.needle_pos_pct""",
            (exp_id,),
        ).fetchall()


@app.get("/experiments/{exp_id}/capability")
def capability(exp_id: int) -> dict:
    with get_conn() as conn:
        row = conn.execute(
            """SELECT AVG(r.is_correct::int) AS accuracy, COUNT(*) AS n
               FROM results r
               JOIN test_cases t ON t.id = r.test_case_id
               WHERE r.experiment_id = %s AND t.split = 'capability'""",
            (exp_id,),
        ).fetchone()
    return row
