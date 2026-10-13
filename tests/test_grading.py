import csv
import pytest
from grading import grade
from nottingham_grader import calculate_metrics, process_batch

@pytest.mark.parametrize("scores,total,level", [
    ((1,1,1),3,1), ((1,2,2),5,1), ((2,2,2),6,2),
    ((2,2,3),7,2), ((2,3,3),8,3), ((3,3,3),9,3)])
def test_grade_boundaries(scores,total,level):
    assert grade(*scores) == {"score":total,"grade":level}

@pytest.mark.parametrize("invalid", [None, "", "abc", True, 0, 4, -1, 1.5, float("nan"), float("inf")])
def test_invalid(invalid):
    with pytest.raises(ValueError):
        grade(invalid,1,1)

def test_extra_numeric_metadata_ignored():
    assert calculate_metrics(v1=1,v2=1,v3=1,case_id="999")["score"] == 3

def test_csv_and_formula_safety(tmp_path):
    source, target = tmp_path/"in.csv", tmp_path/"results.csv"
    source.write_text("case_id,v1,v2,v3\n=1+1,1,1,1\nX,3,3,3\n",encoding="utf-8")
    process_batch(source,target)
    with target.open(newline="") as f:
        rows=list(csv.DictReader(f))
    assert [r["grade"] for r in rows] == ["1","3"]
    assert rows[0]["case_id"]=="'=1+1"
    with pytest.raises(ValueError,match="differ"):
        process_batch(source,source)

def test_bad_row_does_not_overwrite_output(tmp_path):
    source,target=tmp_path/"in.csv",tmp_path/"out.csv"
    target.write_text("original",encoding="utf-8")
    source.write_text("v1,v2,v3\n1,1,9\n",encoding="utf-8")
    with pytest.raises(ValueError,match="Row 2"):
        process_batch(source,target)
    assert target.read_text()=="original"
