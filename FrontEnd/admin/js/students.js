const API_BASE = typeof API_URL !== "undefined" ? API_URL : "http://127.0.0.1:8000";
let currentRecords = [];
let currentUserType = "STUDENT";

document.addEventListener("DOMContentLoaded", () => {
  changeUserType();
});

function changeUserType() {
  currentUserType = document.getElementById("userTypeSelect").value;
  updateViewForUserType();
  filterRecords();
}

function updateViewForUserType() {
  const studentFilters = document.getElementById("studentFilters");
  const facultyHodFilters = document.getElementById("facultyHodFilters");
  const tableHeaders = document.getElementById("tableHeaders");
  
  if (currentUserType === "STUDENT") {
    studentFilters.style.display = "flex";
    facultyHodFilters.style.display = "none";
    tableHeaders.innerHTML = `
      <th>Roll Number</th>
      <th>Name</th>
      <th>Email</th>
      <th>Department</th>
      <th>Batch</th>
      <th>Section</th>
      <th>Contact</th>
      <th>Residence</th>
      <th>Status</th>
      <th>Actions</th>
    `;
  } else if (currentUserType === "FACULTY") {
    studentFilters.style.display = "none";
    facultyHodFilters.style.display = "block";
    tableHeaders.innerHTML = `
      <th>ID</th>
      <th>Name</th>
      <th>Email</th>
      <th>Subject</th>
      <th>Branch</th>
      <th>Experience</th>
      <th>Contact</th>
      <th>Qualification</th>
      <th>Status</th>
      <th>Actions</th>
    `;
  } else if (currentUserType === "HOD") {
    studentFilters.style.display = "none";
    facultyHodFilters.style.display = "block";
    tableHeaders.innerHTML = `
      <th>ID</th>
      <th>Name</th>
      <th>Email</th>
      <th>Branch</th>
      <th>Contact</th>
      <th>Qualification</th>
      <th>Experience</th>
      <th>Status</th>
      <th>Actions</th>
    `;
  }
}

async function filterRecords() {
  const search = document.getElementById("searchInput").value;
  const recordsBody = document.getElementById("records-list");
  recordsBody.innerHTML = '<tr><td colspan="10"><i class="fas fa-spinner fa-spin"></i> Loading...</td></tr>';

  try {
    const token = localStorage.getItem("token");
    let url;

    if (currentUserType === "STUDENT") {
      const dept = document.getElementById("deptFilter").value;
      const year = document.getElementById("yearFilter").value;
      url = `${API_BASE}/admin/students?branch=${dept}&year=${year}&_cache_bust=${Date.now()}`;
      if (search) url += `&search=${search}`;
    } else if (currentUserType === "FACULTY") {
      const branch = document.getElementById("branchFilter").value;
      url = `${API_BASE}/admin/faculty?branch=${branch}`;
      if (search) url += `&search=${search}`;
    } else if (currentUserType === "HOD") {
      const branch = document.getElementById("branchFilter").value;
      url = `${API_BASE}/admin/hods?branch=${branch}`;
      if (search) url += `&search=${search}`;
    }

    const res = await fetch(url, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!res.ok) {
      throw new Error(`Failed to fetch ${currentUserType.toLowerCase()}s`);
    }

    const records = await res.json();
    currentRecords = records;
    recordsBody.innerHTML = "";

    if (records.length === 0) {
      recordsBody.innerHTML = `<tr><td colspan="10" style="text-align: center; color: #999;">No ${currentUserType.toLowerCase()} records found.</td></tr>`;
      return;
    }

    if (currentUserType === "STUDENT") {
      displayStudentRecords(records, recordsBody);
    } else if (currentUserType === "FACULTY") {
      displayFacultyRecords(records, recordsBody);
    } else if (currentUserType === "HOD") {
      displayHodRecords(records, recordsBody);
    }
  } catch (e) {
    console.error(e);
    recordsBody.innerHTML =
      `<tr><td colspan="10" style="color:red; text-align: center;">Error loading ${currentUserType.toLowerCase()} data.</td></tr>`;
  }
}

function displayStudentRecords(students, tbody) {
  students.forEach((std) => {
    const residenceType = std.residence_type || "N/A";
    const statusClass = std.status === "ACTIVE" ? "status-active" : "status-inactive";
    const row = `
      <tr>
        <td><strong>${std.roll_no}</strong></td>
        <td>${std.name}</td>
        <td>${std.email}</td>
        <td>${std.branch}</td>
        <td>${std.batch}</td>
        <td>${std.section}</td>
        <td>${std.mobile || "N/A"}</td>
        <td>${residenceType}</td>
        <td><span class="${statusClass}">${std.status}</span></td>
        <td>
          <button class="action-btn" onclick="viewStudentDetails('${std.id}')" title="View Details">
            <i class="fas fa-eye"></i> View
          </button>
        </td>
      </tr>
    `;
    tbody.innerHTML += row;
  });
}

function displayFacultyRecords(faculty, tbody) {
  faculty.forEach((f) => {
    const row = `
      <tr>
        <td>${f.id}</td>
        <td>${f.name}</td>
        <td>${f.email}</td>
        <td>${f.subject_code || "N/A"} - ${f.subject_name || "N/A"}</td>
        <td>${f.branch || "N/A"}</td>
        <td>${f.experience || "N/A"} years</td>
        <td>${f.mobile || "N/A"}</td>
        <td>${f.qualification || "N/A"}</td>
        <td><span class="status-active">Active</span></td>
        <td>
          <button class="action-btn" onclick="viewFacultyDetails('${f.id}')" title="View Details">
            <i class="fas fa-eye"></i> View
          </button>
        </td>
      </tr>
    `;
    tbody.innerHTML += row;
  });
}

