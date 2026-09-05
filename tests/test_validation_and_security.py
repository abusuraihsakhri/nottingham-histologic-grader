"""
Focused tests for input validation, error handling, and security improvements.
"""
import sys
import os
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from nottingham_grader import calculate_metrics, process_batch
from agents.base import AuditTrail, PHIGuard, SecurityException, _resolve_audit_secret


# ---------------------------------------------------------------------------
# Input validation tests for calculate_metrics
# ---------------------------------------------------------------------------

class TestCalculateMetricsValidation:
    def test_reject_nan(self):
        with pytest.raises(ValueError, match="must be a finite number"):
            calculate_metrics(v1=float("nan"), v2=5.0)

    def test_reject_positive_infinity(self):
        with pytest.raises(ValueError, match="must be a finite number"):
            calculate_metrics(v1=float("inf"))

    def test_reject_negative_infinity(self):
        with pytest.raises(ValueError, match="must be a finite number"):
            calculate_metrics(v1=float("-inf"))

    def test_reject_extremely_large_value(self):
        with pytest.raises(ValueError, match="exceeds safe magnitude"):
            calculate_metrics(v1=1.0e15)

    def test_accept_zero(self):
        res = calculate_metrics(v1=0.0, v2=0.0)
        assert res["score"] == 0.0

    def test_accept_negative_values(self):
        res = calculate_metrics(v1=-5.0, v2=-3.0)
        assert isinstance(res["score"], float)

    def test_accept_string_numeric(self):
        res = calculate_metrics(v1="12.5", v2="3.0")
        assert res["score"] > 0

    def test_accept_none_values(self):
        res = calculate_metrics(v1=None, v2=5.0)
        assert res["score"] > 0

    def test_classification_tiers(self):
        low = calculate_metrics(v1=5.0)
        assert low["classification"] == "Low / Standard"

        mid = calculate_metrics(v1=15.0)
        assert mid["classification"] == "Moderate / Intermediate"

        high = calculate_metrics(v1=30.0)
        assert high["classification"] == "High / Severe"


# ---------------------------------------------------------------------------
# File operation error handling tests
# ---------------------------------------------------------------------------

class TestProcessBatchErrorHandling:
    def test_missing_input_file(self, tmp_path):
        missing = str(tmp_path / "nonexistent.csv")
        with pytest.raises(FileNotFoundError):
            process_batch(missing, str(tmp_path / "out.csv"))

    def test_empty_csv_header(self, tmp_path):
        csv_in = tmp_path / "empty.csv"
        csv_in.write_text("", encoding="utf-8")
        with pytest.raises(ValueError, match="no header row"):
            process_batch(str(csv_in), str(tmp_path / "out.csv"))

    def test_creates_output_directory(self, tmp_path):
        csv_in = tmp_path / "in.csv"
        csv_in.write_text("v1,v2\n10.0,5.0\n", encoding="utf-8")
        out_dir = tmp_path / "subdir"
        out_path = out_dir / "results.csv"
        process_batch(str(csv_in), str(out_path))
        assert out_path.exists()


# ---------------------------------------------------------------------------
# Security tests
# ---------------------------------------------------------------------------

class TestAuditSecurity:
    def test_resolve_from_env(self, monkeypatch):
        monkeypatch.setenv("AUDIT_SECRET_KEY", "test-secret-from-env-12345")
        key = _resolve_audit_secret()
        assert key == "test-secret-from-env-12345"

    def test_audit_trail_with_explicit_key(self):
        trail = AuditTrail(secret_key="test-key-for-unit-tests")
        entry = trail.log("test_actor", "test_tier", "TEST_EVENT", {"detail": "value"})
        assert entry["current_hash"] != ""
        assert entry["prev_hash"] == "GENESIS_BLOCK_0000000000000000"
        assert trail.verify_integrity() is True

    def test_audit_trail_chain_integrity(self):
        trail = AuditTrail(secret_key="chain-test-key")
        trail.log("actor1", "tier1", "EVENT_A", {"a": 1})
        trail.log("actor2", "tier2", "EVENT_B", {"b": 2})
        trail.log("actor3", "tier3", "EVENT_C", {"c": 3})
        assert trail.verify_integrity() is True
        assert len(trail.get_trail()) == 3

    def test_phi_guard_blocks_mrn(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Patient MRN-1234567890 lab results")

    def test_phi_guard_blocks_ssn(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("SSN: 123-45-6789")

    def test_phi_guard_blocks_email(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Contact patient@example.com for follow-up")

    def test_phi_guard_allows_clean_text(self):
        # Should not raise
        PHIGuard.assert_no_phi("Specimen KEY-001 analytical assay optimal")

    def test_phi_redaction(self):
        redacted = PHIGuard.redact_phi("Patient MRN-1234567890 results")
        assert "MRN-1234567890" not in redacted
        assert "[REDACTED_IDENTIFIER]" in redacted
