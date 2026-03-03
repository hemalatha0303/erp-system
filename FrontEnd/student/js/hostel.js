document.addEventListener("DOMContentLoaded", () => {
  loadHostelData();
});

async function loadHostelData() {
  const statusBadge = document.getElementById("status-badge");
  const roommateSection = document.getElementById("roommate-section");
  const roommateList = document.getElementById("roommate-list");

  const feeTotalEl = document.getElementById("fee-total");
  const feePaidEl = document.getElementById("fee-paid");
  const feeDueEl = document.getElementById("fee-due");

  const token = localStorage.getItem("token");

  try {
    const response = await fetch("http://127.0.0.1:8000/student/hostel", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error("Failed to fetch hostel data");
    }

    const data = await response.json();

    const isAllocated = data.room_number !== undefined;

    if (isAllocated) {
      statusBadge.innerText = "Allocated";
      statusBadge.className = "badge allocated";

      document.getElementById("h-block").innerText = "Hostel Block";
      document.getElementById("h-room").innerText = data.room_number;
      document.getElementById("h-type").innerText =
        `${data.sharing}-Seater ${data.room_type}`;
      document.getElementById("h-bed").innerText = "Assigned";

      if (data.fee) {
        feeTotalEl.innerText = `₹ ${data.fee.total.toLocaleString()}`;
        feePaidEl.innerText = `₹ ${data.fee.paid.toLocaleString()}`;

        const dueAmount = data.fee.due;
        feeDueEl.innerText = `₹ ${dueAmount.toLocaleString()}`;

        feeDueEl.style.color = dueAmount > 0 ? "#c0392b" : "#27ae60";
      }

      roommateSection.style.display = "block";
      roommateList.innerHTML = `
                <tr>
                    <td colspan="4" style="text-align:center; color:#999; padding:20px; font-style:italic;">
                        Roommate details not available in this view.
                    </td>
                </tr>
            `;
    } else {
      statusBadge.innerText = "Not Allocated";
      statusBadge.className = "badge";
      statusBadge.style.backgroundColor = "#e0e0e0";
      statusBadge.style.color = "#555";

      document.getElementById("h-block").innerText = "--";
      document.getElementById("h-room").innerText = "--";
      document.getElementById("h-type").innerText = "--";
      document.getElementById("h-bed").innerText = "--";

      roommateSection.style.display = "none";

      feeTotalEl.innerText = "₹ 0";
      feePaidEl.innerText = "₹ 0";
      feeDueEl.innerText = "₹ 0";
    }
  } catch (error) {
    console.error("Error loading hostel data:", error);
    statusBadge.innerText = "Error Loading";
    statusBadge.style.color = "red";
  }
}
