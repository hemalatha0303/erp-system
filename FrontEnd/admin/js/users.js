document.getElementById("drop-zone").addEventListener("click", () => {
  document.getElementById("userFile").click();
});

document.getElementById("userFile").addEventListener("change", function () {
  if (this.files && this.files[0]) {
    document.getElementById("file-name").textContent = this.files[0].name;
  }
});

let generatedCredentials = [];

async function bulkUserSignup() {
  const fileInput = document.getElementById("userFile");
  const roleSelect = document.getElementById("userRole");

  if (!fileInput.files[0]) {
    alert("Please select an Excel file first.");
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  const role = roleSelect.value;

  const btn = document.querySelector(".primary-btn");
  const originalText = btn.innerHTML;
  btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
  btn.disabled = true;

  try {
    const token = localStorage.getItem("token");
    const res = await fetch(
      `http://127.0.0.1:8000/admin/accounts/signup-users?role=${role}`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      },
    );

    const data = await res.json();

    if (res.ok) {
      alert(`Success! Created ${data.count} users.`);
      displayCredentials(data.credentials);
    } else {
      alert("Error: " + (data.detail || "Failed to create users"));
    }
  } catch (error) {
    console.error(error);
    alert("Network Error: Could not connect to server.");
  } finally {
    btn.innerHTML = originalText;
    btn.disabled = false;
  }
}

function displayCredentials(credentials) {
  generatedCredentials = credentials;

  const container = document.getElementById("results-container");
  const tbody = document.getElementById("credentials-list");
  tbody.innerHTML = "";

  credentials.forEach((user, index) => {
    const row = `
            <tr>
                <td>${index + 1}</td>
                <td>${user.email}</td>
                <td>${user.password}</td>
            </tr>
        `;
    tbody.innerHTML += row;
  });

  container.style.display = "block";

  container.scrollIntoView({ behavior: "smooth" });
}

function downloadCredentials() {
  if (generatedCredentials.length === 0) return;

  let csvContent = "data:text/csv;charset=utf-8,";
  csvContent += "Email,Password\n";

  generatedCredentials.forEach((user) => {
    csvContent += `${user.email},${user.password}\n`;
  });

  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", "New_User_Credentials.csv");
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
