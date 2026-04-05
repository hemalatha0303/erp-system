let marksChartInstance = null;
let attChartInstance = null;

const API_BASE = (() => {
  const fromDom = document.body ? document.body.dataset.apiBase : "";
  const fromWindow = window.API_BASE_URL;
  const fromStorage = localStorage.getItem("apiBaseUrl");
  const base = fromDom || fromWindow || fromStorage;
  if (base) return base.replace(/\/+$/, "");

  const origin = window.location.origin;
  if (origin && origin !== "null") {
    const url = new URL(origin);
    url.port = "8000";
    return url.toString().replace(/\/$/, "");
  }

  const hostname = window.location.hostname;
  if (hostname) {
    const protocol = window.location.protocol === "https:" ? "https:" : "http:";
    return `${protocol}//${hostname}:8000`;
  }

  return "http://127.0.0.1:8000";
})();

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => {
    const map = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
    };
    return map[char];
  });
}

function formatValue(value) {
  if (value === null || value === undefined || value === "") return "-";
  return escapeHtml(value);
}

function setButtonLoading(button, isLoading) {
  if (!button) return;
  button.disabled = isLoading;
  button.setAttribute("data-loading", isLoading ? "true" : "false");
}

function renderLookupLoading(content) {
  content.innerHTML = `
    <div class="lookup-status loading">
      <span class="status-spinner"></span>
      <div>
        <div class="lookup-title">Fetching student details</div>
        <div class="lookup-hint">Please wait a moment while we load the record.</div>
      </div>
    </div>
    <div class="lookup-skeleton">
      <div class="skeleton-line skeleton-title"></div>
      <div class="skeleton-grid">
        <div class="skeleton-line"></div>
        <div class="skeleton-line"></div>
        <div class="skeleton-line"></div>
        <div class="skeleton-line"></div>
      </div>
    </div>
  `;
}

function renderLookupError(content, title, message, hint) {
  const safeTitle = escapeHtml(title);
  const safeMessage = escapeHtml(message);
  const safeHint = hint ? escapeHtml(hint) : "";

  content.innerHTML = `
    <div class="lookup-status error">
      <span class="status-icon"><i class="fas fa-circle-exclamation"></i></span>
      <div>
        <div class="lookup-title">${safeTitle}</div>
        <div class="lookup-hint">${safeMessage}</div>
        ${safeHint ? `<div class="lookup-hint">${safeHint}</div>` : ""}
      </div>
    </div>
    <div class="lookup-actions-row">
      <button class="secondary-btn" onclick="lookupStudent()">Retry</button>
    </div>
  `;
}

function renderLookupSuccess(content, data) {
  const fullName =
    `${data.first_name || ""} ${data.last_name || ""}`.trim() || "Student";
  const rollNo = data.roll_no || "";
  const metaParts = [
    data.roll_no,
    data.branch,
    data.batch,
    data.section ? `Sec ${data.section}` : null,
  ].filter(Boolean);

  const fields = [
    { label: "Email", value: data.email },
    { label: "Mobile", value: data.mobile_no },
    { label: "Parent Mobile", value: data.parent_mobile_no },
    { label: "Course", value: data.course },
    { label: "Status", value: data.status },
    { label: "Residence", value: data.residence_type },
  ];

  content.innerHTML = `
    <div class="lookup-header">
      <div>
        <div class="lookup-name">${escapeHtml(fullName)}</div>
        <div class="lookup-sub">${escapeHtml(metaParts.join(" | ") || "Profile details")}</div>
      </div>
      <button class="primary-btn lookup-alert-btn" id="lookup-alert-btn">
        <i class="fas fa-bell"></i> Send Alert
      </button>
    </div>
    <div class="lookup-grid">
      <div class="lookup-item">
        <div class="lookup-label">Roll No</div>
        <div class="lookup-value">${formatValue(rollNo)}</div>
      </div>
      <div class="lookup-item">
        <div class="lookup-label">Branch</div>
        <div class="lookup-value">${formatValue(data.branch)}</div>
      </div>
      <div class="lookup-item">
        <div class="lookup-label">Batch</div>
        <div class="lookup-value">${formatValue(data.batch)}</div>
      </div>
      <div class="lookup-item">
        <div class="lookup-label">Section</div>
        <div class="lookup-value">${formatValue(data.section)}</div>
      </div>
      ${fields
        .map(
          (field) => `
            <div class="lookup-item">
              <div class="lookup-label">${escapeHtml(field.label)}</div>
              <div class="lookup-value">${formatValue(field.value)}</div>
            </div>
          `,
        )
        .join("")}
    </div>
  `;

  const alertBtn = content.querySelector("#lookup-alert-btn");
  if (alertBtn) {
    alertBtn.addEventListener("click", () => openAlertModal(rollNo));
  }
}

