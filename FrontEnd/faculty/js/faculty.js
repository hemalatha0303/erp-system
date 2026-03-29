document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("fac-name")) {
    loadFacultyDashboard();
  }
});

async function loadFacultyDashboard() {
  const options = {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  };
  const dateEl = document.getElementById("current-date");
  if (dateEl)
    dateEl.innerText = new Date().toLocaleDateString("en-US", options);

  try {
    const token = localStorage.getItem("token");
    if (!token) {
      window.location.href = "../../index.html";
      return;
    }

    const resProfile = await fetch(
      "http://127.0.0.1:8000/faculty/get-profile",
      {
        headers: { Authorization: "Bearer " + token },
      },
    );

    if (resProfile.ok) {
      const profile = await resProfile.json();

      if (document.getElementById("fac-name"))
        document.getElementById("fac-name").innerText =
          profile.last_name || "Faculty";

      if (document.getElementById("p-name"))
        document.getElementById("p-name").innerText =
          `${profile.first_name} ${profile.last_name}`;
      if (document.getElementById("p-qual"))
        document.getElementById("p-qual").innerText =
          profile.qualification || "N/A";
      if (document.getElementById("p-exp"))
        document.getElementById("p-exp").innerText =
          `${profile.experience || 0} Years`;
    }

    const resTT = await fetch("http://127.0.0.1:8000/faculty/timetable", {
      headers: { Authorization: "Bearer " + token },
    });

    if (resTT.ok) {
      const ttData = await resTT.json();
      const ttImg = document.getElementById("tt-image");
      const ttMsg = document.getElementById("tt-msg");

      if (ttData.image_url && ttImg) {
        ttImg.src = "/" + ttData.image_url;
        ttImg.style.display = "block";
        if (ttMsg) ttMsg.style.display = "none";
      } else if (ttMsg) {
        ttMsg.innerText = "No timetable uploaded yet.";
      }
    }
  } catch (error) {
    console.error("Dashboard Load Error", error);
  }
}
