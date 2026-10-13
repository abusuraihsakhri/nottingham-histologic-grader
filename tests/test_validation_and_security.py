import pytest
from nottingham_grader import calculate_metrics, process_batch
from agents.base import AuditTrail, PHIGuard, SecurityException, _resolve_audit_secret

@pytest.mark.parametrize("value",[None,0,-1,4,1.5,float("nan"),float("inf"),float("-inf"),1e15])
def test_invalid_scores(value):
    with pytest.raises(ValueError):
        calculate_metrics(v1=value,v2=1,v3=1)

def test_string_scores():
    assert calculate_metrics(v1="1",v2="2",v3="3")["score"]==6

def test_missing_csv(tmp_path):
    with pytest.raises(FileNotFoundError):
        process_batch(tmp_path/"missing.csv",tmp_path/"out.csv")

def test_csv_validation(tmp_path):
    inp=tmp_path/"in.csv"
    inp.write_text("")
    with pytest.raises(ValueError,match="v1,v2,v3"):
        process_batch(inp,tmp_path/"out.csv")
    inp.write_text("v1,v2,v3\n1,2,3\n")
    process_batch(inp,tmp_path/"nested"/"out.csv")
    assert (tmp_path/"nested"/"out.csv").exists()

def test_audit_key_env(monkeypatch):
    monkeypatch.setenv("AUDIT_SECRET_KEY","test-secret")
    assert _resolve_audit_secret()=="test-secret"

def test_audit_tampering():
    trail=AuditTrail(secret_key="unit-test-only")
    trail.log("actor","tier","EVENT",{"key":"value"})
    assert trail.verify_integrity()
    trail.logs[0]["event_type"]="TAMPERED"
    assert not trail.verify_integrity()

def test_phi_guard():
    for value in ["MRN-123456","patient@example.org","123-45-6789"]:
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi(value)
    assert "MRN-123456" not in PHIGuard.redact_phi("MRN-123456")
