import requests
import time
import json
import threading

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidXNyXzZiYjIwYjdkZjJjYTRlNzAiLCJyb2xlIjoiYWRtaW4iLCJpYXQiOjE3Nzk5OTcyNTEsImV4cCI6MTc4MDAwMDg1MX0.Xr6_bNG8wrSPe_x_gZE-2wACC_WLbJfL5vwPyrCFiD0"
BASE = "http://127.0.0.1:5000/api"
headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
get_headers = {"Authorization": f"Bearer {TOKEN}"}

print("=" * 60)
print("GarageHQ Invoice Module - Stress Test Report")
print("=" * 60)

# -------------------------------------------------------
# Preliminary: get a work order
# -------------------------------------------------------
print("\n[PRELIM] Fetching work orders...")
try:
    wo_resp = requests.get(f"{BASE}/work-orders", headers=get_headers, timeout=5)
    print(f"  Work orders status: {wo_resp.status_code}")
    if wo_resp.status_code == 200:
        work_orders = wo_resp.json()
        if isinstance(work_orders, dict) and "work_orders" in work_orders:
            work_orders = work_orders["work_orders"]
        elif isinstance(work_orders, dict) and "data" in work_orders:
            work_orders = work_orders["data"]
        print(f"  Found {len(work_orders)} work orders")
        if work_orders:
            print(f"  First WO keys: {list(work_orders[0].keys())}")
    else:
        print(f"  Response: {wo_resp.text[:200]}")
        work_orders = []
except Exception as e:
    print(f"  Error: {e}")
    work_orders = []

# Also try getting customers
print("\n[PRELIM] Fetching customers...")
try:
    cust_resp = requests.get(f"{BASE}/customers", headers=get_headers, timeout=5)
    print(f"  Customers status: {cust_resp.status_code}")
    if cust_resp.status_code == 200:
        customers = cust_resp.json()
        if isinstance(customers, dict) and "customers" in customers:
            customers = customers["customers"]
        elif isinstance(customers, dict) and "data" in customers:
            customers = customers["data"]
        print(f"  Found {len(customers)} customers")
    else:
        print(f"  Response: {cust_resp.text[:200]}")
        customers = []
except Exception as e:
    print(f"  Error: {e}")
    customers = []

# Get existing invoices to understand structure
print("\n[PRELIM] Fetching existing invoices...")
try:
    inv_resp = requests.get(f"{BASE}/invoices", headers=get_headers, timeout=5)
    print(f"  Invoices status: {inv_resp.status_code}")
    if inv_resp.status_code == 200:
        inv_data = inv_resp.json()
        print(f"  Invoice response keys: {list(inv_data.keys()) if isinstance(inv_data, dict) else 'list'}")
        if isinstance(inv_data, dict) and "invoices" in inv_data:
            invs = inv_data["invoices"]
            if invs:
                print(f"  First invoice keys: {list(invs[0].keys())}")
                print(f"  First invoice sample: {json.dumps(invs[0], indent=2)[:300]}")
        elif isinstance(inv_data, list) and inv_data:
            print(f"  First invoice keys: {list(inv_data[0].keys())}")
    else:
        print(f"  Response: {inv_resp.text[:300]}")
except Exception as e:
    print(f"  Error: {e}")

# -------------------------------------------------------
# TEST 1: Create 50 invoices rapidly
# -------------------------------------------------------
print("\n" + "=" * 60)
print("TEST 1: Create 50 Invoices Rapidly")
print("=" * 60)

wo_id = work_orders[0]["id"] if work_orders else None
cust_id = work_orders[0].get("customer_id") if work_orders else (customers[0]["id"] if customers else None)
print(f"  Using work_order_id={wo_id}, customer_id={cust_id}")

success = 0
errors = 0
times = []
error_codes = {}
created_ids = []

