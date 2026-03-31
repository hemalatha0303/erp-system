const API_BASE = typeof API_URL !== "undefined" ? API_URL : "http://127.0.0.1:8000";
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
      `${API_BASE}/student/payments?semester=${semester}`,
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
      // Build payment mode display with details
      const paymentMode = txn.payment_mode || 'Cash';
      let paymentModeDisplay = paymentMode;
      if (txn.payment_details) {
        paymentModeDisplay += `<br/><small style="color: #666;">${txn.payment_details}</small>`;
      }
      
      txnBody.innerHTML += `
    <tr>
      <td>${txn.date}</td>
      <td style="text-align:left"><strong>${txn.type}</strong></td>
      <td>${txn.ref}</td>
      <td>${paymentModeDisplay}</td>
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

  const txn = currentPaymentData.transactions[index];
  const studentName = localStorage.getItem("studentName") || "Student";
  const rollNo = localStorage.getItem("rollNo") || "N/A";
  
  // Parse payment details based on payment mode
  let paymentDetailsHTML = '';
  if (txn.payment_mode === 'UPI' && txn.payment_details) {
    const parts = txn.payment_details.split(',').map(p => p.trim());
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
  } else if (txn.payment_mode === 'DD' && txn.payment_details) {
    const parts = txn.payment_details.split(',').map(p => p.trim());
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
      <title>Fee Receipt - ${txn.ref}</title>
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
            <div><strong>Receipt No:</strong><br><span>${txn.ref}</span></div>
            <div><strong>Roll No:</strong><br><span>${rollNo}</span></div>
          </div>
          
          <div class="detail-row">
            <div><strong>Student Name:</strong><br><span>${studentName}</span></div>
            <div><strong>Date of Payment:</strong><br><span>${txn.date}</span></div>
          </div>
          
          <div class="detail-row">
            <div><strong>Fee Category:</strong><br><span>${txn.type}</span></div>
            <div><strong>Payment Mode:</strong><br><span>${txn.payment_mode || 'Cash'}</span></div>
          </div>
          
          ${paymentDetailsHTML}
        </div>
        
        <hr class="divider">
        
        <div class="payment-section">
          <div class="payment-success-text">✓ Payment Successfully Paid</div>
          <div class="payment-amount">₹ ${txn.amount.toLocaleString()}</div>
        </div>
        
        <hr class="divider">
        
        <div class="footer">
          <p><strong>Note:</strong></p>
          <p>This is a computer-generated receipt and does not require a physical signature.<br>
          For any discrepancies, please contact the Accounts Department.</p>
          <p style="margin-top: 15px;"><strong>Remaining Balance: ₹${txn.remBalance.toLocaleString()}</strong></p>
        </div>  
      </div>
      <script>
        window.addEventListener('load', function() {
          window.print();
        });
      </script>
    </body>
    </html>
  `;
  
  receiptWindow.document.write(receiptHTML);
  receiptWindow.document.close();
}

// ============ PAYMENT SUBMISSION FUNCTIONS ============

function openPaymentModal() {
  document.getElementById("paymentModal").style.display = "flex";
}

function closePaymentModal() {
  document.getElementById("paymentModal").style.display = "none";
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

async function submitStudentPayment() {
  const feeType = document.getElementById("pay-type").value;
  const amount = parseFloat(document.getElementById("pay-amount").value);
  const paymentMode = document.getElementById("pay-mode").value;

  if (isNaN(amount) || amount <= 0) {
    alert("Please enter a valid amount.");
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
    fee_type: feeType,
    amount: amount,
    payment_mode: paymentMode,
    payment_details: paymentDetails,
  };

  try {
    const res = await fetch(`${API_BASE}/student/payments/submit`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (res.ok) {
      alert("Payment submitted successfully!");
      
      // Display receipt
      displayPaymentReceipt(data, amount, feeType, paymentMode, paymentDetails);
      
      // Reset form and close modal
      document.getElementById("pay-amount").value = "";
      document.getElementById("upi-txn-id").value = "";
      document.getElementById("upi-phone").value = "";
      document.getElementById("upi-name").value = "";
      document.getElementById("dd-account").value = "";
      document.getElementById("dd-mobile").value = "";
      document.getElementById("pay-mode").value = "CASH";
      updatePaymentModeFields();
      closePaymentModal();
      
      // Refresh the fee view
      updateFeeView();
    } else {
      alert("Error: " + (data.detail || "Payment submission failed"));
    }
  } catch (error) {
    console.error(error);
    alert("Network Error");
  }
}

function displayPaymentReceipt(data, amount, feeType, paymentMode, paymentDetails) {
  const studentName = localStorage.getItem("studentName") || "Student";
  const rollNo = localStorage.getItem("rollNo") || "N/A";
  const receiptRef = data.receipt_id || `REC-${Date.now()}`;
  const date = new Date().toLocaleString();

  // Build payment details section HTML
  let paymentDetailsHTML = '';
  if (paymentMode === 'UPI' && paymentDetails.transaction_id) {
    paymentDetailsHTML = `
      <div class="detail-row">
        <div><strong>Transaction ID:</strong><br><span>${paymentDetails.transaction_id || 'N/A'}</span></div>
        <div><strong>Phone Number:</strong><br><span>${paymentDetails.phone_number || 'N/A'}</span></div>
      </div>
      <div class="detail-row">
        <div><strong>Name of Person:</strong><br><span>${paymentDetails.person_name || 'N/A'}</span></div>
        <div>&nbsp;</div>
      </div>
    `;
  } else if (paymentMode === 'DD' && paymentDetails.account_number) {
    paymentDetailsHTML = `
      <div class="detail-row">
        <div><strong>Account Number:</strong><br><span>${paymentDetails.account_number || 'N/A'}</span></div>
        <div><strong>Mobile Number:</strong><br><span>${paymentDetails.mobile_number || 'N/A'}</span></div>
      </div>
    `;
  }

  const receiptWindow = window.open('', '_blank', 'width=750,height=700');
  const receiptHTML = `
    <!DOCTYPE html>
    <html>
    <head>
      <title>Fee Receipt - ${receiptRef}</title>
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
            <div><strong>Receipt No:</strong><br><span>${receiptRef}</span></div>
            <div><strong>Roll No:</strong><br><span>${rollNo}</span></div>
          </div>
          
          <div class="detail-row">
            <div><strong>Student Name:</strong><br><span>${studentName}</span></div>
            <div><strong>Academic Year:</strong><br><span>Current Year</span></div>
          </div>
          
          <div class="detail-row">
            <div><strong>Fee Category:</strong><br><span>${feeType}</span></div>
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

// Close modal when clicking outside
window.onclick = function(event) {
  const modal = document.getElementById("paymentModal");
  if (event.target === modal) {
    modal.style.display = "none";
  }
};
