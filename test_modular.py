"""
Test Modular Architecture:
app.py, compatibility.py, index.html, history.html, style.css, database.db
"""
import os
import sqlite3

from compatibility import check_blood_compatibility, BLOOD_COMPATIBILITY, normalize_blood_group
from app import app, get_history, clear_history_db, save_history, DB_PATH

def test_architecture():
    print("=" * 65)
    print("VERIFYING MODULAR HEMOMATCH ARCHITECTURE")
    print("=" * 65)

    # 1. Verify files exist
    expected_files = [
        "app.py",
        "compatibility.py",
        "templates/index.html",
        "templates/history.html",
        "static/style.css",
        "database.db"
    ]
    for rel_path in expected_files:
        assert os.path.exists(rel_path), f"Missing required file: {rel_path}"
        print(f"  [PASS] File exists: {rel_path}")

    # 2. Test compatibility.py logic
    print("\n--- Testing compatibility.py ---")
    res1 = check_blood_compatibility("O-", "AB+")
    assert res1["compatible"] is True
    print("  [PASS] compatibility.py: O- -> AB+ is Compatible")

    res2 = check_blood_compatibility("A+", "B+")
    assert res2["compatible"] is False
    print("  [PASS] compatibility.py: A+ -> B+ is Not Compatible")

    res_norm = normalize_blood_group("o\u2212")
    assert res_norm == "O-"
    print("  [PASS] compatibility.py: normalize_blood_group handles Unicode minus and lowercase")

    # 3. Test database.db integration
    print("\n--- Testing database.db ---")
    assert os.path.basename(DB_PATH) == "database.db"
    clear_history_db()
    save_history("B+", "AB+", "Compatible", "compatible")
    records = get_history()
    assert len(records) >= 1
    assert records[0]["donor"] == "B+"
    assert records[0]["recipient"] == "AB+"
    print(f"  [PASS] database.db: Successfully written and read from {DB_PATH}")

    # 4. Test Flask Routes in app.py
    print("\n--- Testing app.py routes ---")
    client = app.test_client()

    # GET / (index.html)
    res_index = client.get("/")
    assert res_index.status_code == 200
    assert b"HemoMatch" in res_index.data
    assert b"Donor Blood Group" in res_index.data
    assert b"View History" in res_index.data
    print("  [PASS] app.py: GET / successfully serves index.html")

    # POST / (check & store in database.db)
    res_post = client.post("/", data={"donorBlood": "O+", "recipientBlood": "A+"})
    assert res_post.status_code == 200
    assert b"Compatible Match!" in res_post.data
    print("  [PASS] app.py: POST / evaluates compatibility & renders result")

    # GET /history (history.html)
    res_history = client.get("/history")
    assert res_history.status_code == 200
    assert b"Previous Compatibility Records" in res_history.data
    assert b"Back to Checker" in res_history.data
    assert b"O+" in res_history.data
    assert b"A+" in res_history.data
    print("  [PASS] app.py: GET /history successfully serves history.html with stored records")

    # GET /history?format=json API
    res_json = client.get("/history?format=json")
    assert res_json.status_code == 200
    json_data = res_json.get_json()
    assert isinstance(json_data, list)
    print("  [PASS] app.py: GET /history?format=json returns records as JSON")

    # POST /clear-history
    res_clear = client.post("/clear-history")
    assert res_clear.status_code in (200, 302)
    assert len(get_history()) == 0
    print("  [PASS] app.py: POST /clear-history resets database.db records to 0")

    print("\n" + "=" * 65)
    print("ALL MODULAR COMPONENTS VERIFIED AND OPERATING TOGETHER!")
    print("=" * 65)

if __name__ == "__main__":
    test_architecture()
