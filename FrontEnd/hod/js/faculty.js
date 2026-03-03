async function fetchAllFaculty() {
  const tableContainer = document.getElementById("all-faculty-view");
  const detailContainer = document.getElementById("single-faculty-view");
  const listBody = document.getElementById("faculty-list");
  const token = localStorage.getItem("token");

  detailContainer.style.display = "none";
  tableContainer.style.display = "block";
  listBody.innerHTML =
    "<tr><td colspan='5' style='text-align:center; padding:20px;'>Loading...</td></tr>";

  try {
    const res = await fetch("http://127.0.0.1:8000/hod/faculty", {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!res.ok) throw new Error("Failed to fetch list");

    const data = await res.json();
    listBody.innerHTML = "";

    if (data.length === 0) {
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
  } catch (error) {
    console.error(error);
    listBody.innerHTML =
      "<tr><td colspan='5' style='color:red; text-align:center;'>Error loading data</td></tr>";
  }
}

async function searchFacultyByEmail() {
  const emailInput = document.getElementById("fac-email-search");
  const email = emailInput.value.trim();

  if (!email) {
    alert("Please enter an email address.");
    return;
  }

  const tableContainer = document.getElementById("all-faculty-view");
  const detailContainer = document.getElementById("single-faculty-view");
  const token = localStorage.getItem("token");

  tableContainer.style.display = "none";

  try {
    const encodedEmail = encodeURIComponent(email);
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
      document.getElementById("d-mobile").innerText = data.mobile_no || "N/A";
      document.getElementById("d-gender").innerText = data.gender || "N/A";
      document.getElementById("d-blood").innerText = data.blood_group || "N/A";
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
}
