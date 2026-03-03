async function uploadStudents() {
  const fileInput = document.getElementById("studentFile");
  const statusBox = document.getElementById("upload-status");

  if (!fileInput.files[0]) {
    alert("Please select a file first.");
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  statusBox.innerHTML =
    "<span style='color:blue'>Uploading... Please wait.</span>";

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/admin/upload-students",
      {
        method: "POST",
        headers: {
          Authorization: "Bearer " + localStorage.getItem("token"),
        },
        body: formData,
      },
    );

    const result = await response.json();

    if (response.ok) {
      statusBox.innerHTML = `<span style='color:green'>Success: ${result.message}</span>`;
    } else {
      statusBox.innerHTML = `<span style='color:red'>Error: ${result.detail}</span>`;
    }
  } catch (error) {
    console.error(error);
    statusBox.innerHTML = "<span style='color:red'>Network Error</span>";
  }
}

document.getElementById("studentFile").addEventListener("change", function () {
  document.getElementById("file-name").textContent = this.files[0].name;
});
