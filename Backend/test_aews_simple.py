"""
Simple AEWS Test Script
Tests the Academic Early Warning System API endpoints
"""

import requests
import json
import sys

# Configuration
API_BASE = "http://127.0.0.1:8000"

print("=" * 70)
print("AEWS TEST - Student Risk Assessment")
print("=" * 70)

# Test 1: Test endpoint (no auth required)
print("\n[TEST 1] Individual Student Risk (No Auth Required)")
print("-" * 70)

roll_no = "22CSMA01"  # Change this to your actual roll number
url = f"{API_BASE}/ai/aews/test/student-risk/{roll_no}?semester=1"

print(f"Testing URL: {url}")
print(f"Roll Number: {roll_no}")

try:
    response = requests.get(url, timeout=5)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ SUCCESS! Response:")
        print(json.dumps(data, indent=2))
        
        # Extract key info
        if data.get('status') == 'success':
            print("\n" + "=" * 70)
            print("RISK ASSESSMENT SUMMARY")
            print("=" * 70)
            print(f"Student: {data.get('student_name')} ({data.get('roll_no')})")
            print(f"Risk Level: {data.get('risk_level')}")
            print(f"Failure Probability: {data.get('risk_probability')}%")
            print(f"Explanation: {data.get('explanation')}")
            print("\nRisk Factors:")
            factors = data.get('factors', {})
            print(f"  - Attendance: {factors.get('attendance')}%")
            print(f"  - Backlogs: {factors.get('backlogs')}")
            print(f"  - Previous SGPA: {factors.get('previous_sgpa')}/10")
            print(f"  - Mid Score Average: {factors.get('mid_score_average')}/30")
    else:
        print("\n❌ ERROR Response:")
        print(json.dumps(response.json(), indent=2))
        
except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: Cannot connect to API server")
    print("Make sure backend is running: python -m uvicorn app.main:app --reload --port 8000")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    sys.exit(1)

# Test 2: Batch at-risk students
print("\n\n[TEST 2] Batch At-Risk Students (No Auth Required)")
print("-" * 70)

batch = "2022-26"
url2 = f"{API_BASE}/ai/aews/test/batch-at-risk?batch={batch}&semester=1"

print(f"Testing URL: {url2}")
print(f"Batch: {batch}")

try:
    response2 = requests.get(url2, timeout=5)
    print(f"Status Code: {response2.status_code}")
    
    if response2.status_code == 200:
        data2 = response2.json()
        print("\n✅ SUCCESS! Response:")
        print(json.dumps(data2, indent=2))
        
        print("\n" + "=" * 70)
        print("AT-RISK STUDENTS SUMMARY")
        print("=" * 70)
        print(f"Batch: {data2.get('batch')}")
        print(f"At-Risk Count: {data2.get('at_risk_count')}")
        
        if data2.get('students'):
            print("\nAt-Risk Students:")
            for student in data2.get('students', []):
                print(f"  • {student.get('student_name')} ({student.get('roll_no')})")
                print(f"    Risk Level: {student.get('risk_level')} | Probability: {student.get('risk_probability')}%")
    else:
        print("\n❌ ERROR Response:")
        print(json.dumps(response2.json(), indent=2))
        
except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: Cannot connect to API server")
except Exception as e:
    print(f"\n❌ ERROR: {e}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
