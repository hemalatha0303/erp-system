// Hostel Management JavaScript

const BASE_URL = window.API_BASE_URL || `${window.location.origin}/api`;
let currentEditRoomId = null;
let currentEditAllocationId = null;
let allRooms = [];
let allStudents = [];
let allAllocations = [];

// Helper function to get auth token
function getToken() {
  return localStorage.getItem("token");
}

// Helper function for API requests
async function apiRequest(endpoint, method = "GET", data = null) {
  const options = {
    method,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getToken()}`,
    },
  };

  if (data) {
    options.body = JSON.stringify(data);
  }

  try {
    const response = await fetch(`${BASE_URL}${endpoint}`, options);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error("API Error:", error);
    showAlert(`Error: ${error.message}`, "error");
    throw error;
  }
}

// Alert helper
function showAlert(message, type = "success") {
  const alertDiv = document.createElement("div");
  alertDiv.className = `alert alert-${type}`;
  alertDiv.textContent = message;
  alertDiv.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 15px 20px;
    background: ${type === "success" ? "#52c41a" : "#f5222d"};
    color: white;
    border-radius: 6px;
    z-index: 2000;
    animation: slideInRight 0.3s;
  `;

  document.body.appendChild(alertDiv);
  setTimeout(() => {
    alertDiv.remove();
  }, 3000);
}

// Initialize page
document.addEventListener("DOMContentLoaded", () => {
  loadStatistics();
  loadAllRooms();
  loadAllStudents();
  loadAllAllocations();
  setupTabButtons();
  setupAutoRefresh();
});

// Setup tab buttons
function setupTabButtons() {
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabContents = document.querySelectorAll(".tab-content");

  tabButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const tabName = button.getAttribute("data-tab");

      // Remove active class from all tabs and contents
      tabButtons.forEach((btn) => btn.classList.remove("active"));
      tabContents.forEach((content) => content.classList.remove("active"));

      // Add active class to clicked tab
      button.classList.add("active");
      document.getElementById(tabName).classList.add("active");
    });
  });
}

// Setup auto-refresh every 30 seconds
function setupAutoRefresh() {
  setInterval(() => {
    loadStatistics();
    loadAllRooms();
    loadAllAllocations();
  }, 30000);
}

// ==================== STATISTICS ====================

async function loadStatistics() {
  try {
    const data = await apiRequest("/admin/hostel/statistics");
    document.getElementById("total-rooms").textContent = data.total_rooms;
    document.getElementById("allocated-count").textContent = data.allocated;
    document.getElementById("vacated-count").textContent = data.vacated;
    document.getElementById("not-allocated-count").textContent = data.not_allocated;
  } catch (error) {
    console.error("Failed to load statistics");
  }
}

// ==================== FILE UPLOAD ====================

