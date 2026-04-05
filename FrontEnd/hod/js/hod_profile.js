document.addEventListener("DOMContentLoaded", () => {
  loadHodProfile();
});

async function loadHodProfile() {
  const token = localStorage.getItem("token");

  try {
    const res = await fetch("http://127.0.0.1:8000/hod/profile", {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (res.ok) {
      const data = await res.json();

      document.getElementById("hp-first").value = data.first_name || "";
      document.getElementById("hp-last").value = data.last_name || "";
      document.getElementById("hp-personal-email").value = data.personal_email || "";
      document.getElementById("hp-mobile").value = data.mobile_no || "";
      document.getElementById("hp-qual").value = data.qualification || "";
      document.getElementById("hp-exp").value = data.experience || 0;
      document.getElementById("hp-branch").value = data.branch || "";
      document.getElementById("hp-address").value = data.address || "";
      document.getElementById("hp-email").value = data.email || "";
    } else {
      console.warn("Profile not found or error loading.");
    }
  } catch (error) {
    console.error("Network Error:", error);
  }
}

async function updateHodProfile() {
  const token = localStorage.getItem("token");

  const payload = {
    first_name: document.getElementById("hp-first").value,
    last_name: document.getElementById("hp-last").value,
    personal_email: document.getElementById("hp-personal-email").value,
    mobile_no: document.getElementById("hp-mobile").value,
    qualification: document.getElementById("hp-qual").value,
    experience: parseInt(document.getElementById("hp-exp").value) || 0,
    branch: document.getElementById("hp-branch").value,
    address: document.getElementById("hp-address").value,
  };

  try {
    const res = await fetch("http://127.0.0.1:8000/hod/profile", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });

    if (res.ok) {
      alert("Profile updated successfully!");
    } else {
      const err = await res.json();
      alert(" Update failed: " + (err.detail || "Unknown error"));
    }
  } catch (error) {
    console.error("Error updating profile:", error);
    alert("Network Error");
  }
}
