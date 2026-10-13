"""CLI and CSV support for Nottingham grading of invasive breast carcinoma."""
import argparse
import csv
import json
from pathlib import Path
from grading import grade

def calculate_metrics(**kwargs):
    result = grade(kwargs.get("v1"), kwargs.get("v2"), kwargs.get("v3"))
    result.update(tool="nottingham-histologic-grader",
                  classification="Grade " + str(result["grade"]),
                  clinical_recommendation="Histologic grade only; no treatment recommendation.")
    return result

def process_batch(input_csv, output_csv):
    source, dest = Path(input_csv).resolve(), Path(output_csv).resolve()
    if source == dest:
        raise ValueError("Input and output paths must differ")
    with source.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        if not headers or not all(c in headers for c in ("v1", "v2", "v3")):
            raise ValueError("CSV requires header columns v1,v2,v3")
        if len(set(headers)) != len(headers):
            raise ValueError("Duplicate headers are not supported")
        outputs = ["score", "grade", "classification", "clinical_recommendation"]
        if any(c in headers for c in outputs):
            raise ValueError("Reserved output headers")
        rows = []
        for index, row in enumerate(reader, 2):
            if None in row:
                raise ValueError(f"Row {index}: unexpected extra CSV fields")
            try:
                rows.append({**row, **calculate_metrics(**row)})
            except ValueError as e:
                raise ValueError(f"Row {index}: {e}") from e
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers + outputs, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: ("'" + v if isinstance(v, str) and
                             v.lstrip().startswith(("=", "+", "-", "@")) else v)
                             for k, v in row.items()})
    print(f"Processed {len(rows)} records -> {output_csv}")

def process_single(args):
    """Compatibility entry point for one CLI case."""
    print(json.dumps(calculate_metrics(v1=args.v1, v2=args.v2, v3=args.v3), indent=2))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Nottingham histologic grader")
    sub = parser.add_subparsers(dest="command", required=True)
    single = sub.add_parser("single")
    for c in ("v1", "v2", "v3"):
        single.add_argument("--" + c, type=int, required=True)
    batch = sub.add_parser("batch")
    batch.add_argument("-i", "--input", required=True)
    batch.add_argument("-o", "--output", default="results.csv")
    args = parser.parse_args(argv)
    if args.command == "single":
        process_single(args)
    else:
        process_batch(args.input, args.output)

if __name__ == "__main__":
    main()
