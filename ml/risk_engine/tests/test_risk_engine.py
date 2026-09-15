import unittest
from ml.risk_engine.scoring import (
    RiskInput,
    assess_risk,
    explain_risk_score,
    calculate_hazard_score,
    calculate_vulnerability_score,
    calculate_overall_risk,
    classify_risk_level,
    determine_relocation_priority,
)


class TestRiskEngine(unittest.TestCase):
    def test_low_risk_habitation(self):
        data = RiskInput(
            habitation_id="H_LOW",
            rainfall=20.0,
            elevation=500.0,
            slope=8.0,
            population=150,
            historical_events=0,
            infrastructure_access_score=90.0,
            demographic_vulnerability=20.0,
        )
        res = assess_risk(data)
        self.assertEqual(res.risk_level, "LOW")
        self.assertEqual(res.relocation_priority, "MONITOR")
        self.assertLess(res.overall_score, 40.0)

    def test_critical_risk_habitation(self):
        data = RiskInput(
            habitation_id="H_CRIT",
            rainfall=230.0,
            elevation=2800.0,
            slope=42.0,
            population=2400,
            historical_events=7,
            infrastructure_access_score=10.0,
            demographic_vulnerability=85.0,
        )
        res = assess_risk(data)
        self.assertEqual(res.risk_level, "CRITICAL")
        self.assertEqual(res.relocation_priority, "IMMEDIATE")
        self.assertGreaterEqual(res.overall_score, 80.0)

    def test_high_risk_habitation(self):
        data = RiskInput(
            habitation_id="H001",
            rainfall=120.0,
            elevation=850.0,
            slope=32.0,
            population=1250,
            historical_events=4,
            infrastructure_access_score=35.0,
            demographic_vulnerability=60.0,
        )
        res = assess_risk(data)
        self.assertIn(res.risk_level, ["HIGH", "CRITICAL"])

    def test_explain_breakdown_sums_to_overall_score(self):
        data = RiskInput(
            habitation_id="H001",
            rainfall=120.0,
            elevation=850.0,
            slope=32.0,
            population=1250,
            historical_events=4,
            infrastructure_access_score=40.0,
            demographic_vulnerability=55.0,
        )
        exp = explain_risk_score(data)
        self.assertEqual(exp.formula_version, "v1.0")
        self.assertEqual(exp.methodology_reference, "docs/DATA_SOURCES.md#scoring-methodology")
        self.assertTrue(len(exp.factors) > 0)

        # Factor contributions should sum approximately to overall_score (+- 0.5 for rounding)
        sum_contrib = sum(f.contribution for f in exp.factors)
        self.assertAlmostEqual(sum_contrib, exp.overall_score, delta=0.5)

        # Check descending sort order
        for i in range(len(exp.factors) - 1):
            self.assertGreaterEqual(exp.factors[i].contribution, exp.factors[i+1].contribution)

    def test_deterministic_output(self):
        data = RiskInput(
            habitation_id="H_DET",
            rainfall=100.0,
            elevation=1200.0,
            slope=25.0,
            population=800,
            historical_events=2,
        )
        res1 = assess_risk(data)
        res2 = assess_risk(data)
        self.assertEqual(res1.overall_score, res2.overall_score)
        self.assertEqual(res1.hazard_score, res2.hazard_score)
        self.assertEqual(res1.vulnerability_score, res2.vulnerability_score)


if __name__ == "__main__":
    unittest.main()
