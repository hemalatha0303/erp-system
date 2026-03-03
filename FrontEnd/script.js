function toggleForms() {
  const loginForm = document.getElementById("loginForm");
  const cpForm = document.getElementById("changePasswordForm");
  const msg = document.getElementById("message");

  if (loginForm.style.display === "none") {
    loginForm.style.display = "block";
    cpForm.style.display = "none";
    msg.textContent = "";
  } else {
    loginForm.style.display = "none";
    cpForm.style.display = "block";
    msg.textContent = "";
  }
}

document.getElementById("loginForm").addEventListener("submit", function (e) {
  e.preventDefault();

  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;
  const messageBox = document.getElementById("message");

  if (!username || !password) {
    messageBox.textContent = "Please fill in all fields.";
    messageBox.style.color = "red";
    return;
  }

  const loggerLogic = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: username,
          password: password,
        }),
      });

      if (!res.ok) {
        messageBox.textContent = "Invalid credentials";
        messageBox.style.color = "red";
        return;
      }

      const data = await res.json();
      const token = data.access_token;

      const payload = JSON.parse(atob(token.split(".")[1]));
      const role = payload.role;
      console.log(payload, role);
      localStorage.setItem("token", token);
      messageBox.style.color = "green";
      messageBox.textContent = `Logging in as ${role}...`;

      setTimeout(() => {
        switch (role) {
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
      const loginRes = await fetch("http://127.0.0.1:8000/auth/login", {
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
        "http://127.0.0.1:8000/auth/change-password",
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
        },
      );

      const changeData = await changeRes.json();

      if (changeRes.ok) {
        msg.textContent = "Password Changed! Please Login.";
        msg.style.color = "green";

        setTimeout(() => {
          toggleForms();
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
