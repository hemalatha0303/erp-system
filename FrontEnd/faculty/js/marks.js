async function fetchStudentListForMarks() {
  const year = document.getElementById("mk-year").value;
  const sem = document.getElementById("mk-sem").value;
  const sec = document.getElementById("mk-sec").value.trim().toUpperCase();
  const branch = document
    .getElementById("mk-branch")
    .value.trim()
    .toUpperCase();
  const subject = document.getElementById("mk-sub").value.trim();
  const token = localStorage.getItem("token");

  if (!sec || !branch || !subject) {
    alert("Please enter Branch, Section and Subject");
    return;
  }

  const tableBody = document.getElementById("mk-list");
  const container = document.getElementById("mk-table-container");

  container.style.display = "block";
  tableBody.innerHTML = `<tr><td colspan="12" style="text-align:center;">Loading...</td></tr>`;

  try {
    const res = await fetch(
      `http://127.0.0.1:8000/faculty/class-students?year=${year}&semester=${sem}&section=${sec}&branch=${branch}`,
      { headers: { Authorization: `Bearer ${token}` } },
    );

    if (!res.ok) throw new Error("Failed to fetch students");

    const students = await res.json();
    tableBody.innerHTML = "";

    if (students.length === 0) {
      tableBody.innerHTML = `<tr><td colspan="12">No students found</td></tr>`;
      return;
    }

    students.forEach((stu) => {
      tableBody.innerHTML += `
            <tr data-roll="${stu.roll_no}">
                <td>${stu.roll_no}</td>
                <td>${stu.name}</td>

                <td><input type="number" class="ob1" min="0" max="5" oninput="calcTotals(this)"></td>
                <td><input type="number" class="ob2" min="0" max="5" oninput="calcTotals(this)"></td>

                <td><input type="number" class="d1" min="0" max="10" oninput="calcTotals(this)"></td>
                <td><input type="number" class="d2" min="0" max="10" oninput="calcTotals(this)"></td>

                <td><input type="number" class="s1" min="0" max="5" oninput="calcTotals(this)"></td>
                <td><input type="number" class="s2" min="0" max="5" oninput="calcTotals(this)"></td>

                <td><input type="number" class="o1" min="0" max="5" oninput="calcTotals(this)"></td>
                <td><input type="number" class="o2" min="0" max="5" oninput="calcTotals(this)"></td>

                <td class="mid1-total">0</td>
                <td class="mid2-total">0</td>
            </tr>`;
    });

    document.getElementById("mk-summary").innerText =
      `Total Students: ${students.length}`;

    for (const stu of students) {
      fetchStudentMarks(stu.roll_no, year, sem, subject);
    }
  } catch (err) {
    console.error(err);
    tableBody.innerHTML = `<tr><td colspan="12">Error loading data</td></tr>`;
  }
}

async function fetchStudentMarks(roll, year, sem, subject) {
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
          year: parseInt(year),
          semester: parseInt(sem),
          subject_name: subject,
        }),
      },
    );

    if (!res.ok) return;

    const marks = await res.json();
    console.log("Fetched marks:", marks);

    const row = document.querySelector(`tr[data-roll="${roll}"]`);
    if (!row) return;

    row.querySelector(".ob1").value = marks.openbook1 ?? 0;
    row.querySelector(".ob2").value = marks.openbook2 ?? 0;
    row.querySelector(".d1").value = marks.descriptive1 ?? 0;
    row.querySelector(".d2").value = marks.descriptive2 ?? 0;
    row.querySelector(".s1").value = marks.seminar1 ?? 0;
    row.querySelector(".s2").value = marks.seminar2 ?? 0;
    row.querySelector(".o1").value = marks.objective1 ?? 0;
    row.querySelector(".o2").value = marks.objective2 ?? 0;

    calcTotals(row.querySelector(".ob1"));
  } catch (e) {
    console.warn("Marks fetch failed for", roll, e);
  }
}

function calcTotals(input) {
  const row = input.closest("tr");

  const mid1 =
    (+row.querySelector(".ob1").value || 0) +
    (+row.querySelector(".d1").value || 0) +
    (+row.querySelector(".s1").value || 0) +
    (+row.querySelector(".o1").value || 0);

  const mid2 =
    (+row.querySelector(".ob2").value || 0) +
    (+row.querySelector(".d2").value || 0) +
    (+row.querySelector(".s2").value || 0) +
    (+row.querySelector(".o2").value || 0);

  row.querySelector(".mid1-total").innerText = mid1;
  row.querySelector(".mid2-total").innerText = mid2;
}

