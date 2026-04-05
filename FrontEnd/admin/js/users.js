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
      }
    );

    const rawText = await res.text();
    let data = {};
    try {
      data = rawText ? JSON.parse(rawText) : {};
    } catch (e) {
      data = { message: rawText };
    }

    if (res.ok) {
      const createdUsers = data.created_users || data.credentials || [];
      const skippedUsers = data.skipped_users || [];
      const createdCount =
        data.created_count !== undefined
          ? data.created_count
          : createdUsers.length;
      alert(`Success! Created ${createdCount} users.`);
      displayCredentials(createdUsers, skippedUsers);
    } else {
      let errMsg = data.detail || data.message || rawText || "Failed to create users";
      if (typeof errMsg === "object" && errMsg !== null) {
        const dupes = errMsg.duplicates || [];
        if (dupes.length > 0) {
          const preview = dupes.slice(0, 10).join(", ");
          const more = dupes.length > 10 ? ` (+${dupes.length - 10} more)` : "";
          errMsg = `${errMsg.message || "Duplicate emails found"}: ${preview}${more}`;
        } else {
          errMsg = errMsg.message || "Request failed";
        }
      }
      alert("Error: " + errMsg);
    }
  } catch (error) {
    console.error(error);
    alert("Network Error: Could not connect to server.");
  } finally {
    btn.innerHTML = originalText;
    btn.disabled = false;
  }
}

function displayCredentials(credentials, skipped = []) {
  generatedCredentials = credentials;

  const container = document.getElementById("results-container");
  const tbody = document.getElementById("credentials-list");
  const processingInfo = document.getElementById("processing-info");
  const processingText = document.getElementById("processing-text");
  
  tbody.innerHTML = "";

  if (credentials.length === 0) {
    processingInfo.style.display = "block";
    if (skipped.length > 0) {
      const sample = skipped.slice(0, 5).map((s) => `${s.email}: ${s.reason}`).join(" | ");
      const more = skipped.length > 5 ? ` (+${skipped.length - 5} more)` : "";
      processingText.textContent = `No new accounts created. Skipped: ${sample}${more}`;
    } else {
      processingText.textContent = "No new @vvit.net email accounts were created. Check if emails already exist or are not @vvit.net format.";
    }
    tbody.innerHTML = '<tr><td colspan="3" style="text-align: center; padding: 20px;">No credentials to display</td></tr>';
  } else {
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
  }

  container.style.display = "block";
  container.scrollIntoView({ behavior: "smooth" });
}

function downloadCredentials() {
  if (generatedCredentials.length === 0) {
    alert("No credentials to download.");
    return;
  }

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