for i in range(50):
    start = time.time()
    payload = {
        "work_order_id": wo_id,
        "customer_id": cust_id,
        "notes": f"Stress test invoice {i}",
    }
    try:
        resp = requests.post(f"{BASE}/invoices", json=payload, headers=headers, timeout=5)
        elapsed = time.time() - start
        times.append(elapsed)
        if resp.status_code in [200, 201]:
            success += 1
            try:
                body = resp.json()
                inv_id = body.get("id") or body.get("invoice", {}).get("id")
                if inv_id:
                    created_ids.append(inv_id)
            except:
                pass
        else:
            errors += 1
            error_codes[resp.status_code] = error_codes.get(resp.status_code, 0) + 1
            if errors == 1:
                print(f"  First error body: {resp.text[:200]}")
    except Exception as e:
        errors += 1
        error_codes["exception"] = error_codes.get("exception", 0) + 1

avg_time = sum(times) / len(times) if times else 0
min_time = min(times) if times else 0
max_time = max(times) if times else 0

print(f"  Success: {success}/50")
print(f"  Errors: {errors}/50  (breakdown: {error_codes})")
print(f"  Avg response time: {avg_time:.3f}s")
print(f"  Min response time: {min_time:.3f}s")
print(f"  Max response time: {max_time:.3f}s")
if success == 50:
    print("  RESULT: PASS")
elif success > 0:
    print(f"  RESULT: PARTIAL ({success}/50 succeeded)")
else:
    print("  RESULT: FAIL (0 created)")

# -------------------------------------------------------
# TEST 2: Large date range query
# -------------------------------------------------------
print("\n" + "=" * 60)
print("TEST 2: Query with Large Date Range")
print("=" * 60)

url = f"{BASE}/invoices?date_from=2000-01-01&date_to=2030-12-31"
print(f"  URL: {url}")
try:
    start = time.time()
    resp = requests.get(url, headers=get_headers, timeout=30)
    elapsed = time.time() - start
    print(f"  Status: {resp.status_code}")
    print(f"  Response time: {elapsed:.3f}s")
    if resp.status_code == 200:
        data = resp.json()
        if isinstance(data, dict):
            count = len(data.get("invoices", data.get("data", [])))
        else:
            count = len(data)
        print(f"  Records returned: {count}")
        print(f"  RESULT: PASS (responded in {elapsed:.3f}s)")
    else:
        print(f"  Body: {resp.text[:200]}")
        print(f"  RESULT: FAIL (status {resp.status_code})")
except Exception as e:
    print(f"  Exception: {e}")
    print(f"  RESULT: FAIL (exception)")

# -------------------------------------------------------
# TEST 3: Search with special / malicious characters
# -------------------------------------------------------
print("\n" + "=" * 60)
print("TEST 3: Search with Special / Malicious Characters")
print("=" * 60)

test_queries = [
    ("SQL Injection",       "'; DROP TABLE invoices; --"),
    ("XSS",                 "<script>alert(1)</script>"),
    ("Null bytes",          "%00%0a%0d"),
    ("Path traversal",      "../../../etc/passwd"),
]

all_safe = True
for label, query in test_queries:
    url = f"{BASE}/invoices?search={query}"
    try:
        start = time.time()
        resp = requests.get(url, headers=get_headers, timeout=10)
        elapsed = time.time() - start
        # Acceptable: 200 (handled safely) or 4xx (rejected)
        # Unacceptable: 500 (server error that could signal injection working)
        safe = resp.status_code != 500
        status_word = "SAFE" if safe else "UNSAFE (500 error)"
        if not safe:
            all_safe = False
        print(f"  [{label}] status={resp.status_code} time={elapsed:.3f}s -> {status_word}")
        if resp.status_code == 500:
            print(f"    Body: {resp.text[:200]}")
    except Exception as e:
        print(f"  [{label}] Exception: {e} -> FAIL")
        all_safe = False

print(f"  RESULT: {'PASS (all queries handled safely)' if all_safe else 'FAIL (server errors detected)'}")

# -------------------------------------------------------
# TEST 4a: Max field length — notes 10000 chars
# -------------------------------------------------------
print("\n" + "=" * 60)
print("TEST 4a: Max Field Length — notes = 10000 characters")
print("=" * 60)

