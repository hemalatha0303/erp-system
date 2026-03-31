const API_BASE = typeof API_URL !== "undefined" ? API_URL : "http://127.0.0.1:8000";
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
  return m.mid1 ?? 0;
}

function mid2Total(m) {
  return m.mid2 ?? 0;
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
  const url = `${API_BASE}/student/internal-marks/${year}/${semester}`;
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
            <th>Open Book</th>
            <th>Objective</th>
            <th>Descriptive</th>
            <th>Seminar</th>
            <th>Mid Total (30)</th>
            <th>Status</th>
        </tr>
    `;

  if (marksArray.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8" style="text-align:center">No internal marks found</td></tr>`;
    return;
  }

  marksArray.forEach((s) => {
    const openbook = (type === "mid1" ? s.openbook1 : s.openbook2) ?? 0;
    const objective = (type === "mid1" ? s.objective1 : s.objective2) ?? 0;
    const descriptive = (type === "mid1" ? s.descriptive1 : s.descriptive2) ?? 0;
    const seminar = (type === "mid1" ? s.seminar1 : s.seminar2) ?? 0;

    const total = type === "mid1" ? mid1Total(s) : mid2Total(s);
    const pass = total >= 12;

    tbody.innerHTML += `
            <tr>
                <td>${s.subject_code}</td>
                <td>${s.subject_name}</td>
                <td>${openbook}</td>
                <td>${objective}</td>
                <td>${descriptive}</td>
                <td>${seminar}</td>
                <td>${total}</td>
                <td class="${pass ? "status-pass" : "status-fail"}">${pass ? "Pass" : "Fail"}</td>
            </tr>
        `;
  });

  document.getElementById("sgpa-val").innerText = "--";
  document.getElementById("cgpa-val").innerText = "--";
  document.getElementById("status-val").innerText = "--";
}

async function loadSemesterMarks(semester) {
  semester = Number(semester);
  const year = Math.floor((semester + 1) / 2);

  const res = await fetch(
    `${API_BASE}/student/external-marks/${year}/${semester}`,
    { headers: getAuthHeaders() },
  );

  const data = await res.json();

  const marksArray = data.external_marks || [];
  const semesterResults = data.semester_results || [];
  const sgpaVal = semesterResults.length ? semesterResults[0].sgpa : null;
  const resultStatus = semesterResults.length ? semesterResults[0].result_status : "--";
  const cgpaVal = data.cgpa ?? null;

  const thead = document.querySelector("#marksTable thead");
  const tbody = document.querySelector("#marksTable tbody");

  thead.innerHTML = `
        <tr>
            <th>Subject Code</th>
            <th>Subject Name</th>
            <th>Credits</th>
            <th>Grade</th>
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
            </tr>
        `;
  });

  document.getElementById("sgpa-val").innerText =
    sgpaVal !== null && sgpaVal !== undefined ? Number(sgpaVal).toFixed(2) : "--";
  document.getElementById("cgpa-val").innerText =
    cgpaVal !== null && cgpaVal !== undefined ? Number(cgpaVal).toFixed(2) : "--";
  document.getElementById("status-val").innerText = resultStatus ?? "--";
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

