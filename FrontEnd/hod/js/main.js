if (!localStorage.getItem("token")) window.location.href = "../../index.html";
function loadComponent(elementId, filePath) {
  fetch(filePath)
    .then((response) => response.text())
    .then((data) => {
      document.getElementById(elementId).innerHTML = data;
    });
}

function toggleSidebar() {
  document.querySelector(".sidebar").classList.toggle("active");
}
function confirmLogout() {
  localStorage.clear();
  return confirm("Are you sure you want to log out?");
}
document.addEventListener("DOMContentLoaded", () => {
  loadComponent("sidebar-container", "../components/sidebar.html");
  loadComponent("header-container", "../components/header.html");
});
