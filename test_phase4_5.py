"""
Comprehensive Test Suite for Phase 4 (Database Integration) and Phase 5 (Testing)
"""
import os
import sqlite3
from app import (
    app,
    check_blood_compatibility,
    init_db,
    save_history,
    get_history,
    clear_history_db,
    BLOOD_COMPATIBILITY,
    DB_PATH
)

def run_all_tests():
    print("=" * 65)
    print("RUNNING PHASE 4 & PHASE 5 COMPREHENSIVE TEST SUITE")
    print("=" * 65)

    client = app.test_client()

    # -------------------------------------------------------------
    # 1. Database Operations & History Tests
    # -------------------------------------------------------------
    print("\n[TEST GROUP 1] Database Integration (SQLite & History Table)")
    
    # Reset history for a clean test run
    clear_history_db()
    assert len(get_history()) == 0, "Database should be empty after clear_history_db()"
    print("  [PASS] clear_history_db() works properly.")

    # Test saving a record directly
    save_history("O-", "AB+", "Compatible", "compatible")
    history_records = get_history()
    assert len(history_records) == 1, f"Expected 1 record, got {len(history_records)}"
    assert history_records[0]["donor"] == "O-"
    assert history_records[0]["recipient"] == "AB+"
    assert history_records[0]["result"] == "Compatible"
    assert history_records[0]["status"] == "compatible"
    assert "timestamp" in history_records[0]
    print("  [PASS] save_history() correctly persists record with timestamp.")

    # -------------------------------------------------------------
    # 2. Test Combinations Specified in Phase 5
    # -------------------------------------------------------------
    print("\n[TEST GROUP 2] Donor / Recipient Combinations from Specification")
    
    test_cases = [
        # (donor, recipient, expected_compatible, label)
        ("O\u2212", "AB+", True, "Compatible"),
        ("A+", "B+", False, "Not compatible"),
        ("B+", "AB+", True, "Compatible"),
        ("AB+", "O\u2212", False, "Not compatible"),
        ("O+", "A+", True, "Compatible"),
    ]

    for donor, recipient, expected_compat, label in test_cases:
        res = check_blood_compatibility(donor, recipient)
        status_text = "Compatible" if res["compatible"] else "Not compatible"
        assert res["compatible"] == expected_compat, (
            f"FAIL: {donor} -> {recipient} gave {status_text}, expected {label}"
        )
        safe_donor = donor.replace("\u2212", "-")
        safe_recipient = recipient.replace("\u2212", "-")
        print(f"  [PASS] Donor {safe_donor:<4} -> Recipient {safe_recipient:<4} : {status_text} (matches expected)")

    # Special check on A- and AB-
    res_a_ab = check_blood_compatibility("A\u2212", "AB\u2212")
    res_ab_a = check_blood_compatibility("AB\u2212", "A\u2212")
    print(f"\n  [ANALYSIS: A- vs AB-]:")
    print(f"  * Donor A-  -> Recipient AB- : {'Compatible' if res_a_ab['compatible'] else 'Not compatible'}")
    print(f"    (Per Phase 2 rules, A- can donate to A-, A+, AB-, AB+)")
    print(f"  * Donor AB- -> Recipient A-  : {'Compatible' if res_ab_a['compatible'] else 'Not compatible'}")
    print(f"    (Recipient A- has anti-B antibodies against donor B antigen)")

    # -------------------------------------------------------------
    # 3. Test Empty Selections
    # -------------------------------------------------------------
    print("\n[TEST GROUP 3] Empty Selections Handling")
    empty_cases = [
        ("", "AB+", "empty donor"),
        ("A+", "", "empty recipient"),
        ("", "", "both empty"),
        (None, "O+", "None donor"),
        ("B-", None, "None recipient"),
    ]
    for d, r, desc in empty_cases:
        res = check_blood_compatibility(d, r)
        assert res["compatible"] is False, f"Empty case ({desc}) should not be compatible"
        assert res["status"] == "warning", f"Empty case ({desc}) should have warning status"
        print(f"  [PASS] Handled {desc}: status='{res['status']}', title='{res['title']}'")

    # -------------------------------------------------------------
    # 4. Test Invalid Inputs
    # -------------------------------------------------------------
    print("\n[TEST GROUP 4] Invalid Inputs Handling")
    invalid_cases = ["XYZ", "C+", "123", "O*", "BloodA"]
    for inv in invalid_cases:
        res = check_blood_compatibility(inv, "A+")
        assert res["compatible"] is False
        assert res["status"] == "incompatible"
        assert "Invalid Donor Group" in res["title"]
        print(f"  [PASS] Handled invalid donor '{inv}': {res['title']}")

    # -------------------------------------------------------------
    # 5. Test Repeated Checks
    # -------------------------------------------------------------
    print("\n[TEST GROUP 5] Repeated Checks Logging")
    clear_history_db()
    
    # Perform same check 3 times via client POST
    for i in range(3):
        post_res = client.post("/", data={"donorBlood": "O-", "recipientBlood": "AB+"})
        assert post_res.status_code == 200

    records = get_history()
    assert len(records) == 3, f"Expected 3 records for repeated checks, got {len(records)}"
    for rec in records:
        assert rec["donor"] == "O-"
        assert rec["recipient"] == "AB+"
        assert rec["result"] == "Compatible"
    print(f"  [PASS] All 3 repeated checks recorded as separate entries in database history.")

    # -------------------------------------------------------------
    # 6. Test Web Interface & API Integration
    # -------------------------------------------------------------
    print("\n[TEST GROUP 6] Flask Endpoints & History Display")
    
    # Add an incompatible record
    client.post("/", data={"donorBlood": "A+", "recipientBlood": "B+"})
    
    # Test GET / displays previous checking records
    get_res = client.get("/")
    assert get_res.status_code == 200
    assert b"Recent Checks" in get_res.data
    assert b"Compatible" in get_res.data
    assert b"Not Compatible" in get_res.data
    print("  [PASS] GET / renders history table with previous check records.")

    # Test GET /history API
    api_res = client.get("/history?format=json")
    assert api_res.status_code == 200
    json_history = api_res.get_json()
    assert len(json_history) == 4, f"Expected 4 history items, got {len(json_history)}"
    print("  [PASS] GET /history API returns records as JSON array.")

    # Test POST /clear-history
    clear_res = client.post("/clear-history", json={})
    assert clear_res.status_code == 200
    assert len(get_history()) == 0
    print("  [PASS] POST /clear-history resets database records to 0.")

    print("\n" + "=" * 65)
    print("ALL TESTS IN PHASE 4 AND PHASE 5 COMPLETED SUCCESSFULLY!")
    print("=" * 65)

if __name__ == "__main__":
    run_all_tests()
