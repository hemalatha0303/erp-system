const API_BASE = typeof API_URL !== "undefined" ? API_URL : "http://127.0.0.1:8000";
document.addEventListener("DOMContentLoaded", () => {
  initDashboard();
  loadTimetable();
});

async function initDashboard() {
  const dateElement = document.getElementById("current-date");
  if (dateElement) {
    const dateOptions = {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    };
    dateElement.innerText = new Date().toLocaleDateString("en-US", dateOptions);
  }

  const token = localStorage.getItem("token");
  if (!token) {
    window.location.href = "../../index.html";
    return;
  }

  try {
    const response = await fetch(`${API_BASE}/student/dashboard`, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) throw new Error("Failed to load dashboard data");

    const data = await response.json();

    if (document.getElementById("welcome-name"))
      document.getElementById("welcome-name").innerText =
        data.profile.name.split(" ")[0];

    if (document.getElementById("profile-name"))
      document.getElementById("profile-name").innerText = data.profile.name;

    if (document.getElementById("profile-year"))
      document.getElementById("profile-year").innerText =
        `Sem ${data.profile.semester}`;

    if (document.getElementById("profile-branch"))
      document.getElementById("profile-branch").innerText = data.profile.branch;

    if (document.getElementById("profile-teacher"))
      document.getElementById("profile-teacher").innerText = "N/A";

    const alertBox = document.getElementById("ai-alert-box");
    const alertMsg = document.getElementById("ai-attendance-msg");
    const alertIcon = document.getElementById("ai-icon");
    const alertTitle = document.getElementById("ai-title");

    if (alertBox && alertMsg) {
      alertBox.style.display = "flex";

      // Show AI insight message (Low Risk/High Risk/Moderate Risk)
      if (data.ai_insight) {
        // Parse AI message to determine risk level
        const aiText = data.ai_insight;
        
        if (aiText.includes("Low Risk")) {
          alertBox.className = "alert-box success";
          if (alertIcon) {
            alertIcon.className = "fas fa-check-circle";
            alertIcon.style.color = "#27ae60";
          }
          if (alertTitle) alertTitle.innerText = "Academic Status";
        } else if (aiText.includes("High Risk")) {
          alertBox.className = "alert-box danger";
          if (alertIcon) {
            alertIcon.className = "fas fa-exclamation-circle";
            alertIcon.style.color = "#c0392b";
          }
          if (alertTitle) alertTitle.innerText = "Academic Warning";
        } else if (aiText.includes("Moderate Risk")) {
          alertBox.className = "alert-box warning";
          if (alertIcon) {
            alertIcon.className = "fas fa-exclamation-triangle";
            alertIcon.style.color = "#f39c12";
          }
          if (alertTitle) alertTitle.innerText = "Academic Alert";
        }
        
        alertMsg.innerHTML = aiText.replace(/\n/g, "<br>");
      } else if (data.stats.attendance < 75) {
        // Fallback to attendance warning if ai_insight not available
        alertBox.className = "alert-box danger";
        if (alertTitle) alertTitle.innerText = "Attendance Warning";
        if (alertIcon) {
          alertIcon.className = "fas fa-exclamation-triangle";
          alertIcon.style.color = "#c0392b";
        }
        alertMsg.innerText = `Your current attendance is ${data.stats.attendance}%. It's below the required 75%. Please improve your attendance immediately.`;
      } else {
        alertBox.className = "alert-box success";
        if (alertTitle) alertTitle.innerText = "Attendance Status";
        if (alertIcon) {
          alertIcon.className = "fas fa-check-circle";
          alertIcon.style.color = "#27ae60";
        }
        alertMsg.innerText = `Your current attendance is ${data.stats.attendance}%. Good job! Keep maintaining your attendance.`;
      }
    }
    const circle = document.getElementById("attendance-circle");
    const percentage = data.stats.attendance;
    const degrees = (percentage / 100) * 360;

    if (circle) {
      circle.style.setProperty("--progress", `${degrees}deg`);
      circle.style.setProperty(
        "--color",
        percentage < 75 ? "#e74c3c" : "#2ecc71",
      );
    }
    updateStat("stat-attendance", `${percentage}%`);

    updateStat("stat-cgpa", data.stats.cgpa || "0.0");

    const feeText =
      data.stats.fee_dues > 0
        ? `₹ ${data.stats.fee_dues.toLocaleString()} Due`
        : "No Dues";
    updateStat("stat-fees", feeText);

    updateStat("stat-library", data.stats.library_books);
  } catch (error) {
    console.error("Dashboard Load Error:", error);
  }
}

function updateStat(id, value) {
  const el = document.getElementById(id);
  if (el) el.innerText = value;
}

async function loadTimetable() {
  try {
    const token = localStorage.getItem("token");

    const response = await fetch(`${API_BASE}/student/timetable`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    const data = await response.json();
    const imgElement = document.getElementById("tt-image");
    const msgElement = document.getElementById("tt-msg");

    console.log( data.image_url);
    if (data.image_url) {
      imgElement.src = data.image_url;
      imgElement.style.display = "block";
      msgElement.style.display = "none";
    } else {
      msgElement.textContent = "No timetable uploaded yet.";
    }
  } catch (error) {
    console.error("Error loading timetable:", error);
  }
}
