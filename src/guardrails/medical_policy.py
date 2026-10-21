from __future__ import annotations

import re


def evaluate_medical_safety(text: str) -> list[dict[str, str]]:
    violations: list[dict[str, str]] = []
    normalized = text.strip()

    if re.search(r"(你得了|你就是|确诊|直接按.*治疗)", normalized):
        violations.append(
            {
                "rule_id": "definitive_diagnosis",
                "severity": "high",
                "message": "Definitive diagnosis statements are not allowed.",
            }
        )

    if re.search(r"(\d+\s*mg|每\d+小时|每天\d+次|每日\d+次)", normalized):
        violations.append(
            {
                "rule_id": "dosage_advice",
                "severity": "high",
                "message": "Medication dosage/frequency advice is not allowed.",
            }
        )

    if (
        any(keyword in normalized for keyword in ("胸痛", "呼吸困难", "意识模糊"))
        and any(keyword in normalized for keyword in ("不必去急诊", "先观察", "不用去急诊"))
    ):
        violations.append(
            {
                "rule_id": "emergency_deescalation",
                "severity": "high",
                "message": "Emergency de-escalation language is blocked.",
            }
        )

    if (
        any(keyword in normalized for keyword in ("孕妇", "儿童", "小孩", "老年", "老人"))
        and any(keyword in normalized for keyword in ("服用", "用药", "抗生素", "剂量", "mg"))
    ):
        violations.append(
            {
                "rule_id": "special_population_medication",
                "severity": "high",
                "message": "Medication advice for special populations is blocked.",
            }
        )

    return violations
