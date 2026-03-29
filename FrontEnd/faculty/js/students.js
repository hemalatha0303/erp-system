let allStudentsCache = [];
let alertHandlerBound = false;

async function fetchStudentList() {
  const token = localStorage.getItem("token");
  
  if (!token) {
    throw new Error("Not authenticated. Please log in again.");
  }

  try {
    const response = await fetch("http://127.0.0.1:8000/faculty/student-list", {
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
    "<tr><td colspan='8' style='text-align:center; padding:15px;'><i class='fas fa-spinner fa-spin'></i> Loading students...</td></tr>";

  try {
    allStudentsCache = await fetchStudentList();
    renderLookupResults(tableBody);
  } catch (error) {
    console.error("Student Load Error:", error);
    tableBody.innerHTML = `<tr><td colspan='8' style="color:red; text-align:center; padding:20px;"><i class="fas fa-exclamation-circle"></i> Error: ${error.message}</td></tr>`;
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

function renderRows(tableBody, students, emptyMessage) {
  if (!students || students.length === 0) {
    tableBody.innerHTML =
      `<tr><td colspan='8' style='text-align:center; padding:20px; color:#999;'><i class='fas fa-search'></i> ${emptyMessage}</td></tr>`;
    return;
  }

  tableBody.innerHTML = "";
  students.forEach((student) => {
    const name = `${student.first_name || ""} ${student.last_name || ""}`.trim() || "-";
    const email = student.email || student.user_email || "-";
    const phone = student.mobile_no || "-";
    const parentMobile = student.parent_mobile_no || "-";
    const residenceLabel = formatResidence(student.residence_type);
    const fee = computeFeeStatus(student.payment_records || []);
    const batch = student.batch || "";
    const branch = student.branch || "";
    const section = student.section || "";

    const safeName = (name || "-").replace(/"/g, "&quot;");
    const safeEmail = (email || "-").replace(/"/g, "&quot;");
    const safeBatch = (batch || "").replace(/"/g, "&quot;");
    const safeBranch = (branch || "").replace(/"/g, "&quot;");
    const safeSection = (section || "").replace(/"/g, "&quot;");

    const row = `
      <tr>
        <td style="font-weight: 600; color: #0d47a1;">${student.roll_no || "-"}</td>
        <td>${name}</td>
        <td style="word-break: break-all;">${email}</td>
        <td>${phone}</td>
        <td>${parentMobile}</td>
        <td><span style="padding: 6px 10px; border-radius: 6px; font-weight: 600; background: ${fee.bg}; color: ${fee.color};">${fee.label}</span></td>
        <td>${residenceLabel}</td>
        <td>
          <button class="alert-btn" data-name="${safeName}" data-email="${safeEmail}" data-batch="${safeBatch}" data-branch="${safeBranch}" data-section="${safeSection}">
            <i class="fas fa-paper-plane"></i> Send
          </button>
        </td>
      </tr>
    `;

    tableBody.innerHTML += row;
  });

  bindAlertButtons(tableBody);
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
    "<tr><td colspan='8' style='text-align:center; padding:15px;'><i class='fas fa-spinner fa-spin'></i> Searching...</td></tr>";

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
    const email = btn.getAttribute("data-email") || "";
    const batch = btn.getAttribute("data-batch") || "";
    const branch = btn.getAttribute("data-branch") || "";
    const section = btn.getAttribute("data-section") || "";

    openStudentAlertModal({ name, email, batch, branch, section });
  });
  alertHandlerBound = true;
}

function openStudentAlertModal(student) {
  const modal = document.getElementById("studentAlertModal");
  if (!modal) return;

  document.getElementById("alert-student-name").value = student.name || "Student";
  document.getElementById("alert-student-email").value = student.email || "";
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

async function sendStudentAlert() {
  const token = localStorage.getItem("token");
  if (!token) {
    alert("Session expired. Please log in again.");
    return;
  }

  const email = document.getElementById("alert-student-email").value.trim();
  const batch = document.getElementById("alert-student-batch").value.trim();
  const branch = document.getElementById("alert-student-branch").value.trim();
  const section = document.getElementById("alert-student-section").value.trim();
  const title = document.getElementById("alert-title").value.trim();
  const message = document.getElementById("alert-message").value.trim();
  const category = document.getElementById("alert-category").value;
  const priority = document.getElementById("alert-priority").value;

  if (!email) {
    alert("Student email is missing.");
    return;
  }

  if (!batch) {
    alert("Student batch is missing. Please refresh the list.");
    return;
  }

  if (!title || !message) {
    alert("Please fill in both Title and Message.");
    return;
  }

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

  try {
    const response = await fetch("http://127.0.0.1:8000/faculty/notifications", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || data.message || "Failed to send alert");
    }

    alert("Alert sent successfully!");
    closeStudentAlertModal();
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
};
