"""
Comprehensive End-to-End Test Suite for CivicEase AI REST API.
Validates all endpoints using FastAPI TestClient.
"""
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from api import api_app

client = TestClient(api_app)

def run_api_tests():
    print("=" * 65)
    print(" CIVICEASE AI — COMPLETE REST API END-TO-END VERIFICATION")
    print("=" * 65)

    # 1. System Endpoints
    print("\n[1/7] Testing Root & Health Endpoints...")
    r = client.get("/")
    assert r.status_code == 200, f"Root failed: {r.text}"
    assert r.json()["app"] == "CivicEase AI"
    print("  ✓ GET / -> 200 OK (App: CivicEase AI)")

    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "healthy"
    print("  ✓ GET /health -> 200 OK (Status: healthy)")

    # 2. Authentication Endpoints
    print("\n[2/7] Testing Authentication Endpoints...")
    r = client.get("/api/auth/demo-users")
    assert r.status_code == 200
    assert len(r.json()) >= 2
    print(f"  ✓ GET /api/auth/demo-users -> {len(r.json())} demo accounts available")

    # Login Citizen
    r = client.post("/api/auth/login", json={"username": "citizen", "password": "citizen123"})
    assert r.status_code == 200, f"Login failed: {r.text}"
    user_data = r.json()
    assert user_data["role"] == "citizen"
    print(f"  ✓ POST /api/auth/login -> 200 OK (Authenticated: {user_data['full_name']}, Role: {user_data['role']})")

    # Login Auditor
    r = client.post("/api/auth/login", json={"username": "auditor", "password": "auditor123"})
    assert r.status_code == 200
    assert r.json()["role"] == "auditor"
    print("  ✓ POST /api/auth/login (Auditor) -> 200 OK")

    # 3. Sample Documents & Direct Text Analysis
    print("\n[3/7] Testing Document Analysis Endpoints...")
    r = client.get("/api/documents/samples")
    assert r.status_code == 200
    samples = r.json()
    assert len(samples) >= 1
    print(f"  ✓ GET /api/documents/samples -> Found {len(samples)} sample files: {[s['filename'] for s in samples]}")

    # Analyze Sample PDF
    target_sample = samples[0]["filename"]
    r = client.post(f"/api/documents/analyze-sample/{target_sample}?user_id=1")
    assert r.status_code == 200, f"Analyze sample failed: {r.text}"
    analysis_data = r.json()
    analysis_id = analysis_data["analysis_id"]
    print(f"  ✓ POST /api/documents/analyze-sample/{target_sample} -> 200 OK")
    print(f"    - Score: {analysis_data['composite_score']}/100 ({analysis_data['score_tier']})")
    print(f"    - Issues Detected: {analysis_data['total_issues_count']}")

    # Direct Raw Text Analysis
    r = client.post("/api/documents/analyze-text", json={
        "title": "Elderly Care Grant",
        "text_content": "The applicant shall furnish the requisite documents to the competent authority within the prescribed period. Fee: No application fee is required.",
        "user_id": 1
    })
    assert r.status_code == 200
    print(f"  ✓ POST /api/documents/analyze-text -> 200 OK (Score: {r.json()['composite_score']}/100)")

    # 4. Mode-Specific Tailored Views
    print("\n[4/7] Testing Citizen & Auditor Mode Views...")
    # Citizen View
    r = client.get(f"/api/analysis/{analysis_id}/citizen-view")
    assert r.status_code == 200
    citizen_view = r.json()
    assert "how_to_apply_steps" in citizen_view and len(citizen_view["how_to_apply_steps"]) > 0
    assert "plain_explanation_tamil" in citizen_view and len(citizen_view["plain_explanation_tamil"]) > 0
    print(f"  ✓ GET /api/analysis/{analysis_id}/citizen-view -> 200 OK")
    print(f"    - Service: {citizen_view['service_name'][:50]}...")
    print(f"    - Steps: {len(citizen_view['how_to_apply_steps'])} application steps")
    print(f"    - Checklist: {len(citizen_view['required_documents_checklist'])} required docs")
    print(f"    - Tamil Translation: Present ({len(citizen_view['plain_explanation_tamil'])} chars)")

    # Auditor View
    r = client.get(f"/api/analysis/{analysis_id}/auditor-view")
    assert r.status_code == 200
    auditor_view = r.json()
    assert "score_breakdown" in auditor_view
    assert "severity_summary" in auditor_view
    print(f"  ✓ GET /api/analysis/{analysis_id}/auditor-view -> 200 OK")
    print(f"    - Score Breakdown: {auditor_view['score_breakdown']}")
    print(f"    - Severity Summary: {auditor_view['severity_summary']}")
    print(f"    - Recommendations: {len(auditor_view['prioritized_recommendations'])} actionable items")

    # Auditor Filter by Severity
    r_filtered = client.get(f"/api/analysis/{analysis_id}/auditor-view?severity=HIGH")
    assert r_filtered.status_code == 200
    print(f"  ✓ GET /api/analysis/{analysis_id}/auditor-view?severity=HIGH -> Filtered {r_filtered.json()['filtered_issues_count']} high severity issues")

    # 5. Language Simplification Endpoint
    print("\n[5/7] Testing Language Simplification & Tamil Translation...")
    r = client.post("/api/simplify", json={
        "text": "The applicant shall furnish the requisite documents to the competent authority.",
        "context_topic": "Pension Scheme"
    })
    assert r.status_code == 200
    simp_data = r.json()
    assert "simplified_english" in simp_data and len(simp_data["simplified_english"]) > 0
    assert "tamil_translation" in simp_data and len(simp_data["tamil_translation"]) > 0
    print(f"  ✓ POST /api/simplify -> 200 OK")
    print(f"    - Simplified English: \"{simp_data['simplified_english']}\"")
    print(f"    - Tamil: \"{simp_data['tamil_translation'][:60]}...\"")

    # 6. Report Export Endpoints
    print("\n[6/7] Testing PDF and Markdown Report Export...")
    r_pdf = client.get(f"/api/reports/{analysis_id}/pdf")
    assert r_pdf.status_code == 200
    assert r_pdf.headers.get("content-type") == "application/pdf"
    assert len(r_pdf.content) > 500
    print(f"  ✓ GET /api/reports/{analysis_id}/pdf -> 200 OK (Binary PDF: {len(r_pdf.content)} bytes)")

    r_md = client.get(f"/api/reports/{analysis_id}/markdown")
    assert r_md.status_code == 200
    assert "text/markdown" in r_md.headers.get("content-type", "")
    assert len(r_md.text) > 500
    print(f"  ✓ GET /api/reports/{analysis_id}/markdown -> 200 OK (Markdown text: {len(r_md.text)} chars)")

    # 7. History Endpoint
    print("\n[7/7] Testing History Endpoint...")
    r_hist = client.get("/api/history?limit=5")
    assert r_hist.status_code == 200
    hist = r_hist.json()
    print(f"  ✓ GET /api/history -> Found {len(hist)} previous analysis records")

    print("\n" + "=" * 65)
    print(" ALL REST API ENDPOINTS VERIFIED & WORKING PERFECTLY (100%)! ")
    print("=" * 65)

if __name__ == "__main__":
    run_api_tests()