function displayHodRecords(hods, tbody) {
  hods.forEach((h) => {
    const row = `
      <tr>
        <td>${h.id}</td>
        <td>${h.name}</td>
        <td>${h.email}</td>
        <td>${h.branch || "N/A"}</td>
        <td>${h.mobile || "N/A"}</td>
        <td>${h.qualification || "N/A"}</td>
        <td>${h.experience || "N/A"} years</td>
        <td><span class="status-active">Active</span></td>
        <td>
          <button class="action-btn" onclick="viewHodDetails('${h.id}')" title="View Details">
            <i class="fas fa-eye"></i> View
          </button>
        </td>
      </tr>
    `;
    tbody.innerHTML += row;
  });
}

function viewStudentDetails(studentId) {
  const student = currentRecords.find(s => s.id == studentId);
  if (!student) {
    alert("Student not found");
    return;
  }

  document.getElementById("detail-roll").textContent = student.roll_no || "N/A";
  document.getElementById("detail-firstname").textContent = student.first_name || "N/A";
  document.getElementById("detail-lastname").textContent = student.last_name || "N/A";
  document.getElementById("detail-gender").textContent = student.gender || "N/A";
  document.getElementById("detail-dob").textContent = student.date_of_birth || "N/A";
  document.getElementById("detail-blood").textContent = student.blood_group || "N/A";
  
  document.getElementById("detail-email").textContent = student.email || "N/A";
  document.getElementById("detail-mobile").textContent = student.mobile || "N/A";
  document.getElementById("detail-parent-mobile").textContent = student.parent_mobile || "N/A";
  document.getElementById("detail-parent-name").textContent = student.parentname || "N/A";
  document.getElementById("detail-address").textContent = student.address || "N/A";
  
  document.getElementById("detail-branch").textContent = student.branch || "N/A";
  document.getElementById("detail-batch").textContent = student.batch || "N/A";
  document.getElementById("detail-course").textContent = student.course || "N/A";
  document.getElementById("detail-year").textContent = student.year || "N/A";
  document.getElementById("detail-semester").textContent = student.semester || "N/A";
  document.getElementById("detail-section").textContent = student.section || "N/A";
  document.getElementById("detail-quota").textContent = student.quota || "N/A";
  document.getElementById("detail-admission-date").textContent = student.admission_date || "N/A";
  
  document.getElementById("detail-residence").textContent = student.residence_type || "N/A";
  document.getElementById("detail-status").textContent = student.status || "N/A";
  
  document.getElementById("modalTitle").textContent = `Student Details - ${student.name}`;
  const modal = document.getElementById("detailsModal");
  modal.classList.add("show");
}

function viewFacultyDetails(facultyId) {
  const faculty = currentRecords.find(f => f.id == facultyId);
  if (!faculty) {
    alert("Faculty not found");
    return;
  }

  // Populate modal with faculty details
  document.getElementById("detail-firstname").textContent = faculty.first_name || "N/A";
  document.getElementById("detail-lastname").textContent = faculty.last_name || "N/A";
  document.getElementById("detail-email").textContent = faculty.email || "N/A";
  document.getElementById("detail-mobile").textContent = faculty.mobile || "N/A";
  document.getElementById("detail-address").textContent = faculty.address || "N/A";
  document.getElementById("detail-year").textContent = `${faculty.experience || "N/A"} years`;
  
  document.getElementById("detail-roll").textContent = faculty.id;
  document.getElementById("detail-branch").textContent = faculty.branch || "N/A";
  
  document.getElementById("modalTitle").textContent = `Faculty Details - ${faculty.name}`;
  const modal = document.getElementById("detailsModal");
  modal.classList.add("show");
}

function viewHodDetails(hodId) {
  const hod = currentRecords.find(h => h.id == hodId);
  if (!hod) {
    alert("HOD not found");
    return;
  }

  // Populate modal with HOD details
  document.getElementById("detail-firstname").textContent = hod.first_name || "N/A";
  document.getElementById("detail-lastname").textContent = hod.last_name || "N/A";
  document.getElementById("detail-email").textContent = hod.email || "N/A";
  document.getElementById("detail-mobile").textContent = hod.mobile || "N/A";
  document.getElementById("detail-address").textContent = hod.address || "N/A";
  document.getElementById("detail-year").textContent = `${hod.experience || "N/A"} years`;
  document.getElementById("detail-branch").textContent = hod.branch || "N/A";
  
  document.getElementById("detail-roll").textContent = hod.id;
  
  document.getElementById("modalTitle").textContent = `HOD Details - ${hod.name}`;
  const modal = document.getElementById("detailsModal");
  modal.classList.add("show");
}

function closeDetailsModal() {
  const modal = document.getElementById("detailsModal");
  modal.classList.remove("show");
}

// Close modal when clicking outside
document.addEventListener("click", (event) => {
  const modal = document.getElementById("detailsModal");
  if (event.target === modal) {
    closeDetailsModal();
  }
});
