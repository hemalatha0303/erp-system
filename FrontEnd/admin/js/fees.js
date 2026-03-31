const API_BASE = typeof API_URL !== "undefined" ? API_URL : "http://127.0.0.1:8000";
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
    const res = await fetch(`${API_BASE}/admin/fee-structure`, {
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
    const res = await fetch(`${API_BASE}/payments/payment/${roll}`, {
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
        //html += `<h4 style="margin-top: 15px; color: #0d47a1;">Semester ${semData.semester} (Year ${semData.year})</h4>`;
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
              <th>Payment Mode / Details</th>
              <th>Year</th>
              <th>Amount</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
      `;
      
      data.transactions.forEach((txn) => {
        // Build payment mode display with details
        const paymentMode = txn.payment_mode || 'Cash';
        let paymentModeDisplay = paymentMode;
        if (txn.payment_details) {
          paymentModeDisplay += `<br/><small style="color: #666;">${txn.payment_details}</small>`;
        }
        
        // We pass the data to the print function cleanly
        const printArgs = `'${txn.ref}', '${txn.date}', '${txn.type}', ${txn.amount}, ${txn.year_paid_for}, '${studentName}', '${roll}', '${paymentMode}', '${(txn.payment_details || '').replace(/'/g, "\\'")}'`;
        
        html += `
          <tr>
            <td>${txn.date}</td>
            <td><strong>${txn.ref}</strong></td>
            <td><strong>${txn.type}</strong></td>
            <td>${paymentModeDisplay}</td>
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
function printBill(ref, date, type, amount, year, studentName, rollNo, paymentMode = 'Cash', paymentDetailsStr = '') {
  // Parse payment details based on payment mode
  let paymentDetailsHTML = '';
  
  if (paymentMode === 'UPI' && paymentDetailsStr) {
    const parts = paymentDetailsStr.split(',').map(p => p.trim());
    if (parts.length >= 3) {
      paymentDetailsHTML = `
        <div class="detail-row">
          <div><strong>Transaction ID:</strong><br><span>${parts[0] || 'N/A'}</span></div>
          <div><strong>Phone Number:</strong><br><span>${parts[1] || 'N/A'}</span></div>
        </div>
        <div class="detail-row">
          <div><strong>Name of Person:</strong><br><span>${parts[2] || 'N/A'}</span></div>
          <div>&nbsp;</div>
        </div>
      `;
    }
  } else if (paymentMode === 'DD' && paymentDetailsStr) {
    const parts = paymentDetailsStr.split(',').map(p => p.trim());
    if (parts.length >= 2) {
      paymentDetailsHTML = `
        <div class="detail-row">
          <div><strong>Account Number:</strong><br><span>${parts[0] || 'N/A'}</span></div>
          <div><strong>Mobile Number:</strong><br><span>${parts[1] || 'N/A'}</span></div>
        </div>
      `;
    }
  }
  
  // Opens a new clean window for the receipt
  const receiptWindow = window.open('', '_blank', 'width=750,height=700');
  
  const receiptHTML = `
    <!DOCTYPE html>
    <html>
    <head>
      <title>Fee Receipt - ${ref}</title>
      <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 40px; color: #333; background-color: #f9f9f9; }
        .receipt-box { border: 2px solid #0d47a1; padding: 35px; border-radius: 8px; max-width: 650px; margin: 0 auto; background-color: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        
        .institute-header { text-align: center; margin-bottom: 30px; border-bottom: 3px solid #cc0000; padding-bottom: 15px; }
        .institute-header h1 { margin: 0; color: #cc0000; font-size: 20px; font-weight: bold; letter-spacing: 0.5px; }
        
        .receipt-title { text-align: center; margin-bottom: 25px; }
        .receipt-title h2 { margin: 0; color: #0d47a1; font-size: 18px; }
        
        .details-section { margin-bottom: 25px; }
        .detail-row { display: grid; grid-template-columns: 1fr 1fr; margin-bottom: 12px; font-size: 14px; }
        .detail-row strong { color: #333; font-weight: 600; }
        .detail-row span { color: #555; }
        
        .divider { border: 0; border-top: 1px dashed #bbb; margin: 20px 0; }
        
        .payment-section { text-align: center; margin: 30px 0; }
        .payment-success-text { font-size: 16px; color: #27ae60; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; }
        .payment-amount { font-size: 42px; color: #27ae60; font-weight: bold; margin: 15px 0; }
        
        .footer { margin-top: 40px; text-align: center; font-size: 11px; color: #666; border-top: 1px solid #ddd; padding-top: 20px; line-height: 1.6; }
        
        @media print { 
          body { padding: 0; background-color: white; } 
          .receipt-box { border: 1px solid #0d47a1; box-shadow: none; }
        }
      </style>
    </head>
    <body>
      <div class="receipt-box">
        <div class="institute-header">
          <h1>VASIREDDY VENKATADRI INSTITUTE OF TECHNOLOGY</h1>
        </div>
        
        <div class="receipt-title">
          <h2>Fee Receipt</h2>
        </div>
        
        <div class="details-section">
          <div class="detail-row">
            <div><strong>Receipt No:</strong><br><span>${ref}</span></div>
            <div><strong>Roll No:</strong><br><span>${rollNo}</span></div>
          </div>
          
          <div class="detail-row">
            <div><strong>Student Name:</strong><br><span>${studentName}</span></div>
            <div><strong>Academic Year:</strong><br><span>Year ${year}</span></div>
          </div>
          
          <div class="detail-row">
            <div><strong>Fee Category:</strong><br><span>${type}</span></div>
            <div><strong>Payment Mode:</strong><br><span>${paymentMode}</span></div>
          </div>
          
          <div class="detail-row">
            <div><strong>Date & Time of Payment:</strong><br><span>${date}</span></div>
            <div>&nbsp;</div>
          </div>
          
          ${paymentDetailsHTML}
        </div>
        
        <hr class="divider">
        
        <div class="payment-section">
          <div class="payment-success-text">✓ Payment Successfully Paid</div>
          <div class="payment-amount">₹ ${amount.toLocaleString()}</div>
        </div>
        
        <hr class="divider">
        
        <div class="footer">
          <p><strong>Note:</strong></p>
          <p>This is a computer-generated receipt and does not require a physical signature.<br>
          For any discrepancies, please contact the Accounts Department.</p>
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
  const rollNo = document.getElementById("pay-roll").value.trim();
  const feeType = document.getElementById("pay-type").value;
  const amount = parseFloat(document.getElementById("pay-amount").value);
  const paymentMode = document.getElementById("pay-mode").value;

  if (!rollNo || isNaN(amount) || amount <= 0) {
    alert("Please enter a valid Roll No and Amount.");
    return;
  }

  // Validate mode-specific fields
  let paymentDetails = {};

  if (paymentMode === "UPI") {
    const txnId = document.getElementById("upi-txn-id").value.trim();
    const phone = document.getElementById("upi-phone").value.trim();
    const name = document.getElementById("upi-name").value.trim();

    if (!txnId || !phone || !name) {
      alert("Please fill all UPI payment details (Transaction ID, Phone, Name).");
      return;
    }

    paymentDetails = {
      transaction_id: txnId,
      phone_number: phone,
      person_name: name,
    };
  } else if (paymentMode === "DD") {
    const accountNum = document.getElementById("dd-account").value.trim();
    const mobile = document.getElementById("dd-mobile").value.trim();

    if (!accountNum || !mobile) {
      alert("Please fill all Demand Draft details (Account Number, Mobile).");
      return;
    }

    paymentDetails = {
      account_number: accountNum,
      mobile_number: mobile,
    };
  }

  const payload = {
    roll_no: rollNo,
    fee_type: feeType,
    amount: amount,
    payment_mode: paymentMode,
    payment_details: paymentDetails,
  };

  try {
    const res = await fetch(`${API_BASE}/payments/payment/update`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (res.ok) {
      const receiptId = data.receipt_id || "Generated";
      alert(`Payment recorded successfully!\nReceipt ID: ${receiptId}`);
      closeModal("paymentModal");

      // Auto-refresh the dashboard if the admin is currently viewing the student they just paid for
      if (document.getElementById("rollSearch").value.trim() === rollNo) {
        fetchPaymentDetails();
      }

      // Clear the form inputs
      document.getElementById("pay-roll").value = "";
      document.getElementById("pay-amount").value = "";
      document.getElementById("upi-txn-id").value = "";
      document.getElementById("upi-phone").value = "";
      document.getElementById("upi-name").value = "";
      document.getElementById("dd-account").value = "";
      document.getElementById("dd-mobile").value = "";
      document.getElementById("pay-mode").value = "CASH";
      updatePaymentModeFields();
    } else {
      alert("Error: " + (data.detail || "Update Failed"));
    }
  } catch (error) {
    console.error(error);
    alert("Network Error");
  }
}

function updatePaymentModeFields() {
  const paymentMode = document.getElementById("pay-mode").value;
  const upiFields = document.getElementById("upiFields");
  const ddFields = document.getElementById("ddFields");

  // Hide all fields initially
  upiFields.style.display = "none";
  ddFields.style.display = "none";

  // Show fields based on selected mode
  if (paymentMode === "UPI") {
    upiFields.style.display = "block";
  } else if (paymentMode === "DD") {
    ddFields.style.display = "block";
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