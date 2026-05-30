import requests
import time
import json
import threading

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidXNyXzZiYjIwYjdkZjJjYTRlNzAiLCJyb2xlIjoiYWRtaW4iLCJpYXQiOjE3Nzk5OTcyNTEsImV4cCI6MTc4MDAwMDg1MX0.Xr6_bNG8wrSPe_x_gZE-2wACC_WLbJfL5vwPyrCFiD0"
BASE = "http://127.0.0.1:5000/api"
headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
get_headers = {"Authorization": f"Bearer {TOKEN}"}

CUSTOMER_ID = "cust_2f6d1c37b928"
VEHICLE_ID = "veh_26f76ccf0930"

print("=" * 60)
print("GarageHQ Invoice Module - Stress Test Report")
print("=" * 60)

# -------------------------------------------------------
# SETUP: pre-create 50 work orders so we can create 50 invoices
# -------------------------------------------------------
print("\n[SETUP] Creating 50 work orders for test 1...")
wo_ids = []
for i in range(50):
    payload = {
        "customer_id": CUSTOMER_ID,
        "vehicle_id": VEHICLE_ID,
        "description": f"Stress test WO {i}",
        "issue_type": "Service",
    }
    try:
        r = requests.post(f"{BASE}/work-orders", json=payload, headers=headers, timeout=5)
        if r.status_code in [200, 201]:
            data = r.json()
            wo_id = data.get("data", {}).get("work_order_id") or data.get("work_order_id")
            if wo_id:
                wo_ids.append(wo_id)
    except Exception as e:
        print(f"  WO creation error at i={i}: {e}")

print(f"  Created {len(wo_ids)} work orders")

# -------------------------------------------------------
# TEST 1: Create 50 invoices rapidly
# -------------------------------------------------------
print("\n" + "=" * 60)
print("TEST 1: Create 50 Invoices Rapidly")
print("=" * 60)

success = 0
errors = 0
times = []
error_codes = {}
created_invoice_ids = []

