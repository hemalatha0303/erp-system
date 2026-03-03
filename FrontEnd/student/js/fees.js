document.addEventListener("DOMContentLoaded", () => {
  updateFeeView();
});
function getAuthHeaders() {
  return {
    Accept: "application/json",
    Authorization: `Bearer ${localStorage.getItem("token")}`,
  };
}
let currentPaymentData = null;

async function updateFeeView() {
  const semester = document.getElementById("semesterSelect").value;

  const structureBody = document.getElementById("structureBody");
  const txnBody = document.getElementById("transactionBody");

  structureBody.innerHTML = "";
  txnBody.innerHTML = "";

  try {
    const res = await fetch(
      `http://127.0.0.1:8000/student/payments?semester=${semester}`,
      {
        headers: getAuthHeaders(),
      },
    );

    if (!res.ok) throw new Error("Failed to fetch payment data");

    const currentData = await res.json();
    currentPaymentData = currentData;

    console.log(currentData);
    if (!currentData || !currentData.structure || !currentData.transactions) {
      structureBody.innerHTML = `<tr><td colspan="5">No data available for Semester ${semester}</td></tr>`;
      txnBody.innerHTML = `<tr><td colspan="6">No records found.</td></tr>`;
      return;
    }

    let totalFee = 0;
    let totalPaid = 0;
    let totalBal = 0;

    currentData.structure.forEach((item) => {
      totalFee += item.total;
      totalPaid += item.paid;
      totalBal += item.balance;

      let statusBadge = "";
      if (item.balance === 0) {
        statusBadge = '<span class="status-paid">Paid</span>';
      } else if (item.paid === 0) {
        statusBadge = '<span class="status-due">Unpaid</span>';
      } else {
        statusBadge = '<span class="status-partial">Partial</span>';
      }

      structureBody.innerHTML += `
        <tr>
          <td><strong>${item.type}</strong></td>
          <td>₹ ${item.total.toLocaleString()}</td>
          <td style="color:#28a745">₹ ${item.paid.toLocaleString()}</td>
          <td style="color:#dc3545">₹ ${item.balance.toLocaleString()}</td>
          <td>${statusBadge}</td>
        </tr>
      `;
    });

    structureBody.innerHTML += `
      <tr style="background:#f9f9f9; font-weight:bold;">
        <td>Total</td>
        <td>₹ ${totalFee.toLocaleString()}</td>
       <td style="color:#28a745">₹ ${totalPaid.toLocaleString()}</td>
        <td style="color:#dc3545">₹ ${totalBal.toLocaleString()}</td>
        <td>-</td>
      </tr>
    `;

    currentData.transactions.forEach((txn, index) => {
      txnBody.innerHTML += `
    <tr>
      <td>${txn.date}</td>
      <td style="text-align:left">${txn.type}</td>
      <td>${txn.ref}</td>
      <td style="color:#28a745; font-weight:bold;">₹ ${txn.amount.toLocaleString()}</td>
      <td>₹ ${txn.remBalance.toLocaleString()}</td>
      <td>
        <a href="#" onclick="downloadReceipt(${index}); return false;">
          Download ⬇
        </a>
      </td>
    </tr>
  `;
    });
  } catch (err) {
    console.error(err);
    structureBody.innerHTML = `<tr><td colspan="5">Error loading fee data</td></tr>`;
    txnBody.innerHTML = `<tr><td colspan="6">Try again later</td></tr>`;
  }
}

async function downloadReceipt(index) {
  if (
    !currentPaymentData ||
    !currentPaymentData.transactions ||
    !currentPaymentData.transactions[index]
  ) {
    alert("Receipt data not available.");
    return;
  }

  const { jsPDF } = window.jspdf;
  const txn = currentPaymentData.transactions[index];

  const doc = new jsPDF();

  doc.setFontSize(18);
  doc.text("Payment Receipt", 14, 20);

  doc.setLineWidth(0.5);
  doc.line(14, 22, 196, 22);

  doc.setFontSize(12);
  doc.text(`Date: ${txn.date}`, 14, 35);
  doc.text(`Reference Number: ${txn.ref}`, 14, 45);
  doc.text(`Fee Category: ${txn.type}`, 14, 55);
  doc.text(`Amount Paid: ₹${txn.amount.toLocaleString()}`, 14, 65);
  doc.text(`Remaining Balance: ₹${txn.remBalance.toLocaleString()}`, 14, 75);

  doc.setFontSize(10);
  doc.text("Thank you for your payment.", 14, 95);

  doc.save(`Receipt_${txn.ref}.pdf`);
}
