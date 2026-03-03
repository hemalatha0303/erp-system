async function fetchStudentListForAttendance() {
  const dateVal = document.getElementById("att-date").value;
  const year = document.getElementById("att-year").value;
  const sem = document.getElementById("att-sem").value;

  const sec = document.getElementById("att-sec").value.trim().toUpperCase();
  const branch = document
    .getElementById("att-branch")
    .value.trim()
    .toUpperCase();

  if (!year || !sem || !sec || !branch) {
    alert("Please fill in Year, Semester, Branch, and Section.");
    return;
  }

  const tableBody = document.getElementById("att-list");
  const container = document.getElementById("att-table-container");

  container.style.display = "block";
  tableBody.innerHTML =
    '<tr><td colspan="3" style="text-align:center; padding:20px;">Loading students...</td></tr>';

  try {
    const token = localStorage.getItem("token");

    const queryParams = new URLSearchParams({
      year: year,
      semester: sem,
      section: sec,
      branch: branch,
    });

    const res = await fetch(
      `http://127.0.0.1:8000/faculty/class-students?${queryParams}`,
      {
        headers: { Authorization: `Bearer ${token}` },
      },
    );

    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.detail || "Failed to fetch");
    }

    const students = await res.json();
    tableBody.innerHTML = "";

    if (students.length === 0) {
      tableBody.innerHTML =
        '<tr><td colspan="3" style="text-align:center; padding:20px;">No students found for this selection.</td></tr>';
      updateSummary(0, 0, 0);
      return;
    }

    students.forEach((stu) => {
      const row = `
                <tr>
                    <td class="roll-cell" style="font-family:monospace; font-weight:600;">${stu.roll_no}</td>
                    <td>${stu.name}</td>
                    <td class="text-center">
                        <div class="att-radio-group">
                            <label>
                                <input type="radio" name="att_${stu.roll_no}" value="PRESENT" checked onchange="calculateSummary()"> 
                                <span class="att-label"><i class="fas fa-check"></i> Present</span>
                            </label>
                            <label>
                                <input type="radio" name="att_${stu.roll_no}" value="ABSENT" onchange="calculateSummary()"> 
                                <span class="att-label"><i class="fas fa-times"></i> Absent</span>
                            </label>
                        </div>
                    </td>
                </tr>
            `;
      tableBody.innerHTML += row;
    });

    calculateSummary();
  } catch (error) {
    console.error(error);
    tableBody.innerHTML = `<tr><td colspan="3" style="color:red; text-align:center; padding:20px;">Error: ${error.message}</td></tr>`;
  }
}

function calculateSummary() {
  const total = document.querySelectorAll("#att-list tr").length;
  const present = document.querySelectorAll(
    '#att-list input[value="PRESENT"]:checked',
  ).length;
  const absent = total - present;
  updateSummary(total, present, absent);
}

function updateSummary(total, present, absent) {
  document.getElementById("att-summary").innerHTML =
    `Total: <strong>${total}</strong> | <span style="color:#28a745">Present: <strong>${present}</strong></span> | <span style="color:#dc3545">Absent: <strong>${absent}</strong></span>`;
}

async function submitAttendance() {
  const token = localStorage.getItem("token");

  const dateVal = document.getElementById("att-date").value;
  if (!dateVal) {
    alert("Please select a date first.");
    return;
  }

  const payload = {
    subject_code: document.getElementById("att-sub").value,
    subject_name:
      document.getElementById("att-sub").options[
        document.getElementById("att-sub").selectedIndex
      ].text,
    year: parseInt(document.getElementById("att-year").value),
    semester: parseInt(document.getElementById("att-sem").value),
    date: dateVal,
    period: parseInt(document.getElementById("att-period").value),
    attendance: [],
  };

  const rows = document.querySelectorAll("#att-list tr");
  if (rows.length === 0) {
    alert("No students to submit.");
    return;
  }

  rows.forEach((row) => {
    const roll = row.querySelector(".roll-cell").innerText;

    const status = row.querySelector(`input[name="att_${roll}"]:checked`).value;
    payload.attendance.push({ roll_no: roll, status: status });
  });

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/faculty/attendance/mark",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      },
    );

    const result = await response.json();

    if (response.ok) {
      alert(result.message);
    } else {
      alert("Error: " + (result.detail || "Failed to mark attendance"));
    }
  } catch (error) {
    console.error("Network Error:", error);
    alert("Network Error. Check console.");
  }
}