async function submitMarks() {
  const rows = document.querySelectorAll("#mk-list tr");
  const token = localStorage.getItem("token");

  const subject = document.getElementById("mk-sub").value.trim();
  const year = parseInt(document.getElementById("mk-year").value);
  const sem = parseInt(document.getElementById("mk-sem").value);

  let success = 0,
    fail = 0;

  for (const row of rows) {
    const payload = {
      roll_no: row.dataset.roll,
      subject_name: subject,
      year,
      semester: sem,

      openbook1: +row.querySelector(".ob1").value || 0,
      openbook2: +row.querySelector(".ob2").value || 0,

      descriptive1: +row.querySelector(".d1").value || 0,
      descriptive2: +row.querySelector(".d2").value || 0,

      seminar1: +row.querySelector(".s1").value || 0,
      seminar2: +row.querySelector(".s2").value || 0,

      objective1: +row.querySelector(".o1").value || 0,
      objective2: +row.querySelector(".o2").value || 0,
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
  
  let csvContent = "Roll No,OpenBook_M1,OpenBook_M2,Desc_M1,Desc_M2,Sem_M1,Sem_M2,Obj_M1,Obj_M2\n";

  if (rows.length > 0) {
    rows.forEach(row => {
      const rollNo = row.getAttribute("data-roll");
      
      const ob1 = row.querySelector(".ob1").value || 0;
      const ob2 = row.querySelector(".ob2").value || 0;
      const d1 = row.querySelector(".d1").value || 0;
      const d2 = row.querySelector(".d2").value || 0;
      const s1 = row.querySelector(".s1").value || 0;
      const s2 = row.querySelector(".s2").value || 0;
      const o1 = row.querySelector(".o1").value || 0;
      const o2 = row.querySelector(".o2").value || 0;

      // Append the actual entered marks to the CSV
      csvContent += `${rollNo},${ob1},${ob2},${d1},${d2},${s1},${s2},${o1},${o2}\n`;
    });
  } else {
    alert("Tip: Load a class first to export their marks! Downloading a generic template instead...");
    csvContent += "NAN,0,0,0,0,0,0,0,0\n";
  }

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  
  const link = document.createElement("a");
  link.href = url;
  
  const subject = document.getElementById("mk-sub") ? document.getElementById("mk-sub").value : "Marks";
  link.setAttribute("download", `${subject}_Internal_Marks.csv`); 
  
  document.body.appendChild(link);
  link.click();
  
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

async function uploadMarksExcel() {
  // 1. Get Elements
  const fileInput = document.getElementById("mk-upload-file");
  const file = fileInput.files[0];

  // 2. Get Context (Subject, Year, Sem)
  const subject = document.getElementById("mk-sub").value;
  const year = document.getElementById("mk-year").value;
  const sem = document.getElementById("mk-sem").value;
  const token = localStorage.getItem("token");

  // 3. Validation
  if (!file) {
    alert("Please select an Excel file first.");
    return;
  }
  if (!subject) {
    alert("Please select a Subject.");
    return;
  }

  // 4. Prepare Form Data
  const formData = new FormData();
  formData.append("file", file);

  // 5. Send Request
  // Note: In your Python code, subject_code, year, and semester are distinct arguments,
  // so FastAPI expects them as Query Parameters by default.
  const url = new URL("http://127.0.0.1:8000/faculty/internal-marks/upload");
  url.searchParams.append("subject_code", subject);
  url.searchParams.append("year", year);
  url.searchParams.append("semester", sem);

  try {
    const res = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        // Do NOT set Content-Type header manually when sending FormData;
        // the browser sets it with the boundary automatically.
      },
      body: formData,
    });

    const data = await res.json();

    if (res.ok) {
      alert("✅ " + data.message);
      // Refresh the list to show new marks
      fetchStudentListForMarks();
      // Clear input
      fileInput.value = "";
    } else {
      alert("❌ Upload Failed: " + (data.detail || "Unknown error"));
    }
  } catch (error) {
    console.error("Upload Error:", error);
    alert("❌ Network Error during upload.");
  }
}
