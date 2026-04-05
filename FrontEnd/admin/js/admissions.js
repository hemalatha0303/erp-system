// File template information for different user types
const fileTemplates = {
  STUDENT: "roll_no, email, first_name, last_name, personal_email, gender, residence_type, mobile_no, parent_mobile_no, branch, section, batch, course, quota, admission_date, address, parent_name",
  FACULTY: "first_name, last_name, mobile_no, personal_email, email, address, qualification, years_of_experience, subject_code, subject_name, branch",
  HOD: "first_name, last_name, mobile_no, personal_email, email, address, qualification, years_of_experience, branch"
};

// Update file template based on user type selection
function updateFileTemplate() {
  const userType = document.getElementById("userTypeSelect").value;
  const fileInfo = document.getElementById("fileInfo");
  
  // Update file info with proper formatting
  const template = fileTemplates[userType];
  const columns = template.split(", ");
  
  let htmlContent = `<strong style="color: #0d47a1;">📋 Expected Excel Format for ${userType}:</strong>`;
  htmlContent += `<table style="width: 100%; margin-top: 10px; border-collapse: collapse;">`;
  htmlContent += `<tr style="background: #e3f2fd; border-bottom: 2px solid #0d47a1;">`;
  htmlContent += `<th style="padding: 8px; text-align: left; font-weight: bold;">Column #</th>`;
  htmlContent += `<th style="padding: 8px; text-align: left; font-weight: bold;">Column Name</th>`;
  htmlContent += `<th style="padding: 8px; text-align: left; font-weight: bold;">Example Value</th>`;
  htmlContent += `</tr>`;
  
  // Define examples for each column
  const examples = {
    STUDENT: [
      {col: "roll_no", ex: "CS001"},
      {col: "email", ex: "student@vvit.net"},
      {col: "first_name", ex: "Raj"},
      {col: "last_name", ex: "Kumar"},
      {col: "personal_email", ex: "raj@gmail.com"},
      {col: "gender", ex: "M"},
      {col: "residence_type", ex: "Hostel"},
      {col: "mobile_no", ex: "9876543210"},
      {col: "parent_mobile_no", ex: "9123456789"},
      {col: "branch", ex: "CSE"},
      {col: "section", ex: "A"},
      {col: "batch", ex: "2022-26"},
      {col: "course", ex: "B.Tech"},
      {col: "quota", ex: "General"},
      {col: "admission_date", ex: "2022-07-15"},
      {col: "address", ex: "123 Main St"},
      {col: "parent_name", ex: "Mr. Kumar"}
    ],
    FACULTY: [
      {col: "first_name", ex: "Harika"},
      {col: "last_name", ex: "Dasari"},
      {col: "mobile_no", ex: "9876543210"},
      {col: "personal_email", ex: "harika@gmail.com"},
      {col: "email", ex: "harika@vvit.net"},
      {col: "address", ex: "456 Faculty Lane"},
      {col: "qualification", ex: "M.Tech"},
      {col: "years_of_experience", ex: "5"},
      {col: "subject_code", ex: "CS301"},
      {col: "subject_name", ex: "Data Structures"},
      {col: "branch", ex: "CSE"}
    ],
    HOD: [
      {col: "first_name", ex: "Dr. John"},
      {col: "last_name", ex: "Doe"},
      {col: "mobile_no", ex: "9876543210"},
      {col: "personal_email", ex: "john@gmail.com"},
      {col: "email", ex: "john@vvit.net"},
      {col: "address", ex: "789 Admin Blvd"},
      {col: "qualification", ex: "PhD"},
      {col: "years_of_experience", ex: "10"},
      {col: "branch", ex: "CSE"}
    ]
  };
  
  const roleExamples = examples[userType] || [];
  roleExamples.forEach((item, index) => {
    htmlContent += `<tr style="border-bottom: 1px solid #e0e0e0;">`;
    htmlContent += `<td style="padding: 8px; color: #666;">${index + 1}</td>`;
    htmlContent += `<td style="padding: 8px; font-weight: 500; color: #0d47a1;">${item.col}</td>`;
    htmlContent += `<td style="padding: 8px; color: #333;">${item.ex}</td>`;
    htmlContent += `</tr>`;
  });
  
  htmlContent += `</table>`;
  htmlContent += `<div style="margin-top: 10px; padding: 10px; background: #fff3cd; border-left: 4px solid #ffc107; border-radius: 4px;">`;
  htmlContent += `<strong>⚠️ Important:</strong><br>`;
  htmlContent += `• Email MUST be in @vvit.net domain<br>`;
  htmlContent += `• All columns are required<br>`;
  htmlContent += `• Column order must match exactly`;
  htmlContent += `</div>`;
  
  fileInfo.innerHTML = htmlContent;
}

