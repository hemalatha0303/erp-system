async function uploadRooms() {
  const fileInput = document.getElementById("roomFile");

  if (!fileInput.files[0]) {
    alert("Please select a file first.");
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  try {
    const res = await fetch("http://127.0.0.1:8000/admin/hostel/rooms/upload", {
      method: "POST",
      headers: {
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
      body: formData,
    });

    const data = await res.json();

    if (res.ok) {
      alert("Success: " + data.message);
      fileInput.value = "";
    } else {
      alert("Error: " + (data.detail || "Upload failed"));
    }
  } catch (error) {
    console.error(error);
    alert("Network Error: Could not connect to server.");
  }
}

async function allocateRoom() {
  const rollNo = document.getElementById("alloc-roll").value.trim();
  const roomId = document.getElementById("alloc-room-id").value.trim();

  if (!rollNo || !roomId) {
    alert("Please enter both Roll Number and Room ID.");
    return;
  }

  const payload = {
    roll_no: rollNo,
    room_number: roomId,
  };

  try {
    const res = await fetch("http://127.0.0.1:8000/admin/hostel/allocate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (res.ok) {
      alert("Success: " + data.message);

      document.getElementById("alloc-roll").value = "";
      document.getElementById("alloc-room-id").value = "";
    } else {
      alert("Error: " + (data.detail || "Allocation failed"));
    }
  } catch (error) {
    console.error(error);
    alert("Network Error: Could not connect to server.");
  }
}
async function vacateRoom() {
  const rollNo = document.getElementById("vacate-roll").value.trim();
  const roomId = document.getElementById("vacate-room-id").value.trim();

  if (!rollNo || !roomId) {
    alert("Please enter both Roll Number and Room ID.");
    return;
  }

  const payload = {
    roll_no: rollNo,
    room_number: roomId,
  };

  try {
    const res = await fetch("http://127.0.0.1:8000/admin/hostel/room/vacate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token"),
      },
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (res.ok) {
      alert("Success: " + data.message);

      document.getElementById("vacate-roll").value = "";
      document.getElementById("vacate-room-id").value = "";
    } else {
      alert("Error: " + (data.detail || "Allocation failed"));
    }
  } catch (error) {
    console.error(error);
    alert("Network Error: Could not connect to server.");
  }
}
