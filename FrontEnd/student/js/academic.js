document.addEventListener("DOMContentLoaded", () => {
  updateTable();
});

function getAuthHeaders() {
  return {
    Accept: "application/json",
    Authorization: `Bearer ${localStorage.getItem("token")}`,
  };
}

function mid1Total(m) {
  return m.openbook1 + m.descriptive1 + m.seminar1 + m.objective1;
}

function mid2Total(m) {
  return m.openbook2 + m.descriptive2 + m.seminar2 + m.objective2;
}

async function updateTable() {
  const semester = document.getElementById("semesterSelect").value;
  const type = document.getElementById("examTypeSelect").value;

  const thead = document.querySelector("#marksTable thead");
  const tbody = document.querySelector("#marksTable tbody");

  thead.innerHTML = "";
  tbody.innerHTML = "";

  try {
    if (type === "mid1" || type === "mid2") {
      await loadInternalMarks(semester, type);
    } else {
      await loadSemesterMarks(semester);
    }
  } catch (err) {
    console.error(err);
    tbody.innerHTML = `<tr><td colspan="6">Could not Load marks</td></tr>`;
  }
}

async function loadInternalMarks(semester, type) {
  semester = Number(semester);
  const year = Math.floor((semester + 1) / 2);
  const sem = semester % 2 === 0 ? 2 : 1;

  const url = `http://127.0.0.1:8000/student/internal-marks/${year}/${sem}`;
  console.log("Fetching URL:", url);

  const res = await fetch(url, { headers: getAuthHeaders() });

  if (!res.ok) {
    console.error("Failed to fetch internal marks", res.status, res.statusText);
    return;
  }

  const data = await res.json();
  console.log("Data received:", data);

  const marksArray = data.internal_marks || [];

  const thead = document.querySelector("#marksTable thead");
  const tbody = document.querySelector("#marksTable tbody");

  thead.innerHTML = `
        <tr>
            <th>Subject Code</th>
            <th>Subject Name</th>
            <th>Open Book (${type === "mid1" ? "M1" : "M2"})</th>
            <th>Descriptive (${type === "mid1" ? "M1" : "M2"})</th>
            <th>Seminar (${type === "mid1" ? "M1" : "M2"})</th>
            <th>Objective (${type === "mid1" ? "M1" : "M2"})</th>
            <th>Total (30)</th>
            <th>Status</th>
        </tr>
    `;

  if (marksArray.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8" style="text-align:center">No internal marks found</td></tr>`;
    return;
  }

  marksArray.forEach((s) => {
    const openbook = type === "mid1" ? s.openbook1 : s.openbook2;
    const descriptive = type === "mid1" ? s.descriptive1 : s.descriptive2;
    const seminar = type === "mid1" ? s.seminar1 : s.seminar2;
    const objective = type === "mid1" ? s.objective1 : s.objective2;

    const total = openbook + descriptive + seminar + objective;
    const pass = total >= 12;

    tbody.innerHTML += `
            <tr>
                <td>${s.subject_code}</td>
                <td>${s.subject_name}</td>
                <td>${openbook}</td>
                <td>${descriptive}</td>
                <td>${seminar}</td>
                <td>${objective}</td>
                <td>${total}</td>
                <td class="${pass ? "status-pass" : "status-fail"}">${pass ? "Pass" : "Fail"}</td>
            </tr>
        `;
  });
}

async function loadSemesterMarks(semester) {
  semester = Number(semester);
  const year = Math.floor((semester + 1) / 2);
  const sem = semester % 2 === 0 ? 2 : 1;

  const res = await fetch(
    `http://127.0.0.1:8000/student/external-marks/${year}/${sem}`,
    { headers: getAuthHeaders() },
  );

  const data = await res.json();

  const marksArray = data.semester_results || [];

  const thead = document.querySelector("#marksTable thead");
  const tbody = document.querySelector("#marksTable tbody");

  thead.innerHTML = `
        <tr>
            <th>Subject Code</th>
            <th>Subject Name</th>
            <th>Credits</th>
            <th>Grade</th>
            <th>GPA</th>
        </tr>
    `;

  if (marksArray.length === 0) {
    tbody.innerHTML = `
            <tr>
                <td colspan="5" style="text-align:center">No semester records</td>
            </tr>
        `;
    return;
  }

  marksArray.forEach((s) => {
    tbody.innerHTML += `
            <tr>
                <td>${s.subject_code}</td>
                <td>${s.subject_name}</td>
                <td>${s.credits}</td>
                <td class="status-pass">${s.grade}</td>
                <td><strong>${s.gpa}</strong></td>
            </tr>
        `;
  });
}

async function downloadPdf() {
  const { jsPDF } = window.jspdf;

  const semester = Number(document.getElementById("semesterSelect").value);
  const type = document.getElementById("examTypeSelect").value;

  const doc = new jsPDF();

  doc.setFontSize(16);
  doc.text(
    `Academic Records - Semester ${semester} - ${type.toUpperCase()}`,
    14,
    20,
  );

  const thead = document.querySelector("#marksTable thead");
  const tbody = document.querySelector("#marksTable tbody");

  const headers = Array.from(thead.querySelectorAll("th")).map((th) =>
    th.innerText.trim(),
  );
  const rows = Array.from(tbody.querySelectorAll("tr")).map((tr) =>
    Array.from(tr.querySelectorAll("td")).map((td) => td.innerText.trim()),
  );

  if (rows.length === 0) {
    alert("No data to download!");
    return;
  }

  doc.autoTable({
    head: [headers],
    body: rows,
    startY: 30,
    styles: { fontSize: 9 },
    headStyles: { fillColor: [13, 71, 161] },
  });

  doc.save(`Academic_Records_Sem${semester}_${type}.pdf`);
}
