"""
DrishtiSetu — Shared Contract Compliance Test Suite (Member 6)
Validates every endpoint against API Contract (v2).
Reference: API_CONTRACT.md v2 & GLOBAL_AGENT_INSTRUCTIONS.md Rule 23
"""

import unittest
from fastapi.testclient import TestClient
from backend.drishti_server import app


class TestContractComplianceV2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    # 1. Health Check
    def test_section_1_health_check(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get("status"), "ok")
        self.assertEqual(data.get("service"), "drishtisetu")

    # 2. Get Habitation
    def test_section_2_get_habitation(self):
        res = self.client.get("/api/v1/habitations/H001")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        required_fields = [
            "id", "name", "district", "state", "latitude", "longitude",
            "population", "vulnerability_score", "risk_score", "risk_level",
            "relocation_priority"
        ]
        for f in required_fields:
            self.assertIn(f, data, f"Missing field {f} in habitation response")

    # 3. Risk Analysis
    def test_section_3_risk_analyze(self):
        payload = {
            "habitation_id": "H001",
            "rainfall": 120.0,
            "elevation": 850.0,
            "slope": 32.0,
            "population": 1250,
            "historical_events": 4
        }
        res = self.client.post("/api/v1/risk/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        required_fields = [
            "habitation_id", "hazard_score", "vulnerability_score",
            "historical_score", "overall_score", "risk_level", "relocation_priority"
        ]
        for f in required_fields:
            self.assertIn(f, data)
        self.assertIn(data["risk_level"], ["LOW", "MODERATE", "HIGH", "CRITICAL"])
        self.assertIn(data["relocation_priority"], ["MONITOR", "LONG_TERM", "SHORT_TERM", "IMMEDIATE"])

    # 3A. Risk Explainability (NEW v2)
    def test_section_3a_risk_explain(self):
        res = self.client.get("/api/v1/risk/explain/H001")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("habitation_id", data)
        self.assertIn("overall_score", data)
        self.assertIn("factors", data)
        self.assertIn("formula_version", data)
        self.assertIn("methodology_reference", data)
        self.assertTrue(len(data["factors"]) > 0)
        factor = data["factors"][0]
        self.assertIn("name", factor)
        self.assertIn("contribution", factor)
        self.assertIn("weight", factor)

    # 4. Computer Vision Analysis
    def test_section_4_vision_analyze(self):
        payload = {
            "image_url": "computer_vision/demo_assets/chamoli_landslide_post.png",
            "latitude": 30.552,
            "longitude": 79.566
        }
        res = self.client.post("/api/v1/vision/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("image_id", data)
        self.assertIn("detections", data)
        self.assertIn("model_disclosure", data, "Required model_disclosure field missing in vision output")

    # 5 & 6. GIS Risk Layers
    def test_section_5_and_6_gis_layers(self):
        manifest_res = self.client.get("/api/v1/gis/risk-layers")
        self.assertEqual(manifest_res.status_code, 200)
        manifest = manifest_res.json()
        self.assertIn("layers", manifest)
        layer_names = [l["name"] for l in manifest["layers"]]
        self.assertIn("red_zones", layer_names)
        self.assertIn("habitations", layer_names)
        self.assertIn("relocation_sites", layer_names)
        self.assertIn("land_use_conflict", layer_names)

        # Fetch land-use conflict GeoJSON layer
        layer_res = self.client.get("/api/v1/gis/layers/land-use-conflict")
        self.assertEqual(layer_res.status_code, 200)
        geojson = layer_res.json()
        self.assertEqual(geojson.get("type"), "FeatureCollection")

    # 7. RAG Query
    def test_section_7_rag_query_evidence_found(self):
        payload = {"question": "What factors should be considered when planning relocation from a landslide-prone habitation?"}
        res = self.client.post("/api/v1/rag/query", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("answer", data)
        self.assertIn("sources", data)
        self.assertIn("evidence_sufficient", data)
        self.assertTrue(data["evidence_sufficient"])

    def test_section_7_rag_query_insufficient_evidence(self):
        # Demo insufficient-evidence query from DEMO_FLOW.md
        payload = {"question": "What is the sediment transport model used for coastal erosion prediction on the Konkan coast?"}
        res = self.client.post("/api/v1/rag/query", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertFalse(data["evidence_sufficient"])
        self.assertIn("Insufficient evidence", data["answer"])

    # 8. Relocation Recommendation
    def test_section_8_relocation_recommend(self):
        payload = {"habitation_id": "H001"}
        res = self.client.post("/api/v1/relocation/recommend", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        required_fields = [
            "habitation_id", "recommended_site", "suitability_score",
            "site_capacity", "population_to_relocate", "capacity_sufficient",
            "recommendation", "status", "estimated_cost"
        ]
        for f in required_fields:
            self.assertIn(f, data, f"Missing field {f} in relocation response")
        self.assertIn("land_use_conflict", data["recommended_site"])
        self.assertEqual(data["status"], "PROPOSED")

    # 9. Main Decision Analysis Pipeline
    def test_section_9_decision_analyze(self):
        payload = {"habitation_id": "H001"}
        res = self.client.post("/api/v1/decision/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("habitation", data)
        self.assertIn("risk", data)
        self.assertIn("relocation", data)
        self.assertIn("reasoning", data)
        self.assertIn("evidence", data)
        self.assertIn("evidence_sufficient", data)
        self.assertIn("recommendation", data)
        self.assertIn("land_use_conflict", data["relocation"])

    # 9A. Authority Decision Audit Log (NEW v2)
    def test_section_9a_decision_log_roundtrip(self):
        post_payload = {
            "habitation_id": "H001",
            "recommendation_id": "REC_JOSH_TEST",
            "reviewed_by": "District Magistrate, Chamoli",
            "decision": "ACCEPTED",
            "notes": "Contract test approval for Phase 1 evacuation transit shelter."
        }
        post_res = self.client.post("/api/v1/decision/log", json=post_payload)
        self.assertEqual(post_res.status_code, 200)
        logged = post_res.json()
        self.assertIn("id", logged)
        self.assertEqual(logged["decision"], "ACCEPTED")
        self.assertIn("reviewed_at", logged)

        # Verify entry appears in GET history
        get_res = self.client.get("/api/v1/decision/log/H001")
        self.assertEqual(get_res.status_code, 200)
        history = get_res.json()
        self.assertIsInstance(history, list)
        self.assertGreater(len(history), 0)
        self.assertEqual(history[0]["id"], logged["id"])


if __name__ == "__main__":
    unittest.main()
