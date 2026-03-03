document.addEventListener("DOMContentLoaded", () => {
  filterStudents();
});

let currentEditRoll = null;

async function filterStudents() {
  const search = document.getElementById("searchInput").value;
  const dept = document.getElementById("deptFilter").value;
  const year = document.getElementById("yearFilter").value;

  const tableBody = document.getElementById("student-list");
  tableBody.innerHTML = '<tr><td colspan="7">Loading...</td></tr>';

  try {
    const token = localStorage.getItem("token");
    let url = `http://127.0.0.1:8000/admin/students?branch=${dept}&year=${year}`;
    if (search) url += `&search=${search}`;

    const res = await fetch(url, {
      headers: { Authorization: `Bearer ${token}` },
    });

    const students = await res.json();
    tableBody.innerHTML = "";

    if (students.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="7">No records found.</td></tr>';
      return;
    }
    // <td>
    //     <button class="action-btn" onclick="alert('Feature: Edit coming soon')"><i class="fas fa-edit"></i></button>
    // </td>
    students.forEach((std) => {
      const row = `
                <tr>
                    <td><strong>${std.roll_no}</strong></td>
                    <td>${std.name}</td>
                    <td>${std.branch}</td>
                    <td>${std.year} (${std.semester})</td>
                    <td>${std.mobile}</td>
                    <td><span class="status-active">${std.status}</span></td>

                </tr>
            `;
      tableBody.innerHTML += row;
    });
  } catch (e) {
    tableBody.innerHTML =
      '<tr><td colspan="7" style="color:red">Error loading data.</td></tr>';
  }
}

const modal = document.getElementById("editModal");

function openEditModal(roll) {
  const std = students.find((s) => s.roll === roll);
  if (std) {
    currentEditRoll = roll;
    document.getElementById("e-name").value = std.name;
    document.getElementById("e-dept").value = std.dept;
    document.getElementById("e-status").value = std.status;
    modal.style.display = "flex";
  }
}

function closeModal() {
  modal.style.display = "none";
}

function saveStudent() {
  const std = students.find((s) => s.roll === currentEditRoll);
  if (std) {
    std.name = document.getElementById("e-name").value;
    std.dept = document.getElementById("e-dept").value;
    std.status = document.getElementById("e-status").value;
    alert("Student details updated!");
    closeModal();
    filterStudents();
  }
}

function deleteStudent(roll) {
  if (confirm("Are you sure you want to delete this record?")) {
    students = students.filter((s) => s.roll !== roll);
    filterStudents();
  }
}

window.onclick = function (event) {
  if (event.target == modal) closeModal();
};