// Upload users based on selected type
async function uploadUsers() {
  const fileInput = document.getElementById("userFile");
  const statusBox = document.getElementById("upload-status");
  const userType = document.getElementById("userTypeSelect").value;

  if (!fileInput.files[0]) {
    alert("Please select a file first.");
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  statusBox.innerHTML = "<span style='color:blue'><i class='fas fa-spinner fa-spin'></i> Uploading... Please wait.</span>";

  try {
    const response = await fetch(
      `http://127.0.0.1:8000/admin/upload-students?role=${userType}`,
      {
        method: "POST",
        headers: {
          Authorization: "Bearer " + localStorage.getItem("token"),
        },
        body: formData,
      }
    );

    const result = await response.json();

    if (response.ok) {
      // Check if there are created users in response
      if (result.created_count !== undefined) {
        let message = `<strong>✓ Upload Complete</strong><br>`;
        message += `Created: <span style='color:green'>${result.created_count}</span> | `;
        message += `Skipped: <span style='color:orange'>${result.skipped_count}</span>`;
        if (result.error_count > 0) {
          message += ` | Errors: <span style='color:red'>${result.error_count}</span>`;
        }
        statusBox.innerHTML = `<span style='color:green'>${message}</span>`;
      } else {
        statusBox.innerHTML = `<span style='color:green'>✓ Success: ${result.message}</span>`;
      }
      fileInput.value = ''; // Clear file input
      document.getElementById("file-name").textContent = '';
    } else {
      let errorMsg = result.detail || result.message || 'Upload failed';
      
      // Check for specific error types
      if (errorMsg.includes('Duplicate')) {
        errorMsg = `⚠ Duplicate entry detected. This email may already exist in the database. ${errorMsg}`;
      }
      
      statusBox.innerHTML = `<span style='color:red'><strong>✗ Error:</strong> ${errorMsg}</span>`;
    }
  } catch (error) {
    console.error(error);
    statusBox.innerHTML = "<span style='color:red'><strong>✗ Network Error:</strong> Could not connect to server. Please check if the backend is running on port 8000.</span>";
  }
}

// Drag and drop functionality
document.addEventListener("DOMContentLoaded", function() {
  const dropZone = document.getElementById("drop-zone");
  const fileInput = document.getElementById("userFile");
  const fileName = document.getElementById("file-name");

  // Prevent default drag behaviors
  ["dragenter", "dragover", "dragleave", "drop"].forEach(eventName => {
    dropZone.addEventListener(eventName, preventDefaults, false);
    document.body.addEventListener(eventName, preventDefaults, false);
  });

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  // Highlight drop zone when item is dragged over it
  ["dragenter", "dragover"].forEach(eventName => {
    dropZone.addEventListener(eventName, highlight, false);
  });

  ["dragleave", "drop"].forEach(eventName => {
    dropZone.addEventListener(eventName, unhighlight, false);
  });

  function highlight(e) {
    dropZone.style.borderColor = "#007bff";
    dropZone.style.backgroundColor = "#f0f8ff";
  }

  function unhighlight(e) {
    dropZone.style.borderColor = "#ddd";
    dropZone.style.backgroundColor = "transparent";
  }

  // Handle dropped files
  dropZone.addEventListener("drop", handleDrop, false);

  function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    fileInput.files = files;
    fileName.textContent = files[0].name;
  }

  // Handle file input change
  fileInput.addEventListener("change", function() {
    if (this.files && this.files[0]) {
      fileName.textContent = this.files[0].name;
    }
  });
});
