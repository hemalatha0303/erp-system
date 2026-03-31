const API_BASE = typeof API_URL !== "undefined" ? API_URL : "http://127.0.0.1:8000";
document.addEventListener("DOMContentLoaded", async () => {
  function getAuthHeaders() {
    return {
      Accept: "application/json",
      Authorization: `Bearer ${localStorage.getItem("token")}`,
    };
  }
  try {
    const profileRes = await fetch(`${API_BASE}/student/profile`, {
      headers: getAuthHeaders(),
    });
    const academicsRes = await fetch(
      `${API_BASE}/student/my-academics`,
      {
        headers: getAuthHeaders(),
      },
    );

    if (!profileRes.ok || !academicsRes.ok) {
      throw new Error("Failed to fetch data");
    }

    const profile = await profileRes.json();
    const academicsArr = await academicsRes.json();
    const academics = academicsArr[0];
    console.log(academics, profile);
    document.getElementById("p-name").innerText =
      `${profile.first_name ?? ""} ${profile.last_name ?? ""}`;

    document.getElementById("p-roll").innerText = profile.roll_no ?? "-";

    document.getElementById("p-dept").innerText = academics.branch ?? "-";
    document.getElementById("p-year").innerText =
      `  ${academics.year ?? "-"} / ${academics.semester ?? "-"} `;

    document.getElementById("p-section").innerText = academics.section ?? "-";
    document.getElementById("p-batch").innerText = profile.batch ?? "-";
    document.getElementById("p-course").innerText = profile.course ?? "-";
    // document.getElementById("p-teacher").innerText = "-";

    document.getElementById("p-dob").innerText = profile.date_of_birth ?? "-";
    document.getElementById("p-gender").innerText = profile.gender ?? "-";
    document.getElementById("p-blood").innerText = profile.blood_group ?? "-";
    document.getElementById("p-parent").innerText = profile.parentname ?? "-";
    document.getElementById("p-residence").innerText = profile.residence_type ?? "-";

    document.getElementById("p-email").innerText = academics.user_email ?? "-";
    document.getElementById("p-persemail").innerText = profile.personal_mail ?? "-";
    document.getElementById("p-mobile").innerText = profile.mobile_no ?? "-";
    document.getElementById("p-pmobile").innerText = profile.parent_mobile_no ?? "-";
    document.getElementById("p-address").innerText = profile.address ?? "-";
    
    document.getElementById("p-quota").innerText = profile.quota ?? "-";
    document.getElementById("p-admdate").innerText = profile.admission_date ?? "-";
  } catch (err) {
    console.error(err);
    alert("Failed to load profile data");
  }
});
