# AEWS Integration - Manual Setup & Testing Guide

## Quick Summary
The AEWS (Academic Early Warning System) is now integrated into your ERP. To see it working, you need to:
1. ✅ Install required Python packages
2. ✅ Ensure database has proper student data
3. ✅ Run the backend server
4. ✅ Test the API endpoints
5. ✅ View results in Faculty/HoD dashboards

---
curl http://127.0.0.1:8000/ai/aews/student-risk/22CSMA01?semester=1

## 📋 STEP-BY-STEP INSTRUCTIONS

### **STEP 1: Install Required Python Packages**

The AEWS service needs these packages. Check if they're in your `Backend/requirements.txt`:

```bash
pandas
numpy
scikit-learn
xgboost
shap
joblib
sqlalchemy
fastapi
```

**Action:**
1. Open Terminal in `c:\Users\hemal\Major Project Gallery\erp-deployment\Backend`
2. Run:
   ```powershell
   pip install pandas numpy scikit-learn xgboost shap joblib sqlalchemy fastapi uvicorn
   ```

**Check if installed:**
```powershell
python -c "import pandas, numpy, sklearn, xgboost, shap, joblib; print('All packages installed!')"
```

---

### **STEP 2: Verify Database Structure & Data**

The AEWS needs these database tables with data:
- ✅ **students** - Student records
- ✅ **academic** - Student academic info (batch, branch, semester, backlogs_count, cgpa)
- ✅ **internal_marks** - Mid-term exam scores (mid1_marks, mid2_marks)
- ✅ **attendance_records** - Attendance data (percentage, semester)

**Check your database:**
1. Open your database management tool (MySQL, PostgreSQL, etc.)
2. Run these queries to verify data exists:

```sql
-- Check students exist
SELECT COUNT(*) FROM students;
-- Expected: > 0

-- Check academic records exist
SELECT COUNT(*) FROM academic;
-- Expected: > 0

-- Check internal marks exist
SELECT COUNT(*) FROM internal_marks;
-- Expected: > 0

-- Check attendance records exist
SELECT COUNT(*) FROM attendance_records;
-- Expected: > 0
```

**If data is missing:**
- You need to populate your database first
- Use the existing data upload features or import sample data
- Run migrations from `Backend/` folder

---

### **STEP 3: Start the Backend Server**

**Action:**
```powershell
# Navigate to Backend folder
cd c:\Users\hemal\Major Project Gallery\erp-deployment\Backend

# Run the FastAPI server
python -m uvicorn app.main:app --reload --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

✅ **Server is running!** Keep this terminal open.

---

### **STEP 4: Test API Endpoints (Option A - Using Browser/Postman)**

Open a new terminal/browser to test:

#### **Test 1: Get Individual Student Risk**
```
URL: http://127.0.0.1:8000/ai/aews/student-risk/2022001?semester=1

Method: GET
Headers: Authorization: Bearer <YOUR_FACULTY_OR_HOD_TOKEN>
```

**Expected Response:**
```json
{
  "status": "success",
  "roll_no": "2022001",
  "student_name": "John Doe",
  "semester": 1,
  "risk_level": "HIGH",
  "risk_probability": 72.45,
  "risk_color": "#d32f2f",
  "explanation": "Risk factors: low attendance, 2 backlogs indicate potential academic difficulty.",
  "factors": {
    "attendance": 55.5,
    "backlogs": 2,
    "previous_sgpa": 6.2,
    "mid_score_average": 14.5
  }
}
```

#### **Test 2: Get Batch At-Risk Students**
```
URL: http://127.0.0.1:8000/ai/aews/batch-at-risk?batch=2022-26&semester=1

Method: GET
Headers: Authorization: Bearer <YOUR_HOD_TOKEN>
```

**Expected Response:**
```json
{
  "batch": "2022-26",
  "semester": 1,
  "branch": null,
  "section": null,
  "at_risk_count": 5,
  "students": [
    {
      "roll_no": "2022001",
      "student_name": "John Doe",
      "risk_level": "HIGH",
      "risk_probability": 72.45,
      "explanation": "..."
    },
    ...
  ]
}
```

---

### **STEP 4-ALT: Test Using Python Script**

**Create a test file**: `Backend/test_aews.py`

```python
import requests
import json

# Configuration
API_BASE = "http://127.0.0.1:8000"
TOKEN = "your_faculty_or_hod_token_here"  # Get from login

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Test 1: Individual Student Risk
print("=" * 60)
print("TEST 1: Individual Student Risk Assessment")
print("=" * 60)

roll_no = "2022001"  # Change to actual roll number in your DB
response = requests.get(
    f"{API_BASE}/ai/aews/student-risk/{roll_no}?semester=1",
    headers=headers
)

print(f"Status Code: {response.status_code}")
print(f"Response:\n{json.dumps(response.json(), indent=2)}")

# Test 2: Batch At-Risk Students
print("\n" + "=" * 60)
print("TEST 2: Batch At-Risk Students")
print("=" * 60)

batch = "2022-26"  # Change to actual batch
response = requests.get(
    f"{API_BASE}/ai/aews/batch-at-risk?batch={batch}&semester=1",
    headers=headers
)

print(f"Status Code: {response.status_code}")
print(f"Response:\n{json.dumps(response.json(), indent=2)}")
```

**Run the test:**
```powershell
cd Backend
python test_aews.py
```

---

### **STEP 5: View in Faculty Dashboard**

1. **Open your ERP in browser**: `http://localhost:3000` (or your frontend URL)
2. **Login as Faculty**
3. **Go to**: Student Lookup page
4. **Search for a student** or **Apply filters and click "Apply Filters"**
5. **Look for "Risk" column** in the student table
6. **Click "Check Risk" button** for any student
7. **View popup** with:
   - Risk Level badge (Red/Orange/Green)
   - Failure Probability %
   - Risk Factors breakdown
   - SHAP explanation

