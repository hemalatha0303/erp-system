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
    const response = await fetch("http://127.0.0.1:8000/student/dashboard", {
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
      alertMsg.innerText = data.ai_insight;
      alertBox.style.display = "flex";

      if (data.stats.attendance < 75) {
        alertBox.className = "alert-box danger";
        if (alertTitle) alertTitle.innerText = "Attendance Warning";
        if (alertIcon) alertIcon.className = "fas fa-exclamation-triangle";
      } else {
        alertBox.className = "alert-box success";
        alertBox.style.backgroundColor = "#d5f5e3";
        alertBox.style.borderLeft = "4px solid #27ae60";

        if (alertTitle) alertTitle.innerText = "Attendance Status";
        if (alertIcon) alertIcon.className = "fas fa-check-circle";
        if (alertIcon) alertIcon.style.color = "#27ae60";
      }
    }
    if (alertBox) {
      alertBox.style.display = "flex";

      const dashboardWrapper = document.querySelector(".dashboard-wrapper");
      if (dashboardWrapper) {
        dashboardWrapper.style.marginTop = "1vh";
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

    const response = await fetch("http://127.0.0.1:8000/student/timetable", {
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
