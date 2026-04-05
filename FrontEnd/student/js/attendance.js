document.addEventListener("DOMContentLoaded", () => {
  const today = new Date();
  document.getElementById("att-month").value = today.getMonth() + 1;
  document.getElementById("att-semester").value = 1;

  preloadAcademicInfo();
});

async function preloadAcademicInfo() {
  const token = localStorage.getItem("token");
  if (!token) return;

  try {
    const res = await fetch("http://127.0.0.1:8000/student/my-academics", {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!res.ok) return;
    const data = await res.json();
    if (!Array.isArray(data) || data.length === 0) return;

    const latest = data.reduce((acc, item) => {
      const accKey = (acc.year || 0) * 10 + (acc.semester || 0);
      const itemKey = (item.year || 0) * 10 + (item.semester || 0);
      return itemKey > accKey ? item : acc;
    }, data[0]);

    if (latest.batch) {
      document.getElementById("att-batch").value = latest.batch;
    }
    if (latest.semester) {
      document.getElementById("att-semester").value = latest.semester;
    }
  } catch (error) {
    console.warn("Failed to preload academic info", error);
  }
}

async function loadAttendance() {
  const month = document.getElementById("att-month").value;
  const semester = document.getElementById("att-semester").value;
  const batch = document.getElementById("att-batch").value.trim();
  const token = localStorage.getItem("token");

  if (!token) {
    window.location.href = "../../index.html";
    return;
  }

  if (!semester) {
    alert("Please select semester.");
    return;
  }

  const tableBody = document.getElementById("tableBody");
  tableBody.innerHTML =
    `<tr><td colspan="35" style="text-align:center;">Loading attendance...</td></tr>`;

  try {
    const params = new URLSearchParams();
    params.append("month", month);
    params.append("semester", semester);
    if (batch) params.append("batch", batch);

    const response = await fetch(
      `http://127.0.0.1:8000/student/attendance/monthly?${params.toString()}`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      },
    );

    if (!response.ok) {
      throw new Error("Failed to fetch attendance data");
    }

    const apiData = await response.json();

    const formattedData = transformData(apiData, month);

    renderTable(formattedData);
    await loadSemesterOverview(semester);
  } catch (error) {
    console.error("Attendance Load Error:", error);
    document.getElementById("tableBody").innerHTML =
      `<tr><td colspan="35" style="text-align:center; color:red;">Could not find data</td></tr>`;
    clearSemesterOverview();
  }
}

function transformData(apiData, month) {
  const year = new Date().getFullYear();
  const daysInMonth = new Date(year, month, 0).getDate();
  const daysArray = Array.from({ length: daysInMonth }, (_, i) => i + 1);

  const subjectMap = {};

  Object.keys(apiData.attendance).forEach((dateStr) => {
    const day = parseInt(dateStr.split("-")[2]);
    const dayRecords = apiData.attendance[dateStr];

    dayRecords.forEach((record) => {
      const subjectName = record.subject;
      const status = record.status;

      if (!subjectMap[subjectName]) {
        subjectMap[subjectName] = {};
      }

      let char = "-";
      if (status === "PRESENT") char = "P";
      else if (status === "ABSENT") char = "A";
      else if (status === "LEAVE") char = "L";

      subjectMap[subjectName][day] = char;
    });
  });

  const subjectsArray = Object.keys(subjectMap).map((subName) => {
    return {
      name: subName,
      records: subjectMap[subName],
    };
  });

  return {
    days: daysArray,
    subjects: subjectsArray,
    monthlySummary: apiData.monthly_summary || null,
  };
}

