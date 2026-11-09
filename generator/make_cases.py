"""Build needle-in-a-haystack eval cases for ContextMap.

Example:
    python generator/make_cases.py --split eval --seed 1 --per-cell 50 --out data/cases_eval.jsonl
"""
import argparse
import json
import random
from pathlib import Path

FILLER = [
    "The committee reviewed the quarterly schedule and noted no changes.",
    "Storage racks in the north hall were moved to make room for new boxes.",
    "The weather report expected light rain and steady winds through the week.",
    "Visitors are asked to sign the register at the front desk before entering.",
    "Maintenance crews checked the water pumps and replaced two worn filters.",
    "The library extended its opening hours during the examination period.",
    "A new supplier was listed in the catalogue after a short trial order.",
    "Staff training sessions will continue on the second floor next month.",
]

LENGTHS = {"2K": 2000, "8K": 8000, "16K": 16000}  # approximate tokens
POSITIONS = [10, 50, 90]                          # percent of document
WORDS_PER_TOKEN = 0.75                            # rough English estimate


def random_id(rng: random.Random) -> str:
    letters = "".join(rng.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=2))
    return f"{letters}-{rng.randint(100, 999)}"


def random_code(rng: random.Random) -> str:
    letters = "".join(rng.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=2))
    return f"{letters}-{rng.randint(1, 9)}{rng.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}{rng.randint(0, 9)}"


def build_document(rng: random.Random, target_tokens: int, pos_pct: int, needle: str) -> str:
    target_words = int(target_tokens * WORDS_PER_TOKEN)
    sentences = []
    words = 0
    while words < target_words:
        s = rng.choice(FILLER)
        sentences.append(s)
        words += len(s.split())
    insert_at = int(len(sentences) * pos_pct / 100)
    sentences.insert(insert_at, needle)
    return "\n".join(sentences)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", default="eval", choices=["eval", "capability", "train"])
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--per-cell", type=int, default=50)
    parser.add_argument("--docs-dir", default="data/docs")
    parser.add_argument("--out", default="data/cases_eval.jsonl")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    docs_dir = Path(args.docs_dir) / args.split
    docs_dir.mkdir(parents=True, exist_ok=True)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with out_path.open("w", encoding="utf-8") as out:
        for bucket, tokens in LENGTHS.items():
            for pos in POSITIONS:
                for i in range(args.per_cell):
                    vault = random_id(rng)
                    code = random_code(rng)
                    needle = f"The access code for vault {vault} is {code}."
                    text = build_document(rng, tokens, pos, needle)
                    doc_path = docs_dir / f"{bucket}_{pos}_{i:03d}.txt"
                    doc_path.write_text(text, encoding="utf-8")
                    row = {
                        "split": args.split,
                        "length_bucket": bucket,
                        "doc_tokens": tokens,
                        "needle_pos_pct": pos,
                        "question": f"What is the access code for vault {vault}?",
                        "expected_answer": code,
                        "document_path": str(doc_path),
                    }
                    out.write(json.dumps(row, ensure_ascii=False) + "\n")
                    count += 1
    print(f"Wrote {count} cases to {out_path}")


if __name__ == "__main__":
    main()
