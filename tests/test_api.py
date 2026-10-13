from fastapi.testclient import TestClient
from agents.api import app

client = TestClient(app)

def test_grade_api():
    response = client.post("/api/grade", json={"v1":1,"v2":2,"v3":3})
    assert response.status_code == 200
    assert response.json()["grade"] == 2
    assert response.json()["score"] == 6

def test_grade_api_rejects_invalid_input():
    for payload in ({"v1":0,"v2":2,"v3":3},
                    {"v1":1,"v2":2},
                    {"v1":1.5,"v2":2,"v3":3}):
        assert client.post("/api/grade",json=payload).status_code == 422

def test_static_browser_assets():
    for path in ("/","/core.js","/batch.js","/style.css","/app.js"):
        response = client.get(path)
        assert response.status_code == 200
    assert "Histologic grade calculator" in client.get("/").text

def test_health_does_not_claim_clinical_validation():
    assert "legacy_audit" in client.get("/health").json()
