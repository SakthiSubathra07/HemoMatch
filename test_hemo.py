import sys
from app import app, check_blood_compatibility, BLOOD_COMPATIBILITY

def test_compatibility_logic():
    print("Testing Phase 2: Blood compatibility logic...")

    expected_matches = {
        "O-": ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"],
        "O+": ["O+", "A+", "B+", "AB+"],
        "A-": ["A-", "A+", "AB-", "AB+"],
        "A+": ["A+", "AB+"],
        "B-": ["B-", "B+", "AB-", "AB+"],
        "B+": ["B+", "AB+"],
        "AB-": ["AB-", "AB+"],
        "AB+": ["AB+"]
    }

    all_groups = ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"]

    # Test all 64 biological combinations
    for donor in all_groups:
        for recipient in all_groups:
            res = check_blood_compatibility(donor, recipient)
            is_compat = res["compatible"]
            expected = recipient in expected_matches[donor]
            assert is_compat == expected, f"Failed for {donor} -> {recipient}: got {is_compat}, expected {expected}"

    # Test Unicode minus sign
    res_unicode = check_blood_compatibility("O\u2212", "A+")
    assert res_unicode["compatible"] is True, "Unicode minus test failed"

    # Test selection incomplete
    res_incomplete = check_blood_compatibility("", "A+")
    assert res_incomplete["status"] == "warning", "Incomplete check test failed"

    print("[PASS] Phase 2 tests passed: All 64 compatibility combinations and edge cases verified.")

def test_flask_routes():
    print("Testing Phase 3: Flask routes & backend integration...")
    client = app.test_client()

    # 1. Test GET home route
    res_get = client.get("/")
    assert res_get.status_code == 200, f"GET / returned {res_get.status_code}"
    assert b"HemoMatch" in res_get.data, "HemoMatch title not found in GET response"
    print("[PASS] GET / returned 200 with HemoMatch page.")

    # 2. Test POST form submission (Compatible: O- to AB+)
    res_post_form = client.post("/", data={"donorBlood": "O-", "recipientBlood": "AB+"})
    assert res_post_form.status_code == 200
    assert b"Compatible Match!" in res_post_form.data
    print("[PASS] POST form (O- -> AB+) rendered compatible match.")

    # 3. Test POST form submission (Incompatible: A+ to B+)
    res_post_incompat = client.post("/", data={"donorBlood": "A+", "recipientBlood": "B+"})
    assert res_post_incompat.status_code == 200
    assert b"Not Compatible" in res_post_incompat.data
    print("[PASS] POST form (A+ -> B+) rendered incompatible match.")

    # 4. Test POST JSON API
    res_post_json = client.post("/", json={"donorBlood": "B+", "recipientBlood": "AB+"})
    assert res_post_json.status_code == 200
    json_data = res_post_json.get_json()
    assert json_data["compatible"] is True
    print("[PASS] POST JSON (B+ -> AB+) returned compatible JSON object.")

    print("\nAll Phase 2 & Phase 3 tests passed successfully!")

if __name__ == "__main__":
    test_compatibility_logic()
    test_flask_routes()
