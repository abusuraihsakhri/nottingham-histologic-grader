"""Validated Nottingham score for invasive breast carcinoma."""
import math

def grade(tubules, nuclei, mitoses):
    """Components each scored 1–3; mitotic score must be field-calibrated."""
    scores = []
    for name, value in zip(("tubules", "nuclei", "mitoses"), (tubules, nuclei, mitoses)):
        if isinstance(value, bool):
            raise ValueError(name + " must be 1, 2 or 3")
        try:
            n = float(value)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError(name + " must be 1, 2 or 3") from exc
        if not math.isfinite(n) or n not in (1, 2, 3):
            raise ValueError(name + " must be 1, 2 or 3")
        scores.append(int(n))
    total = sum(scores)
    level = 1 if total <= 5 else (2 if total <= 7 else 3)
    return {"score": total, "grade": level}
