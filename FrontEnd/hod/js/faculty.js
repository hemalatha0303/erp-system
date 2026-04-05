let currentFacultyEmail = null;

function renderFacultyList(data) {
  const tableContainer = document.getElementById("all-faculty-view");
  const detailContainer = document.getElementById("single-faculty-view");
  const listBody = document.getElementById("faculty-list");

  detailContainer.style.display = "none";
  tableContainer.style.display = "block";
  listBody.innerHTML = "";

  if (!data || data.length === 0) {
    listBody.innerHTML =
      "<tr><td colspan='5' style='text-align:center; padding:20px;'>No faculty found.</td></tr>";
    return;
  }

  data.forEach((fac) => {
    const row = `
      <tr>
        <td><strong>${fac.id}</strong></td>
        <td>${fac.name}</td>
        <td>${fac.email}</td>
        <td>${fac.sub || "-"}</td>
        <td>
          <button class="alert-btn" onclick="prefillSearch('${fac.email}')" title="View Full Details">
            <i class="fas fa-eye"></i> Details
          </button>
        </td>
      </tr>
    `;
    listBody.innerHTML += row;
  });
}

async function fetchAllFaculty() {
  const tableContainer = document.getElementById("all-faculty-view");
  const detailContainer = document.getElementById("single-faculty-view");
  const token = localStorage.getItem("token");

  detailContainer.style.display = "none";
  tableContainer.style.display = "block";
  document.getElementById("faculty-list").innerHTML =
    "<tr><td colspan='5' style='text-align:center; padding:20px;'>Loading...</td></tr>";

  try {
    const res = await fetch("http://127.0.0.1:8000/hod/faculty", {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!res.ok) throw new Error("Failed to fetch list");

    const data = await res.json();
    renderFacultyList(data);
  } catch (error) {
    console.error(error);
    document.getElementById("faculty-list").innerHTML =
      "<tr><td colspan='5' style='color:red; text-align:center;'>Error loading data</td></tr>";
  }
}

async function searchFacultyByEmail() {
  const emailInput = document.getElementById("fac-email-search");
  const rawQuery = emailInput.value.trim();
  const query = rawQuery.toLowerCase();

  if (!query) {
    alert("Please enter an email address.");
    return;
  }

  const tableContainer = document.getElementById("all-faculty-view");
  const detailContainer = document.getElementById("single-faculty-view");
  const token = localStorage.getItem("token");

  tableContainer.style.display = "none";

  try {
    if (!query.includes("@")) {
      const res = await fetch("http://127.0.0.1:8000/hod/faculty", {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) throw new Error("Failed to fetch list");
      const data = await res.json();
      const matches = data.filter((f) =>
        (f.name || "").toLowerCase().includes(query) ||
        (f.email || "").toLowerCase().includes(query)
      );

      if (matches.length === 0) {
        alert("No faculty found for this search.");
        return;
      }
      if (matches.length === 1) {
        return prefillSearch(matches[0].email);
      }
      return renderFacultyList(matches);
    }

    const encodedEmail = encodeURIComponent(query);
    const res = await fetch(
      `http://127.0.0.1:8000/hod/view/faculty/${encodedEmail}`,
      {
        headers: { Authorization: `Bearer ${token}` },
      },
    );

    if (res.ok) {
      const data = await res.json();

      document.getElementById("d-name").innerText =
        `${data.first_name} ${data.last_name}`;
      document.getElementById("d-desig").innerText =
        data.qualification || "Faculty";
      document.getElementById("d-id").innerText = data.id;
      document.getElementById("d-email").innerText = data.user_email;
      currentFacultyEmail = data.user_email;
      document.getElementById("d-mobile").innerText = data.mobile_no || "N/A";
      document.getElementById("d-exp").innerText =
        `${data.experience || 0} Years`;
      document.getElementById("d-address").innerText =
        data.address || "No address provided.";

      detailContainer.style.display = "block";
    } else {
      alert("Faculty not found with this email.");
    }
  } catch (error) {
    console.error(error);
    alert("Network Error occurred while searching.");
  }
}

function prefillSearch(email) {
  document.getElementById("fac-email-search").value = email;
  searchFacultyByEmail();
}

function closeDetailView() {
  document.getElementById("single-faculty-view").style.display = "none";
  document.getElementById("fac-email-search").value = "";
  currentFacultyEmail = null;
}

function openFacultyAlertModal() {
  if (!currentFacultyEmail) {
    alert("No faculty selected.");
    return;
  }
  document.getElementById("alert-faculty-email").value = currentFacultyEmail;
  document.getElementById("facultyAlertModal").style.display = "flex";
}

function closeFacultyAlertModal() {
  document.getElementById("facultyAlertModal").style.display = "none";
}

async function sendFacultyAlert() {
  const token = localStorage.getItem("token");
  const email = document.getElementById("alert-faculty-email").value.trim();
  const title = document.getElementById("alert-faculty-title").value.trim();
  const message = document.getElementById("alert-faculty-message").value.trim();
  const priority = document.getElementById("alert-faculty-priority").value;

  if (!email || !title || !message) {
    alert("Please fill in Title and Message.");
    return;
  }

  const payload = {
    title,
    message,
    category: "ALERT",
    priority,
    target_role: "FACULTY",
    target_email: email,
    batch: null,
    branch: null,
    section: null
  };

  try {
    const res = await fetch("http://127.0.0.1:8000/hod/notifications", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });

    const raw = await res.text();
    let data = {};
    try {
      data = raw ? JSON.parse(raw) : {};
    } catch (e) {
      data = { detail: raw };
    }
    if (res.ok) {
      alert("Alert sent successfully!");
      closeFacultyAlertModal();
      document.getElementById("alert-faculty-title").value = "";
      document.getElementById("alert-faculty-message").value = "";
    } else {
      alert("Failed: " + (data.detail || data.message || "Unknown error"));
    }
  } catch (error) {
    console.error(error);
    alert("Network Error while sending the alert.");
  }
}

window.onclick = function(event) {
  const modal = document.getElementById('facultyAlertModal');
  if (event.target == modal) {
      closeFacultyAlertModal();
  }
}