long_notes = "A" * 10000
payload = {
    "work_order_id": wo_id,
    "customer_id": cust_id,
    "notes": long_notes,
}
try:
    start = time.time()
    resp = requests.post(f"{BASE}/invoices", json=payload, headers=headers, timeout=10)
    elapsed = time.time() - start
    print(f"  Status: {resp.status_code}  Time: {elapsed:.3f}s")
    if resp.status_code in [200, 201]:
        print(f"  Server accepted 10k-char notes field")
        print(f"  RESULT: PASS (accepted and stored)")
    elif resp.status_code == 400:
        print(f"  Server rejected (validation): {resp.text[:200]}")
        print(f"  RESULT: PASS (rejected with 400 — validation working)")
    elif resp.status_code == 500:
        print(f"  Server crashed: {resp.text[:200]}")
        print(f"  RESULT: FAIL (500 server error)")
    else:
        print(f"  Body: {resp.text[:200]}")
        print(f"  RESULT: INFO (status {resp.status_code})")
except Exception as e:
    print(f"  Exception: {e}")
    print(f"  RESULT: FAIL")

# -------------------------------------------------------
# TEST 4b: Very large amount
# -------------------------------------------------------
print("\n" + "=" * 60)
print("TEST 4b: Very Large Amount — 9999999999.99")
print("=" * 60)

payload = {
    "work_order_id": wo_id,
    "customer_id": cust_id,
    "notes": "Large amount stress test",
    "amount": 9999999999.99,
    "total": 9999999999.99,
    "subtotal": 9999999999.99,
}
try:
    start = time.time()
    resp = requests.post(f"{BASE}/invoices", json=payload, headers=headers, timeout=10)
    elapsed = time.time() - start
    print(f"  Status: {resp.status_code}  Time: {elapsed:.3f}s")
    if resp.status_code in [200, 201]:
        print(f"  Server accepted large amount")
        print(f"  RESULT: PASS (accepted)")
    elif resp.status_code == 400:
        print(f"  Server rejected (validation): {resp.text[:200]}")
        print(f"  RESULT: PASS (rejected with 400 — validation working)")
    elif resp.status_code == 500:
        print(f"  Server crashed: {resp.text[:200]}")
        print(f"  RESULT: FAIL (500 server error)")
    else:
        print(f"  Body: {resp.text[:200]}")
        print(f"  RESULT: INFO (status {resp.status_code})")
except Exception as e:
    print(f"  Exception: {e}")
    print(f"  RESULT: FAIL")

# -------------------------------------------------------
# TEST 5: 20 concurrent requests to dashboard
# -------------------------------------------------------
print("\n" + "=" * 60)
print("TEST 5: 20 Concurrent Requests to /invoices/dashboard")
print("=" * 60)

concurrent_results = []
concurrent_times = []
lock = threading.Lock()

def make_concurrent_request():
    start = time.time()
    try:
        r = requests.get(f"{BASE}/invoices/dashboard", headers=get_headers, timeout=15)
        elapsed = time.time() - start
        with lock:
            concurrent_results.append(r.status_code)
            concurrent_times.append(elapsed)
    except Exception as e:
        with lock:
            concurrent_results.append(0)
            concurrent_times.append(0)

threads = [threading.Thread(target=make_concurrent_request) for _ in range(20)]
start_all = time.time()
for t in threads:
    t.start()
for t in threads:
    t.join()
total_elapsed = time.time() - start_all

success_count = concurrent_results.count(200)
error_codes_conc = [r for r in concurrent_results if r != 200]
avg_conc = sum(concurrent_times) / len(concurrent_times) if concurrent_times else 0
max_conc = max(concurrent_times) if concurrent_times else 0

print(f"  20 concurrent requests completed in {total_elapsed:.3f}s (wall time)")
print(f"  Success (200): {success_count}/20")
print(f"  Non-200 responses: {error_codes_conc}")
print(f"  Avg per-request time: {avg_conc:.3f}s")
print(f"  Max per-request time: {max_conc:.3f}s")

if success_count == 20:
    print(f"  RESULT: PASS")
elif success_count >= 18:
    print(f"  RESULT: PASS (minor degradation: {success_count}/20)")
else:
    print(f"  RESULT: FAIL ({success_count}/20 succeeded)")

# -------------------------------------------------------
# SUMMARY
# -------------------------------------------------------
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
