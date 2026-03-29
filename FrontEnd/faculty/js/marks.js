async function fetchStudentListForMarks() {
  const batch = document.getElementById("mk-batch").value.trim();
  const sem = document.getElementById("mk-sem").value;
  const sec = document.getElementById("mk-sec").value;
  const branch = document.getElementById("mk-branch").value;
  const subject = document.getElementById("mk-sub").value.trim();
  const token = localStorage.getItem("token");

  if (!batch || !sem || !subject) {
    alert("Please enter Batch, Semester, and Subject Code.");
    return;
  }

  const tableBody = document.getElementById("mk-list");
  const container = document.getElementById("mk-table-container");

  container.style.display = "block";
  tableBody.innerHTML = `<tr><td colspan="13" style="text-align:center;">Loading...</td></tr>`;

  try {
    const queryParams = new URLSearchParams({
      batch: batch,
      branch: branch,
      section: sec,
    });

    const res = await fetch(
      `http://127.0.0.1:8000/faculty/class-students?${queryParams}`,
      { headers: { Authorization: `Bearer ${token}` } },
    );

    if (!res.ok) throw new Error("Failed to fetch students");

    const students = await res.json();
    tableBody.innerHTML = "";

    if (students.length === 0) {
      tableBody.innerHTML = `<tr><td colspan="13">No students found</td></tr>`;
      return;
    }

    students.forEach((stu) => {
      tableBody.innerHTML += `
            <tr data-roll="${stu.roll_no}">
                <td>${stu.roll_no}</td>
                <td>${stu.name}</td>
                <td style="text-align: center"><input type="checkbox" class="ab-checkbox" onchange="toggleABMarks(this)"></td>

                <td><input type="number" class="ob1" min="0" max="20" oninput="calcTotals(this)"></td>
                <td><input type="number" class="ob2" min="0" max="20" oninput="calcTotals(this)"></td>

                <td><input type="number" class="on1" min="0" max="20" oninput="calcTotals(this)"></td>
                <td><input type="number" class="on2" min="0" max="20" oninput="calcTotals(this)"></td>

                <td><input type="number" class="d1" min="0" max="30" oninput="calcTotals(this)"></td>
                <td><input type="number" class="d2" min="0" max="30" oninput="calcTotals(this)"></td>

                <td><input type="number" class="s1" min="0" max="5" oninput="calcTotals(this)"></td>
                <td><input type="number" class="s2" min="0" max="5" oninput="calcTotals(this)"></td>

                <td class="mid1-total">0</td>
                <td class="mid2-total">0</td>
            </tr>`;
    });

    document.getElementById("mk-summary").innerText =
      `Total Students: ${students.length}`;

    for (const stu of students) {
      fetchStudentMarks(stu.roll_no, batch, sem, subject);
    }
  } catch (err) {
    console.error(err);
    tableBody.innerHTML = `<tr><td colspan="13">Error loading data</td></tr>`;
  }
}

function round2(value) {
  return Math.round((value + Number.EPSILON) * 100) / 100;
}

async function fetchStudentMarks(roll, batch, sem, subject) {
  const token = localStorage.getItem("token");

  try {
    const res = await fetch(
      "http://127.0.0.1:8000/faculty/internal-marks/get",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          roll_no: roll,
          batch: batch,
          semester: parseInt(sem),
          subject_name: subject,
          subject_code: subject,
        }),
      },
    );

    if (!res.ok) return;

    const marks = await res.json();
    if (!marks) return;

    const row = document.querySelector(`tr[data-roll="${roll}"]`);
    if (!row) return;

    const isAB = marks.openbook1 === "AB" || marks.openbook1 === null;
    const abCheckbox = row.querySelector(".ab-checkbox");

    if (isAB) {
      abCheckbox.checked = true;
      toggleABMarks(abCheckbox);
    } else {
      row.querySelector(".ob1").value = marks.openbook1 ?? 0;
      row.querySelector(".ob2").value = marks.openbook2 ?? 0;
      row.querySelector(".on1").value = marks.objective1 ?? 0;
      row.querySelector(".on2").value = marks.objective2 ?? 0;
      row.querySelector(".d1").value = marks.descriptive1 ?? 0;
      row.querySelector(".d2").value = marks.descriptive2 ?? 0;
      row.querySelector(".s1").value = marks.seminar1 ?? 0;
      row.querySelector(".s2").value = marks.seminar2 ?? 0;

      calcTotals(row.querySelector(".ob1"));
    }
  } catch (e) {
    console.warn("Marks fetch failed for", roll, e);
  }
}

function calcTotals(input) {
  const row = input.closest("tr");

  const ob1 = +row.querySelector(".ob1").value || 0;
  const ob2 = +row.querySelector(".ob2").value || 0;
  const on1 = +row.querySelector(".on1").value || 0;
  const on2 = +row.querySelector(".on2").value || 0;
  const d1 = +row.querySelector(".d1").value || 0;
  const d2 = +row.querySelector(".d2").value || 0;
  const s1 = +row.querySelector(".s1").value || 0;
  const s2 = +row.querySelector(".s2").value || 0;

  const mid1 = round2((ob1 / 4) + (on1 / 2) + (d1 / 3) + (s1 / 1));
  const mid2 = round2((ob2 / 4) + (on2 / 2) + (d2 / 3) + (s2 / 1));

  row.querySelector(".mid1-total").innerText = mid1;
  row.querySelector(".mid2-total").innerText = mid2;
}

