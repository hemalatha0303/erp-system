// Form navigation function
function showForm(formName) {
  const loginForm = document.getElementById("loginForm");
  const cpForm = document.getElementById("changePasswordForm");
  const fpForm = document.getElementById("forgotPasswordForm");
  const rpForm = document.getElementById("resetPasswordForm");
  const msg = document.getElementById("message");

  // Hide all forms
  loginForm.style.display = "none";
  cpForm.style.display = "none";
  fpForm.style.display = "none";
  rpForm.style.display = "none";

  // Show selected form
  switch (formName) {
    case "login":
      loginForm.style.display = "block";
      break;
    case "changePassword":
      cpForm.style.display = "block";
      break;
    case "forgotPassword":
      fpForm.style.display = "block";
      break;
    case "resetPassword":
      rpForm.style.display = "block";
      break;
  }

  msg.textContent = "";
}

// Legacy function for backward compatibility
function toggleForms() {
  const loginForm = document.getElementById("loginForm");
  const cpForm = document.getElementById("changePasswordForm");
  if (loginForm.style.display === "none") {
    showForm("login");
  } else {
    showForm("changePassword");
  }
}

// LOGIN FORM HANDLER
document.getElementById("loginForm").addEventListener("submit", function (e) {
  e.preventDefault();

  const role = document.getElementById("role").value;
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;
  const messageBox = document.getElementById("message");

  if (!role || !username || !password) {
    messageBox.textContent = "Please fill in all fields.";
    messageBox.style.color = "red";
    return;
  }

  const loggerLogic = async () => {
    try {
      const res = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: username,
          password: password,
          role: role,
        }),
      });

      if (!res.ok) {
        messageBox.textContent = "Invalid credentials or role mismatch";
        messageBox.style.color = "red";
        return;
      }

      const data = await res.json();
      const token = data.access_token;

      const payload = JSON.parse(atob(token.split(".")[1]));
      const userRole = payload.role;
      console.log(payload, userRole);
      localStorage.setItem("token", token);
      messageBox.style.color = "green";
      messageBox.textContent = `Logging in as ${userRole}...`;

      setTimeout(() => {
        switch (userRole) {
          case "STUDENT":
            window.location.href = "student/html/dashboard.html";
            break;
          case "FACULTY":
            window.location.href = "faculty/html/dashboard.html";
            break;
          case "HOD":
            window.location.href = "hod/html/dashboard.html";
            break;
          case "ADMIN":
            window.location.href = "admin/html/dashboard.html";
            break;
          default:
            messageBox.style.color = "red";
            messageBox.textContent = "Unauthorized role";
        }
      }, 500);
    } catch (err) {
      console.error(err);
      messageBox.textContent = "Something went wrong";
      messageBox.style.color = "red";
    }
  };

  loggerLogic();
});

// CHANGE PASSWORD FORM HANDLER
document
  .getElementById("changePasswordForm")
  .addEventListener("submit", async function (e) {
    e.preventDefault();

    const email = document.getElementById("cp-email").value;
    const oldPass = document.getElementById("cp-old").value;
    const newPass = document.getElementById("cp-new").value;
    const msg = document.getElementById("message");

    msg.textContent = "Processing...";
    msg.style.color = "blue";

    try {
      const loginRes = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email, password: oldPass }),
      });

      if (!loginRes.ok) {
        msg.textContent = "Invalid Email or Old Password";
        msg.style.color = "red";
        return;
      }

      const loginData = await loginRes.json();
      const tempToken = loginData.access_token;

      const changeRes = await fetch(
        `${API_URL}/auth/change-password`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${tempToken}`,
          },
          body: JSON.stringify({
            old_password: oldPass,
            new_password: newPass,
          }),
        }
      );

      const changeData = await changeRes.json();

      if (changeRes.ok) {
        msg.textContent = "Password Changed! Please Login.";
        msg.style.color = "green";

        setTimeout(() => {
          showForm("login");
          document.getElementById("username").value = email;
        }, 2000);
      } else {
        msg.textContent = changeData.detail || "Update Failed";
        msg.style.color = "red";
      }
    } catch (err) {
      console.error(err);
      msg.textContent = "Network Error";
      msg.style.color = "red";
    }
  });

// FORGOT PASSWORD FORM HANDLER
document
  .getElementById("forgotPasswordForm")
  .addEventListener("submit", async function (e) {
    e.preventDefault();

    const email = document.getElementById("fp-email").value;
    const msg = document.getElementById("message");

    if (!email.endsWith("@vvit.net")) {
      msg.textContent = "Please enter a valid @vvit.net email address";
      msg.style.color = "red";
      return;
    }

    msg.textContent = "Sending reset link...";
    msg.style.color = "blue";

    try {
      const res = await fetch(`${API_URL}/auth/forgot-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email }),
      });

      const data = await res.json();

      if (res.ok) {
        msg.textContent = data.message || "Reset link sent to your personal email!";
        msg.style.color = "green";
        document.getElementById("forgotPasswordForm").reset();

        setTimeout(() => {
          showForm("login");
        }, 3000);
      } else {
        msg.textContent = data.detail || "Failed to send reset link";
        msg.style.color = "red";
      }
    } catch (err) {
      console.error(err);
      msg.textContent = "Network Error";
      msg.style.color = "red";
    }
  });

// RESET PASSWORD FORM HANDLER
document
  .getElementById("resetPasswordForm")
  .addEventListener("submit", async function (e) {
    e.preventDefault();

    const email = document.getElementById("rp-email").value;
    const token = document.getElementById("rp-token").value;
    const password = document.getElementById("rp-password").value;
    const passwordConfirm = document.getElementById("rp-password-confirm").value;
    const msg = document.getElementById("message");

    if (password !== passwordConfirm) {
      msg.textContent = "Passwords do not match";
      msg.style.color = "red";
      return;
    }

    if (password.length < 6) {
      msg.textContent = "Password must be at least 6 characters long";
      msg.style.color = "red";
      return;
    }

    msg.textContent = "Resetting password...";
    msg.style.color = "blue";

    try {
      const res = await fetch(`${API_URL}/auth/reset-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: email,
          reset_token: token,
          new_password: password,
        }),
      });

      const data = await res.json();

      if (res.ok) {
        msg.textContent = data.message || "Password reset successfully! Redirecting to login...";
        msg.style.color = "green";
        document.getElementById("resetPasswordForm").reset();

        setTimeout(() => {
          showForm("login");
        }, 2000);
      } else {
        msg.textContent = data.detail || "Failed to reset password";
        msg.style.color = "red";
      }
    } catch (err) {
      console.error(err);
      msg.textContent = "Network Error";
      msg.style.color = "red";
    }
  });

// Check for reset token in URL (for email links)
window.addEventListener("load", function () {
  const urlParams = new URLSearchParams(window.location.search);
  const token = urlParams.get("token");
  const email = urlParams.get("email");

  if (token && email) {
    document.getElementById("rp-email").value = email;
    document.getElementById("rp-token").value = token;
    showForm("resetPassword");
    document.getElementById("message").textContent =
      "Enter your new password to complete the reset";
    document.getElementById("message").style.color = "blue";
  }
});
