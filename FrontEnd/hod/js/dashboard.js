document.addEventListener("DOMContentLoaded", () => {
  // Set Date
  const options = {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  };
  const dateEl = document.getElementById("current-date");
  if (dateEl)
    dateEl.innerText = new Date().toLocaleDateString("en-US", options);

  loadProfile();
});

async function loadProfile() {
  try {
    const token = localStorage.getItem("token");
    if (!token) {
      window.location.href = "../../index.html";
      return;
    }

    // Corrected Route: /hod/profile
    const response = await fetch("http://127.0.0.1:8000/hod/profile", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    if (response.ok) {
      const data = await response.json();

      // 1. Welcome Message (First name only)
      const fullName = data.name || "Professor";
      document.getElementById("fac-name").textContent = fullName.split(" ")[0];

      // 2. Profile Card Details
      document.getElementById("p-name").textContent = fullName;
      document.getElementById("p-qual").textContent =
        data.qualification || "N/A";
      document.getElementById("p-dept").textContent = data.department || "N/A";
      document.getElementById("p-exp").textContent =
        `${data.experience || 0} Years`;
    } else {
      console.error("Failed to load profile");
    }
  } catch (error) {
    console.error("Error:", error);
  }
}