function renderTable(data) {
  const tableHead = document.getElementById("tableHead");
  const tableBody = document.getElementById("tableBody");

  tableHead.innerHTML = "";
  tableBody.innerHTML = "";

  if (data.subjects.length === 0) {
    tableBody.innerHTML = `<tr><td colspan="35" style="text-align:center; padding:20px;">No attendance records found for this month.</td></tr>`;
    return;
  }

  let headRow = `<tr><th style="min-width: 180px;">Subject</th>`;

  data.days.forEach((d) => {
    headRow += `<th style="min-width: 30px; padding: 5px;">${String(d).padStart(2, "0")}</th>`;
  });

  headRow += `<th>P</th><th>A</th><th>%</th></tr>`;
  tableHead.innerHTML = headRow;

  let monthPresent = 0;
  let monthTotal = 0;

  data.subjects.forEach((sub) => {
    let p = 0,
      a = 0;
    let totalClasses = 0;

    let row = `<tr><td class="subject">${sub.name}</td>`;

    data.days.forEach((d) => {
      const val = sub.records[d] || "-";

      if (val === "P") {
        p++;
        totalClasses++;
      }
      if (val === "A") {
        a++;
        totalClasses++;
      }
      const cls = val !== "-" ? val.toLowerCase() : "";
      row += `<td class="${cls}">${val}</td>`;
    });

    const percent = totalClasses
      ? ((p / totalClasses) * 100).toFixed(1)
      : "0.0";

    let percentColor = "#28a745";
    if (percent < 75) percentColor = "#dc3545";

    row += `
            <td style="font-weight:bold; color:#007bff">${p}</td>
            <td style="font-weight:bold; color:#dc3545">${a}</td>
            <td style="font-weight:bold; color:${percentColor}">${percent}%</td>
        `;
    row += `</tr>`;

    tableBody.innerHTML += row;

    monthPresent += p;
    monthTotal += totalClasses;
  });

  const monthPercent = monthTotal
    ? ((monthPresent / monthTotal) * 100).toFixed(1)
    : "0.0";
  let monthColor = "#28a745";
  if (monthPercent < 75) monthColor = "#dc3545";

  let summaryRow = `<tr style="background:#f8f9fa; font-weight:600;">`;
  summaryRow += `<td class="subject">Monthly Total</td>`;
  data.days.forEach(() => {
    summaryRow += `<td>-</td>`;
  });
  summaryRow += `
      <td style="color:#007bff">${monthPresent}</td>
      <td style="color:#dc3545">${monthTotal - monthPresent}</td>
      <td style="color:${monthColor}">${monthPercent}%</td>
    </tr>`;
  tableBody.innerHTML += summaryRow;
}

async function loadSemesterOverview(semester) {
  const token = localStorage.getItem("token");
  const summaryEl = {
    total: document.getElementById("sem-total"),
    attended: document.getElementById("sem-attended"),
    absent: document.getElementById("sem-absent"),
    percent: document.getElementById("sem-percent"),
    eligible: document.getElementById("sem-eligible"),
  };
  const subjectBody = document.getElementById("subject-wise-body");
  subjectBody.innerHTML =
    `<tr><td colspan="5" style="text-align:center;">Loading...</td></tr>`;

  try {
    const summaryRes = await fetch(
      `http://127.0.0.1:8000/student/attendance/summary?semester=${semester}`,
      { headers: { Authorization: `Bearer ${token}` } },
    );
    const subjectRes = await fetch(
      `http://127.0.0.1:8000/student/attendance/subject-wise?semester=${semester}`,
      { headers: { Authorization: `Bearer ${token}` } },
    );

    if (summaryRes.ok) {
      const summary = await summaryRes.json();
      summaryEl.total.textContent = summary.total_classes ?? 0;
      summaryEl.attended.textContent = summary.attended_classes ?? 0;
      summaryEl.absent.textContent = summary.absent_classes ?? 0;
      summaryEl.percent.textContent = `${summary.attendance_percentage ?? 0}%`;
      summaryEl.eligible.textContent = summary.eligible_for_exam ? "Eligible" : "Not Eligible";
    }

    if (subjectRes.ok) {
      const rows = await subjectRes.json();
      if (!rows || rows.length === 0) {
        subjectBody.innerHTML =
          `<tr><td colspan="5" style="text-align:center;">No subject attendance found.</td></tr>`;
        return;
      }

      subjectBody.innerHTML = "";
      rows.forEach((row) => {
        subjectBody.innerHTML += `
          <tr>
            <td>${row.subject_code || "-"}</td>
            <td>${row.subject_name || "-"}</td>
            <td>${row.total_classes ?? 0}</td>
            <td>${row.attended_classes ?? 0}</td>
            <td>${row.attendance_percentage ?? 0}%</td>
          </tr>
        `;
      });
    } else {
      subjectBody.innerHTML =
        `<tr><td colspan="5" style="text-align:center; color:red;">Failed to fetch subject-wise attendance.</td></tr>`;
    }
  } catch (error) {
    console.error("Overview Load Error:", error);
    clearSemesterOverview();
  }
}

function clearSemesterOverview() {
  document.getElementById("sem-total").textContent = "0";
  document.getElementById("sem-attended").textContent = "0";
  document.getElementById("sem-absent").textContent = "0";
  document.getElementById("sem-percent").textContent = "0%";
  document.getElementById("sem-eligible").textContent = "-";
  document.getElementById("subject-wise-body").innerHTML =
    `<tr><td colspan="5" style="text-align:center; color:#999;">No data</td></tr>`;
}
