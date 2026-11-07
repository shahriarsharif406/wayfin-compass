"""Score bot answers against eval/golden_questions.yaml.

Usage:
  1. Ask each question in eGain's Test AI Agent and paste the answers into a CSV
     with columns: id,answer
  2. python eval/score_answers.py answers.csv
Prints pass/fail per question and an overall score. Needs: pip install pyyaml
"""
import csv
import sys
from pathlib import Path

import yaml

HANDOFF_WORDS = ("person", "agent", "phone", "email", "call")


def score(answers_csv: str) -> int:
    questions = yaml.safe_load((Path(__file__).parent / "golden_questions.yaml").read_text(encoding="utf-8"))
    with open(answers_csv, newline="", encoding="utf-8") as f:
        answers = {row["id"]: row["answer"] for row in csv.DictReader(f)}

    passed = 0
    for q in questions:
        text = answers.get(q["id"], "").lower()
        problems = []
        if not text:
            problems.append("no answer")
        for phrase in q.get("must_include", []):
            if phrase.lower() not in text:
                problems.append(f"missing '{phrase}'")
        for phrase in q.get("must_not_include", []):
            if phrase.lower() in text:
                problems.append(f"contains '{phrase}'")
        if q.get("expect_handoff") and not any(w in text for w in HANDOFF_WORDS):
            problems.append("no handoff offered")
        ok = not problems
        passed += ok
        print(f"{'PASS' if ok else 'FAIL'} {q['id']}  {'; '.join(problems)}")
    print(f"\n{passed}/{len(questions)} passed")
    return 0 if passed == len(questions) else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(score(sys.argv[1]))
