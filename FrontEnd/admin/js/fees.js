async function createFeeStructure() {
  const payload = {
    year: parseInt(document.getElementById("fs-year").value),
    quota: document.getElementById("fs-quota").value,
    residence_type: document.getElementById("fs-residence").value,
    tuition_fee: parseFloat(document.getElementById("fs-tuition").value),
    bus_fee: parseFloat(document.getElementById("fs-bus").value),
    hostel_fee: parseFloat(document.getElementById("fs-hostel").value),
  };

  if (!payload.year || isNaN(payload.tuition_fee)) {
    alert("Please fill all fields correctly.");
    return;
  }

  try {
    const res = await fetch("http://127.0.0.1:8000/admin/fee-structure", {
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
      closeModal("structureModal");
    } else {
      alert("Error: " + (data.detail || "Failed to create structure"));
    }
  } catch (error) {
    console.error(error);
    alert("Network Error");
  }
}

async function fetchPaymentDetails() {
  const roll = document.getElementById("rollSearch").value.trim();
  if (!roll) {
    alert("Please enter a Roll Number");
    return;
  }

  const resultsDiv = document.getElementById("fee-results");
  resultsDiv.innerHTML = "<p style='text-align:center;'>Loading data...</p>";

  try {
    const res = await fetch(`http://127.0.0.1:8000/payments/payment/${roll}`, {
      headers: { Authorization: "Bearer " + localStorage.getItem("token") },
    });

    const data = await res.json();

    if (!res.ok) {
      resultsDiv.innerHTML = `<p style="color:red; text-align:center;">${data.detail || "Student Not Found"}</p>`;
      return;
    }

    const studentName = data.name || data.profile?.name || roll;
    let html = `<h3 style="margin-bottom: 20px;">${studentName} - Fee Dashboard</h3>`;

    // --- 1. CURRENT DUES (SEMESTER/YEAR BREAKDOWN) ---
    if (data.all_semesters && data.all_semesters.length > 0) {
      data.all_semesters.forEach((semData) => {
        html += `<h4 style="margin-top: 15px; color: #0d47a1;">Semester ${semData.semester} (Year ${semData.year})</h4>`;
        html += `
          <table class="fee-table" style="margin-bottom: 20px;">
            <thead>
              <tr>
                <th>Fee Category</th>
                <th>Total Fee</th>
                <th>Paid Amount</th>
                <th>Balance Due</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
        `;
        
        semData.structure.forEach((f) => {
          html += `
            <tr>
              <td><strong>${f.type}</strong></td>
              <td>₹ ${f.total.toLocaleString()}</td>
              <td class="text-green">₹ ${f.paid.toLocaleString()}</td>
              <td class="text-red">₹ ${f.balance.toLocaleString()}</td>
              <td><strong>${f.status}</strong></td>
            </tr>
          `;
        });
        
        html += `</tbody></table>`;
      });
    } else if (data.fees) { 
      // Fallback for the old single-semester backend format just in case
      html += `
        <table class="fee-table" style="margin-bottom: 20px;">
          <thead>
            <tr>
              <th>Fee Category</th><th>Total Fee</th><th>Paid Amount</th><th>Balance Due</th>
            </tr>
          </thead>
          <tbody>
      `;
      data.fees.forEach((f) => {
        html += `
          <tr>
            <td><strong>${f.fee_type}</strong></td>
            <td>₹ ${f.total_fee.toLocaleString()}</td>
            <td class="text-green">₹ ${f.paid.toLocaleString()}</td>
            <td class="text-red">₹ ${f.balance.toLocaleString()}</td>
          </tr>
        `;
      });
      html += `</tbody></table>`;
    } else {
      html += `<p>No fee structure generated for this student yet.</p>`;
    }

    // --- 2. TRANSACTION HISTORY ---
    html += `<h3 style="margin-top: 30px; border-top: 1px solid #ccc; padding-top: 15px;">Transaction History</h3>`;
    
    if (data.transactions && data.transactions.length > 0) {
      html += `
        <table class="fee-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Reference ID</th>
              <th>Fee Type</th>
              <th>Year</th>
              <th>Amount</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
      `;
      
      data.transactions.forEach((txn) => {
        // We pass the data to the print function cleanly
        const printArgs = `'${txn.ref}', '${txn.date}', '${txn.type}', ${txn.amount}, ${txn.year_paid_for}, '${studentName}', '${roll}'`;
        
        html += `
          <tr>
            <td>${txn.date}</td>
            <td><strong>${txn.ref}</strong></td>
            <td>${txn.type}</td>
            <td>Year ${txn.year_paid_for}</td>
            <td class="text-green"><strong>₹ ${txn.amount.toLocaleString()}</strong></td>
            <td>
              <button class="action-btn" style="padding: 5px 10px; font-size: 0.85rem;" 
                      onclick="printBill(${printArgs})">
                <i class="fas fa-print"></i> Print Bill
              </button>
            </td>
          </tr>
        `;
      });
      html += `</tbody></table>`;
    } else {
      html += `<p style="color: #666; font-style: italic;">No previous transactions found for this student.</p>`;
    }

    resultsDiv.innerHTML = html;

  } catch (error) {
    console.error(error);
    resultsDiv.innerHTML = "<p style='color:red'>Network Error connecting to server.</p>";
  }
}

// --- NEW FUNCTION: GENERATE AND PRINT BILL ---
function printBill(ref, date, type, amount, year, studentName, rollNo) {
  // Opens a new clean window for the receipt
  const receiptWindow = window.open('', '_blank', 'width=700,height=500');
  
  const receiptHTML = `
    <!DOCTYPE html>
    <html>
    <head>
      <title>Fee Receipt - ${ref}</title>
      <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 40px; color: #333; }
        .receipt-box { border: 2px solid #0d47a1; padding: 30px; border-radius: 8px; max-width: 600px; margin: 0 auto; }
        .header { text-align: center; border-bottom: 2px solid #eee; padding-bottom: 20px; margin-bottom: 20px; }
        .header h1 { margin: 0; color: #0d47a1; font-size: 24px; }
        .header p { margin: 5px 0 0; color: #666; }
        .row { display: flex; justify-content: space-between; margin-bottom: 12px; font-size: 16px; }
        .row strong { color: #555; }
        .amount-box { margin-top: 30px; background: #f4f6f8; padding: 15px; text-align: center; border-radius: 6px; }
        .amount-box h2 { margin: 0; color: #27ae60; font-size: 28px; }
        .footer { margin-top: 40px; text-align: center; font-size: 12px; color: #999; border-top: 1px solid #eee; padding-top: 20px; }
        @media print { body { padding: 0; } .receipt-box { border: none; } }
      </style>
    </head>
    <body>
      <div class="receipt-box">
        <div class="header">
          <p>Fee Receipt</p>
        </div>
        
        <div class="row"><strong>Receipt No:</strong> <span>${ref}</span></div>
        <div class="row"><strong>Date of Payment:</strong> <span>${date}</span></div>
        <div class="row"><strong>Student Name:</strong> <span>${studentName}</span></div>
        <div class="row"><strong>Roll Number:</strong> <span>${rollNo}</span></div>
        
        <hr style="border: 0; border-top: 1px dashed #ccc; margin: 20px 0;">
        
        <div class="row"><strong>Fee Category:</strong> <span>${type}</span></div>
        <div class="row"><strong>Academic Year:</strong> <span>Year ${year}</span></div>
        
        <div class="amount-box">
          <span style="font-size: 14px; color: #666; text-transform: uppercase;">Amount Paid Successfully</span>
          <h2>₹ ${amount.toLocaleString()}</h2>
        </div>
        
        <div class="footer">
          This is a computer-generated receipt and does not require a physical signature.<br>
          For any discrepancies, please contact the Accounts Department.
        </div>  
      </div>
      <script>
        // Automatically trigger the print dialog once the window loads
        window.onload = function() {
          window.print();
        };
      </script>
    </body>
    </html>
  `;

  receiptWindow.document.write(receiptHTML);
  receiptWindow.document.close();
}


async function updatePayment() {
  const payload = {
    roll_no: document.getElementById("pay-roll").value.trim(),
    fee_type: document.getElementById("pay-type").value,
    amount: parseFloat(document.getElementById("pay-amount").value),
    payment_mode: document.getElementById("pay-mode").value,
  };

  if (!payload.roll_no || isNaN(payload.amount) || payload.amount <= 0) {
    alert("Please enter a valid Roll No and Amount.");
    return;
  }

  try {
    const res = await fetch("http://127.0.0.1:8000/payments/payment/update", {
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
      closeModal("paymentModal");

      // Auto-refresh the dashboard if the admin is currently viewing the student they just paid for
      if (document.getElementById("rollSearch").value.trim() === payload.roll_no) {
        fetchPaymentDetails();
      }
      
      // Clear the form inputs
      document.getElementById("pay-amount").value = "";
    } else {
      alert("Error: " + (data.detail || "Update Failed"));
    }
  } catch (error) {
    console.error(error);
    alert("Network Error");
  }
}

function openModal(id) {
  document.getElementById(id).style.display = "flex";
}

function closeModal(id) {
  document.getElementById(id).style.display = "none";
}

window.onclick = function (event) {
  if (event.target.classList.contains("modal")) {
    event.target.style.display = "none";
  }
};