STATUSES = [
    "Not Assessed",
    "Not Applicable",
    "Compliant",
    "Partially Compliant",
    "Non-Compliant",
    "Pending Verification",
]


def risk_score(likelihood: int, impact: int):
    if not 1 <= likelihood <= 5 or not 1 <= impact <= 5:
        raise ValueError("Risk dimensions must be between 1 and 5")
    score = likelihood * impact
    return {
        "score": score,
        "band": "Critical"
        if score >= 17
        else "High"
        if score >= 10
        else "Moderate"
        if score >= 5
        else "Low",
    }


def metrics(assessments, evidence_counts):
    eligible = [
        a for a in assessments if a.status != "Not Applicable" or a.stage != "Approved"
    ]
    assessed = [
        a for a in eligible if a.status not in ("Not Assessed", "Pending Verification")
    ]
    verified = [a for a in eligible if a.stage == "Approved"]
    # Unassessed eligible controls contribute zero; only approved ratings contribute credit.
    credit = sum(
        {"Compliant": 1, "Partially Compliant": 0.5}.get(a.status, 0) for a in verified
    )
    pct = lambda n: round(100 * n / len(eligible), 1) if eligible else None
    return {
        "eligible": len(eligible),
        "approved_na": len(assessments) - len(eligible),
        "score": pct(credit),
        "coverage": pct(len(assessed)),
        "verified": pct(len(verified)),
        "evidence_coverage": pct(
            sum(bool(evidence_counts.get(a.id)) for a in eligible)
        ),
        "method": "Equal weight v1; approved ratings only: compliant=1, partial=0.5, others=0. Ordinal management indicator, not certification.",
    }
