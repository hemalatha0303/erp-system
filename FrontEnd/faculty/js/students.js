const API_BASE = typeof API_URL !== "undefined" ? API_URL : "http://127.0.0.1:8000";
let allStudentsCache = [];
let alertHandlerBound = false;

async function fetchStudentList() {
  const token = localStorage.getItem("token");
  
  if (!token) {
    throw new Error("Not authenticated. Please log in again.");
  }

  try {
    const response = await fetch(`${API_BASE}/faculty/student-list`, {
      method: "GET",
      headers: { 
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json"
      },
    });

    if (!response.ok) {
      let errorMsg = `Error ${response.status}`;
      try {
        const errData = await response.json();
        if (errData.detail) {
          errorMsg = errData.detail;
        } else if (errData.message) {
          errorMsg = errData.message;
        }
      } catch (e) {
        // If response body is not JSON, keep the status code message
      }
      throw new Error(errorMsg);
    }

    const data = await response.json();
    if (!Array.isArray(data)) {
      console.warn("Student list response is not an array:", data);
      return [];
    }
    return data;
  } catch (e) {
    console.error("Fetch error:", e);
    throw e;
  }
}

async function loadStudentLookup() {
  const tableBody = document.getElementById("lookup-body");
  const resultCard = document.getElementById("lookup-result");

  resultCard.style.display = "block";
  tableBody.innerHTML =
    "<tr><td colspan='9' style='text-align:center; padding:15px;'><i class='fas fa-spinner fa-spin'></i> Loading students...</td></tr>";

  try {
    allStudentsCache = await fetchStudentList();
    renderLookupResults(tableBody);
  } catch (error) {
    console.error("Student Load Error:", error);
    tableBody.innerHTML = `<tr><td colspan='9' style="color:red; text-align:center; padding:20px;"><i class="fas fa-exclamation-circle"></i> Error: ${error.message}</td></tr>`;
  }
}

function renderLookupResults(tableBody) {
  const searchText = document
    .getElementById("lookup-search")
    .value.trim()
    .toUpperCase();
  const feeStatus = document.getElementById("lookup-fee-status").value;
  const branch = document.getElementById("lookup-branch").value;
  const residence = document.getElementById("lookup-residence").value;
  const section = document.getElementById("lookup-section").value;

  const filtered = allStudentsCache.filter((student) => {
    if (searchText) {
      const fullName = `${student.first_name || ""} ${student.last_name || ""}`.toUpperCase();
      const roll = (student.roll_no || "").toUpperCase();
      if (!roll.includes(searchText) && !fullName.includes(searchText)) {
        return false;
      }
    }

    if (branch && branch !== "ALL" && student.branch !== branch) {
      return false;
    }

    if (section && section !== "ALL" && student.section !== section) {
      return false;
    }

    if (residence && residence !== "ALL") {
      const normalized = normalizeResidence(student.residence_type);
      if (residence === "DAY_SCHOLAR" && normalized !== "DAY_SCHOLAR") {
        return false;
      }
      if (residence === "HOSTELER" && normalized !== "HOSTELER") {
        return false;
      }
    }

    if (feeStatus) {
      const computed = computeFeeStatus(student.payment_records || []);
      if (computed.value !== feeStatus) {
        return false;
      }
    }

    return true;
  });

  renderRows(tableBody, filtered, "No students match your filters");
}

