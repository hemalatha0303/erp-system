document.addEventListener("DOMContentLoaded", () => {
  loadProfile();
});

async function loadProfile() {
  const token = localStorage.getItem("token");
  if (!token) {
    window.location.href = "../../index.html";
    return;
  }

  try {
    const res = await fetch("http://127.0.0.1:8000/faculty/get-profile", {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (res.ok) {
      const data = await res.json();

      document.getElementById("pf-fname").textContent = data.first_name || "-";
      document.getElementById("pf-lname").textContent = data.last_name || "-";
      document.getElementById("pf-email").textContent = data.user_email || data.email || "-";
      document.getElementById("pf-persemail").textContent = data.personal_email || "-";
      document.getElementById("pf-mobile").textContent = data.mobile_no || "-";
      document.getElementById("pf-dept").textContent = data.branch || "-";
      document.getElementById("pf-subcode").textContent = data.subject_code || "-";
      document.getElementById("pf-subname").textContent = data.subject_name || "-";
      document.getElementById("pf-qual").textContent = data.qualification || "-";
      document.getElementById("pf-exp").textContent = data.experience || "0";
      document.getElementById("pf-addr").textContent = data.address || "-";
    } else {
      console.error("Failed to load profile");
    }
  } catch (error) {
    console.error("Network Error:", error);
  }
}
