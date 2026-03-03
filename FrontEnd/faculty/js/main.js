if (!localStorage.getItem("token")) window.location.href = "../../index.html";
function loadComponent(elementId, filePath) {
  fetch(filePath)
    .then((response) => response.text())
    .then((data) => {
      document.getElementById(elementId).innerHTML = data;
      if (elementId === "sidebar-container") highlightCurrentPage();
    });
}

function highlightCurrentPage() {
  const page = window.location.pathname.split("/").pop();
  const links = document.querySelectorAll(".nav-links a");
  links.forEach((link) => {
    if (link.getAttribute("href").includes(page)) link.classList.add("active");
  });
}
function confirmLogout() {
  localStorage.clear();
  return confirm("Are you sure you want to log out?");
}
document.addEventListener("DOMContentLoaded", () => {
  loadComponent("sidebar-container", "../components/sidebar.html");
  loadComponent("header-container", "../components/header.html");
});
