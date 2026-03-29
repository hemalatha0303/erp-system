document.addEventListener("DOMContentLoaded", () => {
  updateLibraryView();
});

async function updateLibraryView() {
  const semester = document.getElementById("semesterSelect").value;
  const searchText = document.getElementById("searchInput").value.toLowerCase();

  const tableBody = document.getElementById("book-list");
  const countIssued = document.getElementById("count-issued");
  const countReturned = document.getElementById("count-returned");
  const countOverdue = document.getElementById("count-overdue");

  const token = localStorage.getItem("token");
  if (!token) {
    window.location.href = "../../index.html";
    return;
  }

  try {
    const response = await fetch(
      `http://127.0.0.1:8000/library/student/books?semester=${semester}`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      },
    );

    if (!response.ok) {
      throw new Error("Failed to fetch library records");
    }

    const data = await response.json();
    const books = data.books || [];

    tableBody.innerHTML = "";
    let issued = 0;
    let returned = 0;
    let overdue = 0;

    if (books.length === 0) {
      tableBody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 20px; color: #666;">No books found for Semester ${semester}.</td></tr>`;
      updateCounts(0, 0, 0);
      return;
    }

    books.forEach((book) => {
      if (
        book.book_code.toLowerCase().includes(searchText) ||
        book.title.toLowerCase().includes(searchText)
      ) {
        let statusClass = "status-issued";
        const status = book.status ? book.status.toUpperCase() : "ISSUED";

        if (status === "RETURNED") {
          statusClass = "status-returned";
          returned++;
        } else if (status === "OVERDUE") {
          statusClass = "status-overdue";
          overdue++;
        } else {
          statusClass = "status-issued";
          issued++;
        }

        const issueDate = book.issued_date || "-";
        const returnDate = book.return_date || "-";

        const row = `
                    <tr>
                        <td><strong>${book.book_code}</strong></td>
                        <td>${book.title}</td>
                        <td>${book.author}</td>
                        <td>${issueDate}</td>
                        <td>${returnDate}</td>
                        <td><span class="status-badge ${statusClass}">${status}</span></td>
                    </tr>
                `;
        tableBody.innerHTML += row;
      }
    });

    updateCounts(issued, returned, overdue);
  } catch (error) {
    console.error("Library Error:", error);
    tableBody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:red; padding: 20px;">Error loading library data.</td></tr>`;
  }
}

function updateCounts(i, r, o) {
  const elIssued = document.getElementById("count-issued");
  const elReturned = document.getElementById("count-returned");
  const elOverdue = document.getElementById("count-overdue");

  if (elIssued) elIssued.innerText = i;
  if (elReturned) elReturned.innerText = r;
  if (elOverdue) elOverdue.innerText = o;
}
