if (!localStorage.getItem("token")) window.location.href = "../../index.html";

const API_BASE = `${window.location.origin}/api`;
const LOCAL_API_ORIGINS = [
  "http://127.0.0.1:8000",
  "http://localhost:8000",
  "http://0.0.0.0:8000",
];
window.API_BASE_URL = API_BASE;
window.API_URL = API_BASE;
const _origFetch = window.fetch.bind(window);

function rewriteApiUrl(url) {
  for (const origin of LOCAL_API_ORIGINS) {
    if (url.startsWith(origin)) {
      return `${API_BASE}${url.slice(origin.length)}`;
    }
  }
  return url;
}

window.fetch = (input, init) => {
  if (typeof input === "string") {
    return _origFetch(rewriteApiUrl(input), init);
  }
  if (input instanceof Request) {
    const rewrittenUrl = rewriteApiUrl(input.url);
    if (rewrittenUrl !== input.url) {
      return _origFetch(new Request(rewrittenUrl, input), init);
    }
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
  document.querySelector(".sidebar").classList.toggle("active");
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