async function lookupStudent() {
  const input = document.getElementById("lookup-roll");
  const button = document.getElementById("lookup-btn");
  const roll = input ? input.value.trim().toUpperCase() : "";
  if (!roll) {
    alert("Please enter a roll number");
    return;
  }

  const container = document.getElementById("student-details-card");
  const content = document.getElementById("lookup-result-content");
  const token = localStorage.getItem("token");

  if (!container || !content) return;

  container.style.display = "block";
  setButtonLoading(button, true);
  renderLookupLoading(content);

  try {
    if (!token) {
      throw new Error("Session expired. Please sign in again.");
    }

    const res = await fetch(
      `${API_BASE}/hod/student/${encodeURIComponent(roll)}`,
      {
        headers: { Authorization: `Bearer ${token}` },
      },
    );

    if (!res.ok) {
      let errorMsg = `Error ${res.status}`;
      try {
        const errData = await res.json();
        if (errData.detail) {
          errorMsg =
            typeof errData.detail === "string"
              ? errData.detail
              : JSON.stringify(errData.detail);
        }
      } catch (e) {
        console.error("Could not parse error response:", e);
        // Error body not JSON, use status code
      }

      if (res.status === 404) {
        errorMsg = "No student found for that roll number.";
      }

      if (res.status === 401) {
        errorMsg = "Session expired. Please sign in again.";
      }

      throw new Error(errorMsg);
    }

    const data = await res.json();
    if (data) {
      renderLookupSuccess(content, data);
    }
  } catch (e) {
    console.error("Student lookup error:", e);
    let errorMsg = "Network Error";
    if (e instanceof Error) {
      errorMsg = e.message;
    }
    if (typeof errorMsg !== "string") {
      errorMsg = JSON.stringify(errorMsg);
    }

    const isNetworkError =
      errorMsg === "Failed to fetch" ||
      /NetworkError|Failed to connect|Load failed/i.test(errorMsg);

    const title = isNetworkError
      ? "Can't reach the server"
      : "Unable to load student details";
    const hint = isNetworkError
      ? `Make sure the backend is running at ${API_BASE}.`
      : "";

    renderLookupError(content, title, errorMsg, hint);
  } finally {
    setButtonLoading(button, false);
  }
}

// --- 2. Batch Analytics (Table + Charts) ---
async function fetchStudentAnalytics() {
  const batch = document.getElementById("st-batch").value.trim();
  const branch = document.getElementById("st-branch").value;
  const sem = document.getElementById("st-sem").value;
  const sec = document.getElementById("st-sec").value;
  const token = localStorage.getItem("token");

  const table = document.getElementById("st-results");
  const chartContainer = document.getElementById("analytics-charts");
  const tbody = document.getElementById("student-list");

  // Show sections
  table.style.display = "block";
  tbody.innerHTML =
    "<tr><td colspan='6' style='text-align:center;'>Fetching Data...</td></tr>";

  try {
    const params = new URLSearchParams();
    if (batch) params.append("batch", batch);
    if (branch && branch !== "ALL") params.append("branch", branch);
    if (sem && sem !== "ALL") params.append("semester", sem);
    if (sec && sec !== "ALL") params.append("section", sec);

    const res = await fetch(
      `${API_BASE}/hod/students-analytics?${params.toString()}`,
      {
        headers: { Authorization: `Bearer ${token}` },
      },
    );

    if (res.ok) {
      const data = await res.json();
      tbody.innerHTML = "";

      if (data.length === 0) {
        tbody.innerHTML =
          "<tr><td colspan='6' style='text-align:center;'>No data found for this batch.</td></tr>";
        chartContainer.style.display = "none";
        return;
      }

      // A. Populate Table
      data.forEach((s) => {
        const row = `
                    <tr>
                        <td style="font-weight:600;">${s.roll}</td>
                        <td>${s.name}</td>
                        <td>${s.m1}</td>
                        <td>${s.m2}</td>
                        <td>${s.att}</td>
                        <td>${s.ph || "-"}</td>
                    </tr>
                `;
        tbody.innerHTML += row;
      });

      // B. Render Charts
      chartContainer.style.display = "grid";
      renderCharts(data);
    } else {
      tbody.innerHTML =
        "<tr><td colspan='6' style='color:red; text-align:center;'>Failed to fetch data</td></tr>";
      chartContainer.style.display = "none";
    }
  } catch (error) {
    console.error(error);
    tbody.innerHTML =
      "<tr><td colspan='6' style='color:red; text-align:center;'>Network Error</td></tr>";
    chartContainer.style.display = "none";
  }
}

