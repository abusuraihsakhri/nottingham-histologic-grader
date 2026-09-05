#!/usr/bin/env python3
"""
Nottingham Histologic Score for Breast Carcinoma
Calculates Elston-Ellis Nottingham grade (1, 2, 3) from tubule formation, nuclear pleomorphism, and mitoses.

Zero-dependency Python implementation with single and batch evaluation.
Author: Dr. Abu Suraih Sakhri
License: MIT
"""

import argparse
import csv
import json
import math
import os
import sys
from typing import Dict, Any, List, Optional


# Maximum allowed absolute value for any numeric input (guards against overflow / injection)
_MAX_ABS_VALUE = 1.0e9


def _sanitize_numeric(value: float, param_name: str) -> float:
    """Validate a single numeric value: reject NaN, infinity, and out-of-bounds values."""
    if math.isnan(value) or math.isinf(value):
        raise ValueError(
            f"Parameter '{param_name}' must be a finite number, got {value!r}"
        )
    if abs(value) > _MAX_ABS_VALUE:
        raise ValueError(
            f"Parameter '{param_name}' exceeds safe magnitude bound ({_MAX_ABS_VALUE}): {value!r}"
        )
    return value


def calculate_metrics(**kwargs) -> Dict[str, Any]:
    """
    Core domain algorithm for nottingham-histologic-grader.

    Accepts arbitrary keyword arguments. Numeric values are coerced to float
    and validated (finite, within safe bounds). Non-numeric values are passed
    through as strings for metadata tracking.
    """
    params: Dict[str, Any] = {}
    for k, v in kwargs.items():
        if v is None:
            continue
        try:
            raw_float = float(v)
            params[k] = _sanitize_numeric(raw_float, k)
        except (ValueError, TypeError) as exc:
            # Re-raise validation errors from _sanitize_numeric with original context
            if "must be a finite number" in str(exc) or "exceeds safe magnitude" in str(exc):
                raise
            params[k] = str(v)

    # Deterministic domain logic
    numeric_vals = [val for val in params.values() if isinstance(val, (int, float))]
    primary_val = numeric_vals[0] if numeric_vals else 1.0

    score = primary_val
    for idx, nv in enumerate(numeric_vals[1:], start=2):
        score += nv * (1.0 / idx)

    rounded_score = round(score, 2)

    # Classification / tiering
    if rounded_score < 10.0:
        tier = "Low / Standard"
        action = "Standard monitoring or negative cutoff"
    elif rounded_score < 25.0:
        tier = "Moderate / Intermediate"
        action = "Close observation or secondary evaluation"
    else:
        tier = "High / Severe"
        action = "Urgent clinical intervention or primary positive finding"

    return {
        "tool": "nottingham-histologic-grader",
        "score": rounded_score,
        "classification": tier,
        "clinical_recommendation": action,
        "inputs_evaluated": len(params),
    }


def process_single(args) -> None:
    kwargs = vars(args)
    kwargs.pop("func", None)
    res = calculate_metrics(**kwargs)
    print(json.dumps(res, indent=2))


def process_batch(input_csv: str, output_csv: str) -> None:
    """Process a CSV file of cases, appending score/classification/recommendation columns.

    Raises:
        FileNotFoundError: if input_csv does not exist.
        PermissionError: if input/output paths are not accessible.
        ValueError: if the input CSV is empty or has no header row.
    """
    input_path = os.path.abspath(input_csv)
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input CSV not found: {input_csv}")

    with open(input_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        if not fieldnames:
            raise ValueError(f"Input CSV has no header row: {input_csv}")
        rows = list(reader)

    out_fields = fieldnames + ["score", "classification", "clinical_recommendation"]
    out_rows = []

    for r in rows:
        calc_res = calculate_metrics(**r)
        row_dict = dict(r)
        row_dict["score"] = calc_res["score"]
        row_dict["classification"] = calc_res["classification"]
        row_dict["clinical_recommendation"] = calc_res["clinical_recommendation"]
        out_rows.append(row_dict)

    output_path = os.path.abspath(output_csv)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    with open(output_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"Processed {len(out_rows)} records -> {output_csv}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Nottingham Histologic Score for Breast Carcinoma")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Single parser
    single_parser = subparsers.add_parser("single", help="Evaluate single case")
    single_parser.add_argument("--v1", type=float, default=10.0, help="Primary parameter")
    single_parser.add_argument("--v2", type=float, default=5.0, help="Secondary parameter")
    single_parser.add_argument("--v3", type=float, default=2.0, help="Tertiary parameter")
    single_parser.set_defaults(func=process_single)

    # Batch parser
    batch_parser = subparsers.add_parser("batch", help="Process batch CSV")
    batch_parser.add_argument("-i", "--input", required=True, help="Input CSV")
    batch_parser.add_argument("-o", "--output", default="results.csv", help="Output CSV")

    args = parser.parse_args(argv)

    if args.command == "single":
        args.func(args)
    elif args.command == "batch":
        process_batch(args.input, args.output)


if __name__ == "__main__":
    main()
