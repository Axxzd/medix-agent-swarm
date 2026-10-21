from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.guardrails.medical_policy import evaluate_medical_safety
from src.guardrails.output_policy import check_required_citations, validate_evidence_sources


def test_definitive_diagnosis_is_blocked() -> None:
    violations = evaluate_medical_safety("根据你的症状，你就是肺炎，直接按肺炎治疗。")
    assert any(v["rule_id"] == "definitive_diagnosis" for v in violations)
    assert any(v["severity"] == "high" for v in violations)


def test_dosage_advice_is_blocked() -> None:
    violations = evaluate_medical_safety("建议布洛芬400mg，每8小时一次，每天3次。")
    assert any(v["rule_id"] == "dosage_advice" for v in violations)


def test_emergency_deescalation_is_blocked() -> None:
    violations = evaluate_medical_safety("胸痛和呼吸困难可以先在家观察，不必去急诊。")
    assert any(v["rule_id"] == "emergency_deescalation" for v in violations)


def test_special_population_medication_advice_is_blocked() -> None:
    violations = evaluate_medical_safety("孕妇可以直接服用该抗生素，每天两次。")
    assert any(v["rule_id"] == "special_population_medication" for v in violations)


def test_required_citation_classes_are_enforced() -> None:
    result = check_required_citations(
        required_classes=["medical_claim", "numeric_threshold", "triage_decision"],
        provided_classes=["medical_claim"],
        allow_safe_close=False,
    )
    assert result["valid"] is False
    assert set(result["missing"]) == {"numeric_threshold", "triage_decision"}


def test_evidence_source_allowlist_passes() -> None:
    violations = validate_evidence_sources(
        [
            {
                "source_type": "guideline",
                "url": "https://www.who.int/news-room",
                "title": "WHO guidance",
            }
        ]
    )
    assert violations == []


def test_evidence_source_denylist_is_blocked() -> None:
    violations = validate_evidence_sources(
        [
            {
                "source_type": "web",
                "url": "https://some-forum.example.com/thread/1",
                "title": "forum post",
            }
        ]
    )
    assert any(v["rule_id"] == "evidence_source_denylist" for v in violations)