async function uploadRooms() {
  const fileInput = document.getElementById("roomFile");

  if (!fileInput.files[0]) {
    showAlert("Please select a file first.", "error");
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  try {
    const response = await fetch(`${BASE_URL}/admin/hostel/rooms/upload`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Upload failed");
    }

    const data = await response.json();
    showAlert(data.message);
    fileInput.value = "";
    loadAllRooms();
    loadStatistics();
  } catch (error) {
    showAlert(`Error: ${error.message}`, "error");
  }
}

// ==================== HOSTEL ROOMS ====================

async function loadAllRooms() {
  try {
    const data = await apiRequest("/admin/hostel/rooms");
    allRooms = data.rooms;
    renderRoomsTable();
    updateRoomSelect();
  } catch (error) {
    console.error("Failed to load rooms");
  }
}

function renderRoomsTable() {
  const tbody = document.getElementById("roomsTableBody");

  if (allRooms.length === 0) {
    tbody.innerHTML =
      '<tr><td colspan="7" style="text-align: center; color: #999;">No hostel rooms found</td></tr>';
    return;
  }

  tbody.innerHTML = allRooms
    .map(
      (room) => `
    <tr>
      <td><strong>${room.room_number}</strong></td>
      <td>${room.room_type}</td>
      <td>${room.sharing}</td>
      <td>${room.capacity}</td>
      <td>${room.occupied}</td>
      <td>${room.available}</td>
      <td>
        <div class="action-buttons">
          <button class="btn-edit btn-small" onclick="openEditRoomModal(${room.id})">
            <i class="fas fa-edit"></i> Edit
          </button>
          <button class="btn-delete btn-small" onclick="deleteRoom(${room.id})">
            <i class="fas fa-trash"></i> Delete
          </button>
        </div>
      </td>
    </tr>
  `
    )
    .join("");
}

async function addRoom() {
  const roomNumber = document.getElementById("room-number").value.trim();
  const sharing = parseInt(document.getElementById("room-sharing").value);
  const roomType = document.getElementById("room-type").value;
  const capacity = parseInt(document.getElementById("room-capacity").value);

  if (!roomNumber || !roomType) {
    showAlert("Please fill in all fields", "error");
    return;
  }

  try {
    const response = await apiRequest("/admin/hostel/room/create", "POST", {
      room_number: roomNumber,
      sharing,
      room_type: roomType,
      capacity,
    });

    showAlert(response.message);
    document.getElementById("roomForm").reset();
    loadAllRooms();
    loadStatistics();
  } catch (error) {
    showAlert(`Error: ${error.message}`, "error");
  }
}

function openEditRoomModal(roomId) {
  const room = allRooms.find((r) => r.id === roomId);
  if (!room) return;

  currentEditRoomId = roomId;
  document.getElementById("modalTitle").textContent = `Edit Room ${room.room_number}`;
  document.getElementById("edit-sharing").value = room.sharing;
  document.getElementById("edit-type").value = room.room_type;
  document.getElementById("edit-capacity").value = room.capacity;

  const modal = document.getElementById("editModal");
  modal.classList.add("show");
}

function closeEditModal() {
  document.getElementById("editModal").classList.remove("show");
  currentEditRoomId = null;
}

async function saveRoomChanges() {
  const sharing = parseInt(document.getElementById("edit-sharing").value);
  const roomType = document.getElementById("edit-type").value;
  const capacity = parseInt(document.getElementById("edit-capacity").value);

  if (!sharing || !roomType || !capacity) {
    showAlert("Please fill in all fields", "error");
    return;
  }

  try {
    const response = await apiRequest(
      `/admin/hostel/room/${currentEditRoomId}`,
      "PUT",
      {
        sharing,
        room_type: roomType,
        capacity,
      }
    );

    showAlert(response.message);
    closeEditModal();
    loadAllRooms();
  } catch (error) {
    showAlert(`Error: ${error.message}`, "error");
  }
}

async function deleteRoom(roomId) {
  if (!confirm("Are you sure you want to delete this room?")) return;

  try {
    const response = await apiRequest(
      `/admin/hostel/room/${roomId}`,
      "DELETE"
    );

    showAlert(response.message);
    loadAllRooms();
    loadStatistics();
  } catch (error) {
    showAlert(`Error: ${error.message}`, "error");
  }
}

function updateRoomSelect() {
  const select = document.getElementById("room-select");
  select.innerHTML = '<option value="">Select a room</option>';

  allRooms
    .filter((room) => room.available > 0)
    .forEach((room) => {
      const option = document.createElement("option");
      option.value = room.id;
      option.textContent = `${room.room_number} (${room.available} available)`;
      select.appendChild(option);
    });
}

// ==================== STUDENTS ====================

async function loadAllStudents() {
  try {
    const data = await apiRequest("/admin/hostel/students");
    allStudents = data.students;
  } catch (error) {
    console.error("Failed to load students");
  }
}

function getStudentByRollNo(rollNo) {
  return allStudents.find((s) => s.roll_no === rollNo);
}

// ==================== ALLOCATIONS ====================

async function loadAllAllocations() {
  try {
    const data = await apiRequest("/admin/hostel/allocations");
    allAllocations = data.allocations;
    renderAllocationsTable();
  } catch (error) {
    console.error("Failed to load allocations");
  }
}

function renderAllocationsTable() {
  const tbody = document.getElementById("allocationsTableBody");

  if (allAllocations.length === 0) {
    tbody.innerHTML =
      '<tr><td colspan="9" style="text-align: center; color: #999;">No allocations found</td></tr>';
    return;
  }

  tbody.innerHTML = allAllocations
    .map(
      (alloc) => `
    <tr>
      <td><strong>${alloc.roll_no}</strong></td>
      <td>${alloc.name}</td>
      <td>${alloc.year}</td>
      <td>${alloc.branch}</td>
      <td>${alloc.section}</td>
      <td>${alloc.room_number}</td>
      <td>${alloc.room_type}</td>
      <td>
        <span class="status-badge status-${alloc.status.toLowerCase()}">
          ${alloc.status}
        </span>
      </td>
      <td>
        <div class="action-buttons">
          <button class="btn-status btn-small" onclick="openStatusModal(${alloc.allocation_id})">
            <i class="fas fa-exchange-alt"></i> Update
          </button>
        </div>
      </td>
    </tr>
  `
    )
    .join("");
}

async function allocateStudent() {
  const rollNo = document.getElementById("student-rollno").value.trim();
  const roomId = document.getElementById("room-select").value;

  if (!rollNo || !roomId) {
    showAlert("Please enter roll number and select a room", "error");
    return;
  }

  // Find student by roll number
  const student = getStudentByRollNo(rollNo);
  if (!student) {
    showAlert(`Student with roll number ${rollNo} not found`, "error");
    return;
  }

  try {
    const response = await apiRequest("/admin/hostel/allocation/create", "POST", {
      student_id: student.id,
      room_id: parseInt(roomId),
    });

    showAlert(response.message);
    document.getElementById("allocationForm").reset();
    loadAllAllocations();
    loadAllRooms();
    loadStatistics();
  } catch (error) {
    showAlert(`Error: ${error.message}`, "error");
  }
}

function openStatusModal(allocationId) {
  const allocation = allAllocations.find((a) => a.allocation_id === allocationId);
  if (!allocation) return;

  currentEditAllocationId = allocationId;
  document.getElementById("status-select").value = allocation.status;

  const modal = document.getElementById("statusModal");
  modal.classList.add("show");
}

function closeStatusModal() {
  document.getElementById("statusModal").classList.remove("show");
  currentEditAllocationId = null;
}

async function updateAllocationStatus() {
  const newStatus = document.getElementById("status-select").value;

  if (!newStatus) {
    showAlert("Please select a status", "error");
    return;
  }

  try {
    const response = await apiRequest(
      `/admin/hostel/allocation/${currentEditAllocationId}/status`,
      "PUT",
      {
        allocation_id: currentEditAllocationId,
        status: newStatus,
      }
    );

    showAlert(response.message);
    closeStatusModal();
    loadAllAllocations();
    loadAllRooms();
    loadStatistics();
  } catch (error) {
    showAlert(`Error: ${error.message}`, "error");
  }
}

// Close modal when clicking outside
document.addEventListener("click", (event) => {
  const editModal = document.getElementById("editModal");
  const statusModal = document.getElementById("statusModal");

  if (event.target === editModal) {
    closeEditModal();
  }
  if (event.target === statusModal) {
    closeStatusModal();
  }
});