async function fetchStudentRisk(rollNo, semester = 1) {
  const token = localStorage.getItem("token");
  try {
    const response = await fetch(
      `${API_BASE}/ai/aews/student-risk/${encodeURIComponent(rollNo)}?semester=${semester}`,
      {
        headers: { Authorization: `Bearer ${token}` },
      }
    );

    if (!response.ok) {
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error("Error fetching risk:", error);
    return null;
  }
}

function renderRows(tableBody, students, emptyMessage) {
  if (!students || students.length === 0) {
    tableBody.innerHTML =
      `<tr><td colspan='9' style='text-align:center; padding:20px; color:#999;'><i class='fas fa-search'></i> ${emptyMessage}</td></tr>`;
    return;
    
  }

  tableBody.innerHTML = "";
  students.forEach((student) => {
    const name = `${student.first_name || ""} ${student.last_name || ""}`.trim() || "-";
    const email = (student.email || student.user_email || student.personal_email || "").trim();
    const phone = student.mobile_no || "-";
    const parentMobile = student.parent_mobile_no || "-";
    const residenceLabel = formatResidence(student.residence_type);
    const fee = computeFeeStatus(student.payment_records || []);
    const batch = student.batch || "";
    const branch = student.branch || "";
    const section = student.section || "";

    const safeName = (name || "-").replace(/"/g, "&quot;");
    const safeEmail = email.replace(/"/g, "&quot;");
    const safeBatch = (batch || "").replace(/"/g, "&quot;");
    const safeBranch = (branch || "").replace(/"/g, "&quot;");
    const safeSection = (section || "").replace(/"/g, "&quot;");
    const safeRollNo = (student.roll_no || "").replace(/"/g, "&quot;");
    console.log("Student object:", student);
    const row = `
      <tr>
        <td style="font-weight: 600; color: #0d47a1;">${student.roll_no || "-"}</td>
        <td>${name}</td>
        <td style="word-break: break-all;">${email || "-"}</td>
        <td>${phone}</td>
        <td>${parentMobile}</td>
        <td><span style="padding: 6px 10px; border-radius: 6px; font-weight: 600; background: ${fee.bg}; color: ${fee.color};">${fee.label}</span></td>
        <td>${residenceLabel}</td>
        <td>
          <button class="risk-btn" data-roll-no="${safeRollNo}" data-name="${safeName}" data-semester="${student.semester != null ? student.semester : 1}">
            <i class="fas fa-heartbeat"></i> Check Risk
          </button>
        </td>
        <td>
          <button class="alert-btn" data-roll-no="${safeRollNo}" data-name="${safeName}" data-email="${safeEmail}" data-batch="${safeBatch}" data-branch="${safeBranch}" data-section="${safeSection}">
            <i class="fas fa-paper-plane"></i> Send
          </button>
        </td>
      </tr>
    `;

    tableBody.innerHTML += row;
  });

  bindAlertButtons(tableBody);
  bindRiskButtons(tableBody);
}

async function searchStudent() {
  const query = document.getElementById("lookup-search").value.trim();
  if (!query) {
    alert("Please enter a roll number or student name.");
    return;
  }

  const tableBody = document.getElementById("lookup-body");
  const resultCard = document.getElementById("lookup-result");

  resultCard.style.display = "block";
  tableBody.innerHTML =
    "<tr><td colspan='9' style='text-align:center; padding:15px;'><i class='fas fa-spinner fa-spin'></i> Searching...</td></tr>";

  try {
    if (allStudentsCache.length === 0) {
      allStudentsCache = await fetchStudentList();
    }

    const searchText = query.toUpperCase();
    const filtered = allStudentsCache.filter((student) => {
      const fullName = `${student.first_name || ""} ${student.last_name || ""}`.toUpperCase();
      const roll = (student.roll_no || "").toUpperCase();
      return roll.includes(searchText) || fullName.includes(searchText);
    });
    console.log("Filtered students:", filtered);
    renderRows(tableBody, filtered, "No students found for this search");
  } catch (error) {
    console.error("Student Search Error:", error);
    tableBody.innerHTML = `<tr><td colspan='8' style="color:red; text-align:center; padding:20px;"><i class="fas fa-exclamation-circle"></i> Error: ${error.message}</td></tr>`;
  }
}

function normalizeResidence(value) {
  if (!value) return "";
  const normalized = value.toString().trim().toUpperCase();
  if (normalized.includes("DAY")) return "DAY_SCHOLAR";
  if (normalized.includes("HOSTEL")) return "HOSTELER";
  return normalized;
}

function formatResidence(value) {
  const normalized = normalizeResidence(value);
  if (normalized === "DAY_SCHOLAR") return "Day Scholar";
  if (normalized === "HOSTELER") return "Hostel";
  return "-";
}

function computeFeeStatus(records) {
  if (!records || records.length === 0) {
    return { value: "unpaid", label: "Unpaid", bg: "#ffebee", color: "#c62828" };
  }

  const hasPaid = records.some((r) => (r.status || "").toUpperCase() === "PAID" && (r.amount_paid || 0) > 0);
  const hasPending = records.some((r) => {
    const status = (r.status || "").toUpperCase();
    const total = r.total_amount || 0;
    const paid = r.amount_paid || 0;
    return status === "PENDING" || total > paid;
  });

  if (hasPaid && hasPending) {
    return { value: "partial", label: "Partial", bg: "#fff3e0", color: "#ef6c00" };
  }
  if (hasPaid && !hasPending) {
    return { value: "paid", label: "Paid", bg: "#e8f5e9", color: "#2e7d32" };
  }
  return { value: "unpaid", label: "Unpaid", bg: "#ffebee", color: "#c62828" };
}

function bindAlertButtons(tableBody) {
  if (alertHandlerBound) return;
  tableBody.addEventListener("click", (event) => {
    const btn = event.target.closest(".alert-btn");
    if (!btn) return;

    const name = btn.getAttribute("data-name") || "Student";
    const email = (btn.getAttribute("data-email") || "").trim();
    const roll = (btn.getAttribute("data-roll-no") || "").trim();
    const batch = btn.getAttribute("data-batch") || "";
    const branch = btn.getAttribute("data-branch") || "";
    const section = btn.getAttribute("data-section") || "";

    if (!email && !roll) {
      alert("No email or roll number available for this student.");
      return;
    }

    console.log("Clicked student:", { name, email, roll });
    openStudentAlertModal({ name, email, roll_no: roll, batch, branch, section });
  });
  alertHandlerBound = true;
}

function openStudentAlertModal(student) {
  const modal = document.getElementById("studentAlertModal");
  if (!modal) return;

  document.getElementById("alert-student-name").value = student.name || "Student";
  document.getElementById("alert-student-email").value = student.email || "";
  const rollEl = document.getElementById("alert-student-roll");
  if (rollEl) rollEl.value = student.roll_no || "";
  document.getElementById("alert-student-batch").value = student.batch || "";
  document.getElementById("alert-student-branch").value = student.branch || "";
  document.getElementById("alert-student-section").value = student.section || "";

  document.getElementById("alert-title").value = "";
  document.getElementById("alert-message").value = "";
  document.getElementById("alert-category").value = "GENERAL";
  document.getElementById("alert-priority").value = "NORMAL";

  modal.style.display = "flex";
}

function closeStudentAlertModal() {
  const modal = document.getElementById("studentAlertModal");
  if (modal) {
    modal.style.display = "none";
  }
}

function isValidStudentEmail(email) {
  if (!email || email === "-") return false;
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

async function sendStudentAlert() {
  const token = localStorage.getItem("token");
  if (!token) {
    alert("Session expired. Please log in again.");
    return;
  }

  const email = document.getElementById("alert-student-email").value.trim();
  const rollEl = document.getElementById("alert-student-roll");
  const roll = rollEl ? rollEl.value.trim() : "";
  const batch = document.getElementById("alert-student-batch").value.trim();
  const branch = document.getElementById("alert-student-branch").value.trim();
  const section = document.getElementById("alert-student-section").value.trim();
  const title = document.getElementById("alert-title").value.trim();
  const message = document.getElementById("alert-message").value.trim();
  const category = document.getElementById("alert-category").value;
  const priority = document.getElementById("alert-priority").value;

  if (!isValidStudentEmail(email) && !roll) {
    alert("Enter a valid student email or ensure roll number is set (reload the student list).");
    return;
  }

  if (!batch) {
    alert("Student batch is missing. Please open Send from the student row or risk panel so batch is filled.");
    return;
  }

  if (!title || !message) {
    alert("Please fill in both Title and Message.");
    return;
  }

  const emailOk = isValidStudentEmail(email);
  let notificationOk = false;
  let alertOk = false;

  try {
    if (emailOk) {
      const payload = {
        title,
        message,
        target_role: "STUDENT",
        batch,
        branch: branch || null,
        section: section || null,
        target_email: email,
        category,
        priority,
      };
      const response = await fetch(`${API_BASE}/faculty/notifications`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || data.message || "Failed to send notification");
      }
      notificationOk = true;
    } else if (roll) {
      const severity =
        priority === "CRITICAL" ? "CRITICAL" : priority === "IMPORTANT" ? "WARNING" : "WARNING";
      const ar = await fetch(`${API_BASE}/faculty/alerts/send`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          student_roll: roll,
          title,
          message,
          severity,
        }),
      });
      const alertData = await ar.json();
      if (!ar.ok) {
        throw new Error(alertData.detail || alertData.message || "Failed to save student alert");
      }
      alertOk = true;
    }

    if (notificationOk || alertOk) {
      alert(
        notificationOk
          ? "Message delivered to the student Notifications inbox."
          : "Message saved for the student (visible under Notifications → Alerts when they log in).",
      );
      closeStudentAlertModal();
    } else {
      alert("Could not deliver message: add a valid email or roll number.");
    }
  } catch (error) {
    console.error("Alert Send Error:", error);
    alert("Error: " + (error.message || "Failed to send alert"));
  }
}

window.onclick = function (event) {
  const modal = document.getElementById("studentAlertModal");
  if (modal && event.target === modal) {
    closeStudentAlertModal();
  }

  const riskModal = document.getElementById("riskModal");
  if (riskModal && event.target === riskModal) {
    closeRiskModal();
  }
};

// ===================================
// RISK ASSESSMENT FUNCTIONS
// ===================================

let currentRiskData = null;

function bindRiskButtons(tableBody) {
  tableBody.addEventListener("click", async (event) => {
    const btn = event.target.closest(".risk-btn");
    if (!btn) return;

    const rollNo = btn.getAttribute("data-roll-no");
    const name = btn.getAttribute("data-name");
    const semester = parseInt(btn.getAttribute("data-semester") || "1", 10) || 1;

    await showRiskAssessment(rollNo, name, semester);
  });
}

async function showRiskAssessment(rollNo, studentName, semester) {
  const modal = document.getElementById("riskModal");
  if (!modal) return;

  // Show loading state
  document.getElementById("risk-student-name").textContent = studentName;
  document.getElementById("risk-level-container").innerHTML = '<div style="text-align:center;"><i class="fas fa-spinner fa-spin"></i> Loading risk assessment...</div>';
  document.getElementById("risk-explanation").textContent = "";
  document.getElementById("risk-factors").innerHTML = "";
  modal.style.display = "flex";

  try {
    const riskData = await fetchStudentRisk(rollNo, semester);

    if (!riskData || riskData.status !== "success") {
      document.getElementById("risk-level-container").innerHTML = `<div style="color:red;"><i class="fas fa-exclamation-circle"></i> Could not fetch risk data</div>`;
      return;
    }

    currentRiskData = riskData;
    populateRiskModal(riskData);
  } catch (error) {
    console.error("Error loading risk assessment:", error);
    document.getElementById("risk-level-container").innerHTML = `<div style="color:red;"><i class="fas fa-exclamation-circle"></i> Error loading data</div>`;
  }
}

function populateRiskModal(riskData) {
  const rollNo = riskData.roll_no || "N/A";
  const studentName = riskData.student_name || "Student";
  const riskLevel = riskData.risk_level || "UNKNOWN";
  const probability = riskData.risk_probability || 0;
  const explanation = riskData.explanation || "No explanation available";
  const factors = riskData.factors || {};

  document.getElementById("risk-student-name").textContent = `${studentName} (${rollNo})`;

  // Red = high, Yellow = medium, Green = low
  let bgColor = "#2e7d32";
  let textColor = "#fff";
  let icon = "fa-check-circle";
  let accent = "#2e7d32";

  if (riskLevel === "HIGH") {
    bgColor = "#c62828";
    textColor = "#fff";
    icon = "fa-exclamation-circle";
    accent = "#c62828";
  } else if (riskLevel === "MEDIUM") {
    bgColor = "#fdd835";
    textColor = "#333";
    icon = "fa-exclamation-triangle";
    accent = "#f9a825";
  }

  const badgeHtml = `<div style="padding:10px 16px; border-radius:20px; font-weight:600; background:${bgColor}; color:${textColor}; display:inline-block;">
    <i class="fas ${icon}" style="margin-right:8px;"></i>${riskLevel}
  </div>`;

  document.getElementById("risk-level-container").innerHTML = `<label style="display:block; font-weight:600; margin-bottom:8px; color:#555;">Risk Level:</label>
    <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
      ${badgeHtml}
      <span id="risk-probability" style="font-size:18px; font-weight:600; color:#333;">${probability}% failure risk</span>
    </div>`;

  document.getElementById("risk-explanation").textContent = explanation;

  const factorsHtml = `
    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
      <div style="padding:8px; background:#fff; border-left: 4px solid ${accent}; border-radius:4px;">
        <div style="font-size:12px; color:#999;">Attendance</div>
        <div style="font-size:16px; font-weight:600; color:#333;">${factors.attendance || 0}%</div>
      </div>
      <div style="padding:8px; background:#fff; border-left: 4px solid ${accent}; border-radius:4px;">
        <div style="font-size:12px; color:#999;">Backlogs</div>
        <div style="font-size:16px; font-weight:600; color:#333;">${factors.backlogs || 0}</div>
      </div>
      <div style="padding:8px; background:#fff; border-left: 4px solid ${accent}; border-radius:4px;">
        <div style="font-size:12px; color:#999;">Prev SGPA</div>
        <div style="font-size:16px; font-weight:600; color:#333;">${factors.previous_sgpa || 0}/10</div>
      </div>
      <div style="padding:8px; background:#fff; border-left: 4px solid ${accent}; border-radius:4px;">
        <div style="font-size:12px; color:#999;">Mid Score Avg</div>
        <div style="font-size:16px; font-weight:600; color:#333;">${factors.mid_score_average || 0}/30</div>
      </div>
    </div>
  `;

  document.getElementById("risk-factors").innerHTML = factorsHtml;
}

function closeRiskModal() {
  const modal = document.getElementById("riskModal");
  if (modal) {
    modal.style.display = "none";
  }
}

async function sendAlertFromRisk() {
  if (!currentRiskData) {
    alert("No risk data available");
    return;
  }

  const rollNo = currentRiskData.roll_no || "";
  const studentName = currentRiskData.student_name;
  const riskLevel = currentRiskData.risk_level;
  const probability = currentRiskData.risk_probability;
  const studentEmail = (currentRiskData.student_email || "").trim();
  const batch = (currentRiskData.batch || "").trim();
  const branch = (currentRiskData.branch || "").trim();
  const section = (currentRiskData.section || "").trim();

  closeRiskModal();

  document.getElementById("alert-student-name").value = studentName || "Student";
  const rollEl = document.getElementById("alert-student-roll");
  if (rollEl) rollEl.value = rollNo;
  document.getElementById("alert-student-email").value = studentEmail;
  document.getElementById("alert-student-batch").value = batch;
  document.getElementById("alert-student-branch").value = branch;
  document.getElementById("alert-student-section").value = section;
  document.getElementById("alert-title").value = `Academic Risk Alert - ${riskLevel} Risk (${probability}%)`;
  document.getElementById("alert-message").value = `
Student Analysis:
- Risk Level: ${riskLevel}
- Failure Probability: ${probability}%
- Analysis: ${currentRiskData.explanation}

Please review and contact the student if necessary to provide academic support.
  `;
  document.getElementById("alert-category").value = "ACADEMIC";
  document.getElementById("alert-priority").value = riskLevel === "HIGH" ? "CRITICAL" : "IMPORTANT";

  document.getElementById("studentAlertModal").style.display = "flex";
}

