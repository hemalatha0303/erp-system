document.addEventListener("DOMContentLoaded", () => {
  const today = new Date().toISOString().split("T")[0];

  const issueDateEl = document.getElementById("issue-date");
  const returnDateEl = document.getElementById("actual-return-date");
  const dueDateEl = document.getElementById("return-due-date");

  if (issueDateEl) issueDateEl.value = today;
  if (returnDateEl) returnDateEl.value = today;

  if (dueDateEl) {
    const due = new Date();
    due.setDate(due.getDate() + 15);
    dueDateEl.value = due.toISOString().split("T")[0];
  }

  fetchBookCatalog();
});

async function uploadBooks() {
  const fileInput = document.getElementById("bookFile");
  if (!fileInput.files[0]) {
    alert("Please select an Excel file.");
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  try {
    const res = await fetch("http://127.0.0.1:8000/library/books/upload", {
      method: "POST",
      headers: { Authorization: "Bearer " + localStorage.getItem("token") },
      body: formData,
    });
    const data = await res.json();

    if (res.ok) {
      alert(data.message);
      fetchBookCatalog();
    } else alert("Error: " + (data.detail || "Upload failed"));
  } catch (error) {
    console.error(error);
    alert("Network Error");
  }
}

async function issueBooks() {
  const srno = document.getElementById("issue-roll").value.trim();
  const codes = document.getElementById("issue-codes").value.trim();

  if (!srno || !codes) {
    alert("Please fill Roll No and Book Codes");
    return;
  }

  const codeList = codes
    .split(",")
    .map((c) => c.trim())
    .filter((c) => c !== "");

  const payload = {
    srno: srno,
    semester: parseInt(document.getElementById("issue-sem").value),
    book_codes: codeList,
    issued_date: document.getElementById("issue-date").value,
    expected_return_date: document.getElementById("return-due-date").value,
  };

  try {
    const res = await fetch("http://127.0.0.1:8000/library/issue", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (res.ok) {
      alert(data.message);

      document.getElementById("issue-codes").value = "";
      fetchBookCatalog();
    } else {
      alert("Error: " + (data.detail || "Issue failed"));
    }
  } catch (error) {
    console.error(error);
    alert("Network Error");
  }
}

async function fetchPendingBooks() {
  const srno = document.getElementById("return-roll").value.trim();
  const sem = document.getElementById("return-sem").value;

  if (!srno) {
    alert("Enter Roll Number");
    return;
  }

  try {
    const res = await fetch(
      `http://127.0.0.1:8000/library/pending?srno=${srno}&semester=${sem}`,
      {
        headers: { Authorization: "Bearer " + localStorage.getItem("token") },
      },
    );
    const data = await res.json();

    const container = document.getElementById("pending-books-container");
    const list = document.getElementById("pending-list");
    list.innerHTML = "";

    if (data.length === 0) {
      list.innerHTML =
        "<p style='color:grey; text-align:center;'>No pending books found for this semester.</p>";
      container.style.display = "block";
      return;
    }

    data.forEach((issue) => {
      const item = `
                <div class="pending-item">
                    <input type="checkbox" class="return-checkbox" value="${issue.book_code}">
                    <div class="book-info">
                        <span class="book-code">${issue.book_code}</span>
                        <span>Issued: ${issue.issued_date} (Due: ${issue.expected_return_date})</span>
                    </div>
                </div>
            `;
      list.innerHTML += item;
    });

    container.style.display = "block";
  } catch (error) {
    console.error(error);
    alert("Error fetching pending books");
  }
}

async function returnBooks() {
  const checkboxes = document.querySelectorAll(".return-checkbox:checked");
  const selectedCodes = Array.from(checkboxes).map((cb) => cb.value);

  if (selectedCodes.length === 0) {
    alert("Select at least one book to return.");
    return;
  }

  const payload = {
    srno: document.getElementById("return-roll").value,
    semester: parseInt(document.getElementById("return-sem").value),
    year: 3,
    book_codes: selectedCodes,
    return_date: document.getElementById("actual-return-date").value,
  };

  try {
    const res = await fetch("http://127.0.0.1:8000/library/return", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (res.ok) {
      alert(data.message);
      fetchPendingBooks();
      fetchBookCatalog();
    } else {
      alert("Error: " + (data.detail || "Return failed"));
    }
  } catch (error) {
    console.error(error);
    alert("Network Error");
  }
}

async function fetchBookCatalog() {
  const search = document.getElementById("catalog-search").value || "";
  const listBody = document.getElementById("catalog-list");

  listBody.innerHTML = "<tr><td colspan='4'>Loading...</td></tr>";

  try {
    const url = search
      ? `http://127.0.0.1:8000/library/books?search=${search}`
      : "http://127.0.0.1:8000/library/books";

    const res = await fetch(url, {
      headers: { Authorization: "Bearer " + localStorage.getItem("token") },
    });

    if (res.ok) {
      const books = await res.json();
      listBody.innerHTML = "";

      if (books.length === 0) {
        listBody.innerHTML =
          "<tr><td colspan='4' style='text-align:center;'>No books found.</td></tr>";
        return;
      }

      books.forEach((b) => {
        const row = `
                    <tr style="border-bottom:1px solid #eee;">
                        <td style="padding:10px; font-weight:bold;">${b.code}</td>
                        <td style="padding:10px;">${b.title}</td>
                        <td style="padding:10px;">${b.author}</td>
                        <td style="padding:10px; color:${b.available_copies > 0 ? "green" : "red"}">
                            ${b.available_copies}
                        </td>
                    </tr>
                `;
        listBody.innerHTML += row;
      });
    }
  } catch (e) {
    console.error("Catalog Fetch Error", e);
    listBody.innerHTML =
      "<tr><td colspan='4' style='color:red;'>Error fetching catalog.</td></tr>";
  }
}
