const API_BASE = typeof API_URL !== "undefined" ? API_URL : "http://127.0.0.1:8000";
function toggleTimetableInputs() {
  const type = document.getElementById("tt-type").value;
  const classInputs = document.querySelectorAll(".class-only");
  const facInputs = document.querySelectorAll(".fac-only");

  if (type === "CLASS") {
    classInputs.forEach((el) => (el.style.display = "inline-block"));
    facInputs.forEach((el) => (el.style.display = "none"));
  } else {
    classInputs.forEach((el) => (el.style.display = "none"));
    facInputs.forEach((el) => (el.style.display = "inline-block"));
  }
}

async function uploadTimetable() {
  const file = document.getElementById("tt-file").files[0];
  if (!file) {
    alert("Please select an image file.");
    return;
  }

  const batchInput = document.getElementById("tt-year").value.trim();
  const semester = document.getElementById("tt-sem").value;
  const branch = document.getElementById("tt-branch").value;
  const type = document.getElementById("tt-type").value;

  if (!batchInput || !semester || !branch) {
    alert("Please fill in all required fields: Batch, Semester, Branch");
    return;
  }

  // Extract year from batch format (e.g., "2022-26" -> 2022)
  const yearMatch = batchInput.match(/^(\d{4})/);
  const year = yearMatch ? parseInt(yearMatch[1]) : parseInt(batchInput);
  
  if (isNaN(year)) {
    alert("Invalid batch format. Expected format: YYYY-XX (e.g., 2022-26) or just the year (e.g., 2022)");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);
  formData.append("year", year);
  formData.append("semester", semester);
  formData.append("branch", branch);

  if (type === "CLASS") {
    const section = document.getElementById("tt-sec").value;
    if (!section) {
      alert("Please enter Section for Class Timetable");
      return;
    }
    formData.append("section", section);
  } else {
    const facEmail = document.getElementById("tt-fac-email").value;
    if (!facEmail) {
      alert("Please enter Faculty Email for Faculty Workload");
      return;
    }
    formData.append("faculty_email", facEmail);
  }

  try {
    const token = localStorage.getItem("token");
    const res = await fetch(`${API_BASE}/hod/timetable/upload`, {
      method: "POST",
      headers: { Authorization: "Bearer " + token },
      body: formData,
    });

    const data = await res.json();

    if (res.ok) {
      alert(data.message || "Timetable uploaded successfully");
      document.getElementById("tt-file").value = "";
      document.getElementById("tt-year").value = "";
      document.getElementById("tt-sec").value = "";
      document.getElementById("tt-branch").value = "";
      document.getElementById("tt-fac-email").value = "";
    } else {
      let errorDetail = data.detail || data.message || "Upload failed";
      if (typeof errorDetail !== 'string') {
        errorDetail = JSON.stringify(errorDetail);
      }
      console.error("Upload error:", errorDetail);
      alert("Error: " + errorDetail);
    }
  } catch (e) {
    console.error("Network error:", e);
    alert("Network Error: " + (e.message || "Failed to upload timetable"));
  }
}