function renderCharts(students) {
  const attendanceBuckets = {
    "Excellent (>=85%)": 0,
    "Good (70-84%)": 0,
    "Average (50-69%)": 0,
    "Low (<50%)": 0,
  };

  const academicBuckets = {
    "Excellent (>=80%)": 0,
    "Good (60-79%)": 0,
    "Average (40-59%)": 0,
    "Poor (<40%)": 0,
  };

  students.forEach((s) => {
    const att = parseFloat(String(s.att).replace("%", "")) || 0;
    if (att >= 85) attendanceBuckets["Excellent (>=85%)"] += 1;
    else if (att >= 70) attendanceBuckets["Good (70-84%)"] += 1;
    else if (att >= 50) attendanceBuckets["Average (50-69%)"] += 1;
    else attendanceBuckets["Low (<50%)"] += 1;

    const total = (s.m1 || 0) + (s.m2 || 0);
    const percent = (total / 60) * 100;
    if (percent >= 80) academicBuckets["Excellent (>=80%)"] += 1;
    else if (percent >= 60) academicBuckets["Good (60-79%)"] += 1;
    else if (percent >= 40) academicBuckets["Average (40-59%)"] += 1;
    else academicBuckets["Poor (<40%)"] += 1;
  });

  if (marksChartInstance) marksChartInstance.destroy();
  if (attChartInstance) attChartInstance.destroy();

  const ctx1 = document.getElementById("marksChart").getContext("2d");
  marksChartInstance = new Chart(ctx1, {
    type: "pie",
    data: {
      labels: Object.keys(academicBuckets),
      datasets: [
        {
          label: "Academic Performance",
          data: Object.values(academicBuckets),
          backgroundColor: ["#2e7d32", "#1976d2", "#f9a825", "#c62828"],
          borderWidth: 1
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: { display: true, text: "Academic Performance (Mid Scores)" },
      }
    },
  });

  const ctx2 = document.getElementById("attendanceChart").getContext("2d");
  attChartInstance = new Chart(ctx2, {
    type: "pie",
    data: {
      labels: Object.keys(attendanceBuckets),
      datasets: [
        {
          label: "Attendance",
          data: Object.values(attendanceBuckets),
          backgroundColor: ["#2e7d32", "#0288d1", "#f9a825", "#d32f2f"],
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: { display: true, text: "Attendance Distribution" },
      }
    },
  });
}

// --- 3. ALERT LOGIC ---
function openAlertModal(roll) {
  document.getElementById('alert-target-roll').value = roll;
  document.getElementById('alertModal').style.display = 'flex';
}

function closeAlertModal() {
  document.getElementById('alertModal').style.display = 'none';
}

async function sendStudentAlert() {
  const payload = {
      student_roll: document.getElementById('alert-target-roll').value.trim(),
      severity: document.getElementById('alert-severity').value,
      title: document.getElementById('alert-title').value.trim(),
      message: document.getElementById('alert-message').value.trim()
  };

  if (!payload.student_roll || !payload.title || !payload.message) {
      alert("Please fill in the Title and Message fields.");
      return;
  }

  const token = localStorage.getItem("token");

  try {
      const res = await fetch(`${API_BASE}/hod/alerts/send`, {
          method: "POST",
          headers: {
              "Content-Type": "application/json",
              "Authorization": `Bearer ${token}`
          },
          body: JSON.stringify(payload)
      });

      const data = await res.json();
      
      if (res.ok) {
          alert( data.message);
          closeAlertModal();
          

          document.getElementById('alert-title').value = "";
          document.getElementById('alert-message').value = "";
      } else {
          alert("Failed: " + (data.detail || "Unknown error"));
      }
  } catch (error) {
      console.error("Alert Error:", error);
      alert("Network Error while sending the alert.");
  }
}


window.onclick = function(event) {
  const modal = document.getElementById('alertModal');
  if (event.target == modal) {
      closeAlertModal();
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("lookup-roll");
  if (!input) return;

  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      lookupStudent();
    }
  });
});




