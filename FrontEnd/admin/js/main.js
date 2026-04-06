if (!localStorage.getItem("token")) window.location.href = "../../index.html";

const API_BASE = `${window.location.protocol}//${window.location.hostname}:8000`;
const LOCAL_API_ORIGIN = "http://127.0.0.1:8000";
const _origFetch = window.fetch.bind(window);
window.fetch = (input, init) => {
  if (typeof input === "string" && input.startsWith(LOCAL_API_ORIGIN)) {
    return _origFetch(input.replace(LOCAL_API_ORIGIN, API_BASE), init);
  }
  if (input instanceof Request && input.url.startsWith(LOCAL_API_ORIGIN)) {
    return _origFetch(new Request(input.url.replace(LOCAL_API_ORIGIN, API_BASE), input), init);
  }
  return _origFetch(input, init);
};

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
  const sidebar = document.querySelector(".sidebar");
  sidebar.classList.toggle("active");

  const mainContent = document.querySelector(".main-content");
  if (window.innerWidth <= 768) {
    if (sidebar.classList.contains("active")) {
      mainContent.style.marginLeft = "250px";
    } else {
      mainContent.style.marginLeft = "0";
    }
  }
}
function confirmLogout(event) {
  event.preventDefault();
  if (confirm("Are you sure you want to log out?")) {
    localStorage.clear();
    window.location.href = "../../index.html";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadComponent("sidebar-container", "../components/sidebar.html");
  loadComponent("header-container", "../components/header.html");
});
