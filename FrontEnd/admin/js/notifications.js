function toggleBatchInput() {
  const target = document.getElementById("n-target").value;
  const batchGroup = document.getElementById("batch-group");
  batchGroup.style.display = target === "STUDENT" ? "block" : "none";
}

async function sendNotification() {
  const token = localStorage.getItem("token");

  const payload = {
    title: document.getElementById("n-title").value,
    message: document.getElementById("n-message").value,
    category: document.getElementById("n-category").value, // New
    priority: document.getElementById("n-priority").value, // New
    target_role: document.getElementById("n-target").value,
    batch: document.getElementById("n-batch").value.trim() || null,
  };

  try {
    const response = await fetch("http://127.0.0.1:8000/admin/notifications", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (response.ok) {
      alert(" Notification Sent Successfully!");
      document.getElementById("notification-form").reset();
      toggleBatchInput();
    } else {
      const error = await response.json();
      alert(" Error: " + (error.detail || "Failed to send"));
    }
  } catch (err) {
    console.error(err);
    alert(" Network Error");
  }
}