---

### **STEP 6: View in HoD Dashboard**

1. **Login as HoD**
2. **Go to**: Student Management → Batch Analytics section
3. **Enter batch details** (e.g., "2022-26") and click "Fetch Analytics"
4. **Table appears** with student data
5. **Look for "Risk" column** with "Check" button
6. **Click button** to see risk assessment for each student

---

## 🔍 TROUBLESHOOTING

### **Problem 1: "AttributeError: Student has no attribute 'roll_no'"**
**Solution:** The Student model doesn't have `roll_no` field
- Check your Student model in `Backend/app/models/student.py`
- If the field is named differently (e.g., `student_id`, `srno`), update the AEWS service

### **Problem 2: "No attribute 'backlogs_count'"**
**Solution:** Academic model field name mismatch
- Check `Backend/app/models/academic.py`
- Update AEWS service to use correct field names
- Common names: `backlogs`, `backlogs_count`, `failed_courses`

### **Problem 3: 401 Unauthorized Error**
**Solution:** Authentication token is missing or invalid
- Make sure you're logged in as Faculty or HoD
- Get token from login response
- Add it to Authorization header: `Bearer <token>`

### **Problem 4: 404 Student Not Found**
**Solution:** Roll number doesn't exist in database
- Use a roll number that's actually in your database
- Check the exact format (e.g., "2022001" vs "CS/2022/001")

### **Problem 5: Risk Modal Doesn't Show in Frontend**
**Solution:** Frontend JavaScript may not be loaded
- Clear browser cache: `Ctrl+Shift+Delete`
- Hard refresh: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
- Check browser console for errors: `F12` → Console tab

### **Problem 6: "Cannot find module 'aews_service'"**
**Solution:** Import error in ai_route.py
- Make sure file is at: `Backend/app/services/aews_service.py`
- Check Python import is correct
- Run: `python -c "from app.services.aews_service import AEWSService; print('OK')"`

---

## 📊 SAMPLE TEST DATA

If your database is empty, create sample data:

```sql
-- Sample student
INSERT INTO students (roll_no, first_name, last_name, email, batch, branch)
VALUES ('2022001', 'John', 'Doe', 'john@college.edu', '2022-26', 'CSE');

-- Sample academic record
INSERT INTO academic (sid, semester, batch, branch, backlogs_count, cgpa)
VALUES (1, 1, '2022-26', 'CSE', 2, 6.5);

-- Sample attendance
INSERT INTO attendance_records (roll_no, semester, percentage)
VALUES ('2022001', 1, 65.5);

-- Sample internal marks
INSERT INTO internal_marks (roll_no, semester, mid1_marks, mid2_marks)
VALUES ('2022001', 1, 20, 18);
```

---

## ✅ VERIFICATION CHECKLIST

Before declaring success, verify:

- [ ] Python packages installed
- [ ] Database has student data
- [ ] Backend server running (port 8000)
- [ ] API endpoint returns JSON (not errors)
- [ ] Risk level is calculated (HIGH/MEDIUM/LOW)
- [ ] Probability is a number between 0-100
- [ ] Explanation text is generated
- [ ] Risk factors show actual values
- [ ] Faculty page loads with Risk column
- [ ] HoD page loads with Risk column
- [ ] Risk button opens popup modal
- [ ] Popup shows color-coded badge
- [ ] Can send alert from risk modal

---

## 🎯 EXPECTED WORKFLOW

### Faculty View:
```
Faculty Login
    ↓
Student Lookup Page
    ↓
Search/Filter Students
    ↓
See Student Table with "Risk" Column
    ↓
Click "Check Risk" Button
    ↓
Risk Modal Popup Shows:
  - Student name & roll
  - Risk badge (Red/Orange/Green)
  - Failure probability %
  - Risk factor breakdown
  - SHAP explanation
    ↓
(Optional) Click "Send Alert to Student"
    ↓
Pre-filled alert with risk details
```

### HoD View:
```
HoD Login
    ↓
Batch Analytics
    ↓
Enter batch & click "Fetch Analytics"
    ↓
See student table with "Risk" column
    ↓
Click "Check" for any student
    ↓
Same risk popup shows
    ↓
(Optional) Send academic alert
```

---

## 📞 COMMON QUESTIONS

**Q: Do I need ML model files (.pkl)?**
A: No! The AEWS service uses rule-based calculation, not pre-trained models. It works without .pkl files.

**Q: What if a student has no marks/attendance data?**
A: The system returns 0 for missing data, so they're treated as high-risk (which is conservative).

**Q: Can I customize risk thresholds?**
A: Yes! Edit `Backend/app/services/aews_service.py`:
```python
HIGH_RISK_THRESHOLD = 0.6    # Change this
MEDIUM_RISK_THRESHOLD = 0.35  # Change this
```

**Q: Does it work in real-time?**
A: Yes! Risk is calculated on-demand when you click the button.

**Q: Can students see their own risk?**
A: Currently no. It's Faculty/HoD only. Can be extended to student dashboard if needed.

---

## 🚀 NEXT STEPS (After Verification)

1. Test with different students to verify accuracy
2. Adjust risk thresholds if needed (too strict/lenient)
3. Monitor for data quality issues
4. Use alerts to identify at-risk students early
5. Track intervention success rates
6. Fine-tune weights if you have historical outcome data

---

## 📞 Need Help?

If you encounter issues:
1. Check the **Troubleshooting** section above
2. Look at terminal error messages
3. Check browser console (F12)
4. Verify database has actual student data
5. Ensure all files were updated correctly

