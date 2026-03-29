let inboxNotifications = [];
let inboxLoaded = false;

function showTab(tab) {
  const sendView = document.getElementById("send-view");
  const inboxView = document.getElementById("inbox-view");
  const tabSend = document.getElementById("tab-send");
  const tabInbox = document.getElementById("tab-inbox");

  if (tab === "send") {
    sendView.style.display = "block";
    inboxView.style.display = "none";
    tabSend.classList.add("active");
    tabInbox.classList.remove("active");
  } else {
    sendView.style.display = "none";
    inboxView.style.display = "block";
    tabInbox.classList.add("active");
    tabSend.classList.remove("active");
    if (!inboxLoaded) fetchInboxNotifications();
  }
}

function toggleTargetFilters() {
  const target = document.getElementById("n-target").value;
  const batchGroup = document.getElementById("batch-group");
  const facultyGroup = document.getElementById("faculty-group");
  const studentGroup = document.getElementById("student-group");

  if (target === "FACULTY") {
    batchGroup.style.display = "block";
    facultyGroup.style.display = "grid";
    studentGroup.style.display = "none";
  } else if (target === "STUDENT") {
    batchGroup.style.display = "block";
    facultyGroup.style.display = "none";
    studentGroup.style.display = "grid";
  } else {
    batchGroup.style.display = "none";
    facultyGroup.style.display = "none";
    studentGroup.style.display = "none";
  }
}

async function sendHodNotification() {
  const token = localStorage.getItem("token");
  const targetRole = document.getElementById("n-target").value;
  const batch = document.getElementById("n-batch").value.trim();
  const branchFaculty = document.getElementById("n-branch-faculty").value;
  const branchStudent = document.getElementById("n-branch-student").value;
  const section = document.getElementById("n-section").value;

  if (targetRole === "FACULTY" && !batch) {
    alert("Please enter batch for faculty notifications.");
    return;
  }
  if (targetRole === "STUDENT" && !batch) {
    alert("Please enter batch for student notifications.");
    return;
  }

  const payload = {
    title: document.getElementById("n-title").value,
    message: document.getElementById("n-message").value,
    category: document.getElementById("n-category").value,
    priority: document.getElementById("n-priority").value,
    target_role: targetRole,
    batch: targetRole === "ALL" ? null : batch || null,
    branch:
      targetRole === "FACULTY"
        ? (branchFaculty === "ALL" ? null : branchFaculty)
        : targetRole === "STUDENT"
        ? (branchStudent === "ALL" ? null : branchStudent)
        : null,
    section:
      targetRole === "STUDENT" && section !== "ALL" ? section : null,
  };

  try {
    const response = await fetch("http://127.0.0.1:8000/hod/notifications", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (response.ok) {
      alert("Notification sent successfully!");
      document.getElementById("hod-notification-form").reset();
      toggleTargetFilters();
    } else {
      const raw = await response.text();
      let error = {};
      try {
        error = raw ? JSON.parse(raw) : {};
      } catch (e) {
        error = { detail: raw };
      }
      alert("Error: " + (error.detail || error.message || "Failed to send"));
    }
  } catch (err) {
    console.error(err);
    alert("Network Error");
  }
}

async function fetchInboxNotifications() {
  inboxLoaded = true;
  const token = localStorage.getItem("token");
  const listContainer = document.getElementById("notification-list");
  listContainer.innerHTML = `<div style="text-align:center; padding:20px; color:#666;">Loading notifications...</div>`;

  try {
    const response = await fetch("http://127.0.0.1:8000/hod/notifications", {
      headers: { Authorization: `Bearer ${token}` }
    });

    if (response.ok) {
      const data = await response.json();
      const mapped = data
        .filter((n) => !n.sender_role || n.sender_role === "ADMIN")
        .map((item) => ({
          id: item.id,
          title: item.title,
          message: item.message,
          category: item.category || "GENERAL",
          priority: (item.priority || "NORMAL").toUpperCase(),
          timestamp: new Date(item.created_at),
          time: formatTimeAgo(item.created_at),
          icon: getIconForCategory(item.category || "GENERAL"),
        }));

      inboxNotifications = mapped.sort((a, b) => b.timestamp - a.timestamp);
      renderInbox("ALL");
    } else {
      listContainer.innerHTML = `<div class="error-msg" style="color:red; text-align:center;">Failed to load notifications</div>`;
    }
  } catch (error) {
    console.error("Error:", error);
    listContainer.innerHTML = `<div class="error-msg" style="color:red; text-align:center;">Network error</div>`;
  }
}

function getIconForCategory(category) {
  const map = {
    ACADEMIC: "fa-graduation-cap",
    FEES: "fa-money-bill-wave",
    HOSTEL: "fa-bed",
    LIBRARY: "fa-book",
    EVENT: "fa-calendar-alt",
    GENERAL: "fa-bullhorn",
    ALERT: "fa-exclamation-triangle"
  };
  return map[category] || "fa-bell";
}

function formatTimeAgo(dateString) {
  const date = new Date(dateString);
  const now = new Date();
  const seconds = Math.floor((now - date) / 1000);
  if (seconds < 60) return "Just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes} mins ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} hours ago`;
  return `${Math.floor(hours / 24)} days ago`;
}

function renderInbox(filter) {
  const container = document.getElementById("notification-list");
  container.innerHTML = "";

  const filtered =
    filter === "ALL"
      ? inboxNotifications
      : inboxNotifications.filter((n) => n.category === filter);

  if (filtered.length === 0) {
    container.innerHTML = `<div class="empty-state" style="text-align:center; padding:30px; color:#888;">No notifications found.</div>`;
    return;
  }

  filtered.forEach((item) => {
    const priorityClass = `priority-${item.priority.toLowerCase()}`;
    const typeClass = `type-${item.category.toLowerCase()}`;
    const card = `
      <div class="notif-card ${priorityClass}">
        <div class="notif-icon ${typeClass}">
          <i class="fas ${item.icon}"></i>
        </div>
        <div class="notif-content">
          <div class="notif-header">
            <span class="notif-title">${item.title}</span>
            <span class="notif-tag">${item.category}</span>
          </div>
          <div class="notif-msg">${item.message}</div>
          <span class="notif-time">${item.time}</span>
        </div>
      </div>
    `;
    container.innerHTML += card;
  });
}

function filterInbox(category, btn) {
  document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
  btn.classList.add("active");
  renderInbox(category);
}

document.addEventListener("DOMContentLoaded", () => {
  toggleTargetFilters();
});
