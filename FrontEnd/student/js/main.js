if (!localStorage.getItem("token")) window.location.href = "../../index.html";

function loadComponent(elementId, filePath) {
  fetch(filePath)
    .then((response) => {
      if (!response.ok) throw new Error("Network response was not ok");
      return response.text();
    })
    .then((data) => {
      document.getElementById(elementId).innerHTML = data;

      if (elementId === "sidebar-container") {
        highlightCurrentPage();
      }
    })
    .catch((error) => console.error("Error loading component:", error));
}

function highlightCurrentPage() {
  const currentPage = window.location.pathname.split("/").pop();
  const links = document.querySelectorAll(".nav-links a");

  links.forEach((link) => {
    link.classList.remove("active");
    if (link.getAttribute("href").includes(currentPage)) {
      link.classList.add("active");
    }
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
