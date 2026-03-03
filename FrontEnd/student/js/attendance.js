document.addEventListener("DOMContentLoaded", () => {
  const today = new Date();
  document.getElementById("att-month").value = today.getMonth() + 1;
  document.getElementById("att-year").value = today.getFullYear();

  loadAttendance();
});

async function loadAttendance() {
  const month = document.getElementById("att-month").value;
  const year = document.getElementById("att-year").value;
  const token = localStorage.getItem("token");

  if (!token) {
    window.location.href = "../../index.html";
    return;
  }

  try {
    const response = await fetch(
      `http://127.0.0.1:8000/student/attendance/monthly?month=${month}&year=${year}`,
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

    const formattedData = transformData(apiData, month, year);

    renderTable(formattedData);
  } catch (error) {
    console.error("Attendance Load Error:", error);
    document.getElementById("tableBody").innerHTML =
      `<tr><td colspan="35" style="text-align:center; color:red;">Could not find data</td></tr>`;
  }
}

function transformData(apiData, month, year) {
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
  });
}
