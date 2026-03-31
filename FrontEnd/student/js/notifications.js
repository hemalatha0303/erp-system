const API_BASE = typeof API_URL !== "undefined" ? API_URL : "http://127.0.0.1:8000";
document.addEventListener("DOMContentLoaded", () => {
  fetchNotifications();
});

let notifications = [];

async function fetchNotifications() {
  const token = localStorage.getItem("token");
  const listContainer = document.getElementById("notification-list");
  listContainer.innerHTML = `<div style="text-align:center; padding:20px; color:#666;">Loading notifications...</div>`;

  try {

    const [notifResponse, alertResponse] = await Promise.all([
      fetch(`${API_BASE}/student/notifications`, { headers: { Authorization: `Bearer ${token}` } }),
      fetch(`${API_BASE}/student/alerts`, { headers: { Authorization: `Bearer ${token}` } })
    ]);

    let combinedData = [];

    if (notifResponse.ok) {
      const data = await notifResponse.json();
      const mappedNotifs = data.map((item) => ({
        id: `notif_${item.id}`,
        title: item.title,
        message: item.message,
        category: item.category, 
        priority: item.priority, 
        timestamp: new Date(item.created_at), 
        time: formatTimeAgo(item.created_at),
        icon: getIconForCategory(item.category),
      }));
      combinedData.push(...mappedNotifs);
    }


    if (alertResponse.ok) {
      const alerts = await alertResponse.json();
      const mappedAlerts = alerts.map((item) => {

        let prio = 'NORMAL';
        if (item.severity === 'CRITICAL') prio = 'CRITICAL';
        if (item.severity === 'WARNING') prio = 'HIGH';

        return {
          id: `alert_${item.id}`,
          title: `[${item.sender_role} ALERT] ${item.title}`,
          message: item.message,
          category: 'ALERT', 
          priority: prio,
          timestamp: new Date(item.created_at), 
          time: formatTimeAgo(item.created_at),
          icon: "fa-exclamation-triangle",
        };
      });
      combinedData.push(...mappedAlerts);
    }


    combinedData.sort((a, b) => b.timestamp - a.timestamp);
    
    notifications = combinedData;
    renderNotifications("ALL");

  } catch (error) {
    console.error("Error:", error);
    listContainer.innerHTML = `<div class="error-msg" style="color:red; text-align:center;">Failed to load notifications</div>`;
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

function renderNotifications(filter) {
  const container = document.getElementById("notification-list");
  container.innerHTML = "";

  const filtered = filter === "ALL"
      ? notifications
      : notifications.filter((n) => n.category === filter);

  if (filtered.length === 0) {
    container.innerHTML = `<div class="empty-state" style="text-align:center; padding:30px; color:#888;">No notifications found for this category.</div>`;
    return;
  }

  filtered.forEach((item) => {
    const priorityClass = `priority-${item.priority.toLowerCase()}`;
    const typeClass = `type-${item.category.toLowerCase()}`;


    const isAlert = item.category === 'ALERT';
    const borderStyle = isAlert ? 'border-left: 5px solid #e74c3c; background-color: #fffaf9;' : '';

    const card = `
        <div class="notif-card ${priorityClass}" style="${borderStyle}">
            <div class="notif-icon ${typeClass}">
                <i class="fas ${item.icon}"></i>
            </div>
            <div class="notif-content">
                <div class="notif-header">
                    <span class="notif-title" style="${isAlert ? 'color:#c62828; font-weight:bold;' : ''}">${item.title}</span>
                    <span class="notif-tag">${item.category}</span>
                </div>
                <div class="notif-msg">${item.message}</div>
                <div class="notif-footer">
                    <span class="notif-time">${item.time}</span>
                </div>
            </div>
        </div>
    `;
    container.innerHTML += card;
  });
}


function filterNotifications(category, btn) {
  document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
  btn.classList.add("active");
  renderNotifications(category);
}

function markAllAsRead() {
    alert("All notifications marked as read!");
}