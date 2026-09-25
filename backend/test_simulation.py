from app import build_local_simulation_result


def test_simulation_uses_policy_specific_hospitalization_data():
    policy_a = {
        "coverage": {"hospitalization": True},
        "financial": {"deductible": "5%"},
        "limits": {"room_rent": "Policy A room limit"},
    }
    policy_b = {
        "coverage": {"hospitalization": False},
        "financial": {"deductible": "Not applicable"},
        "limits": {},
    }

    result_a = build_local_simulation_result("What if I am hospitalized?", policy_a)
    result_b = build_local_simulation_result("What if I am hospitalized?", policy_b)

    assert result_a["coverage_status"] == "covered"
    assert result_a["financial_considerations"]["deductible"] == "5%"
    assert result_b["coverage_status"] == "excluded"
    assert result_b["financial_considerations"]["deductible"] == "Not applicable"


def test_simulation_does_not_invent_missing_policy_values():
    result = build_local_simulation_result("What if I need surgery?", {"coverage": {}, "financial": {}, "limits": {}})

    assert result["coverage_status"] == "not_specified"
    assert result["financial_considerations"]["deductible"] == "Not specified in your uploaded policy."
    assert result["missing_information"]