function toggleABMarks(checkbox) {
  const row = checkbox.closest("tr");
  const markInputs = row.querySelectorAll("input[type='number']");

  if (checkbox.checked) {
    markInputs.forEach((input) => {
      input.disabled = true;
      input.value = "";
    });
    row.querySelector(".mid1-total").innerText = "AB";
    row.querySelector(".mid2-total").innerText = "AB";
  } else {
    markInputs.forEach((input) => {
      input.disabled = false;
    });
    calcTotals(markInputs[0]);
  }
}

async function submitMarks() {
  const rows = document.querySelectorAll("#mk-list tr");
  const token = localStorage.getItem("token");

  const subject = document.getElementById("mk-sub").value.trim();
  const batch = document.getElementById("mk-batch").value.trim();
  const sem = parseInt(document.getElementById("mk-sem").value);

  if (!batch || !subject || !sem) {
    alert("Please provide Batch, Subject Code and Semester before saving.");
    return;
  }

  let success = 0,
    fail = 0;

  for (const row of rows) {
    const isAB = row.querySelector(".ab-checkbox").checked;

    const payload = {
      roll_no: row.dataset.roll,
      subject_name: subject,
      subject_code: subject,
      batch: batch,
      semester: sem,

      openbook1: isAB ? 0 : (+row.querySelector(".ob1").value || 0),
      openbook2: isAB ? 0 : (+row.querySelector(".ob2").value || 0),

      objective1: isAB ? 0 : (+row.querySelector(".on1").value || 0),
      objective2: isAB ? 0 : (+row.querySelector(".on2").value || 0),

      descriptive1: isAB ? 0 : (+row.querySelector(".d1").value || 0),
      descriptive2: isAB ? 0 : (+row.querySelector(".d2").value || 0),

      seminar1: isAB ? 0 : (+row.querySelector(".s1").value || 0),
      seminar2: isAB ? 0 : (+row.querySelector(".s2").value || 0),
    };

    try {
      const res = await fetch(
        "http://127.0.0.1:8000/faculty/internal-marks/update",
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(payload),
        },
      );

      res.ok ? success++ : fail++;
    } catch {
      fail++;
    }
  }

  alert(`Marks Update Complete\nSuccess: ${success}\nFailed: ${fail}`);
}

function downloadMarksExcelTemplate() {
  const rows = document.querySelectorAll("#mk-list tr[data-roll]");

  let csvContent = "Roll No,Subject Code,Subject Name,OpenBook1,OpenBook2,Objective1,Objective2,Descriptive1,Descriptive2,Seminar1,Seminar2\n";

  if (rows.length > 0) {
    rows.forEach((row) => {
      const rollNo = row.getAttribute("data-roll");
      const isAB = row.querySelector(".ab-checkbox").checked;

      const subjectCode = document.getElementById("mk-sub")?.value || "";
      const subjectName = subjectCode;
      const ob1 = isAB ? 0 : (row.querySelector(".ob1").value || 0);
      const ob2 = isAB ? 0 : (row.querySelector(".ob2").value || 0);
      const on1 = isAB ? 0 : (row.querySelector(".on1").value || 0);
      const on2 = isAB ? 0 : (row.querySelector(".on2").value || 0);
      const d1 = isAB ? 0 : (row.querySelector(".d1").value || 0);
      const d2 = isAB ? 0 : (row.querySelector(".d2").value || 0);
      const s1 = isAB ? 0 : (row.querySelector(".s1").value || 0);
      const s2 = isAB ? 0 : (row.querySelector(".s2").value || 0);

      csvContent += `${rollNo},${subjectCode},${subjectName},${ob1},${ob2},${on1},${on2},${d1},${d2},${s1},${s2}\n`;
    });
  } else {
    alert("Tip: Load a class first to export their marks! Downloading a generic template instead...");
    csvContent += "NAN,CS301,CS301,0,0,0,0,0,0,0,0\n";
  }

  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.href = url;

  const subject = document.getElementById("mk-sub")
    ? document.getElementById("mk-sub").value
    : "Marks";
  link.setAttribute("download", `${subject}_Internal_Marks.csv`);

  document.body.appendChild(link);
  link.click();

  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

async function uploadMarksExcel() {
  const fileInput = document.getElementById("mk-upload-file");
  const file = fileInput.files[0];

  const subject = document.getElementById("mk-sub").value.trim();
  const batch = document.getElementById("mk-batch").value.trim();
  const sem = document.getElementById("mk-sem").value;
  const branch = document.getElementById("mk-branch").value;
  const section = document.getElementById("mk-sec").value;
  const token = localStorage.getItem("token");

  if (!file) {
    alert("Please select an Excel file first.");
    return;
  }
  if (!subject || !batch || !sem) {
    alert("Please provide Batch, Subject Code and Semester for upload.");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  const url = new URL("http://127.0.0.1:8000/faculty/internal-marks/upload");
  url.searchParams.append("subject_code", subject);
  url.searchParams.append("semester", sem);
  url.searchParams.append("batch", batch);
  url.searchParams.append("branch", branch);
  url.searchParams.append("section", section);

  try {
    const res = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });

    const data = await res.json();

    if (res.ok) {
      alert("Success: " + data.message);
      fetchStudentListForMarks();
      fileInput.value = "";
    } else {
      alert("Upload Failed: " + (data.detail || "Unknown error"));
    }
  } catch (error) {
    console.error("Upload Error:", error);
    alert("Network Error during upload.");
  }
}

