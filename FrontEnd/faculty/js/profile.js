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

      document.getElementById("pf-fname").value = data.first_name || "";
      document.getElementById("pf-lname").value = data.last_name || "";
      document.getElementById("pf-mobile").value = data.mobile_no || "";
      document.getElementById("pf-dob").value = data.date_of_birth || "";
      document.getElementById("pf-gender").value = data.gender || "Male";
      document.getElementById("pf-blood").value = data.blood_group || "O+";
      document.getElementById("pf-qual").value = data.qualification || "";
      document.getElementById("pf-exp").value = data.experience || 0;
      document.getElementById("pf-addr").value = data.address || "";
    } else {
      console.error("Failed to load profile");
    }
  } catch (error) {
    console.error("Network Error:", error);
  }
}

async function updateProfile() {
  const token = localStorage.getItem("token");

  const payload = {
    first_name: document.getElementById("pf-fname").value,
    last_name: document.getElementById("pf-lname").value,
    gender: document.getElementById("pf-gender").value,
    blood_group: document.getElementById("pf-blood").value,
    date_of_birth: document.getElementById("pf-dob").value,
    mobile_no: document.getElementById("pf-mobile").value,
    address: document.getElementById("pf-addr").value,
    qualification: document.getElementById("pf-qual").value,
    experience: parseInt(document.getElementById("pf-exp").value) || 0,
  };

  try {
    const res = await fetch("http://127.0.0.1:8000/faculty/profile", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });

    if (res.ok) {
      alert("Profile updated successfully!");

      location.reload();
    } else {
      const err = await res.json();
      alert(" Update failed: " + (err.detail || "Unknown error"));
    }
  } catch (error) {
    console.error("Error updating profile:", error);
    alert("Network Error");
  }
}

function enableEdit() {
  document.querySelectorAll("#profile-form input").forEach(input => {
    input.removeAttribute("readonly");
  });
}
