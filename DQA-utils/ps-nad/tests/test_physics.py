import pytest
import json
import os
from ps_nad.physics_gate import PhysicsGate

@pytest.fixture
def mock_rules(tmp_path):
    """Creates a temporary rules file for testing."""
    rules = {
        "PM2.5": {
            "min_value": 0,
            "max_value": 500,
            "max_delta_per_hour": 50
        }
    }
    # Ensure the path mimics the expected structure
    d = tmp_path / "src"
    d.mkdir(parents=True, exist_ok=True)
    p = d / "physics_rules.json"
    p.write_text(json.dumps(rules))
    return str(p)

def test_hard_limit_validation(mock_rules):
    """Test that values outside min/max are invalidated."""
    gate = PhysicsGate(rules_path=mock_rules)
    
    # Valid value
    res_valid = gate.validate_event("PM2.5", 25.0, 20.0)
    assert res_valid['valid'] == True
    
    # Invalid (Negative)
    res_invalid = gate.validate_event("PM2.5", -5.0, 10.0)
    assert res_invalid['valid'] == False
    assert res_invalid['physical_score'] == 0.0
    assert "Reasonableness Error" in res_invalid['reason']

def test_stability_validation(mock_rules):
    """
    Test the stability logic.
    Note: Current logic returns False only if delta > max_delta * 2.
    """
    gate = PhysicsGate(rules_path=mock_rules)
    
    # 1. Extreme Jump: 20 to 150 (Delta 130). 
    # Limit is 50, threshold for False is 100.
    res_extreme = gate.validate_event("PM2.5", 150.0, 20.0)
    assert res_extreme['valid'] == False
    assert res_extreme['physical_score'] == 0.1
    assert "Stability Error" in res_extreme['reason']

    # 2. Moderate Jump: 20 to 80 (Delta 60).
    # Over the limit (50) but under the 'Hard Failure' threshold (100).
    # This should return valid=True but could be flagged by score in real scenarios.
    res_mod = gate.validate_event("PM2.5", 80.0, 20.0)
    assert res_mod['valid'] == True

def test_proxy_correlation_validation(mock_rules):
    """Test that proxy data (like wind) can influence validation."""
    # We update the mock rules to include a wind correlation
    with open(mock_rules, 'r') as f:
        rules = json.load(f)
    rules['PM2.5']['wind_speed_correlation'] = 'negative'
    with open(mock_rules, 'w') as f:
        json.dump(rules, f)

    gate = PhysicsGate(rules_path=mock_rules)
    
    # High wind (20m/s) with a PM spike (20 to 80) should be highly suspicious
    res = gate.validate_event("PM2.5", 80.0, 20.0, proxy_data={'wind_speed': 20.0})
    assert res['valid'] == False
    assert "Correlation Error" in res['reason']