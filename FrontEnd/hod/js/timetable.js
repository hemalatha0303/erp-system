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

  const formData = new FormData();
  formData.append("file", file);
  formData.append("year", document.getElementById("tt-year").value);
  formData.append("semester", document.getElementById("tt-sem").value);
  formData.append("branch", document.getElementById("tt-branch").value);

  const type = document.getElementById("tt-type").value;

  if (type === "CLASS") {
    formData.append("section", document.getElementById("tt-sec").value);
    formData.append("faculty_email", "");
  } else {
    formData.append("section", "");
    formData.append(
      "faculty_email",
      document.getElementById("tt-fac-email").value,
    );
  }

  try {
    const token = localStorage.getItem("token");
    const res = await fetch("http://127.0.0.1:8000/hod/timetable/upload", {
      method: "POST",
      headers: { Authorization: "Bearer " + token },
      body: formData,
    });
    const data = await res.json();

    if (res.ok) alert(data.message);
    else alert("Error: " + (data.detail || "Upload failed"));
  } catch (e) {
    console.error(e);
    alert("Network Error");
  }
}
