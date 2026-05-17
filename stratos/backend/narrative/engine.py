from datetime import UTC, datetime

from stratos.config import load_config
from stratos.database.db import connect, upsert_job
from stratos.backend.signals.macro import derive_macro_conditions


def _matches(conditions: dict[str, str], required: dict[str, str]) -> float:
    if not required:
        return 0.0
    hits = sum(1 for key, value in required.items() if conditions.get(key) == value)
    return hits / len(required)


def evaluate_narratives() -> list[dict]:
    conditions = derive_macro_conditions()
    rules = load_config("macro_rules.yaml").get("rules", {})
    narratives = []
    for name, rule in rules.items():
        match = _matches(conditions, rule.get("conditions", {}))
        if match >= 0.67:
            narratives.append({
                "rule_name": name,
                "confidence": round(match * float(rule.get("confidence", 0.6)), 2),
                "narrative": rule.get("narrative", ""),
                "implication": rule.get("implication", ""),
            })
    return sorted(narratives, key=lambda item: item["confidence"], reverse=True)


def run_narrative_job() -> None:
    now = datetime.now(UTC).isoformat()
    narratives = evaluate_narratives()
    with connect() as conn:
        conn.execute("DELETE FROM narratives")
        for item in narratives:
            conn.execute(
                "INSERT INTO narratives(rule_name, as_of, confidence, narrative, implication) VALUES(?, ?, ?, ?, ?)",
                (item["rule_name"], now, item["confidence"], item["narrative"], item["implication"]),
            )
    upsert_job("narratives", "success", now, f"{len(narratives)} narratives active")