for i, wo_id in enumerate(wo_ids):
    start = time.time()
    payload = {
        "work_order_id": wo_id,
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
                inv_id = (body.get("data") or {}).get("invoice_id") or body.get("id")
                if inv_id:
                    created_invoice_ids.append(inv_id)
            except Exception:
                pass
        else:
            errors += 1
            code = resp.status_code
            error_codes[code] = error_codes.get(code, 0) + 1
            if errors <= 2:
                print(f"  Error sample [{i}]: {resp.status_code} {resp.text[:150]}")
    except Exception as e:
        errors += 1
        error_codes["exception"] = error_codes.get("exception", 0) + 1

avg_time = sum(times) / len(times) if times else 0
min_time = min(times) if times else 0
max_time = max(times) if times else 0
total_time = sum(times)

print(f"  Attempted: 50")
print(f"  Success: {success}")
print(f"  Errors: {errors}  (breakdown: {error_codes})")
print(f"  Total elapsed: {total_time:.3f}s")
print(f"  Avg response time: {avg_time:.3f}s")
print(f"  Min response time: {min_time:.3f}s")
print(f"  Max response time: {max_time:.3f}s")
if success == 50:
    t1_result = "PASS"
elif success > 0:
    t1_result = f"PARTIAL ({success}/50 succeeded)"
else:
    t1_result = "FAIL (0 created)"
print(f"  RESULT: {t1_result}")

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
        if isinstance(data, dict) and "data" in data:
            count = data["data"].get("count", len(data["data"].get("invoices", [])))
        elif isinstance(data, dict) and "invoices" in data:
            count = len(data["invoices"])
        elif isinstance(data, list):
            count = len(data)
        else:
            count = "unknown"
        print(f"  Records returned: {count}")
        if elapsed < 5.0:
            t2_result = f"PASS (responded in {elapsed:.3f}s, {count} records)"
        else:
            t2_result = f"SLOW ({elapsed:.3f}s > 5s threshold)"
    else:
        print(f"  Body: {resp.text[:200]}")
        t2_result = f"FAIL (status {resp.status_code})"
except Exception as e:
    print(f"  Exception: {e}")
    t2_result = "FAIL (exception)"
print(f"  RESULT: {t2_result}")

# -------------------------------------------------------
# TEST 3: Search with special / malicious characters
# -------------------------------------------------------
print("\n" + "=" * 60)
print("TEST 3: Search with Special / Malicious Characters")
print("=" * 60)

test_queries = [
    ("SQL Injection",   "'; DROP TABLE invoices; --"),
    ("XSS",             "<script>alert(1)</script>"),
    ("Null bytes",      "%00%0a%0d"),
    ("Path traversal",  "../../../etc/passwd"),
]

t3_results = {}
all_safe = True
for label, query in test_queries:
    url = f"{BASE}/invoices?search={query}"
    try:
        start = time.time()
        resp = requests.get(url, headers=get_headers, timeout=10)
        elapsed = time.time() - start
        # 200 or 4xx = handled; 500 = server error (bad)
        if resp.status_code == 500:
            safe = False
            all_safe = False
            verdict = "UNSAFE (500)"
        else:
            safe = True
            verdict = "SAFE"
        t3_results[label] = (resp.status_code, elapsed, verdict)
        print(f"  [{label:20s}] status={resp.status_code} time={elapsed:.3f}s -> {verdict}")
        if resp.status_code == 500:
            print(f"    Body: {resp.text[:200]}")
    except Exception as e:
        t3_results[label] = (0, 0, "FAIL")
        all_safe = False
        print(f"  [{label:20s}] Exception: {e} -> FAIL")

t3_result = "PASS (all queries handled safely)" if all_safe else "FAIL (server errors detected)"
print(f"  RESULT: {t3_result}")

# -------------------------------------------------------
# TEST 4a: Max field length — notes = 10000 chars
# -------------------------------------------------------
print("\n" + "=" * 60)
print("TEST 4a: Max Field Length — notes = 10000 characters")
print("=" * 60)

# Create a fresh WO for this test
r_wo = requests.post(f"{BASE}/work-orders", json={
    "customer_id": CUSTOMER_ID,
    "vehicle_id": VEHICLE_ID,
    "description": "Max-field-length test WO",
    "issue_type": "Service",
}, headers=headers, timeout=5)
long_wo_id = None
if r_wo.status_code in [200, 201]:
    long_wo_id = r_wo.json().get("data", {}).get("work_order_id")

long_notes = "A" * 10000
payload = {
    "work_order_id": long_wo_id,
    "notes": long_notes,
}
try:
    start = time.time()
    resp = requests.post(f"{BASE}/invoices", json=payload, headers=headers, timeout=10)
    elapsed = time.time() - start
    print(f"  Note length: 10000 chars")
    print(f"  Status: {resp.status_code}  Time: {elapsed:.3f}s")
    if resp.status_code in [200, 201]:
        print(f"  Server accepted 10k-char notes (no truncation error)")
        t4a_result = "PASS (accepted 10000-char notes)"
    elif resp.status_code == 400:
        print(f"  Server rejected (validation): {resp.text[:200]}")
        t4a_result = "PASS (rejected with 400 — validation working)"
    elif resp.status_code == 500:
        print(f"  Server crashed: {resp.text[:200]}")
        t4a_result = "FAIL (500 server error on large notes)"
    else:
        print(f"  Body: {resp.text[:200]}")
        t4a_result = f"INFO (status {resp.status_code})"
except Exception as e:
    print(f"  Exception: {e}")
    t4a_result = "FAIL (exception)"
print(f"  RESULT: {t4a_result}")

# -------------------------------------------------------
# TEST 4b: Very large amount
# -------------------------------------------------------
print("\n" + "=" * 60)
print("TEST 4b: Very Large Amount — 9999999999.99")
print("=" * 60)

# Create a fresh WO
r_wo2 = requests.post(f"{BASE}/work-orders", json={
    "customer_id": CUSTOMER_ID,
    "vehicle_id": VEHICLE_ID,
    "description": "Large amount test WO",
    "issue_type": "Service",
}, headers=headers, timeout=5)
large_amt_wo_id = None
if r_wo2.status_code in [200, 201]:
    large_amt_wo_id = r_wo2.json().get("data", {}).get("work_order_id")

# First create the invoice
r_inv = requests.post(f"{BASE}/invoices", json={"work_order_id": large_amt_wo_id}, headers=headers, timeout=5)
inv_id_for_large = None
if r_inv.status_code in [200, 201]:
    inv_id_for_large = r_inv.json().get("data", {}).get("invoice_id")
    print(f"  Created invoice: {inv_id_for_large}")

# Try to update with large amount via line item or direct update
# First check what update endpoint looks like
if inv_id_for_large:
    payload_update = {
        "amount": 9999999999.99,
        "total": 9999999999.99,
        "subtotal": 9999999999.99,
        "grand_total": 9999999999.99,
        "customer_amount": 9999999999.99,
    }
    try:
        start = time.time()
        resp_upd = requests.put(f"{BASE}/invoices/{inv_id_for_large}", json=payload_update, headers=headers, timeout=10)
        elapsed = time.time() - start
        print(f"  PUT /invoices/{inv_id_for_large} status={resp_upd.status_code}  time={elapsed:.3f}s")
        print(f"  Body: {resp_upd.text[:300]}")
        if resp_upd.status_code == 500:
            t4b_result = "FAIL (500 on large amount)"
        elif resp_upd.status_code in [200, 201, 400, 422]:
            t4b_result = f"PASS (status {resp_upd.status_code})"
        else:
            t4b_result = f"INFO (status {resp_upd.status_code})"
    except Exception as e:
        print(f"  Exception: {e}")
        t4b_result = "FAIL (exception)"
else:
    # Try direct creation with large amount fields
    payload2 = {
        "work_order_id": large_amt_wo_id,
        "notes": "Large amount stress test",
        "amount": 9999999999.99,
        "grand_total": 9999999999.99,
    }
    try:
        start = time.time()
        resp = requests.post(f"{BASE}/invoices", json=payload2, headers=headers, timeout=10)
        elapsed = time.time() - start
        print(f"  Status: {resp.status_code}  Time: {elapsed:.3f}s")
        print(f"  Body: {resp.text[:200]}")
        if resp.status_code == 500:
            t4b_result = "FAIL (500 server error on large amount)"
        else:
            t4b_result = f"PASS (status {resp.status_code})"
    except Exception as e:
        print(f"  Exception: {e}")
        t4b_result = "FAIL (exception)"

print(f"  RESULT: {t4b_result}")

# -------------------------------------------------------
# TEST 5: 20 Concurrent requests to /invoices/dashboard
# -------------------------------------------------------
print("\n" + "=" * 60)
print("TEST 5: 20 Concurrent Requests to /invoices/dashboard")
print("=" * 60)

concurrent_results = []
concurrent_times = []
lock = threading.Lock()

def make_concurrent_request():
    t_start = time.time()
    try:
        r = requests.get(f"{BASE}/invoices/dashboard", headers=get_headers, timeout=15)
        elapsed = time.time() - t_start
        with lock:
            concurrent_results.append(r.status_code)
            concurrent_times.append(elapsed)
    except Exception as e:
        elapsed = time.time() - t_start
        with lock:
            concurrent_results.append(0)
            concurrent_times.append(elapsed)

threads = [threading.Thread(target=make_concurrent_request) for _ in range(20)]
wall_start = time.time()
for t in threads:
    t.start()
for t in threads:
    t.join()
wall_elapsed = time.time() - wall_start

success_count = concurrent_results.count(200)
error_list = [r for r in concurrent_results if r != 200]
avg_conc = sum(concurrent_times) / len(concurrent_times) if concurrent_times else 0
max_conc = max(concurrent_times) if concurrent_times else 0
min_conc = min(concurrent_times) if concurrent_times else 0

print(f"  Threads: 20")
print(f"  Wall-clock time: {wall_elapsed:.3f}s")
print(f"  Success (200): {success_count}/20")
print(f"  Non-200 responses: {error_list}")
print(f"  Per-request avg: {avg_conc:.3f}s  min: {min_conc:.3f}s  max: {max_conc:.3f}s")

if success_count == 20:
    t5_result = "PASS (20/20 succeeded)"
elif success_count >= 18:
    t5_result = f"PARTIAL (minor degradation: {success_count}/20)"
else:
    t5_result = f"FAIL ({success_count}/20 succeeded, errors: {error_list})"
print(f"  RESULT: {t5_result}")

# -------------------------------------------------------
# FINAL SUMMARY
# -------------------------------------------------------
print("\n" + "=" * 60)
print("FINAL SUMMARY")
print("=" * 60)
print(f"  TEST 1 - 50 rapid invoice creates:     {t1_result}")
print(f"  TEST 2 - Large date range query:        {t2_result}")
print(f"  TEST 3 - Special/malicious char search: {t3_result}")
print(f"  TEST 4a - 10000-char notes field:       {t4a_result}")
print(f"  TEST 4b - Max amount 9999999999.99:     {t4b_result}")
print(f"  TEST 5 - 20 concurrent dashboard reqs:  {t5_result}")
print("=" * 60)
